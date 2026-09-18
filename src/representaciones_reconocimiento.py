# Dashboard · Semana 07 — Representaciones del reconocimiento
"""Experimento reproducible de Semana 07 adaptado al dominio logístico."""

from __future__ import annotations

import json
from pathlib import Path

from src.representaciones.reconocimiento import (
    contexto_dataset,
    evaluar_parada,
    evaluaciones_pod,
)


ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "sem-07-representaciones-evidencia.md"


def ejecutar_representaciones() -> dict:
    """Ejecuta las tres representaciones sobre los mismos perfiles Amazon."""
    contexto = contexto_dataset()
    perfiles = contexto["perfiles"]
    evaluaciones = [evaluar_parada(perfil["pedido_id"]) for perfil in perfiles]
    return {
        "contexto": contexto,
        "evaluaciones": evaluaciones,
        "pod": evaluaciones_pod(),
    }


def generar_evidencia(resultados: dict | None = None) -> str:
    """Genera la evidencia Markdown a partir de una ejecución reproducible."""
    resultados = resultados or ejecutar_representaciones()
    contexto = resultados["contexto"]
    perfiles = contexto["perfiles"]
    evaluaciones = resultados["evaluaciones"]
    pod = resultados["pod"]

    lineas = [
        "# Semana 07 — Evidencia reproducible de representaciones",
        "",
        "> Generado por `python -m src.representaciones_reconocimiento`.",
        "",
        "## 1. Datos reales Amazon",
        "",
    ]
    estadisticas = contexto["estadisticas"]
    lineas += [
        f"- Registros procesados: **{contexto['fuente']['total_registros']:,}**.",
        f"- Rutas: **{contexto['fuente']['rutas']}**.",
        f"- Variables: `{estadisticas['campos']}`.",
        f"- Mediana: `{estadisticas['mediana']}`.",
        f"- P75: `{estadisticas['q3']}`.",
        f"- IQR: `{estadisticas['iqr']}`.",
        "",
        "### Distribución de hechos derivados",
        "",
        "| Hechos activados | Registros |",
        "|---:|---:|",
    ]
    for item in contexto["distribucion_hechos"]:
        lineas.append(f"| {item['cantidad_hechos']} | {item['registros']:,} |")

    lineas += [
        "",
        "## 2. Perfiles demostrativos reales",
        "",
        "| Criterio | Pedido | Vector | Distancia normalizada | Hechos |",
        "|---|---|---|---:|---|",
    ]
    for perfil, evaluacion in zip(perfiles, evaluaciones):
        lineas.append(
            f"| {perfil['criterio']} | `{perfil['pedido_id']}` | "
            f"`{perfil['vector']}` | {evaluacion['numerica']['distancia_normalizada']:.3f} | "
            f"`{evaluacion['simbolica']['hechos']}` |"
        )

    lineas += [
        "",
        "## 3. AFD logístico POD — escenarios controlados",
        "",
        "> Amazon no registra eventos A/V/F/C; estas secuencias son pruebas diseñadas.",
        "",
        "| Secuencia | Estado final | ¿Aceptada? |",
        "|---|---|---|",
    ]
    for item in pod:
        lineas.append(f"| `{item['secuencia']}` | `{item['estado_final']}` | **{item['aceptada']}** |")

    lineas += [
        "",
        "## 4. Procedencia serializada",
        "",
        "```json",
        json.dumps(evaluaciones[0]["procedencia"], ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lineas), encoding="utf-8")
    return "\n".join(lineas)


def mostrar_resultados(resultados: dict) -> None:
    """Muestra en consola las salidas numéricas, simbólicas y secuenciales."""
    print("Representación numérica — distancia euclidiana normalizada")
    for evaluacion in resultados["evaluaciones"]:
        print(
            f"  {evaluacion['pedido']['pedido_id']}: "
            f"{evaluacion['numerica']['distancia_normalizada']:.3f}"
        )

    print("\nRepresentación simbólica — hechos y conclusiones")
    for evaluacion in resultados["evaluaciones"]:
        acciones = [
            regla["accion"]
            for regla in evaluacion["simbolica"]["reglas_activadas"]
        ]
        print(
            f"  {evaluacion['pedido']['pedido_id']}: "
            f"hechos={evaluacion['simbolica']['hechos']}; conclusiones={acciones}"
        )

    print("\nAutómata POD — aceptación de secuencias")
    for evaluacion in resultados["pod"]:
        veredicto = "aceptada" if evaluacion["aceptada"] else "rechazada"
        print(
            f"  {evaluacion['secuencia']}: {veredicto} "
            f"({evaluacion['estado_final']})"
        )


def main() -> int:
    resultados = ejecutar_representaciones()
    generar_evidencia(resultados)
    mostrar_resultados(resultados)
    print(f"\nReporte generado: {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
