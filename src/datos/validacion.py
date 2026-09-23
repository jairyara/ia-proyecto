"""Valida una instantánea CSV completa antes de escribir, sin pandas ni floats."""

import csv
from dataclasses import dataclass
from datetime import date, time
from decimal import Decimal, InvalidOperation
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import re


COLUMNAS = (
    "pedido_id", "route_id", "stop_id", "station_code", "fecha", "hora_salida_utc",
    "tipo_parada", "lat", "lng", "zone_id", "distancia_deposito_km", "num_paquetes",
    "volumen_total_m3", "volumen_promedio_m3", "tiempo_servicio_seg",
    "tiene_ventana_horaria", "duracion_ventana_min", "secuencia_real",
    "capacidad_vehiculo_m3", "retrasado_estimado",
)
DECIMALES = (
    "lat", "lng", "distancia_deposito_km", "volumen_total_m3", "volumen_promedio_m3",
    "tiempo_servicio_seg", "duracion_ventana_min", "capacidad_vehiculo_m3",
)
CAMPOS_RUTA = ("station_code", "fecha", "hora_salida_utc", "capacidad_vehiculo_m3")


class ErrorValidacion(ValueError):
    """Fuente inválida; nunca se salta una fila para completar el seed."""


@dataclass(frozen=True)
class ManifiestoAmazon:
    fuente: str
    version: str
    sha256: str
    procedencia: str
    paradas: int
    rutas: int
    estaciones: int

    def __post_init__(self):
        if self.fuente != "amazon-logistica":
            raise ErrorValidacion("El importador solo admite fuente amazon-logistica.")
        if not isinstance(self.version, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", self.version):
            raise ErrorValidacion("Versión inválida en manifiesto.")
        if not isinstance(self.sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", self.sha256):
            raise ErrorValidacion("SHA-256 inválido en manifiesto.")
        if not isinstance(self.procedencia, str) or not self.procedencia.strip():
            raise ErrorValidacion("Falta procedencia en manifiesto.")
        if any(type(n) is not int or n <= 0 for n in (self.paradas, self.rutas, self.estaciones)):
            raise ErrorValidacion("Los conteos del manifiesto deben ser enteros positivos.")


def cargar_manifiesto(ruta: Path) -> ManifiestoAmazon:
    try:
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        return ManifiestoAmazon(**datos)
    except (TypeError, json.JSONDecodeError, UnicodeError) as exc:
        raise ErrorValidacion("Formato de manifiesto inválido.") from exc


@dataclass(frozen=True)
class AmazonValidado:
    filas: tuple[dict, ...]
    rutas: dict[str, dict]
    estaciones: tuple[str, ...]


def _fila(fila: dict) -> dict:
    if None in fila or any(v is None or not v or v != v.strip() for v in fila.values()):
        raise ErrorValidacion("Columnas faltantes/sobrantes, valores vacíos o espacios externos.")
    for campo, limite in (("pedido_id", 80), ("route_id", 100), ("stop_id", 40), ("station_code", 40), ("zone_id", 80)):
        if len(fila[campo]) > limite or any(ord(c) < 32 for c in fila[campo]):
            raise ErrorValidacion(f"Texto inválido en {campo}.")
    resultado = dict(fila)
    for campo in DECIMALES:
        if not re.fullmatch(r"-?\d+(?:\.\d+)?", fila[campo], flags=re.ASCII):
            raise ErrorValidacion(f"Decimal inválido en {campo}.")
        valor = Decimal(fila[campo])
        if not valor.is_finite() or (campo not in ("lat", "lng") and valor < 0):
            raise ErrorValidacion(f"Valor fuera de rango en {campo}.")
        resultado[campo] = valor
    if not -90 <= resultado["lat"] <= 90 or not -180 <= resultado["lng"] <= 180:
        raise ErrorValidacion("Coordenadas fuera de rango.")
    if resultado["capacidad_vehiculo_m3"] <= 0:
        raise ErrorValidacion("Capacidad del vehículo debe ser positiva.")
    for campo in ("num_paquetes", "secuencia_real"):
        if not re.fullmatch(r"\d+", fila[campo], flags=re.ASCII) or int(fila[campo]) > 2147483647:
            raise ErrorValidacion(f"Entero no negativo inválido en {campo}.")
        resultado[campo] = int(fila[campo])
    for campo in ("tiene_ventana_horaria", "retrasado_estimado"):
        if fila[campo] not in ("0", "1"):
            raise ErrorValidacion(f"Bandera inválida en {campo}; usar 0/1.")
        resultado[campo] = fila[campo] == "1"
    if fila["tipo_parada"] not in ("Station", "Dropoff"):
        raise ErrorValidacion("Tipo de parada desconocido.")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fila["fecha"], flags=re.ASCII):
        raise ErrorValidacion("Fecha debe usar YYYY-MM-DD.")
    if not re.fullmatch(r"\d{2}:\d{2}:\d{2}", fila["hora_salida_utc"], flags=re.ASCII):
        raise ErrorValidacion("Hora UTC debe usar HH:MM:SS sin conversión de zona.")
    resultado["fecha"] = date.fromisoformat(fila["fecha"])
    resultado["hora_salida_utc"] = time.fromisoformat(fila["hora_salida_utc"])
    return resultado


def validar_amazon(contenido: bytes, manifiesto: ManifiestoAmazon) -> AmazonValidado:
    """Hash y CSV se verifican sobre los mismos bytes; no hay relectura al insertar."""
    if sha256(contenido).hexdigest() != manifiesto.sha256:
        raise ErrorValidacion("SHA-256 del CSV no coincide con el manifiesto.")
    filas, rutas, estaciones, pedidos, paradas = [], {}, set(), set(), set()
    try:
        lector = csv.DictReader(StringIO(contenido.decode("utf-8-sig"), newline=""), strict=True)
        if lector.fieldnames != list(COLUMNAS):
            raise ErrorValidacion("Cabecera CSV no coincide con las 20 columnas esperadas.")
        for original in lector:
            try:
                fila = _fila(original)
                pedido, ruta, parada = fila["pedido_id"], fila["route_id"], fila["stop_id"]
                if pedido in pedidos or (ruta, parada) in paradas:
                    raise ErrorValidacion("pedido_id o (route_id, stop_id) duplicado.")
                datos_ruta = {c: fila[c] for c in CAMPOS_RUTA}
                if ruta in rutas and rutas[ruta] != datos_ruta:
                    raise ErrorValidacion("Metadatos inconsistentes dentro de una ruta.")
                rutas[ruta] = datos_ruta
                pedidos.add(pedido)
                paradas.add((ruta, parada))
                estaciones.add(fila["station_code"])
                filas.append(fila)
            except (ValueError, InvalidOperation) as exc:
                raise ErrorValidacion(f"Fila {lector.line_num}: {exc}") from exc
    except (UnicodeError, csv.Error) as exc:
        raise ErrorValidacion("CSV corrupto o codificación diferente de UTF-8.") from exc
    if (len(filas), len(rutas), len(estaciones)) != (manifiesto.paradas, manifiesto.rutas, manifiesto.estaciones):
        raise ErrorValidacion("Conteos CSV distintos del manifiesto (paradas/rutas/estaciones).")
    return AmazonValidado(tuple(filas), rutas, tuple(sorted(estaciones)))
