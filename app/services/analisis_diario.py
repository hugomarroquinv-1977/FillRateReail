"""Servicio de análisis diario de Fill Rate.

Lee archivos Excel de la carpeta insumos/ con formato:
Pedido DD-mm-YYYY.xlsx

Columnas reales del Excel (según imagen 2):
- Columna A: Descri Clase (Categoría)
- Columna C: Centro de Carne
- Columna G: Pedido
- Columna H: Asignado
- Columna I: Diferencia
- Columna J: Sin Asignar
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Carpeta de insumos (solo lectura, nunca se modifica)
INSUMOS_PATH = Path("Insumos")

# Patrón para nombres de archivo: Pedido DD-mm-YYYY.xlsx
PATRON_ARCHIVO_PEDIDO = re.compile(r"^Pedido (\d{2})-(\d{2})-(\d{4})\.xlsx$")


def interpretar_fecha_nombre_archivo(nombre_archivo: str) -> Optional[datetime]:
    """Interpreta la fecha de un archivo tipo Pedido DD-mm-YYYY.xlsx.

    Args:
        nombre_archivo: Nombre del archivo Excel.

    Returns:
        Objeto datetime si coincide el patrón, None en caso contrario.
    """
    match = PATRON_ARCHIVO_PEDIDO.match(nombre_archivo)
    if not match:
        return None

    dia, mes, ano = int(match.group(1)), int(match.group(2)), int(match.group(3))
    try:
        return datetime(ano, mes, dia)
    except ValueError:
        return None


def listar_archivos_pedido(carpeta: Path = INSUMOS_PATH) -> list[tuple[datetime, Path]]:
    """Lista todos los archivos Pedido DD-mm-YYYY.xlsx con su fecha interpretada.

    Args:
        carpeta: Carpeta donde buscar los archivos.

    Returns:
        Lista de tuplas (fecha, ruta_archivo) ordenada por fecha descendente.
    """
    if not carpeta.exists():
        return []

    archivos_con_fecha = []
    for archivo in carpeta.glob("Pedido *.xlsx"):
        fecha = interpretar_fecha_nombre_archivo(archivo.name)
        if fecha is not None:
            archivos_con_fecha.append((fecha, archivo))

    # Ordenar por fecha descendente (más reciente primero)
    archivos_con_fecha.sort(key=lambda x: x[0], reverse=True)
    return archivos_con_fecha


def obtener_archivo_mas_reciente(carpeta: Path = INSUMOS_PATH) -> Optional[tuple[datetime, Path, pd.DataFrame]]:
    """Obtiene el archivo Pedido más reciente que se pueda leer correctamente.

    Intenta leer los archivos en orden descendente por fecha. Si el más reciente
    no se puede leer (ej. bloqueado por Excel), prueba con el siguiente.

    Args:
        carpeta: Carpeta donde buscar los archivos.

    Returns:
        Tupla (fecha, ruta, dataframe) o None si no se puede leer ningún archivo.
    """
    archivos = listar_archivos_pedido(carpeta)
    if not archivos:
        return None

    for fecha, ruta in archivos:
        try:
            df = pd.read_excel(ruta, sheet_name=0, header=None)
            return fecha, ruta, df
        except Exception:
            continue

    return None


def leer_archivo_por_fecha(fecha_objetivo: datetime, carpeta: Path = INSUMOS_PATH) -> Optional[pd.DataFrame]:
    """Lee el archivo Pedido para una fecha específica.

    Args:
        fecha_objetivo: Fecha a buscar (formato DD-mm-YYYY).
        carpeta: Carpeta donde buscar.

    Returns:
        DataFrame con los datos o None si no se encuentra.
    """
    nombre_esperado = f"Pedido {fecha_objetivo.day:02d}-{fecha_objetivo.month:02d}-{fecha_objetivo.year}.xlsx"
    ruta = carpeta / nombre_esperado

    if not ruta.exists():
        return None

    try:
        return pd.read_excel(ruta, sheet_name=0, header=None)
    except Exception:
        return None


def leer_archivos_por_mes_ano(mes: int, ano: int, carpeta: Path = INSUMOS_PATH) -> list[tuple[datetime, pd.DataFrame]]:
    """Lee todos los archivos Pedido de un mes y año específicos.

    Args:
        mes: Mes (1-12).
        ano: Año (ej. 2026).
        carpeta: Carpeta donde buscar.

    Returns:
        Lista de tuplas (fecha, dataframe) ordenada por fecha ascendente.
    """
    resultados = []
    archivos = listar_archivos_pedido(carpeta)

    for fecha, ruta in archivos:
        if fecha.month == mes and fecha.year == ano:
            try:
                df = pd.read_excel(ruta, sheet_name=0, header=None)
                resultados.append((fecha, df))
            except Exception:
                continue

    # Ordenar por fecha ascendente
    resultados.sort(key=lambda x: x[0])
    return resultados


def extraer_datos_factura(df: pd.DataFrame) -> pd.DataFrame:
    """Extrae y limpia los datos relevantes de un DataFrame de factura.

    Columnas mapeadas según imagen 2:
    - A (índice 0): Descri Clase
    - C (índice 2): Centro de Carne
    - G (índice 6): Pedido
    - H (índice 7): Asignado
    - J (índice 9): Sin Asignar

    Args:
        df: DataFrame leído del Excel sin encabezados.

    Returns:
        DataFrame con columnas: categoria, centro_carne, pedido, asignado, sin_asignar.
    """
    if df.empty:
        return pd.DataFrame(
            columns=["categoria", "centro_carne", "pedido", "asignado", "sin_asignar", "faltante"]
        )

    datos = pd.DataFrame()
    datos["categoria"] = df.iloc[:, 0] if df.shape[1] > 0 else None
    datos["centro_carne"] = df.iloc[:, 2] if df.shape[1] > 2 else None
    datos["pedido"] = pd.to_numeric(df.iloc[:, 6], errors="coerce") if df.shape[1] > 6 else None
    datos["asignado"] = pd.to_numeric(df.iloc[:, 7], errors="coerce") if df.shape[1] > 7 else None
    datos["sin_asignar"] = pd.to_numeric(df.iloc[:, 9], errors="coerce") if df.shape[1] > 9 else None

    # Calcular faltante = pedido - asignado
    datos["faltante"] = datos["pedido"] - datos["asignado"]

    # Eliminar filas donde todo esté vacío
    datos = datos.dropna(how="all").reset_index(drop=True)

    return datos


def calcular_estado_fill_rate(df: pd.DataFrame) -> dict:
    """Calcula las métricas de Fill Rate para un DataFrame.

    Implementa: Fill Rate % = (Suma Asignado / Suma Pedido) × 100

    Args:
        df: DataFrame con columnas pedido y asignado.

    Returns:
        Diccionario con total_pedido, total_asignado, fill_rate_pct.
    """
    if df.empty:
        return {
            "total_pedido": 0,
            "total_asignado": 0,
            "fill_rate_pct": 0.0,
        }

    total_pedido = df["pedido"].sum()
    total_asignado = df["asignado"].sum()

    if total_pedido > 0:
        fill_rate_pct = round((total_asignado / total_pedido) * 100, 2)
    else:
        fill_rate_pct = 0.0

    return {
        "total_pedido": int(total_pedido),
        "total_asignado": int(total_asignado),
        "fill_rate_pct": fill_rate_pct,
    }


def obtener_estado_ultima_fecha(carpeta: Path = INSUMOS_PATH) -> Optional[dict]:
    """Obtiene el estado de Fill Rate de la fecha más reciente.

    Args:
        carpeta: Carpeta donde buscar los archivos.

    Returns:
        Diccionario con fecha, total_pedido, total_asignado, fill_rate_pct,
        datos_por_centro, o None si no hay archivos.
    """
    resultado = obtener_archivo_mas_reciente(carpeta)
    if resultado is None:
        return None

    fecha, ruta, df_raw = resultado
    df = extraer_datos_factura(df_raw)

    estado = calcular_estado_fill_rate(df)

    # Agrupación por Centro de Carne
    if not df.empty and "centro_carne" in df.columns:
        agrupacion = (
            df.groupby("centro_carne", dropna=False)
            .agg(
                total_pedido=("pedido", "sum"),
                total_asignado=("asignado", "sum"),
                total_faltante=("faltante", "sum"),
            )
            .reset_index()
        )

        # Calcular % de fill rate por centro
        agrupacion["fill_rate_pct"] = (
            (agrupacion["total_asignado"] / agrupacion["total_pedido"]) * 100
        ).where(agrupacion["total_pedido"] > 0, 0).round(2)

        datos_por_centro = agrupacion.to_dict("records")
    else:
        datos_por_centro = []

    return {
        "fecha": fecha.strftime("%d-%m-%Y"),
        "fecha_objeto": fecha,
        "total_pedido": estado["total_pedido"],
        "total_asignado": estado["total_asignado"],
        "fill_rate_pct": estado["fill_rate_pct"],
        "datos_por_centro": datos_por_centro,
    }


def obtener_estado_mes_ano(mes: int, ano: int, carpeta: Path = INSUMOS_PATH) -> Optional[dict]:
    """Obtiene el estado acumulado de Fill Rate para un mes y año.

    Acumula todos los archivos desde el día 1 del mes hasta la última fecha disponible.

    Args:
        mes: Mes (1-12).
        ano: Año (ej. 2026).
        carpeta: Carpeta donde buscar.

    Returns:
        Diccionario con mes, ano, total_pedido, total_asignado, fill_rate_pct,
        o None si no hay datos.
    """
    archivos_mes = leer_archivos_por_mes_ano(mes, ano, carpeta)

    if not archivos_mes:
        return None

    # Combinar todos los DataFrames del mes
    todos_los_datos = []
    fechas_encontradas = []

    for fecha, df_raw in archivos_mes:
        df = extraer_datos_factura(df_raw)
        if not df.empty:
            todos_los_datos.append(df)
            fechas_encontradas.append(fecha)

    if not todos_los_datos:
        return None

    df_combinado = pd.concat(todos_los_datos, ignore_index=True)
    estado = calcular_estado_fill_rate(df_combinado)

    fecha_primera = min(fechas_encontradas).strftime("%d-%m-%Y")
    fecha_ultima = max(fechas_encontradas).strftime("%d-%m-%Y")

    return {
        "mes": mes,
        "ano": ano,
        "fecha_primera": fecha_primera,
        "fecha_ultima": fecha_ultima,
        "dias_con_datos": len(fechas_encontradas),
        "total_pedido": estado["total_pedido"],
        "total_asignado": estado["total_asignado"],
        "fill_rate_pct": estado["fill_rate_pct"],
    }


def obtener_analisis_categoria(carpeta: Path = INSUMOS_PATH) -> Optional[dict]:
    """Obtiene análisis de faltante por categoría (columna A = Descri Clase).

    Tres clasificaciones:
    1. Total completo y % (todas las filas por categoría)
    2. Total parciales y % (filas con faltante > 0)
    3. Total sin asignar (columna J) y %

    Args:
        carpeta: Carpeta donde buscar los archivos.

    Returns:
        Diccionario con las tres clasificaciones o None si no hay datos.
    """
    archivos = listar_archivos_pedido(carpeta)

    if not archivos:
        return None

    todos_los_datos = []

    for _, ruta in archivos:
        try:
            df_raw = pd.read_excel(ruta, sheet_name=0, header=None)
            df = extraer_datos_factura(df_raw)
            if not df.empty:
                todos_los_datos.append(df)
        except Exception:
            continue

    if not todos_los_datos:
        return None

    df_combinado = pd.concat(todos_los_datos, ignore_index=True)

    # Clasificación 1: Total completo por categoría (todas las filas)
    total_por_categoria = (
        df_combinado.groupby("categoria", dropna=False)
        .agg(
            total_filas=("pedido", "count"),
            total_pedido=("pedido", "sum"),
            total_asignado=("asignado", "sum"),
            total_faltante=("faltante", "sum"),
            total_sin_asignar=("sin_asignar", "sum"),
        )
        .reset_index()
    )

    total_filas_global = total_por_categoria["total_filas"].sum()
    total_pedido_global = total_por_categoria["total_pedido"].sum()
    total_faltante_global = total_por_categoria["total_faltante"].sum()
    total_sin_asignar_global = total_por_categoria["total_sin_asignar"].sum()

    total_por_categoria["pct_filas"] = (
        (total_por_categoria["total_filas"] / total_filas_global) * 100
    ).round(2)
    if total_faltante_global > 0:
        total_por_categoria["pct_faltante"] = (
            (total_por_categoria["total_faltante"] / total_faltante_global) * 100
        ).round(2)
    else:
        total_por_categoria["pct_faltante"] = 0.0

    if total_sin_asignar_global > 0:
        total_por_categoria["pct_sin_asignar"] = (
            (total_por_categoria["total_sin_asignar"] / total_sin_asignar_global) * 100
        ).round(2)
    else:
        total_por_categoria["pct_sin_asignar"] = 0.0

    # Clasificación 2: Solo filas con faltante > 0 (parciales)
    df_con_faltante = df_combinado[df_combinado["faltante"] > 0]

    if not df_con_faltante.empty:
        parciales_por_categoria = (
            df_con_faltante.groupby("categoria", dropna=False)
            .agg(
                filas_con_faltante=("pedido", "count"),
                total_faltante=("faltante", "sum"),
            )
            .reset_index()
        )

        total_filas_faltante = parciales_por_categoria["filas_con_faltante"].sum()
        total_faltante_parciales = parciales_por_categoria["total_faltante"].sum()

        parciales_por_categoria["pct_filas_faltante"] = (
            (parciales_por_categoria["filas_con_faltante"] / total_filas_faltante) * 100
        ).round(2)
        parciales_por_categoria["pct_faltante_parciales"] = (
            (parciales_por_categoria["total_faltante"] / total_faltante_parciales) * 100
        ).round(2)
    else:
        parciales_por_categoria = pd.DataFrame(
            columns=["categoria", "filas_con_faltante", "total_faltante", "pct_filas_faltante", "pct_faltante_parciales"]
        )
        total_filas_faltante = 0
        total_faltante_parciales = 0

    # Clasificación 3: Sin asignar (columna J) - ya está en total_por_categoria como total_sin_asignar

    return {
        "total_filas_global": int(total_filas_global),
        "total_pedido_global": int(total_pedido_global),
        "total_faltante_global": int(total_faltante_global),
        "total_sin_asignar_global": int(total_sin_asignar_global),
        "total_por_categoria": total_por_categoria.to_dict("records"),
        "parciales_por_categoria": parciales_por_categoria.to_dict("records"),
        "total_filas_faltante": int(total_filas_faltante),
        "total_faltante_parciales": int(total_faltante_parciales),
    }


if __name__ == "__main__":
    # Prueba rápida
    estado = obtener_estado_ultima_fecha()
    if estado:
        print("=== Última fecha ===")
        print(f"Fecha: {estado['fecha']}")
        print(f"Total pedido: {estado['total_pedido']}")
        print(f"Total asignado: {estado['total_asignado']}")
        print(f"Fill Rate: {estado['fill_rate_pct']}%")
        print(f"Centros: {len(estado['datos_por_centro'])}")

    analisis = obtener_analisis_categoria()
    if analisis:
        print("\n=== Análisis por Categoría ===")
        print(f"Total filas: {analisis['total_filas_global']}")
        print(f"Total faltante: {analisis['total_faltante_global']}")
        print(f"Total sin asignar: {analisis['total_sin_asignar_global']}")
        print(f"Categorías: {len(analisis['total_por_categoria'])}")
