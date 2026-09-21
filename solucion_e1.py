from pathlib import Path

import pandas as pd


# 1) Diagnóstico del CSV
# Primero quiero ver el estado real del archivo antes de decidir
# qué filas son válidas. Esto me ayuda a encontrar errores de tipo, nulos y
# valores que no cumplen las reglas de negocio.

def cargar_ventas() -> pd.DataFrame:
    """Carga el CSV usando rutas relativas desde el proyecto y no paths hardcodeados."""
    base_dir = Path(__file__).resolve().parent
    ruta_csv = base_dir / "E1_pandas" / "Datos" / "ventas.csv"
    return pd.read_csv(ruta_csv)


def diagnosticar_ventas(frame: pd.DataFrame) -> None:
    """Muestra shape, dtypes, nulos y lista de filas sospechosas."""
    print("=== Diagnóstico inicial ===")
    print(f"Shape: {frame.shape}")
    print("\nTipos de columna:\n", frame.dtypes)
    print("\nValores nulos por columna:\n", frame.isna().sum())

    print("\nFilas que parecen inválidas:")
    hay_problemas = False

    for indice, fila in frame.iterrows():
        unidades = pd.to_numeric(fila["unidades"], errors="coerce")
        precio = pd.to_numeric(fila["precio_unitario"], errors="coerce")
        motivos = []

        if pd.isna(unidades):
            motivos.append("unidades nula")
        elif unidades <= 0:
            motivos.append("unidades no positiva")

        if pd.isna(precio):
            motivos.append("precio_unitario nulo")
        elif precio <= 0:
            motivos.append("precio_unitario no positivo")

        if motivos:
            hay_problemas = True
            print(
                f"- fila {indice}: {fila.to_dict()} -> "
                f"motivo(s): {', '.join(motivos)}"
            )

    if not hay_problemas:
        print("No se detectan filas problemáticas en este CSV.")


# 2) Validación de ventas
# Aquí aplico la regla mínima del ejercicio: solo las filas donde unidades y
# precio_unitario sean numéricos y mayores que cero pasan a la lista de válidas.
# La columna 'importe' se calcula solo para esas filas correctas.
def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve (validos, errores)."""
    copia = frame.copy()

    # Convertimos columnas a numérico para que strings como "na" o "0" se manejen
    # de forma consistente. Los valores que no puedan convertirse pasan a NaN.
    copia["unidades"] = pd.to_numeric(copia["unidades"], errors="coerce")
    copia["precio_unitario"] = pd.to_numeric(copia["precio_unitario"], errors="coerce")

    valid_mask = copia["unidades"].gt(0) & copia["precio_unitario"].gt(0)

    validos = copia.loc[valid_mask].copy()
    validos["importe"] = validos["unidades"] * validos["precio_unitario"]

    errores = copia.loc[~valid_mask].copy()
    errores["motivo"] = ""

    for indice, fila in errores.iterrows():
        motivos = []
        if pd.isna(fila["unidades"]) or fila["unidades"] <= 0:
            motivos.append("unidades inválida")
        if pd.isna(fila["precio_unitario"]) or fila["precio_unitario"] <= 0:
            motivos.append("precio_unitario inválido")
        errores.at[indice, "motivo"] = "; ".join(motivos)

    return validos.reset_index(drop=True), errores.reset_index(drop=True)


def main() -> None:
    ventas = cargar_ventas()
    diagnosticar_ventas(ventas)

    validos, errores = validar_ventas(ventas)

    print("\n=== Resultado de la validación ===")
    print(f"Filas válidas: {len(validos)}")
    print(f"Filas con errores: {len(errores)}")
    print("\nPreview de válidas:\n", validos.head())
    print("\nPreview de errores:\n", errores.head())


if __name__ == "__main__":
    main()
