# E2 — Arquitectura modular, Clean Code y SOLID (30 min)

**Sesión:** 21 sep 2026  
**Referencia:** `../03_oop_clean_code_solid.py`

## Meta

Transformar tu solución de ventas en un paquete ejecutable:

```text
ventas_app/
  __init__.py
  loader.py
  validator.py
  metrics.py
  cli.py
```

## Parte 1 — Esqueleto (10 min)

1. Crea el paquete y los ficheros vacíos.
2. Define excepciones `DataLoadError` y `ValidationError` (módulo propio o en `loader`/`validator`).
3. Haz que `loader.load(path) -> DataFrame` falle si el fichero no existe.

## Parte 2 — Lógica (10 min)

1. Mueve la validación a `validator.py` (SRP).
2. Mueve agregaciones a `metrics.py`.
3. En `cli.py`, orquesta con `argparse`:

```bash
python -m ventas_app.cli --input Datos/ventas.csv --output Datos/ventas_limpias.csv
```

## Parte 3 — SOLID explícito (8 min)

En `ventas_app/DESIGN.md` (o final del README), escribe **3 bullets**:

- Principio aplicado
- Fichero/clase
- Por qué cumple

Ejemplo: “DIP — `cli.py` depende de un Protocol `SalesRepository`, no de CSV concreto”.

## Parte 4 — Clean Code express (2 min)

Elimina al menos: un nombre críptico, un número mágico y un `print` de depuración suelto (sustituye por logging básico si quieres).

## Extensión

Añade `JsonSalesRepository` (lee un `.json` lista de records) sin tocar `metrics.py`.

## Puente al Proyecto I

El Proyecto I tiene **dos entregas obligatorias** (`proyectos/proyecto_i/`):

1. **Parte A** — pipeline sobre `ventas.csv` (este ejercicio es el núcleo).
2. **Parte B** — el mismo enfoque con un dataset público elegido de internet.

## Hecho cuando…

El CLI corre y el DESIGN.md cita 3 principios con anclaje real al código.
