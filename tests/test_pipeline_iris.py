import unittest

from src.pipeline_iris import run_experiment


class IrisPipelineTests(unittest.TestCase):
    def test_iris_pipeline_matches_the_course_reference(self) -> None:
        result = run_experiment()

        self.assertEqual(result.training_samples, 112)
        self.assertEqual(result.test_samples, 38)
        self.assertAlmostEqual(result.accuracy, 0.9210526315789473)
        self.assertEqual(
            result.confusion_matrix,
            ((12, 0, 0), (0, 12, 1), (0, 2, 11)),
        )


if __name__ == "__main__":
    unittest.main()

