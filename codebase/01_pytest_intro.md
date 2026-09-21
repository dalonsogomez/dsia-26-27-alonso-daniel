# Sesión 28 sep 2026 — pytest, test suites y aserciones

Ejercicio 30 min: `ejercicios/E3_pytest.md`

## Arranque de la demo (exposición)

```bash
cd 2_pruebas_y_despliegue/ejemplos
pytest -q
pytest -vv
pytest -q test_calculator.py::test_divide_by_zero_raises
```

## Guion corto de los 30 min de teoría

1. **Pirámide de tests** — unitarios vs integración vs E2E (5 min).
2. **AAA** — Arrange / Act / Assert sobre `add` / `divide` (8 min).
3. **raises + parametrize + fixtures** en vivo (10 min).
4. **CI** — abrir `.github/workflows/ci.yml` y explicar el gate de merge (7 min).

## Patrones que debes salir sabiendo escribir

```python
def test_ok():
    assert f(1) == 2

def test_error():
    with pytest.raises(ValueError):
        f(-1)

@pytest.mark.parametrize("x, expected", [(0, 0), (1, 1)])
def test_many(x, expected):
    assert f(x) == expected

@pytest.fixture
def sample_df():
    return pd.DataFrame({"unidades": [1, None], "precio_unitario": [10, 5]})
```

## Buenas prácticas

- Nombres: `test_<unidad>_<escenario>_<resultado>`.
- Unitarios sin red ni reloj real.
- `tmp_path` si necesitas ficheros.
- Marca integración: `@pytest.mark.integration`.

## Puente al Proyecto I

Tu validador de ventas debe tener ≥ 8 tests antes de dar por cerrado el 10 %.
