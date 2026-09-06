"""Utilidades geoespaciales y de cálculo de distancias."""

from __future__ import annotations

# math: biblioteca estándar de Python para funciones matemáticas y trigonométricas (seno, coseno, radianes, arcotangente)
import math


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calcula la distancia geodésica en kilómetros entre dos coordenadas GPS usando la fórmula de Haversine.

    FÓRMULA MATEMÁTICA DE HAVERSINE:
        Δφ = radians(lat2 - lat1)
        Δλ = radians(lon2 - lon1)
        a = sin²(Δφ / 2) + cos(φ1) · cos(φ2) · sin²(Δλ / 2)
        c = 2 · atan2(√a, √(1 - a))
        d = R · c

    TÉRMINOS:
    - φ1, φ2: Latitudes de los puntos 1 y 2 en radianes.
    - Δφ, Δλ: Diferencia de latitud y longitud en radianes.
    - a: Cuadrado de la mitad de la longitud de la cuerda entre los dos puntos proyectados.
    - c: Distancia angular en radianes sobre el gran círculo.
    - R: Radio medio de la Tierra (6,371.0 km).
    - d: Distancia geodésica mínima sobre la esfera en kilómetros.
    """
    # ESTA VARIABLE radio_tierra_km (float) GUARDA: El radio medio terrestre R = 6371.0 km
    radio_tierra_km = 6371.0

    # ESTA VARIABLE dlat (float) GUARDA: Diferencia de latitud Δφ convertida a radianes
    dlat = math.radians(lat2 - lat1)

    # ESTA VARIABLE dlon (float) GUARDA: Diferencia de longitud Δλ convertida a radianes
    dlon = math.radians(lon2 - lon1)

    # ESTA VARIABLE a (float) GUARDA: La fórmula del seno del semiversorio (semiversine)
    # a = sin²(Δφ/2) + cos(lat1) * cos(lat2) * sin²(Δλ/2)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )

    # ESTA VARIABLE c (float) GUARDA: La distancia angular en radianes usando atan2 para estabilidad numérica
    # c = 2 · atan2(√a, √(1 - a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    # Retorna la distancia en kilómetros: d = R · c
    return radio_tierra_km * c
