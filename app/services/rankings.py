"""Servicio de rankings de importancia comercial (R22, R23, R24, R25, R26, R27, R28).

- R22: Cruzar los productos con el archivo de ventas del mes anterior.
- R23: Cruzar los productos con las ventas del mismo mes del año anterior.
- R24: Generar rankings independientes por kilos vendidos y por ventas en colones.
- R25: Generar los rankings por Centro de Carne, por categoría y a nivel consolidado.
- R26: Mantener separados los indicadores históricos de ambos períodos, sin ponderaciones no aprobadas.
- R27: Si un producto no aparece en el histórico de ventas, mostrarlo como dato no disponible (no como cero).
- R28: No convertir las ventas históricas en una supuesta pérdida económica real sin metodología aprobada.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd


def cargar_ventas(ruta_archivo: str, hoja: int = 0) -> pd.DataFrame:
    """Carga un archivo de ventas históricas.

    Args:
        ruta_archivo: Ruta al archivo Excel de ventas.
        hoja: Índice o nombre de la hoja a leer.

    Returns:
        DataFrame con los datos de ventas.
    """
    df = pd.read_excel(ruta_archivo, sheet_name=hoja, header=None)

    # Detectar fila de encabezados (primera fila no vacía)
    fila_encabezados = None
    for idx in range(df.shape[0]):
        if not df.iloc[idx].isna().all():
            fila_encabezados = idx
            break

    if fila_encabezados is None:
        return pd.DataFrame()

    encabezados = [str(c) if pd.notna(c) else f"Col_{i}" for i, c in enumerate(df.iloc[fila_encabezados].tolist())]
    datos = df.iloc[fila_encabezados + 1 :].copy()
    datos.columns = encabezados
    datos = datos.dropna(how="all").reset_index(drop=True)

    return datos


def cruzar_con_ventas(
    df_productos: pd.DataFrame,
    df_ventas: pd.DataFrame,
    col_producto: str = "Descri Articulo",
    col_centro: Optional[str] = None,
    col_ventas_kg: str = "Cantidad",
    col_ventas_crc: str = "Total",
    periodo: str = "no indicado",
) -> pd.DataFrame:
    """Cruza productos con ventas históricas (R22, R23, R27).

    Si un producto no aparece en el histórico, se muestra como "no disponible"
    (no como cero ventas).

    Args:
        df_productos: DataFrame con los productos del Fill Rate.
        df_ventas: DataFrame con el histórico de ventas.
        col_producto: Columna que identifica al producto en ambos DataFrames.
        col_centro: Columna de Centro de Carne (opcional, para cruce por centro).
        col_ventas_kg: Columna de kilos vendidos en el archivo de ventas.
        col_ventas_crc: Columna de ventas en colones en el archivo de ventas.
        periodo: Identificador del período de ventas (ej. "Octubre 2026").

    Returns:
        DataFrame con productos cruzados con sus ventas históricas o "no disponible".
    """
    if df_ventas.empty:
        df_productos = df_productos.copy()
        df_productos[f"Ventas_kg_{periodo}"] = "no disponible"
        df_productos[f"Ventas_crc_{periodo}"] = "no disponible"
        df_productos[f"Periodo_ventas_{periodo}"] = "no disponible"
        return df_productos

    # Agrupar ventas por producto (y por centro si existe)
    if col_centro and col_centro in df_ventas.columns and col_centro in df_productos.columns:
        ventas_agrupadas = (
            df_ventas.groupby([col_centro, col_producto], dropna=False)
            .agg(
                Ventas_kg=(col_ventas_kg, "sum"),
                Ventas_crc=(col_ventas_crc, "sum"),
            )
            .reset_index()
        )
        columnas_cruce = [col_centro, col_producto]
    else:
        ventas_agrupadas = (
            df_ventas.groupby(col_producto, dropna=False)
            .agg(
                Ventas_kg=(col_ventas_kg, "sum"),
                Ventas_crc=(col_ventas_crc, "sum"),
            )
            .reset_index()
        )
        columnas_cruce = [col_producto]

    # Renombrar columnas de ventas con el período
    ventas_agrupadas = ventas_agrupadas.rename(
        columns={
            "Ventas_kg": f"Ventas_kg_{periodo}",
            "Ventas_crc": f"Ventas_crc_{periodo}",
        }
    )
    ventas_agrupadas[f"Periodo_ventas_{periodo}"] = periodo

    # Cruzar (left join: mantener todos los productos del Fill Rate)
    resultado = df_productos.merge(
        ventas_agrupadas,
        on=columnas_cruce,
        how="left",
    )

    # R27: productos sin ventas históricas -> "no disponible", no cero
    columnas_venta = [f"Ventas_kg_{periodo}", f"Ventas_crc_{periodo}"]
    for col in columnas_venta:
        if col in resultado.columns:
            resultado[col] = resultado[col].fillna("no disponible")

    return resultado


def ranking_por_kilos(
    df: pd.DataFrame,
    col_producto: str = "Descri Articulo",
    col_ventas_kg: str = "Ventas_kg_no indicado",
    col_centro: Optional[str] = None,
    col_categoria: Optional[str] = None,
    top_n: Optional[int] = None,
) -> pd.DataFrame:
    """Genera ranking independiente por kilos vendidos (R24, R25).

    Args:
        df: DataFrame con productos cruzados con ventas.
        col_producto: Columna del producto.
        col_ventas_kg: Columna de ventas en kilos (ya debe ser numérica).
        col_centro: Columna de Centro de Carne (opcional).
        col_categoria: Columna de Categoría (opcional).
        top_n: Número de productos destacados (pendiente de definir, R26).

    Returns:
        DataFrame ordenado de mayor a menor por kilos vendidos.
    """
    # Filtrar solo filas con ventas numéricas (excluir "no disponible")
    df_valido = df[pd.to_numeric(df[col_ventas_kg], errors="coerce").notna()].copy()

    if df_valido.empty:
        return pd.DataFrame()

    df_valido[col_ventas_kg] = pd.to_numeric(df_valido[col_ventas_kg])

    columnas_agrupacion = [col_producto]
    if col_centro and col_centro in df_valido.columns:
        columnas_agrupacion.insert(0, col_centro)
    if col_categoria and col_categoria in df_valido.columns:
        columnas_agrupacion.append(col_categoria)

    ranking = (
        df_valido.groupby(columnas_agrupacion, dropna=False)[col_ventas_kg]
        .sum()
        .reset_index()
        .sort_values(col_ventas_kg, ascending=False)
    )

    if top_n is not None:
        ranking = ranking.head(top_n)

    ranking["Metrica"] = "Kilos vendidos"
    return ranking


def ranking_por_colones(
    df: pd.DataFrame,
    col_producto: str = "Descri Articulo",
    col_ventas_crc: str = "Ventas_crc_no indicado",
    col_centro: Optional[str] = None,
    col_categoria: Optional[str] = None,
    top_n: Optional[int] = None,
) -> pd.DataFrame:
    """Genera ranking independiente por ventas en colones (R24, R25).

    Args:
        df: DataFrame con productos cruzados con ventas.
        col_producto: Columna del producto.
        col_ventas_crc: Columna de ventas en colones (ya debe ser numérica).
        col_centro: Columna de Centro de Carne (opcional).
        col_categoria: Columna de Categoría (opcional).
        top_n: Número de productos destacados (pendiente de definir, R26).

    Returns:
        DataFrame ordenado de mayor a menor por ventas en colones.
    """
    df_valido = df[pd.to_numeric(df[col_ventas_crc], errors="coerce").notna()].copy()

    if df_valido.empty:
        return pd.DataFrame()

    df_valido[col_ventas_crc] = pd.to_numeric(df_valido[col_ventas_crc])

    columnas_agrupacion = [col_producto]
    if col_centro and col_centro in df_valido.columns:
        columnas_agrupacion.insert(0, col_centro)
    if col_categoria and col_categoria in df_valido.columns:
        columnas_agrupacion.append(col_categoria)

    ranking = (
        df_valido.groupby(columnas_agrupacion, dropna=False)[col_ventas_crc]
        .sum()
        .reset_index()
        .sort_values(col_ventas_crc, ascending=False)
    )

    if top_n is not None:
        ranking = ranking.head(top_n)

    ranking["Metrica"] = "Ventas en colones"
    return ranking


def rankings_completos(
    df: pd.DataFrame,
    col_producto: str = "Descri Articulo",
    col_ventas_kg: str = "Ventas_kg_no indicado",
    col_ventas_crc: str = "Ventas_crc_no indicado",
    col_centro: Optional[str] = None,
    col_categoria: Optional[str] = None,
) -> dict:
    """Genera todos los rankings comerciales (R22-R28).

    Retorna rankings independientes por kilos y por colones, por Centro de Carne,
    por categoría y a nivel consolidado.

    Args:
        df: DataFrame con productos cruzados con ventas.
        col_producto: Columna del producto.
        col_ventas_kg: Columna de ventas en kilos.
        col_ventas_crc: Columna de ventas en colones.
        col_centro: Columna de Centro de Carne (opcional).
        col_categoria: Columna de Categoría (opcional).

    Returns:
        Diccionario con claves:
        - ranking_kilos_consolidado
        - ranking_colones_consolidado
        - ranking_kilos_por_centro (si col_centro existe)
        - ranking_colones_por_centro (si col_centro existe)
        - ranking_kilos_por_categoria (si col_categoria existe)
        - ranking_colones_por_categoria (si col_categoria existe)
    """
    resultado = {}

    # Nivel consolidado (R25 - Total División Retail)
    resultado["ranking_kilos_consolidado"] = ranking_por_kilos(
        df, col_producto, col_ventas_kg, None, None
    )
    resultado["ranking_colones_consolidado"] = ranking_por_colones(
        df, col_producto, col_ventas_crc, None, None
    )

    # Por Centro de Carne (R25)
    if col_centro and col_centro in df.columns:
        for centro, grupo in df.groupby(col_centro, dropna=False):
            clave_centro = str(centro).replace(" ", "_")
            resultado[f"ranking_kilos_centro_{clave_centro}"] = ranking_por_kilos(
                grupo, col_producto, col_ventas_kg, None, None
            )
            resultado[f"ranking_colones_centro_{clave_centro}"] = ranking_por_colones(
                grupo, col_producto, col_ventas_crc, None, None
            )

    # Por Categoría (R25)
    if col_categoria and col_categoria in df.columns:
        for categoria, grupo in df.groupby(col_categoria, dropna=False):
            clave_categoria = str(categoria).replace(" ", "_")
            resultado[f"ranking_kilos_categoria_{clave_categoria}"] = ranking_por_kilos(
                grupo, col_producto, col_ventas_kg, None, None
            )
            resultado[f"ranking_colones_categoria_{clave_categoria}"] = ranking_por_colones(
                grupo, col_producto, col_ventas_crc, None, None
            )

    return resultado


if __name__ == "__main__":
    import pandas as pd

    # Datos de prueba del contexto (datos ficticios, sección 9.7 - octubre 2026)
    df_ventas_octubre = pd.DataFrame(
        {
            "Centro": ["CC A", "CC A", "CC B", "CC B"],
            "Descri Articulo": ["R001", "C001", "R001", "C001"],
            "Ventas kg": [900, 500, 350, 700],
            "Ventas ₡": [4500000, 1500000, 1750000, 2100000],
        }
    )

    df_productos = pd.DataFrame(
        {
            "Descri Articulo": ["R001", "C001", "R001", "C001"],
            "Centro": ["CC A", "CC A", "CC B", "CC B"],
        }
    )

    print("=" * 70)
    print("RANKINGS DE IMPORTANCIA COMERCIAL (R22-R28)")
    print("=" * 70)

    # Cruzar con ventas (R22)
    df_cruzado = cruzar_con_ventas(
        df_productos,
        df_ventas_octubre,
        col_producto="Descri Articulo",
        col_centro="Centro",
        col_ventas_kg="Ventas kg",
        col_ventas_crc="Ventas ₡",
        periodo="Octubre 2026",
    )

    print("\n--- Productos cruzados con ventas (R22, R27) ---")
    print(df_cruzado.to_string(index=False))

    # Rankings consolidados (R24, R25)
    rankings = rankings_completos(
        df_cruzado,
        col_producto="Descri Articulo",
        col_ventas_kg="Ventas_kg_Octubre 2026",
        col_ventas_crc="Ventas_crc_Octubre 2026",
        col_centro="Centro",
    )

    print("\n--- Ranking por kilos vendidos (consolidado) ---")
    print(rankings["ranking_kilos_consolidado"].to_string(index=False))

    print("\n--- Ranking por ventas en colones (consolidado) ---")
    print(rankings["ranking_colones_consolidado"].to_string(index=False))

    # Rankings por Centro de Carne (R25)
    print("\n--- Ranking por kilos por Centro de Carne ---")
    for clave, df_centro in rankings.items():
        if "centro_" in clave and "kilos" in clave:
            print(f"\n{clave}:")
            print(df_centro.to_string(index=False))
