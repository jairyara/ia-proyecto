"""Experimento reproducible de la Semana 5: sistema híbrido de trazabilidad.

Ejecuta las tres consultas de prueba de la guía contra el motor híbrido
(reglas expertas + TF-IDF + regresión logística) y genera el reporte de
evidencia ``reports/sem-05-sistema-hibrido.md``.

Uso::

    python -m src.sistema_hibrido
"""

from __future__ import annotations

import json
from pathlib import Path

from src.hibrido.sistema import CONSULTAS_EJEMPLO, ROOT, answer

REPORT_PATH = ROOT / "reports" / "sem-05-sistema-hibrido-evidencia.md"


def main() -> None:
    resultados = [(consulta, answer(consulta)) for consulta in CONSULTAS_EJEMPLO]
    for consulta, resultado in resultados:
        print(consulta)
        print(
            json.dumps(
                {
                    "reglas": resultado["reglas"],
                    "evidencia": resultado["evidencia"],
                    "similitud": round(resultado["similitud"], 3),
                    "clase": resultado["clase"],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        print()

    lineas = [
        "# Semana 05 — Evidencia reproducible del sistema híbrido",
        "",
        "Generado por `python src/sistema_hibrido.py`. El análisis completo",
        "está en `reports/sem-05-sistema-hibrido.md`.",
        "",
    ]
    for indice, (consulta, resultado) in enumerate(resultados, start=1):
        lineas += [
            f"## Consulta {indice}",
            f"- **Entrada:** {consulta}",
            f"- **Reglas activadas:** {', '.join(resultado['reglas']) or 'ninguna'}",
            f"- **Evidencia recuperada:** {resultado['evidencia']}",
            f"- **Similitud coseno (TF-IDF):** {resultado['similitud']:.3f}",
            f"- **Clase predicha (LogisticRegression):** `{resultado['clase']}`",
            "",
        ]
    REPORT_PATH.write_text("\n".join(lineas), encoding="utf-8")
    print(f"Reporte generado: {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
