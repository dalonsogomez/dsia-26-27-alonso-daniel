"""Comprueba que el entorno del curso está activo y usable.

Uso:
  python check_entorno.py
  python check_entorno.py --strict    # falla si no estás dentro de .venv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Chequeo de entorno DSIA")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exige que sys.executable viva dentro de un directorio .venv",
    )
    args = parser.parse_args()

    print("Python:", sys.version.split()[0])
    print("Executable:", sys.executable)

    in_venv = ".venv" in sys.executable.replace("\\", "/")
    if not in_venv:
        msg = "parece que no estás usando .venv"
        if args.strict:
            print("FALLO:", msg)
            print("Activa primero: source .venv/bin/activate  (Windows: .venv\\Scripts\\activate)")
            return 2
        print("AVISO:", msg, "(continúo igual; usa --strict para exigirlo)")

    try:
        import pandas as pd
        import pytest
    except ImportError as exc:
        print("FALLO: falta dependencia —", exc)
        print("Ejecuta (con venv activo): pip install -r requirements.txt")
        return 1

    root = Path(__file__).resolve().parents[2]
    req = root / "requirements.txt"
    if not req.exists():
        print("FALLO: no encuentro requirements.txt en", root)
        return 1

    print(f"Repo root: {root}")
    print(f"pandas={pd.__version__} | pytest={pytest.__version__}")
    print("VIRTUAL_ENV:", __import__("os").environ.get("VIRTUAL_ENV", "(no definido)"))
    print("ENTORNO OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
