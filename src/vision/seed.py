"""CLI fase 4; sin descarga, subida pública, API, interfaz ni entrenamiento."""

import argparse
import json
import os
from pathlib import Path
import sys

from dotenv import dotenv_values
from sqlalchemy.exc import SQLAlchemyError

from src.configuracion import ErrorConfiguracion, ROOT
from src.datos.validacion import cargar_manifiesto
from src.persistencia.sesion import crear_motor
from src.vision.importacion import ErrorImportacionVisual, importar_piloto
from src.vision.manifiesto import DEFAULT_MANIFIESTO, DEFAULT_RAIZ


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originales", type=Path, default=DEFAULT_RAIZ)
    parser.add_argument("--manifiesto", type=Path, default=DEFAULT_MANIFIESTO)
    parser.add_argument("--csv", type=Path, default=ROOT / "data/amazon_pedidos.csv")
    parser.add_argument("--amazon", type=Path, default=ROOT / "data/manifests/amazon-v1.json")
    parser.add_argument("--almacenamiento", type=Path)
    parser.add_argument("--version", default="v1")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    motor = None
    try:
        valores = {**dotenv_values(ROOT / ".env", interpolate=False), **os.environ}
        almacen = args.almacenamiento or Path(valores.get("VISUAL_STORAGE_ROOT") or ROOT / "data/visual/almacen")
        if not args.dry_run:
            motor = crear_motor()
        resultado = importar_piloto(args.originales, args.manifiesto, args.csv, cargar_manifiesto(args.amazon),
                                    almacen, motor=motor, dry_run=args.dry_run, version=args.version)
        print(json.dumps(resultado, ensure_ascii=False))
        return 0
    except (ErrorConfiguracion, ValueError, ErrorImportacionVisual) as exc:
        print(f"Error: {exc}", file=sys.stderr)
    except OSError:
        print("Error: archivos no disponibles; revisa rutas y permisos.", file=sys.stderr)
    except SQLAlchemyError:
        print("Error: PostgreSQL no disponible o esquema sin migrar; revisa alembic upgrade head.", file=sys.stderr)
    finally:
        if motor is not None:
            motor.dispose()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
