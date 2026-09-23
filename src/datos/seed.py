"""CLI: python -m src.datos.seed [--dry-run] [--csv ... --manifiesto ...]."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import sys

from sqlalchemy.exc import SQLAlchemyError

from src.configuracion import ErrorConfiguracion, ROOT
from src.datos.importacion import ErrorImportacion, importar_amazon
from src.datos.validacion import ErrorValidacion, cargar_manifiesto
from src.persistencia.sesion import crear_motor


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Importar paradas Amazon sin modificar versiones existentes.")
    parser.add_argument("--csv", type=Path, default=ROOT / "data/amazon_pedidos.csv")
    parser.add_argument("--manifiesto", type=Path, default=ROOT / "data/manifests/amazon-v1.json")
    parser.add_argument("--dry-run", action="store_true", help="Validar sin conectar a BD ni escribir archivos.")
    args = parser.parse_args(argv)
    motor = None
    try:
        manifiesto = cargar_manifiesto(args.manifiesto)
        if not args.dry_run:
            motor = crear_motor()
        resultado = importar_amazon(args.csv, manifiesto, motor=motor, dry_run=args.dry_run)
        print(json.dumps(asdict(resultado), ensure_ascii=False))
        return 0
    except (ErrorConfiguracion, ErrorValidacion, ErrorImportacion) as exc:
        print(f"Error: {exc}", file=sys.stderr)
    except OSError:
        print("Error: no se pudo leer el CSV o manifiesto.", file=sys.stderr)
    except SQLAlchemyError:
        print("Error: PostgreSQL no disponible o esquema sin migrar; revisa configuración y alembic upgrade head.", file=sys.stderr)
    finally:
        if motor is not None:
            motor.dispose()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
