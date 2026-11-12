"""Servicio de agregación de indicadores (R14, R15).

- R14: Fill Rate consolidado con totales, no promedio de porcentajes.
- R15: Calcular Fill Rate y kilos faltantes para:
    - Producto
    - Categoría
    - Centro de Carne
    - Categoría dentro de cada Centro de Carne
    - Total de la División Retail
"""

from __future__ import annotations

from typing import Optional

import pandas as pd


def agregar_por_columnas(
    df: pd.DataFrame,
    columnas_agrupacion: list[str],
    nombre_nivel: str,
) -> pd.DataFrame:
    """Agrega Fill Rate y kilos faltantes por uno o más niveles de agrupación.

    Implementa R14 (consolidado con totales) y parte de R15.

    Args:
        df: DataFrame con columnas calculadas (salida de calcular_dataframe).
        columnas_agrupacion: Columnas por las cuales agrupar.
        nombre_nivel: Nombre descriptivo del nivel (para la columna 'Nivel').

    Returns:
        DataFrame con: columnas de agrupación, Pedido kg, Entrega kg,
        Faltante kg, Fill Rate %, Registros.
    """
    df_valido = df[df["Es valido"] == True].copy()  # noqa: E712

    if df_valido.empty:
        return pd.DataFrame()

    agrupado = (
        df_valido.groupby(columnas_agrupacion, dropna=False)
        .agg(
            Pedido_kg=("Kilos solicitados", "sum"),
            Entrega_kg=("Kilos entregados", "sum"),
            Registros=("Kilos solicitados", "count"),
        )
        .reset_index()
    )

    agrupado["Faltante_kg"] = (
        agrupado["Pedido_kg"] - agrupado["Entrega_kg"]
    ).round(2)

    # R14: Fill Rate con totales, no promedio de porcentajes
    agrupado["Fill Rate %"] = (
        (agrupado["Entrega_kg"] / agrupado["Pedido_kg"]) * 100
    ).where(agrupado["Pedido_kg"] > 0, None).round(2)

    agrupado["Nivel"] = nombre_nivel

    # Reordenar columnas
    columnas_finales = (
        columnas_agrupacion
        + ["Pedido_kg", "Entrega_kg", "Faltante_kg", "Fill Rate %", "Registros", "Nivel"]
    )
    return agrupado[columnas_finales]


def agregar_por_producto(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega por producto (R15 - nivel Producto)."""
    return agregar_por_columnas(
        df,
        columnas_agrupacion=["Descri Articulo"] if "Descri Articulo" in df.columns else ["Artículo"],
        nombre_nivel="Producto",
    )


def agregar_por_categoria(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega por categoría (R15 - nivel Categoría)."""
    return agregar_por_columnas(
        df,
        columnas_agrupacion=["Descri Clase"] if "Descri Clase" in df.columns else ["Categoría"],
        nombre_nivel="Categoría",
    )


def agregar_por_centro_carne(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega por Centro de Carne (R15 - nivel Centro de Carne).

    Si el DataFrame no tiene columna de Centro de Carne, retorna vacío con aviso.
    """
    col_cc = None
    for candidato in ["Centro de Carne", "Centro", "CC"]:
        if candidato in df.columns:
            col_cc = candidato
            break

    if col_cc is None:
        # No hay columna de Centro de Carne en los datos; se omite este nivel
        return pd.DataFrame()

    return agregar_por_columnas(
        df,
        columnas_agrupacion=[col_cc],
        nombre_nivel="Centro de Carne",
    )


def agregar_por_categoria_dentro_centro_carne(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega por categoría dentro de cada Centro de Carne (R15).

    Si falta alguna de las dos columnas, retorna vacío.
    """
    col_cc = None
    for candidato in ["Centro de Carne", "Centro", "CC"]:
        if candidato in df.columns:
            col_cc = candidato
            break

    col_cat = None
    for candidato in ["Descri Clase", "Categoría", "Categoria"]:
        if candidato in df.columns:
            col_cat = candidato
            break

    if col_cc is None or col_cat is None:
        return pd.DataFrame()

    return agregar_por_columnas(
        df,
        columnas_agrupacion=[col_cc, col_cat],
        nombre_nivel="Categoría dentro de Centro de Carne",
    )


def agregar_total_division_retail(df: pd.DataFrame) -> pd.DataFrame:
    """Agrega el total de la División Retail (R15 - nivel Total).

    Implementa R14: Fill Rate con totales globales.
    """
    df_valido = df[df["Es valido"] == True].copy()  # noqa: E712

    if df_valido.empty:
        return pd.DataFrame()

    pedido_total = df_valido["Kilos solicitados"].sum()
    entrega_total = df_valido["Kilos entregados"].sum()
    faltante_total = pedido_total - entrega_total

    if pedido_total > 0:
        fill_rate = round((entrega_total / pedido_total) * 100, 2)
    else:
        fill_rate = None

    return pd.DataFrame(
        [
            {
                "Nivel": "Total División Retail",
                "Pedido_kg": round(pedido_total, 2),
                "Entrega_kg": round(entrega_total, 2),
                "Faltante_kg": round(faltante_total, 2),
                "Fill Rate %": fill_rate,
                "Registros": len(df_valido),
            }
        ]
    )


def agregar_todos_los_niveles(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Ejecuta todas las agregaciones de R15 y retorna un diccionario por nivel.

    Returns:
        Diccionario con claves: producto, categoria, centro_carne,
        categoria_dentro_centro, total.
    """
    return {
        "producto": agregar_por_producto(df),
        "categoria": agregar_por_categoria(df),
        "centro_carne": agregar_por_centro_carne(df),
        "categoria_dentro_centro": agregar_por_categoria_dentro_centro_carne(df),
        "total": agregar_total_division_retail(df),
    }


if __name__ == "__main__":
    import pandas as pd

    # Datos de prueba del contexto (datos ficticios de aceptación)
    df_prueba = pd.DataFrame(
        {
            "Descri Clase": ["Res", "Res", "Cerdo", "Cerdo", "Res", "Cerdo", "Res", "Cerdo"],
            "Descri Articulo": ["R001", "R001", "C001", "C001", "R001", "C001", "R001", "C001"],
            "Pedido": [100, 120, 50, 80, 40, 30, 60, 70],
            "Recibido": [75, 90, 50, 80, 20, 30, 20, 56],
        }
    )

    # Primero calcular Fill Rate por registro
    from app.services.calculo_fill_rate import calcular_dataframe

    df_calc = calcular_dataframe(df_prueba)

    print("=" * 70)
    print("AGREGACIONES POR NIVEL (R14, R15)")
    print("=" * 70)

    # Por categoría
    print("\n--- Por Categoría ---")
    print(agregar_por_categoria(df_calc).to_string(index=False))

    # Por producto
    print("\n--- Por Producto ---")
    print(agregar_por_producto(df_calc).to_string(index=False))

    # Total División Retail
    print("\n--- Total División Retail ---")
    print(agregar_total_division_retail(df_calc).to_string(index=False))

    # Centro de Carne (no existe en datos de prueba, debería estar vacío)
    print("\n--- Centro de Carne (espera vacío si no hay columna) ---")
    resultado_cc = agregar_por_centro_carne(df_calc)
    print(f"Filas: {len(resultado_cc)} (vacío si no hay columna Centro de Carne)")
