"""Servicio de lectura y validación de insumos Excel (R01-R04, R05, R08).

Lee las hojas de Fill Rate del archivo de insumos sin modificarlo,
detecta columnas, cuenta filas de datos y registra errores de lectura.
"""

from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

# Ruta al archivo de insumos entregado (no se modifica)
INSUMOS_PATH = Path("Insumos") / "Fill Rate Noviembre - Diciembre 2025.xlsx"

# Hojas de Fill Rate que contienen datos reales de reporte
HOJAS_FILL_RATE = ["FR NOV 2025", "FR DIC 2025"]

# Hoja de histórico de ventas
HOJA_VENTAS = "Kilos Vendidos Nov - Dic"


def leer_hoja(ruta_archivo: Path, nombre_hoja: str) -> Tuple[pd.DataFrame, List[str]]:
    """Lee una hoja de Excel y devuelve el DataFrame y una lista de errores.

    Args:
        ruta_archivo: Ruta al archivo Excel.
        nombre_hoja: Nombre de la hoja a leer.

    Returns:
        Tupla con el DataFrame leído y una lista de mensajes de error (vacía si todo ok).
    """
    errores: List[str] = []

    try:
        df = pd.read_excel(ruta_archivo, sheet_name=nombre_hoja, header=None)
    except Exception as exc:  # pylint: disable=broad-except
        errores.append(f"No se pudo leer la hoja '{nombre_hoja}': {exc}")
        return pd.DataFrame(), errores

    # Detectar la fila de encabezados: primera fila que no esté completamente vacía
    fila_encabezados = None
    for idx in range(df.shape[0]):
        fila = df.iloc[idx]
        if not fila.isna().all():
            fila_encabezados = idx
            break

    if fila_encabezados is None:
        errores.append(f"La hoja '{nombre_hoja}' no contiene filas con datos.")
        return pd.DataFrame(), errores

    # Usar la fila detectada como encabezados
    encabezados = df.iloc[fila_encabezados].tolist()
    encabezados = [str(c) if pd.notna(c) else f"Col_{i}" for i, c in enumerate(encabezados)]

    # Datos: filas después de los encabezados
    datos = df.iloc[fila_encabezados + 1 :].copy()
    datos.columns = encabezados

    # Eliminar filas completamente vacías
    datos = datos.dropna(how="all").reset_index(drop=True)

    return datos, errores


def leer_insumos(ruta_archivo: Path = INSUMOS_PATH) -> Dict[str, dict]:
    """Lee todas las hojas relevantes del archivo de insumos.

    Args:
        ruta_archivo: Ruta al archivo Excel de insumos.

    Returns:
        Diccionario con el resultado por hoja:
        {
            "FR NOV 2025": {"dataframe": df, "columnas": [...], "filas_datos": N, "errores": [...]},
            ...
        }
    """
    resultados: Dict[str, dict] = {}

    hojas_a_leer = HOJAS_FILL_RATE + [HOJA_VENTAS]

    for hoja in hojas_a_leer:
        df, errores = leer_hoja(ruta_archivo, hoja)
        resultados[hoja] = {
            "dataframe": df,
            "columnas": df.columns.tolist() if not df.empty else [],
            "filas_datos": len(df) if not df.empty else 0,
            "errores": errores,
        }

    return resultados


def imprimir_resumen(resultados: Dict[str, dict]) -> None:
    """Imprime en consola el resumen de lectura de cada hoja."""
    print("=" * 60)
    print("LECTURA DE INSUMOS EXCEL")
    print("=" * 60)
    print(f"Archivo: {INSUMOS_PATH}")
    print()

    for hoja, info in resultados.items():
        print(f"Hoja: {hoja}")
        print(f"  Columnas: {info['columnas']}")
        print(f"  Filas de datos: {info['filas_datos']}")
        if info["errores"]:
            print("  Errores:")
            for err in info["errores"]:
                print(f"    - {err}")
        print()


if __name__ == "__main__":
    resultados = leer_insumos()
    imprimir_resumen(resultados)
