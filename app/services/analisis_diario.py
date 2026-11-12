"""Servicio de análisis diario de Fill Rate.

Lee archivos Excel de la carpeta insumos/ con formato:
Pedido DD-mm-YYYY.xlsx

Columnas reales del Excel (según imagen 2, índice base 0):
- Columna A (0): Descri Clase / Categoría
- Columna C (2): Centro de Carne
- Columna G (6): Pedido
- Columna H (7): Asignado
- Columna I (8): Diferencia
- Columna J (9): Sin Asignar

LÓGICA DE CONTEO (no sumar valores):
- Total líneas de pedido: contar filas donde columna G tiene valor (excluyendo encabezado fila 1)
- Líneas asignadas: contar filas donde columna H tiene valor y H != 0
- Sin asignar: contar filas donde columna H es 0 o vacía
- Parciales: contar filas donde H < G (asignado menor que pedido)
- Fill Rate % = (líneas con H ≠ 0 / total líneas de pedido) × 100
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Carpeta de insumos (solo lectura, nunca se modifica)
INSUMOS_PATH = Path("Insumos")

# Carpeta de archivos cargados por el usuario (temporal, puede ser efímera en Render)
CARGA_TEMPORAL_PATH = Path("datos") / "carga_temporal"

# Patrón para nombres de archivo: Pedido DD-mm-YYYY.xlsx
PATRON_ARCHIVO_PEDIDO = re.compile(r"^Pedido (\d{2})-(\d{2})-(\d{4})\.xlsx$")


def asegurar_carpeta_carga_temporal() -> Path:
    """Crea la carpeta de carga temporal si no existe."""
    CARGA_TEMPORAL_PATH.mkdir(parents=True, exist_ok=True)
    return CARGA_TEMPORAL_PATH


def interpretar_fecha_nombre_archivo(nombre_archivo: str) -> Optional[datetime]:
    """Interpreta la fecha de un archivo tipo Pedido DD-mm-YYYY.xlsx."""
    match = PATRON_ARCHIVO_PEDIDO.match(nombre_archivo)
    if not match:
        return None

    dia, mes, ano = int(match.group(1)), int(match.group(2)), int(match.group(3))
    try:
        return datetime(ano, mes, dia)
    except ValueError:
        return None


def listar_archivos_pedido(
    carpeta_insumos: Path = INSUMOS_PATH,
    carpeta_carga: Path = CARGA_TEMPORAL_PATH,
) -> list[tuple[datetime, Path]]:
    """Lista todos los archivos Pedido DD-mm-YYYY.xlsx con su fecha interpretada.

    Busca en ambas carpetas: insumos/ (repositorio) y datos/carga_temporal/ (subidos por usuario).

    Ordena por fecha descendente (más reciente primero).
    """
    archivos_con_fecha = []

    for carpeta in [carpeta_insumos, carpeta_carga]:
        if not carpeta.exists():
            continue
        for archivo in carpeta.glob("Pedido *.xlsx"):
            fecha = interpretar_fecha_nombre_archivo(archivo.name)
            if fecha is not None:
                archivos_con_fecha.append((fecha, archivo))

    archivos_con_fecha.sort(key=lambda x: x[0], reverse=True)
    return archivos_con_fecha


def guardar_archivo_cargado(contenido: bytes, nombre_archivo: str) -> Path:
    """Guarda un archivo subido por el usuario en la carpeta temporal.

    Args:
        contenido: Bytes del archivo.
        nombre_archivo: Nombre del archivo (debe ser Pedido DD-mm-YYYY.xlsx).

    Returns:
        Ruta del archivo guardado.
    """
    carpeta = asegurar_carpeta_carga_temporal()
    ruta = carpeta / nombre_archivo
    with open(ruta, "wb") as f:
        f.write(contenido)
    return ruta


def leer_archivo_excel(ruta: Path) -> Optional[pd.DataFrame]:
    """Lee un archivo Excel sin encabezados.

    Intenta leer el archivo. Si falla (bloqueado por Excel, etc.), devuelve None.
    """
    try:
        df = pd.read_excel(ruta, sheet_name=0, header=None)
        return df
    except Exception:
        return None


def obtener_archivo_mas_reciente(
    carpeta_insumos: Path = INSUMOS_PATH,
    carpeta_carga: Path = CARGA_TEMPORAL_PATH,
) -> Optional[tuple[datetime, Path, pd.DataFrame]]:
    """Obtiene el archivo Pedido más reciente que se pueda leer correctamente.

    Intenta leer los archivos en orden descendente por fecha.
    Si el más reciente está bloqueado, prueba con el siguiente.
    Busca en ambas carpetas: insumos/ y datos/carga_temporal/.
    """
    archivos = listar_archivos_pedido(carpeta_insumos, carpeta_carga)
    if not archivos:
        return None

    for fecha, ruta in archivos:
        df = leer_archivo_excel(ruta)
        if df is not None:
            return fecha, ruta, df

    return None


def obtener_archivo_por_fecha(
    fecha_objetivo: datetime,
    carpeta_insumos: Path = INSUMOS_PATH,
    carpeta_carga: Path = CARGA_TEMPORAL_PATH,
) -> Optional[pd.DataFrame]:
    """Lee el archivo Pedido para una fecha específica.

    Busca primero en la carpeta de carga temporal (archivos subidos por usuario)
    y luego en la carpeta de insumos.
    """
    nombre_esperado = f"Pedido {fecha_objetivo.day:02d}-{fecha_objetivo.month:02d}-{fecha_objetivo.year}.xlsx"

    # Buscar primero en carga temporal
    ruta = carpeta_carga / nombre_esperado
    if ruta.exists():
        return leer_archivo_excel(ruta)

    # Luego en insumos
    ruta = carpeta_insumos / nombre_esperado
    if ruta.exists():
        return leer_archivo_excel(ruta)

    return None


def leer_archivos_por_mes_ano(
    mes: int,
    ano: int,
    carpeta_insumos: Path = INSUMOS_PATH,
    carpeta_carga: Path = CARGA_TEMPORAL_PATH,
) -> list[tuple[datetime, pd.DataFrame]]:
    """Lee todos los archivos Pedido de un mes y año específicos.

    Busca en ambas carpetas: insumos/ y datos/carga_temporal/.

    Retorna lista de tuplas (fecha, dataframe) ordenada por fecha ascendente.
    """
    resultados = []
    archivos = listar_archivos_pedido(carpeta_insumos, carpeta_carga)

    for fecha, ruta in archivos:
        if fecha.month == mes and fecha.year == ano:
            df = leer_archivo_excel(ruta)
            if df is not None:
                resultados.append((fecha, df))

    resultados.sort(key=lambda x: x[0])
    return resultados


def contar_filas_con_valor(df: pd.DataFrame, columna_idx: int, valor_excluir: Optional[float] = None) -> int:
    """Cuenta filas donde una columna tiene un valor válido (no vacío, no NaN).

    Opcionalmente excluye filas donde el valor sea igual a valor_excluir.

    Args:
        df: DataFrame con los datos.
        columna_idx: Índice de la columna (base 0).
        valor_excluir: Si se especifica, no contar filas donde el valor sea igual a este.

    Returns:
        Número de filas que cumplen la condición.
    """
    if df.empty or df.shape[1] <= columna_idx:
        return 0

    columna = df.iloc[:, columna_idx]

    # Convertir a numérico, errores se convierten en NaN
    columna_numerica = pd.to_numeric(columna, errors="coerce")

    # Contar no nulos
    mask_valido = columna_numerica.notna()

    if valor_excluir is not None:
        mask_valido = mask_valido & (columna_numerica != valor_excluir)

    return int(mask_valido.sum())


def contar_filas_por_categoria(df: pd.DataFrame) -> dict:
    """Cuenta filas por categoría (columna A, índice 0).

    Retorna diccionario {categoria: conteo_filas}.
    """
    if df.empty or df.shape[1] <= 0:
        return {}

    columna_categoria = df.iloc[:, 0].astype(str).str.strip()
    # Eliminar filas vacías o encabezados repetidos
    columna_categoria = columna_categoria[columna_categoria != ""]
    columna_categoria = columna_categoria[columna_categoria != "Descri Clase"]

    conteo = columna_categoria.value_counts()
    return conteo.to_dict()


def extraer_estadisticas_archivo(df: pd.DataFrame) -> dict:
    """Extrae estadísticas de conteo de un DataFrame de archivo Excel.

    Lógica de conteo (no sumar):
    - total_lineas_pedido: filas donde columna G (índice 6) tiene valor
    - lineas_asignadas: filas donde columna H (índice 7) tiene valor y H != 0
    - lineas_sin_asignar: filas donde columna H es 0 o vacía
    - lineas_parciales: filas donde H < G (asignado menor que pedido)

    Args:
        df: DataFrame leído del Excel sin encabezados.

    Returns:
        Diccionario con los conteos y porcentajes.
    """
    if df.empty:
        return {
            "total_lineas_pedido": 0,
            "lineas_asignadas": 0,
            "lineas_sin_asignar": 0,
            "lineas_parciales": 0,
            "fill_rate_pct": 0.0,
        }

    # Fila 1 (índice 0) es encabezado, saltarla
    datos = df.iloc[1:].copy() if len(df) > 1 else pd.DataFrame()

    if datos.empty:
        return {
            "total_lineas_pedido": 0,
            "lineas_asignadas": 0,
            "lineas_sin_asignar": 0,
            "lineas_parciales": 0,
            "fill_rate_pct": 0.0,
        }

    # Columna G (índice 6): Pedido
    if datos.shape[1] > 6:
        columna_pedido = pd.to_numeric(datos.iloc[:, 6], errors="coerce")
        total_lineas_pedido = int(columna_pedido.notna().sum())
    else:
        total_lineas_pedido = 0

    # Columna H (índice 7): Asignado
    if datos.shape[1] > 7:
        columna_asignado = pd.to_numeric(datos.iloc[:, 7], errors="coerce")

        # Líneas asignadas: H tiene valor y H != 0
        mask_asignado = columna_asignado.notna() & (columna_asignado != 0)
        lineas_asignadas = int(mask_asignado.sum())

        # Sin asignar: H es 0 o vacía
        mask_sin_asignado = columna_asignado.isna() | (columna_asignado == 0)
        lineas_sin_asignar = int(mask_sin_asignado.sum())
    else:
        columna_asignado = pd.Series([float('nan')] * len(datos))
        lineas_asignadas = 0
        lineas_sin_asignar = total_lineas_pedido

    # Parciales: H < G (asignado menor que pedido, y H != 0)
    if datos.shape[1] > 6 and datos.shape[1] > 7:
        mask_parcial = (
            columna_asignado.notna()
            & (columna_asignado != 0)
            & (columna_asignado < columna_pedido)
        )
        lineas_parciales = int(mask_parcial.sum())
    else:
        lineas_parciales = 0

    # Fill Rate % = (líneas asignadas / total líneas de pedido) × 100
    if total_lineas_pedido > 0:
        fill_rate_pct = round((lineas_asignadas / total_lineas_pedido) * 100, 2)
    else:
        fill_rate_pct = 0.0

    return {
        "total_lineas_pedido": total_lineas_pedido,
        "lineas_asignadas": lineas_asignadas,
        "lineas_sin_asignar": lineas_sin_asignar,
        "lineas_parciales": lineas_parciales,
        "fill_rate_pct": fill_rate_pct,
    }


def agregar_estadisticas(estadisticas_lista: list[dict]) -> dict:
    """Agrega estadísticas de múltiples archivos sumando los conteos.

    Args:
        estadisticas_lista: Lista de diccionarios con estadísticas individuales.

    Returns:
        Diccionario con totales agregados y fill rate calculado.
    """
    total_pedido = sum(e["total_lineas_pedido"] for e in estadisticas_lista)
    total_asignadas = sum(e["lineas_asignadas"] for e in estadisticas_lista)
    total_sin_asignar = sum(e["lineas_sin_asignar"] for e in estadisticas_lista)
    total_parciales = sum(e["lineas_parciales"] for e in estadisticas_lista)

    if total_pedido > 0:
        fill_rate_pct = round((total_asignadas / total_pedido) * 100, 2)
    else:
        fill_rate_pct = 0.0

    return {
        "total_lineas_pedido": total_pedido,
        "lineas_asignadas": total_asignadas,
        "lineas_sin_asignar": total_sin_asignar,
        "lineas_parciales": total_parciales,
        "fill_rate_pct": fill_rate_pct,
    }


def obtener_estado_ultima_fecha(
    carpeta_insumos: Path = INSUMOS_PATH,
    carpeta_carga: Path = CARGA_TEMPORAL_PATH,
) -> Optional[dict]:
    """Obtiene el estado de Fill Rate de la fecha más reciente.

    Busca en ambas carpetas: insumos/ y datos/carga_temporal/.

    Returns:
        Diccionario con fecha, conteos y fill rate, o None si no hay archivos.
    """
    resultado = obtener_archivo_mas_reciente(carpeta_insumos, carpeta_carga)
    if resultado is None:
        return None

    fecha, ruta, df = resultado
    estadisticas = extraer_estadisticas_archivo(df)

    # Agrupación por Centro de Carne (columna C, índice 2)
    datos_por_centro = []
    if not df.empty and df.shape[1] > 2:
        datos = df.iloc[1:].copy() if len(df) > 1 else pd.DataFrame()
        if not datos.empty and datos.shape[1] > 2:
            columna_centro = datos.iloc[:, 2].astype(str).str.strip()
            columna_centro = columna_centro[columna_centro != ""]
            columna_centro = columna_centro[columna_centro != "Centro de Carnes"]

            for centro, grupo in datos.groupby(columna_centro, dropna=False):
                stats_centro = extraer_estadisticas_archivo(pd.DataFrame(grupo))
                datos_por_centro.append({
                    "centro_carne": str(centro),
                    **stats_centro,
                })

            # Ordenar por total de pedido descendente
            datos_por_centro.sort(key=lambda x: x["total_lineas_pedido"], reverse=True)

    return {
        "fecha": fecha.strftime("%d-%m-%Y"),
        "fecha_objeto": fecha,
        **estadisticas,
        "datos_por_centro": datos_por_centro,
    }


def obtener_estado_mes_ano(
    mes: int,
    ano: int,
    carpeta_insumos: Path = INSUMOS_PATH,
    carpeta_carga: Path = CARGA_TEMPORAL_PATH,
) -> Optional[dict]:
    """Obtiene el estado acumulado de Fill Rate para un mes y año.

    Suma los conteos de todas las filas de todos los archivos del mes.
    Busca en ambas carpetas: insumos/ y datos/carga_temporal/.

    Args:
        mes: Mes (1-12).
        ano: Año (ej. 2026).
        carpeta_insumos: Carpeta de insumos del repositorio.
        carpeta_carga: Carpeta de carga temporal (archivos subidos por usuario).

    Returns:
        Diccionario con totales del mes, o None si no hay datos.
    """
    archivos_mes = leer_archivos_por_mes_ano(mes, ano, carpeta_insumos, carpeta_carga)

    if not archivos_mes:
        return None

    estadisticas_lista = []
    fechas_encontradas = []

    for fecha, df in archivos_mes:
        stats = extraer_estadisticas_archivo(df)
        if stats["total_lineas_pedido"] > 0:
            estadisticas_lista.append(stats)
            fechas_encontradas.append(fecha)

    if not estadisticas_lista:
        return None

    agregado = agregar_estadisticas(estadisticas_lista)

    fecha_primera = min(fechas_encontradas).strftime("%d-%m-%Y")
    fecha_ultima = max(fechas_encontradas).strftime("%d-%m-%Y")

    return {
        "mes": mes,
        "ano": ano,
        "fecha_primera": fecha_primera,
        "fecha_ultima": fecha_ultima,
        "dias_con_datos": len(fechas_encontradas),
        **agregado,
    }


def obtener_analisis_categoria(
    carpeta_insumos: Path = INSUMOS_PATH,
    carpeta_carga: Path = CARGA_TEMPORAL_PATH,
) -> Optional[dict]:
    """Obtiene análisis de faltante por categoría (columna A = Descri Clase).

    Tres clasificaciones contando filas (no sumando valores):
    1. Total completo: contar filas por categoría
    2. Parciales: contar filas donde faltante > 0 (H < G y H != 0)
    3. Sin asignar (columna J): contar filas donde columna J tiene valor

    Busca en ambas carpetas: insumos/ y datos/carga_temporal/.

    Args:
        carpeta_insumos: Carpeta de insumos del repositorio.
        carpeta_carga: Carpeta de carga temporal (archivos subidos por usuario).

    Returns:
        Diccionario con las tres clasificaciones, o None si no hay datos.
    """
    archivos = listar_archivos_pedido(carpeta_insumos, carpeta_carga)

    if not archivos:
        return None

    todos_los_datos = []

    for _, ruta in archivos:
        df = leer_archivo_excel(ruta)
        if df is not None and not df.empty:
            # Saltar fila 1 (encabezado)
            datos = df.iloc[1:].copy() if len(df) > 1 else pd.DataFrame()
            if not datos.empty:
                todos_los_datos.append(datos)

    if not todos_los_datos:
        return None

    df_combinado = pd.concat(todos_los_datos, ignore_index=True)

    total_filas_global = len(df_combinado)

    # Categoría (columna A, índice 0) - limpiar encabezados repetidos
    if df_combinado.shape[1] > 0:
        columna_categoria = df_combinado.iloc[:, 0].astype(str).str.strip()
        mascara_valida = (columna_categoria != "") & (columna_categoria != "Descri Clase")
        df_valido = df_combinado[mascara_valida].copy()
        df_valido["_categoria"] = columna_categoria[mascara_valida].reset_index(drop=True)
    else:
        df_valido = pd.DataFrame()
        df_valido["_categoria"] = pd.Series([], dtype=str)

    # Totales globales usando extraer_estadisticas_archivo en el dataframe completo
    stats_global = extraer_estadisticas_archivo(df_valido)
    total_pedido_global = stats_global["total_lineas_pedido"]
    total_faltante_global = stats_global["total_lineas_pedido"] - stats_global["lineas_asignadas"]
    total_sin_asignar_global = stats_global["lineas_sin_asignar"]

    # Clasificación 1: Total completo por categoría
    total_por_categoria = []

    for categoria, grupo in df_valido.groupby("_categoria", dropna=False):
        stats = extraer_estadisticas_archivo(grupo)
        filas_categoria = stats["total_lineas_pedido"]
        faltante_categoria = filas_categoria - stats["lineas_asignadas"]
        sin_asignar_categoria = stats["lineas_sin_asignar"]

        total_por_categoria.append({
            "categoria": str(categoria),
            "total_filas": filas_categoria,
            "pct_filas": round((filas_categoria / total_filas_global) * 100, 2) if total_filas_global > 0 else 0.0,
            "total_pedido": filas_categoria,
            "total_asignado": stats["lineas_asignadas"],
            "total_faltante": faltante_categoria,
            "pct_faltante": round((faltante_categoria / total_filas_global) * 100, 2) if total_filas_global > 0 else 0.0,
            "total_sin_asignar": sin_asignar_categoria,
            "pct_sin_asignar": round((sin_asignar_categoria / total_filas_global) * 100, 2) if total_filas_global > 0 else 0.0,
        })

    # Ordenar por total de filas descendente
    total_por_categoria.sort(key=lambda x: x["total_filas"], reverse=True)

    # Clasificación 2: Parciales (filas donde H < G y H != 0, es decir, faltante > 0)
    df_con_faltante = df_valido[
        (df_valido.shape[1] > 6) &
        (pd.to_numeric(df_valido.iloc[:, 6], errors="coerce").notna()) &
        (df_valido.shape[1] > 7) &
        (pd.to_numeric(df_valido.iloc[:, 7], errors="coerce").notna()) &
        (pd.to_numeric(df_valido.iloc[:, 6], errors="coerce") > pd.to_numeric(df_valido.iloc[:, 7], errors="coerce")) &
        (pd.to_numeric(df_valido.iloc[:, 7], errors="coerce") != 0)
    ]

    parciales_por_categoria = []
    total_filas_faltante = len(df_con_faltante)
    total_faltante_parciales = 0

    if not df_con_faltante.empty and "_categoria" in df_con_faltante.columns:
        for categoria, grupo in df_con_faltante.groupby("_categoria", dropna=False):
            stats = extraer_estadisticas_archivo(grupo)
            filas_categoria = stats["total_lineas_pedido"]
            faltante_categoria = filas_categoria - stats["lineas_asignadas"]
            total_faltante_parciales += faltante_categoria

            parciales_por_categoria.append({
                "categoria": str(categoria),
                "filas_con_faltante": filas_categoria,
                "pct_filas_faltante": round((filas_categoria / total_filas_faltante) * 100, 2) if total_filas_faltante > 0 else 0.0,
                "total_faltante": faltante_categoria,
                "pct_faltante_parciales": round((faltante_categoria / total_faltante_parciales) * 100, 2) if total_faltante_parciales > 0 else 0.0,
            })

        # Ordenar por filas con faltante descendente
        parciales_por_categoria.sort(key=lambda x: x["filas_con_faltante"], reverse=True)

    # Clasificación 3: Sin asignar (columna J, índice 9) - ya está en total_por_categoria

    return {
        "total_filas_global": total_filas_global,
        "total_pedido_global": total_pedido_global,
        "total_faltante_global": total_faltante_global,
        "total_sin_asignar_global": total_sin_asignar_global,
        "total_por_categoria": total_por_categoria,
        "parciales_por_categoria": parciales_por_categoria,
        "total_filas_faltante": total_filas_faltante,
        "total_faltante_parciales": total_faltante_parciales,
    }


if __name__ == "__main__":
    # Prueba rápida
    estado = obtener_estado_ultima_fecha()
    if estado:
        print("=== Última fecha ===")
        print(f"Fecha: {estado['fecha']}")
        print(f"Total líneas pedido: {estado['total_lineas_pedido']}")
        print(f"Líneas asignadas: {estado['lineas_asignadas']}")
        print(f"Líneas sin asignar: {estado['lineas_sin_asignar']}")
        print(f"Líneas parciales: {estado['lineas_parciales']}")
        print(f"Fill Rate: {estado['fill_rate_pct']}%")

    analisis = obtener_analisis_categoria()
    if analisis:
        print("\n=== Análisis por Categoría ===")
        print(f"Total filas: {analisis['total_filas_global']}")
        print(f"Categorías: {len(analisis['total_por_categoria'])}")
