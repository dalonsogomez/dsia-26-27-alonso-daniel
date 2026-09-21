"""
Sesión 3 (21 sep 2026): OOP, Clean Code y SOLID — ejemplo guiado.

Ejecutar desde la raíz del repo o desde esta carpeta:
    python 03_oop_clean_code_solid.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pandas as pd


class DataLoadError(Exception):
    """Error al cargar datos de origen."""


class ValidationError(Exception):
    """Datos que no cumplen reglas de negocio."""


@dataclass(frozen=True)
class SalesRecord:
    region: str
    product: str
    units: float
    unit_price: float

    @property
    def amount(self) -> float:
        return self.units * self.unit_price


class SalesRepository(Protocol):
    """Abstracción de lectura (Dependency Inversion)."""

    def load(self) -> pd.DataFrame: ...


class CsvSalesRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> pd.DataFrame:
        if not self._path.exists():
            raise DataLoadError(f"No existe el fichero: {self._path}")
        return pd.read_csv(self._path)


class SalesValidator:
    """Single Responsibility: solo valida."""

    def split(self, frame: pd.DataFrame) -> tuple[list[SalesRecord], pd.DataFrame]:
        work = frame.copy()
        work["unidades"] = pd.to_numeric(work["unidades"], errors="coerce")
        work["precio_unitario"] = pd.to_numeric(work["precio_unitario"], errors="coerce")
        ok = work["unidades"].notna() & (work["unidades"] > 0) & (work["precio_unitario"] > 0)
        valid_rows = [
            SalesRecord(
                region=str(row.region),
                product=str(row.producto),
                units=float(row.unidades),
                unit_price=float(row.precio_unitario),
            )
            for row in work.loc[ok].itertuples(index=False)
        ]
        return valid_rows, work.loc[~ok]


class SalesMetrics:
    """Open/Closed: se pueden añadir métricas sin tocar el validador."""

    def total_by_region(self, records: list[SalesRecord]) -> dict[str, float]:
        totals: dict[str, float] = {}
        for record in records:
            totals[record.region] = totals.get(record.region, 0.0) + record.amount
        return dict(sorted(totals.items(), key=lambda item: item[1], reverse=True))


def main() -> None:
    data_path = Path(__file__).resolve().parent / "Datos" / "ventas.csv"
    repo: SalesRepository = CsvSalesRepository(data_path)
    validator = SalesValidator()
    metrics = SalesMetrics()

    frame = repo.load()
    records, errors = validator.split(frame)
    print(f"Registros válidos: {len(records)} | inválidos: {len(errors)}")
    print("Importe por región:")
    for region, total in metrics.total_by_region(records).items():
        print(f"  {region}: {total:.2f}")


if __name__ == "__main__":
    main()
