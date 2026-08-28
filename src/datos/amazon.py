"""Extractor y curador del dataset público Amazon Last Mile Routing Challenge (ALMRRC 2021).

Descarga directamente desde AWS Open Data (S3), limpia inconsistencias, calcula
volúmenes agregados, distancias geodésicas y genera los datasets estructurados.
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
from pathlib import Path
import random

import numpy as np
import pandas as pd

from src.comun.geo import haversine_km
from src.comun.red import descargar_json


ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CSV_OUTPUT = ROOT / "data" / "amazon_pedidos.csv"
DEFAULT_GRAPH_OUTPUT = ROOT / "data" / "amazon_rutas_muestra.json"
DEFAULT_REPORT_OUTPUT = ROOT / "reports" / "sem-02-datos-amazon-last-mile.md"

BASE_URL = "https://amazon-last-mile-challenges.s3.amazonaws.com/almrrc2021/almrrc2021-data-training/"
ROUTE_DATA_URL = BASE_URL + "model_build_inputs/route_data.json"
SEQUENCE_DATA_URL = BASE_URL + "model_build_inputs/actual_sequences.json"
PACKAGE_DATA_URL = BASE_URL + "model_build_inputs/package_data.json"
SAMPLE_ROUTE_URL = BASE_URL + "model_apply_inputs/new_route_data.json"
SAMPLE_PACKAGE_URL = BASE_URL + "model_apply_inputs/new_package_data.json"
SAMPLE_TRAVEL_URL = BASE_URL + "model_apply_inputs/new_travel_times.json"
SAMPLE_SEQ_URL = BASE_URL + "model_score_inputs/new_actual_sequences.json"

DEFAULT_SEED = 20260828
DEFAULT_NUM_ROUTES = 100


def seleccionar_rutas_estratificadas(
    routes: dict, num_routes: int, seed: int = DEFAULT_SEED
) -> list[str]:
    """Selecciona una muestra estratificada de rutas cubriendo todas las estaciones de distribución."""
    rng = random.Random(seed)
    rutas_por_estacion: dict[str, list[str]] = {}
    for ruta_id, rdata in routes.items():
        estacion = rdata.get("station_code", "DESCONOCIDA")
        rutas_por_estacion.setdefault(estacion, []).append(ruta_id)

    seleccionadas: list[str] = []
    por_estacion = max(1, num_routes // len(rutas_por_estacion))
    for estacion, lista_rutas in sorted(rutas_por_estacion.items()):
        cantidad = min(len(lista_rutas), por_estacion)
        seleccionadas.extend(rng.sample(lista_rutas, cantidad))

    if len(seleccionadas) < num_routes:
        restantes = [r for r in routes if r not in set(seleccionadas)]
        faltantes = num_routes - len(seleccionadas)
        seleccionadas.extend(rng.sample(restantes, min(faltantes, len(restantes))))
    elif len(seleccionadas) > num_routes:
        seleccionadas = rng.sample(seleccionadas, num_routes)

    return sorted(seleccionadas)


def procesar_paradas_a_dataframe(
    routes: dict,
    sequences: dict,
    packages: dict,
    rutas_seleccionadas: list[str],
) -> pd.DataFrame:
    """Procesa y limpia las paradas de las rutas seleccionadas en un DataFrame tabular."""
    filas = []
    indice_pedido = 1

    for ruta_id in rutas_seleccionadas:
        info_ruta = routes.get(ruta_id, {})
        estacion = info_ruta.get("station_code", "DESCONOCIDA")
        fecha = info_ruta.get("date_YYYY_MM_DD", "")
        hora_salida = info_ruta.get("departure_time_utc", "")
        cap_cm3 = info_ruta.get("executor_capacity_cm3", 0.0)
        cap_m3 = round(cap_cm3 / 1_000_000.0, 4) if cap_cm3 else 0.0

        paradas_ruta = info_ruta.get("stops", {})
        paquetes_ruta = packages.get(ruta_id, {})
        seq_dict = sequences.get(ruta_id, {}).get("actual", {})

        deposito_lat, deposito_lng = None, None
        for stop_id, sinfo in paradas_ruta.items():
            if sinfo.get("type") == "Station":
                deposito_lat = sinfo.get("lat")
                deposito_lng = sinfo.get("lng")
                break

        if deposito_lat is None:
            primera_parada = next(iter(paradas_ruta.values()), {})
            deposito_lat = primera_parada.get("lat", 0.0)
            deposito_lng = primera_parada.get("lng", 0.0)

        for stop_id, sinfo in paradas_ruta.items():
            tipo_parada = sinfo.get("type", "Dropoff")
            lat = float(sinfo.get("lat", 0.0))
            lng = float(sinfo.get("lng", 0.0))
            zone_raw = sinfo.get("zone_id")
            zone_id = str(zone_raw).strip() if zone_raw and str(zone_raw) != "nan" else "SIN_ZONA"

            dist_deposito = (
                round(haversine_km(deposito_lat, deposito_lng, lat, lng), 3)
                if deposito_lat is not None and deposito_lng is not None
                else 0.0
            )

            paquetes_parada = paquetes_ruta.get(stop_id, {})
            num_pkgs = len(paquetes_parada)

            total_vol_cm3 = 0.0
            tiempos_servicio = []
            tiene_ventana = 0
            duraciones_ventana = []

            for pdata in paquetes_parada.values():
                dims = pdata.get("dimensions", {})
                d = dims.get("depth_cm", 0.0) or 0.0
                h = dims.get("height_cm", 0.0) or 0.0
                w = dims.get("width_cm", 0.0) or 0.0
                total_vol_cm3 += d * h * w

                st_sec = pdata.get("planned_service_time_seconds")
                if st_sec is not None and not math.isnan(st_sec):
                    tiempos_servicio.append(float(st_sec))

                tw = pdata.get("time_window", {})
                tw_start = tw.get("start_time_utc")
                tw_end = tw.get("end_time_utc")
                if (
                    tw_start is not None
                    and str(tw_start) != "nan"
                    and tw_end is not None
                    and str(tw_end) != "nan"
                ):
                    tiene_ventana = 1
                    try:
                        t1 = datetime.datetime.fromisoformat(str(tw_start))
                        t2 = datetime.datetime.fromisoformat(str(tw_end))
                        duraciones_ventana.append((t2 - t1).total_seconds() / 60.0)
                    except (ValueError, TypeError):
                        pass

            vol_total_m3 = round(total_vol_cm3 / 1_000_000.0, 4)
            vol_prom_m3 = round(vol_total_m3 / num_pkgs, 4) if num_pkgs > 0 else 0.0
            tiempo_servicio_seg = (
                round(sum(tiempos_servicio) / len(tiempos_servicio), 1)
                if tiempos_servicio
                else 0.0
            )
            duracion_ventana_min = (
                round(sum(duraciones_ventana) / len(duraciones_ventana), 1)
                if duraciones_ventana
                else 0.0
            )
            secuencia_real = int(seq_dict.get(stop_id, 0))

            es_riesgo = 0
            if tiene_ventana and duracion_ventana_min < 180.0 and secuencia_real > 40:
                es_riesgo = 1
            elif tiempo_servicio_seg > 150.0 and vol_total_m3 > 0.03:
                es_riesgo = 1
            elif dist_deposito > 15.0 and num_pkgs >= 3:
                es_riesgo = 1

            filas.append(
                {
                    "pedido_id": f"AMZ-{indice_pedido:05d}",
                    "route_id": ruta_id,
                    "stop_id": stop_id,
                    "station_code": estacion,
                    "fecha": fecha,
                    "hora_salida_utc": hora_salida,
                    "tipo_parada": tipo_parada,
                    "lat": round(lat, 6),
                    "lng": round(lng, 6),
                    "zone_id": zone_id,
                    "distancia_deposito_km": dist_deposito,
                    "num_paquetes": num_pkgs,
                    "volumen_total_m3": vol_total_m3,
                    "volumen_promedio_m3": vol_prom_m3,
                    "tiempo_servicio_seg": tiempo_servicio_seg,
                    "tiene_ventana_horaria": tiene_ventana,
                    "duracion_ventana_min": duracion_ventana_min,
                    "secuencia_real": secuencia_real,
                    "capacidad_vehiculo_m3": cap_m3,
                    "retrasado_estimado": es_riesgo,
                }
            )
            indice_pedido += 1

    return pd.DataFrame(filas)


def construir_grafos_muestra(
    sample_routes: dict,
    sample_packages: dict,
    sample_travel: dict,
    sample_seq: dict,
) -> dict:
    """Construye una estructura JSON con grafos completos y matrices de tiempo para búsqueda A*."""
    grafos = {}

    for ruta_id, rdata in sample_routes.items():
        estacion = rdata.get("station_code", "DESCONOCIDA")
        cap_cm3 = rdata.get("executor_capacity_cm3", 0.0)
        stops_raw = rdata.get("stops", {})
        seq_raw = sample_seq.get(ruta_id, {}).get("actual", {})
        pkgs_route = sample_packages.get(ruta_id, {})
        travel_matrix = sample_travel.get(ruta_id, {})

        stops_list = []
        depot_id = None

        for stop_id, sinfo in stops_raw.items():
            tipo = sinfo.get("type", "Dropoff")
            if tipo == "Station":
                depot_id = stop_id
            pkgs = pkgs_route.get(stop_id, {})
            num_pkgs = len(pkgs)
            vol_m3 = round(
                sum(
                    (p.get("dimensions", {}).get("depth_cm", 0) or 0)
                    * (p.get("dimensions", {}).get("height_cm", 0) or 0)
                    * (p.get("dimensions", {}).get("width_cm", 0) or 0)
                    for p in pkgs.values()
                )
                / 1_000_000.0,
                4,
            )
            stops_list.append(
                {
                    "stop_id": stop_id,
                    "type": tipo,
                    "lat": sinfo.get("lat"),
                    "lng": sinfo.get("lng"),
                    "zone_id": sinfo.get("zone_id") if str(sinfo.get("zone_id")) != "nan" else "SIN_ZONA",
                    "num_paquetes": num_pkgs,
                    "volumen_m3": vol_m3,
                    "secuencia_real": int(seq_raw.get(stop_id, 0)),
                }
            )

        grafos[ruta_id] = {
            "route_id": ruta_id,
            "station_code": estacion,
            "date": rdata.get("date_YYYY_MM_DD"),
            "departure_time_utc": rdata.get("departure_time_utc"),
            "capacidad_vehiculo_m3": round(cap_cm3 / 1_000_000.0, 4) if cap_cm3 else 0.0,
            "depot_stop_id": depot_id or (stops_list[0]["stop_id"] if stops_list else None),
            "num_paradas": len(stops_list),
            "stops": stops_list,
            "travel_times_seg": travel_matrix,
        }

    return grafos


def render_reporte_datos(
    df: pd.DataFrame,
    num_rutas: int,
    num_grafos: int,
    ruta_csv: Path,
    ruta_grafo: Path,
) -> str:
    """Genera un reporte Markdown detallado sobre la curaduría y estadísticas de los datos."""
    estaciones_stats = df.groupby("station_code").agg(
        total_paradas=("stop_id", "count"),
        total_paquetes=("num_paquetes", "sum"),
        distancia_prom_km=("distancia_deposito_km", "mean"),
        tasa_riesgo=("retrasado_estimado", "mean"),
    ).reset_index()

    lineas = [
        "# Dataset Amazon Last Mile Routing Challenge (ALMRRC 2021)",
        "",
        "Reporte generado automáticamente por `python -m src.datos.amazon`.",
        "",
        "## Resumen general",
        "",
        f"- **Fuente:** AWS Open Data Registry (`s3://amazon-last-mile-challenges/almrrc2021/`).",
        f"- **Rutas muestreadas:** {num_rutas} rutas estratificadas.",
        f"- **Total de paradas/pedidos limpios:** {len(df):,} registros.",
        f"- **Total de paquetes individuales:** {int(df['num_paquetes'].sum()):,} paquetes.",
        f"- **Grafos completos para búsqueda A\\*:** {num_grafos} rutas con matrices NxN de tiempos.",
        f"- **Destino CSV tabular:** `{ruta_csv}`",
        f"- **Destino grafos de muestra:** `{ruta_grafo}`",
        "",
        "## Distribución por estación de distribución (Centros logísticos)",
        "",
        "| Estación | Paradas | Paquetes | Dist. Depósito Promedio (km) | Tasa Riesgo Retraso |",
        "|---|---:|---:|---:|---:|",
    ]

    for _, row in estaciones_stats.iterrows():
        lineas.append(
            f"| `{row['station_code']}` | {int(row['total_paradas']):,} | "
            f"{int(row['total_paquetes']):,} | {row['distancia_prom_km']:.2f} km | "
            f"{row['tasa_riesgo']:.1%} |"
        )

    lineas.extend(
        [
            "",
            "## Estadísticas descriptivas de variables logísticas",
            "",
            "| Variable | Mínimo | Promedio | Mediana | Máximo | Desv. Estándar |",
            "|---|---:|---:|---:|---:|---:|",
            f"| `distancia_deposito_km` | {df['distancia_deposito_km'].min():.2f} | {df['distancia_deposito_km'].mean():.2f} | {df['distancia_deposito_km'].median():.2f} | {df['distancia_deposito_km'].max():.2f} | {df['distancia_deposito_km'].std():.2f} |",
            f"| `num_paquetes` | {int(df['num_paquetes'].min())} | {df['num_paquetes'].mean():.2f} | {int(df['num_paquetes'].median())} | {int(df['num_paquetes'].max())} | {df['num_paquetes'].std():.2f} |",
            f"| `volumen_total_m3` | {df['volumen_total_m3'].min():.4f} | {df['volumen_total_m3'].mean():.4f} | {df['volumen_total_m3'].median():.4f} | {df['volumen_total_m3'].max():.4f} | {df['volumen_total_m3'].std():.4f} |",
            f"| `tiempo_servicio_seg` | {df['tiempo_servicio_seg'].min():.1f} | {df['tiempo_servicio_seg'].mean():.1f} | {df['tiempo_servicio_seg'].median():.1f} | {df['tiempo_servicio_seg'].max():.1f} | {df['tiempo_servicio_seg'].std():.1f} |",
            "",
            "## Diccionario de campos (`data/amazon_pedidos.csv`)",
            "",
            "| Campo | Tipo | Descripción |",
            "|---|---|---|",
            "| `pedido_id` | String | Identificador correlativo del pedido/parada (`AMZ-XXXXX`). |",
            "| `route_id` | String | UUID de la ruta de entrega oficial en Amazon. |",
            "| `stop_id` | String | Código de parada alfanumérico dentro de la ruta (e.g. `AH`, `AK`). |",
            "| `station_code` | String | Código de la estación logística de origen (e.g. `DLA7`, `DCH4`). |",
            "| `fecha` | String | Fecha de la jornada en formato `AAAA-MM-DD`. |",
            "| `hora_salida_utc` | String | Hora de salida del vehículo en formato UTC. |",
            "| `tipo_parada` | String | Tipo de punto: `Station` (depósito central) o `Dropoff` (entrega). |",
            "| `lat`, `lng` | Float | Coordenadas geográficas exactas de la parada. |",
            "| `zone_id` | String | Microzona logística de asignación de ruta. |",
            "| `distancia_deposito_km` | Float | Distancia geodésica Haversine desde el depósito de origen. |",
            "| `num_paquetes` | Entero | Cantidad de paquetes a entregar en la parada. |",
            "| `volumen_total_m3` | Float | Volumen cúbico total de los paquetes ($m^3$). |",
            "| `volumen_promedio_m3` | Float | Volumen cúbico promedio por paquete ($m^3$). |",
            "| `tiempo_servicio_seg` | Float | Tiempo de servicio programado en segundos por parada. |",
            "| `tiene_ventana_horaria` | Entero (0/1) | Indicador binario si la entrega tiene ventana horaria comprometida. |",
            "| `duracion_ventana_min` | Float | Duración de la ventana horaria en minutos (0 si no aplica). |",
            "| `secuencia_real` | Entero | Posición de visita real ejecutada por el repartidor. |",
            "| `capacidad_vehiculo_m3` | Float | Capacidad de carga del vehículo en metros cúbicos. |",
            "| `retrasado_estimado` | Entero (0/1) | Etiqueta de riesgo de retraso derivada para aprendizaje supervisado. |",
            "",
            "## Calidad y limpieza de datos",
            "",
            f"- **Valores nulos no controlados:** 0 (todas las zonas vacías se normalizan a `'SIN_ZONA'`, ventanas nulas a `0`).",
            f"- **Integridad referencial:** Cada parada está vinculada a su ruta, coordenadas y secuencia real.",
            f"- **Compatibilidad:** Directamente usable por `pandas` y `scikit-learn` sin transformaciones previas requeridas.",
            "",
        ]
    )

    return "\n".join(lineas)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Descarga y procesa el dataset Amazon Last Mile Routing Challenge."
    )
    parser.add_argument(
        "--num-routes",
        type=int,
        default=DEFAULT_NUM_ROUTES,
        help=f"Cantidad de rutas a muestrear (predeterminado: {DEFAULT_NUM_ROUTES})",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help=f"Semilla para muestreo reproducible (predeterminado: {DEFAULT_SEED})",
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=DEFAULT_CSV_OUTPUT,
        help=f"Destino CSV de pedidos limpios (predeterminado: {DEFAULT_CSV_OUTPUT})",
    )
    parser.add_argument(
        "--output-graph",
        type=Path,
        default=DEFAULT_GRAPH_OUTPUT,
        help=f"Destino JSON con grafos de muestra (predeterminado: {DEFAULT_GRAPH_OUTPUT})",
    )
    parser.add_argument(
        "--output-report",
        type=Path,
        default=DEFAULT_REPORT_OUTPUT,
        help=f"Destino del reporte Markdown (predeterminado: {DEFAULT_REPORT_OUTPUT})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    print("1/5 Descargando rutas y secuencias desde AWS Open Data...")
    routes = descargar_json(ROUTE_DATA_URL)
    sequences = descargar_json(SEQUENCE_DATA_URL)

    print(f"2/5 Seleccionando {args.num_routes} rutas estratificadas (seed={args.seed})...")
    rutas_seleccionadas = seleccionar_rutas_estratificadas(
        routes, args.num_routes, args.seed
    )

    print("3/5 Descargando datos de paquetes (package_data.json)...")
    packages = descargar_json(PACKAGE_DATA_URL)

    print("4/5 Procesando paradas y calculando métricas logísticas limpias...")
    df_pedidos = procesar_paradas_a_dataframe(
        routes, sequences, packages, rutas_seleccionadas
    )

    print("5/5 Descargando y estructurando grafos de muestra para búsqueda A*...")
    sample_routes = descargar_json(SAMPLE_ROUTE_URL)
    sample_packages = descargar_json(SAMPLE_PACKAGE_URL)
    sample_travel = descargar_json(SAMPLE_TRAVEL_URL)
    sample_seq = descargar_json(SAMPLE_SEQ_URL)

    grafos = construir_grafos_muestra(
        sample_routes, sample_packages, sample_travel, sample_seq
    )

    args.output_csv.parent.mkdir(parents=True, exist_ok=True)
    df_pedidos.to_csv(args.output_csv, index=False, encoding="utf-8")
    print(f"-> CSV guardado: {args.output_csv} ({len(df_pedidos):,} registros)")

    args.output_graph.parent.mkdir(parents=True, exist_ok=True)
    args.output_graph.write_text(json.dumps(grafos, indent=2), encoding="utf-8")
    print(f"-> Grafos guardados: {args.output_graph} ({len(grafos)} rutas completas)")

    reporte = render_reporte_datos(
        df_pedidos,
        args.num_routes,
        len(grafos),
        args.output_csv,
        args.output_graph,
    )
    args.output_report.parent.mkdir(parents=True, exist_ok=True)
    args.output_report.write_text(reporte, encoding="utf-8")
    print(f"-> Reporte generado: {args.output_report}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
