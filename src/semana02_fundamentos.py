"""Primer modelo supervisado reproducible de la semana 2."""

from __future__ import annotations

from dataclasses import dataclass

from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


RANDOM_STATE = 42


@dataclass(frozen=True)
class ExperimentResult:
    """Métricas estables que permiten validar y reutilizar el experimento."""

    training_samples: int
    test_samples: int
    accuracy: float
    confusion_matrix: tuple[tuple[int, ...], ...]


def run_experiment() -> ExperimentResult:
    """Entrena y evalúa el pipeline indicado en la guía de la semana 2."""

    features, target = load_iris(return_X_y=True)
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=target,
    )
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    matrix = confusion_matrix(y_test, predictions)
    return ExperimentResult(
        training_samples=len(x_train),
        test_samples=len(x_test),
        accuracy=float(accuracy_score(y_test, predictions)),
        confusion_matrix=tuple(tuple(int(value) for value in row) for row in matrix),
    )


def main() -> None:
    result = run_experiment()
    print(f"Muestras entrenamiento: {result.training_samples}")
    print(f"Muestras prueba: {result.test_samples}")
    print(f"Accuracy: {result.accuracy:.3f}")
    print("Matriz de confusión:")
    for row in result.confusion_matrix:
        print(list(row))


if __name__ == "__main__":
    main()

