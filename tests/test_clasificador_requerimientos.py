from pathlib import Path
import tempfile
import unittest

from src.clasificador_requerimientos import (
    DEFAULT_DOMAIN_INPUT,
    DEFAULT_INPUT,
    UNCLASSIFIED,
    classify_requirement,
    contains_keyword,
    load_requirements,
    normalize_text,
    render_report,
)


class NormalizeTextTests(unittest.TestCase):
    def test_normalizes_accents_and_a_star(self) -> None:
        self.assertEqual(normalize_text("  RÚTA con A*  "), "ruta con a estrella")

    def test_keyword_matching_uses_complete_words(self) -> None:
        normalized = normalize_text("Las plantas se inspeccionan a diario")
        self.assertFalse(contains_keyword(normalized, "plan"))


class ClassificationTests(unittest.TestCase):
    def test_returns_unclassified_without_evidence(self) -> None:
        result = classify_requirement("Registrar el color corporativo")
        self.assertEqual(result.primary, UNCLASSIFIED)

    def test_preserves_secondary_areas(self) -> None:
        result = classify_requirement(
            "Calcular una ruta A* y validar restricciones de ventana horaria"
        )
        self.assertEqual(result.primary, "Búsqueda y optimización")
        self.assertIn("Sistemas expertos", result.detected)
        self.assertIn("a estrella", result.matched_keywords[result.primary])

    def test_reference_dataset_matches_expected_areas(self) -> None:
        requirements = load_requirements(DEFAULT_INPUT)
        mismatches = [
            requirement.identifier
            for requirement in requirements
            if classify_requirement(requirement.description).primary
            != requirement.expected_area
        ]
        self.assertEqual(mismatches, [])

    def test_domain_dataset_matches_expected_areas(self) -> None:
        requirements = load_requirements(DEFAULT_DOMAIN_INPUT)
        mismatches = [
            requirement.identifier
            for requirement in requirements
            if classify_requirement(requirement.description).primary
            != requirement.expected_area
        ]
        self.assertEqual(mismatches, [])


class CsvValidationTests(unittest.TestCase):
    def _write_csv(self, content: str) -> Path:
        temporary = tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", encoding="utf-8", delete=False
        )
        self.addCleanup(Path(temporary.name).unlink, missing_ok=True)
        with temporary:
            temporary.write(content)
        return Path(temporary.name)

    def test_rejects_missing_required_header(self) -> None:
        path = self._write_csv("id,texto\n1,Una ruta\n")
        with self.assertRaisesRegex(ValueError, "Faltan columnas obligatorias"):
            load_requirements(path)

    def test_rejects_unknown_expected_area(self) -> None:
        path = self._write_csv(
            "id,descripcion,area_esperada\n1,Una ruta,Área inexistente\n"
        )
        with self.assertRaisesRegex(ValueError, "área esperada desconocida"):
            load_requirements(path)

    def test_accepts_the_course_csv_with_only_description(self) -> None:
        path = self._write_csv("descripcion\nCalcular una ruta\n")
        requirements = load_requirements(path, minimum_cases=1)

        self.assertEqual(requirements[0].identifier, "CASO-001")
        self.assertEqual(requirements[0].description, "Calcular una ruta")

    def test_requires_twenty_cases_by_default(self) -> None:
        path = self._write_csv(
            "id,descripcion,area_esperada\n"
            "1,Calcular una ruta,Búsqueda y optimización\n"
        )
        with self.assertRaisesRegex(ValueError, "al menos 20 casos"):
            load_requirements(path)

    def test_allows_an_explicit_smaller_minimum_for_auxiliary_inputs(self) -> None:
        path = self._write_csv(
            "id,descripcion,area_esperada\n"
            "1,Calcular una ruta,Búsqueda y optimización\n"
        )
        self.assertEqual(len(load_requirements(path, minimum_cases=1)), 1)

    def test_report_includes_metrics_and_evidence(self) -> None:
        requirements = load_requirements(DEFAULT_INPUT)
        report = render_report(requirements, DEFAULT_INPUT.name)
        self.assertIn("Coincidencia: **100.00%** (20/20).", report)
        self.assertIn("Evidencia principal", report)


if __name__ == "__main__":
    unittest.main()
