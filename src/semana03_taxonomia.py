"""Línea base simbólica para clasificar requerimientos logísticos.

El módulo usa reglas explícitas y normalización de texto. No pretende sustituir
un modelo entrenado: ofrece una referencia determinista, interpretable y fácil
de auditar para la taxonomía definida durante la semana 3.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import re
import sys
import unicodedata


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "data" / "requerimientos_logistica.csv"
DEFAULT_REPORT = ROOT / "reports" / "semana03.md"
UNCLASSIFIED = "Requiere análisis"


@dataclass(frozen=True)
class Category:
    """Área de IA y vocabulario que aporta evidencia para clasificarla."""

    name: str
    component: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class Requirement:
    """Caso del dominio con una clasificación manual opcional."""

    identifier: str
    description: str
    expected_area: str | None = None


@dataclass(frozen=True)
class Classification:
    """Resultado ordenado con evidencia de todas las áreas detectadas."""

    primary: str
    detected: tuple[str, ...]
    scores: dict[str, int]
    matched_keywords: dict[str, tuple[str, ...]]


CATEGORIES: tuple[Category, ...] = (
    Category(
        "Búsqueda y optimización",
        "Planificación de rutas con A* sobre el grafo de entregas.",
        (
            "a estrella",
            "ruta",
            "rutas",
            "grafo",
            "camino",
            "distancia",
            "optimizar",
            "optimizacion",
            "flota",
            "entrega",
            "entregas",
            "despacho",
            "despachos",
            "logistica",
        ),
    ),
    Category(
        "Aprendizaje automático predictivo",
        "Estimación de demanda o clasificación del riesgo de retraso.",
        (
            "predecir",
            "prediccion",
            "modelo predictivo",
            "aprendizaje supervisado",
            "riesgo de retraso",
            "retraso",
            "retrasos",
            "pronostico",
            "pronosticar",
            "demanda",
            "tiempo de entrega",
        ),
    ),
    Category(
        "Sistemas expertos",
        "Validación trazable de restricciones operativas.",
        (
            "regla",
            "reglas",
            "restriccion",
            "restricciones",
            "ventana horaria",
            "ventanas horarias",
            "capacidad del vehiculo",
            "capacidad de los vehiculos",
            "prioridad",
            "cadena de frio",
            "politica operativa",
        ),
    ),
    Category(
        "Visión por computador",
        "Verificación de paquetes a partir de imágenes.",
        (
            "imagen",
            "imagenes",
            "camara",
            "fotografia",
            "paquete",
            "paquetes",
            "etiqueta",
            "etiquetas",
            "dano visible",
            "verificacion visual",
        ),
    ),
    Category(
        "Robótica y sistemas autónomos",
        "Ciclo de control y replanificación ante novedades.",
        (
            "agente autonomo",
            "sistema autonomo",
            "ciclo de control",
            "percibir",
            "actuar",
            "replanificar",
            "replanificacion",
            "via cerrada",
            "pedido nuevo",
            "novedad",
        ),
    ),
    Category(
        "Sistemas de recomendación",
        "Presentación de planes y alternativas al operador.",
        (
            "recomendar",
            "recomendacion",
            "recomendaciones",
            "alternativa de ruta",
            "alternativas de ruta",
            "preferencia del operador",
        ),
    ),
    Category(
        "Procesamiento de lenguaje natural",
        "Explicaciones o novedades expresadas en lenguaje natural.",
        (
            "lenguaje natural",
            "texto",
            "mensaje",
            "mensajes",
            "explicacion textual",
            "instruccion escrita",
        ),
    ),
)

CATEGORY_NAMES = frozenset(category.name for category in CATEGORIES)


def normalize_text(text: str) -> str:
    """Normaliza tildes, mayúsculas y puntuación sin alterar tokens."""

    text = text.strip().lower()
    text = re.sub(r"\ba\s*\*", "a estrella", text)
    decomposed = unicodedata.normalize("NFD", text)
    without_accents = "".join(
        character
        for character in decomposed
        if unicodedata.category(character) != "Mn"
    )
    alphanumeric = re.sub(r"[^a-z0-9]+", " ", without_accents)
    return re.sub(r"\s+", " ", alphanumeric).strip()


def contains_keyword(normalized_text: str, keyword: str) -> bool:
    """Comprueba palabras o frases completas para evitar falsos positivos."""

    normalized_keyword = normalize_text(keyword)
    if not normalized_keyword:
        return False
    return f" {normalized_keyword} " in f" {normalized_text} "


def classify_requirement(description: str) -> Classification:
    """Clasifica un requerimiento y conserva la evidencia de cada regla."""

    normalized = normalize_text(description)
    scores: dict[str, int] = {}
    matched_keywords: dict[str, tuple[str, ...]] = {}

    for category in CATEGORIES:
        matches = tuple(
            keyword
            for keyword in category.keywords
            if contains_keyword(normalized, keyword)
        )
        scores[category.name] = len(matches)
        matched_keywords[category.name] = matches

    ranked = sorted(
        (
            (scores[category.name], index, category.name)
            for index, category in enumerate(CATEGORIES)
            if scores[category.name] > 0
        ),
        key=lambda item: (-item[0], item[1]),
    )
    detected = tuple(name for _, _, name in ranked)
    return Classification(
        primary=detected[0] if detected else UNCLASSIFIED,
        detected=detected or (UNCLASSIFIED,),
        scores=scores,
        matched_keywords=matched_keywords,
    )


def _normalized_header(header: str) -> str:
    return normalize_text(header).replace(" ", "")


def load_requirements(path: Path) -> list[Requirement]:
    """Carga y valida casos desde un CSV UTF-8, incluido UTF-8 con BOM."""

    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo de entrada: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader.fieldnames:
            raise ValueError("El CSV está vacío o no contiene encabezados.")

        original_headers = list(reader.fieldnames)
        reader.fieldnames = [_normalized_header(header) for header in reader.fieldnames]
        required_headers = {"id", "descripcion"}
        missing = required_headers.difference(reader.fieldnames)
        if missing:
            raise ValueError(
                "Faltan columnas obligatorias "
                f"{sorted(missing)}. Encabezados encontrados: {original_headers}"
            )

        requirements: list[Requirement] = []
        seen_identifiers: set[str] = set()
        for row_number, row in enumerate(reader, start=2):
            identifier = (row.get("id") or "").strip()
            description = (row.get("descripcion") or "").strip()
            expected = (row.get("areaesperada") or "").strip() or None

            if not identifier or not description:
                raise ValueError(
                    f"Fila {row_number}: 'id' y 'descripcion' no pueden estar vacíos."
                )
            if identifier in seen_identifiers:
                raise ValueError(f"Fila {row_number}: id duplicado '{identifier}'.")
            if expected is not None and expected not in CATEGORY_NAMES:
                raise ValueError(
                    f"Fila {row_number}: área esperada desconocida '{expected}'."
                )

            seen_identifiers.add(identifier)
            requirements.append(Requirement(identifier, description, expected))

    if not requirements:
        raise ValueError("El CSV no contiene requerimientos.")
    return requirements


def _escape_markdown(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def render_report(requirements: list[Requirement], input_name: str) -> str:
    """Crea un informe Markdown determinista con resultados y evidencia."""

    evaluated = [
        (requirement, classify_requirement(requirement.description))
        for requirement in requirements
    ]
    comparable = [item for item in evaluated if item[0].expected_area is not None]
    correct = sum(
        classification.primary == requirement.expected_area
        for requirement, classification in comparable
    )

    lines = [
        "# Semana 03 — Taxonomía del dominio logístico",
        "",
        "Reporte generado por `python3 -m src.semana03_taxonomia`.",
        "",
        "## Configuración",
        "",
        f"- Entrada: `{input_name}`",
        f"- Casos procesados: **{len(evaluated)}**",
        "- Método: reglas deterministas sobre palabras y frases completas.",
        "- Desempate: orden documentado de las áreas en el código.",
        "",
        "## Componentes y áreas",
        "",
        "| Área | Componente del proyecto |",
        "|---|---|",
    ]
    lines.extend(
        f"| {category.name} | {category.component} |" for category in CATEGORIES
    )
    lines.extend(
        [
            "",
            "## Clasificación de requerimientos",
            "",
            "| ID | Requerimiento | Principal | Áreas detectadas | Evidencia principal | Esperada | Estado |",
            "|---|---|---|---|---|---|---|",
        ]
    )

    for requirement, classification in evaluated:
        expected = requirement.expected_area or "No definida"
        if requirement.expected_area is None:
            status = "Sin referencia"
        elif classification.primary == requirement.expected_area:
            status = "Coincide"
        else:
            status = "Revisar"
        detected = ", ".join(classification.detected)
        evidence = ", ".join(
            f"`{keyword}`"
            for keyword in classification.matched_keywords.get(
                classification.primary, ()
            )
        ) or "—"
        lines.append(
            "| "
            + " | ".join(
                (
                    _escape_markdown(requirement.identifier),
                    _escape_markdown(requirement.description),
                    classification.primary,
                    detected,
                    evidence,
                    expected,
                    status,
                )
            )
            + " |"
        )

    lines.extend(["", "## Resultado frente a la referencia", ""])
    if comparable:
        accuracy = 100 * correct / len(comparable)
        lines.append(
            f"Coincidencia: **{accuracy:.2f}%** ({correct}/{len(comparable)})."
        )
    else:
        lines.append("No hay clasificaciones manuales para comparar.")

    lines.extend(
        [
            "",
            "## Limitaciones",
            "",
            "- Las reglas dependen del vocabulario explícito y no comprenden el contexto.",
            "- Los empates se resuelven por el orden de las categorías, por lo que deben revisarse.",
            "- Una coincidencia con la referencia valida los casos actuales, no generaliza a todo el dominio.",
            "- La salida conserva áreas secundarias para no reducir requerimientos híbridos a una sola técnica.",
            "",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Clasifica requerimientos logísticos por área de IA."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"CSV de entrada (predeterminado: {DEFAULT_INPUT})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_REPORT,
        help=f"Reporte Markdown (predeterminado: {DEFAULT_REPORT})",
    )
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Finaliza con código 1 si una clasificación difiere de la referencia.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        requirements = load_requirements(args.input)
        report = render_report(requirements, args.input.name)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2

    classifications = [
        classify_requirement(requirement.description) for requirement in requirements
    ]
    mismatches = sum(
        requirement.expected_area is not None
        and classification.primary != requirement.expected_area
        for requirement, classification in zip(
            requirements, classifications, strict=True
        )
    )
    print(f"Casos procesados: {len(requirements)}")
    print(f"Discrepancias: {mismatches}")
    print(f"Reporte generado: {args.output}")
    return 1 if args.fail_on_mismatch and mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
