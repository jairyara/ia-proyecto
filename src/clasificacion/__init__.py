"""Módulo de clasificación simbólica y taxonomía de IA para logística."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.clasificacion.requerimientos import (
        CATEGORIES,
        CATEGORY_NAMES,
        Category,
        Classification,
        Requirement,
        classify_requirement,
        contains_keyword,
        load_requirements,
        normalize_text,
        render_report,
    )

__all__ = [
    "CATEGORIES",
    "CATEGORY_NAMES",
    "Category",
    "Classification",
    "Requirement",
    "classify_requirement",
    "contains_keyword",
    "load_requirements",
    "normalize_text",
    "render_report",
]


def __getattr__(name: str):
    import src.clasificacion.requerimientos as req
    if hasattr(req, name):
        return getattr(req, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
