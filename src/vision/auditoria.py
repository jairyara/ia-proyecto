"""Reverificación offline del piloto fijado; no descarga, escribe ni conecta a BD."""

import argparse
import json
from pathlib import Path
import sys

from src.vision.manifiesto import DEFAULT_MANIFIESTO, DEFAULT_RAIZ, auditar_piloto, hash_archivo


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raiz", type=Path, default=DEFAULT_RAIZ)
    parser.add_argument("--manifiesto", type=Path, default=DEFAULT_MANIFIESTO)
    args = parser.parse_args(argv)
    try:
        esperado = json.loads(args.manifiesto.read_text(encoding="utf-8"))
        resultado = auditar_piloto(args.raiz, manifiesto=esperado)
        print(json.dumps({
            "estado": "auditoria_tecnica_aprobada", **resultado["conteos"],
            "bytes_total": resultado["bytes_total"],
            "manifiesto_sha256": hash_archivo(args.manifiesto),
            "nota": "La revisión visual y limitaciones se documentan aparte; no se evalúa un clasificador.",
        }, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error de auditoría: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
