# Dashboard · Semana 07 — Representaciones del reconocimiento
"""Experimento reproducible oficial + adaptación real Amazon de Semana 07."""

from __future__ import annotations

import json
from pathlib import Path

from src.representaciones.caso_clase import ejecutar_caso_clase
from src.representaciones.reconocimiento import (
    contexto_dataset,
    evaluar_parada,
    evaluaciones_pod,
)


ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "reports" / "sem-07-representaciones-evidencia.md"


def generar_evidencia() -> str:
    """Ejecuta ambos niveles y genera la evidencia Markdown regenerable."""
    clase = ejecutar_caso_clase()
    contexto = contexto_dataset()
    perfiles = contexto["perfiles"]
    evaluaciones = [evaluar_parada(perfil["pedido_id"]) for perfil in perfiles]
    pod = evaluaciones_pod()

    lineas = [
        "# Semana 07 — Evidencia reproducible de representaciones",
        "",
        "> Generado por `python -m src.representaciones_reconocimiento`.",
        "",
        "## 1. Caso oficial de clase",
        "",
        f"- Muestra: `{clase['numerica']['muestra']}`",
        f"- Referencia: `{clase['numerica']['referencia']}`",
        f"- Distancia euclidiana: `{clase['numerica']['distancia_euclidiana']:.3f}`",
        f"- Conclusión simbólica: `{clase['simbolica']['conclusion']}`",
        "",
        "| Secuencia | Estado final | ¿Aceptada? |",
        "|---|---|---|",
    ]
    for item in clase["automata"]["secuencias"]:
        lineas.append(f"| `{item['secuencia']}` | `{item['estado_final']}` | **{item['aceptada']}** |")

    estadisticas = contexto["estadisticas"]
    lineas += [
        "",
        "## 2. Datos reales Amazon",
        "",
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
        "## 3. Perfiles demostrativos reales",
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
        "## 4. AFD logístico POD — escenarios controlados",
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
        "## 5. Procedencia serializada",
        "",
        "```json",
        json.dumps(evaluaciones[0]["procedencia"], ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    REPORT_PATH.write_text("\n".join(lineas), encoding="utf-8")
    return "\n".join(lineas)


def main() -> int:
    contenido = generar_evidencia()
    print(contenido.splitlines()[0])
    print(f"Reporte generado: {REPORT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
