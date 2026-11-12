"""Servicio de análisis de recurrencia de faltantes (R17, R18, R19, R20).

- R17: Consolidar el histórico diario de faltantes por Centro de Carne, categoría y artículo.
- R18: Contar la cantidad de fechas diferentes en las que un mismo producto registra
  kilos faltantes mayores que cero.
- R19: Identificar faltantes recurrentes cuando un producto tenga faltantes en dos o más
  fechas distintas.
- R20: Identificar faltantes en días consecutivos. Si falta el archivo de una fecha
  intermedia, no se debe asumir que existió o no un faltante ese día.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd


def consolidar_historico_diario(
    df: pd.DataFrame,
    col_fecha: str = "Fecha",
    col_centro: Optional[str] = None,
    col_categoria: Optional[str] = None,
    col_articulo: Optional[str] = None,
    col_faltantes: str = "Kilos faltantes",
) -> pd.DataFrame:
    """Consolida el histórico diario de faltantes (R17).

    Agrupa los faltantes por fecha y, si existen, por Centro de Carne, categoría y artículo.

    Args:
        df: DataFrame con los datos diarios ya calculados (con columna de faltantes).
        col_fecha: Nombre de la columna de fecha.
        col_centro: Nombre de la columna de Centro de Carne (opcional).
        col_categoria: Nombre de la columna de Categoría (opcional).
        col_articulo: Nombre de la columna de Artículo (opcional).
        col_faltantes: Nombre de la columna de kilos faltantes.

    Returns:
        DataFrame consolidado con faltantes por fecha y nivel de agrupación.
    """
    columnas_agrupacion = [col_fecha]

    if col_centro and col_centro in df.columns:
        columnas_agrupacion.append(col_centro)
    if col_categoria and col_categoria in df.columns:
        columnas_agrupacion.append(col_categoria)
    if col_articulo and col_articulo in df.columns:
        columnas_agrupacion.append(col_articulo)

    consolidado = (
        df.groupby(columnas_agrupacion, dropna=False)
        .agg(
            Faltante_total_kg=(col_faltantes, "sum"),
            Registros=(col_faltantes, "count"),
        )
        .reset_index()
    )

    return consolidado


def contar_fechas_con_faltante(
    df: pd.DataFrame,
    col_fecha: str = "Fecha",
    col_identificador: str = "Descri Articulo",
    col_faltantes: str = "Kilos faltantes",
) -> pd.DataFrame:
    """Cuenta fechas diferentes con faltantes > 0 por producto (R18).

    Args:
        df: DataFrame con datos diarios.
        col_fecha: Columna de fecha.
        col_identificador: Columna que identifica al producto (artículo).
        col_faltantes: Columna de kilos faltantes.

    Returns:
        DataFrame con identificador del producto, fechas_con_faltante y faltante_total_kg.
    """
    df_faltantes = df[df[col_faltantes] > 0].copy()

    if df_faltantes.empty:
        return pd.DataFrame(
            columns=[col_identificador, "Fechas_con_faltante", "Faltante_total_kg"]
        )

    conteo = (
        df_faltantes.groupby(col_identificador, dropna=False)
        .agg(
            Fechas_con_faltante=(col_fecha, "nunique"),
            Faltante_total_kg=(col_faltantes, "sum"),
        )
        .reset_index()
    )

    return conteo.sort_values("Fechas_con_faltante", ascending=False)


def identificar_faltantes_recurrentes(
    df_conteo: pd.DataFrame,
    umbral_fechas: int = 2,
) -> pd.DataFrame:
    """Identifica faltantes recurrentes (R19).

    Un producto es recurrente si tiene faltantes en dos o más fechas distintas.

    Args:
        df_conteo: Resultado de contar_fechas_con_faltante().
        umbral_fechas: Número mínimo de fechas para considerar recurrencia (por defecto 2).

    Returns:
        DataFrame solo con productos recurrentes.
    """
    if df_conteo.empty:
        return df_conteo

    recurrentes = df_conteo[df_conteo["Fechas_con_faltante"] >= umbral_fechas].copy()
    return recurrentes.sort_values("Fechas_con_faltante", ascending=False)


def analizar_dias_consecutivos(
    df: pd.DataFrame,
    col_fecha: str = "Fecha",
    col_identificador: str = "Descri Articulo",
    col_faltantes: str = "Kilos faltantes",
) -> pd.DataFrame:
    """Analiza faltantes en días consecutivos (R20).

    Identifica productos con faltantes en fechas consecutivas. Si falta una fecha
    intermedia en los archivos, no se asume que hubo o no faltante ese día.

    Args:
        df: DataFrame con datos diarios.
        col_fecha: Columna de fecha (debe ser tipo datetime).
        col_identificador: Columna que identifica al producto.
        col_faltantes: Columna de kilos faltantes.

    Returns:
        DataFrame con productos que tienen faltantes en días consecutivos y las fechas.
    """
    df_faltantes = df[df[col_faltantes] > 0].copy()

    if df_faltantes.empty:
        return pd.DataFrame(
            columns=[col_identificador, "Fecha", "Faltante_kg", "Es_consecutivo"]
        )

    # Asegurar que la fecha sea datetime
    df_faltantes[col_fecha] = pd.to_datetime(df_faltantes[col_fecha], errors="coerce")
    df_faltantes = df_faltantes.dropna(subset=[col_fecha])

    resultados = []

    for identificador, grupo in df_faltantes.groupby(col_identificador, dropna=False):
        fechas_ordenadas = sorted(grupo[col_fecha].unique())

        for i in range(len(fechas_ordenadas) - 1):
            fecha_actual = fechas_ordenadas[i]
            fecha_siguiente = fechas_ordenadas[i + 1]
            diferencia_dias = (fecha_siguiente - fecha_actual).days

            es_consecutivo = diferencia_dias == 1

            resultados.append(
                {
                    col_identificador: identificador,
                    "Fecha_inicio": fecha_actual.strftime("%Y-%m-%d"),
                    "Fecha_siguiente": fecha_siguiente.strftime("%Y-%m-%d"),
                    "Dias_diferencia": diferencia_dias,
                    "Es_consecutivo": es_consecutivo,
                }
            )

    if not resultados:
        return pd.DataFrame(
            columns=[
                col_identificador,
                "Fecha_inicio",
                "Fecha_siguiente",
                "Dias_diferencia",
                "Es_consecutivo",
            ]
        )

    return pd.DataFrame(resultados)


def reporte_recurrencia_completo(
    df: pd.DataFrame,
    col_fecha: str = "Fecha",
    col_identificador: str = "Descri Articulo",
    col_faltantes: str = "Kilos faltantes",
) -> dict:
    """Genera el reporte completo de recurrencia (R17, R18, R19, R20).

    Returns:
        Diccionario con:
        - historico: consolidado diario.
        - conteo_fechas: conteo de fechas con faltante por producto.
        - recurrentes: productos con faltantes recurrentes (2+ fechas).
        - consecutivos: análisis de días consecutivos.
    """
    historico = consolidar_historico_diario(
        df,
        col_fecha=col_fecha,
        col_faltantes=col_faltantes,
    )

    conteo = contar_fechas_con_faltante(
        df,
        col_fecha=col_fecha,
        col_identificador=col_identificador,
        col_faltantes=col_faltantes,
    )

    recurrentes = identificar_faltantes_recurrentes(conteo)

    consecutivos = analizar_dias_consecutivos(
        df,
        col_fecha=col_fecha,
        col_identificador=col_identificador,
        col_faltantes=col_faltantes,
    )

    return {
        "historico": historico,
        "conteo_fechas": conteo,
        "recurrentes": recurrentes,
        "consecutivos": consecutivos,
    }


if __name__ == "__main__":
    import pandas as pd

    # Datos de prueba del contexto (datos ficticios de aceptación, sección 9.6)
    df_prueba = pd.DataFrame(
        {
            "Fecha": [
                "2026-11-01",
                "2026-11-01",
                "2026-11-02",
                "2026-11-02",
                "2026-11-01",
                "2026-11-02",
            ],
            "Centro": ["CC A", "CC B", "CC A", "CC B", "CC A", "CC B"],
            "Descri Articulo": ["R001", "R001", "R001", "R001", "C001", "C001"],
            "Kilos faltantes": [55, 20, 0, 0, 26, 26],
        }
    )

    print("=" * 70)
    print("ANÁLISIS DE RECURRENCIA DE FALTANTES (R17, R18, R19, R20)")
    print("=" * 70)

    reporte = reporte_recurrencia_completo(
        df_prueba,
        col_fecha="Fecha",
        col_identificador="Descri Articulo",
        col_faltantes="Kilos faltantes",
    )

    print("\n--- Conteo de fechas con faltante por producto (R18) ---")
    print(reporte["conteo_fechas"].to_string(index=False))

    print("\n--- Faltantes recurrentes (2+ fechas) (R19) ---")
    print(reporte["recurrentes"].to_string(index=False))

    print("\n--- Análisis de días consecutivos (R20) ---")
    print(reporte["consecutivos"].to_string(index=False))
