"""Servicio de exportación de resultados (R30, R31).

- R30: Permitir exportar los datos y resultados en Excel y PDF.
- R31: Mantener identificable la fuente de cada cálculo.

Genera archivos localmente en la carpeta configurada (reportes/).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
from fpdf import FPDF
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Carpeta local configurable para reportes generados
CARPETA_REPORTES = Path("reportes")


def asegurar_carpeta_reportes() -> Path:
    """Crea la carpeta de reportes si no existe."""
    CARPETA_REPORTES.mkdir(parents=True, exist_ok=True)
    return CARPETA_REPORTES


def _nombre_archivo(prefijo: str, extension: str) -> str:
    """Genera un nombre de archivo con fecha y hora."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefijo}_{timestamp}.{extension}"


def exportar_excel(
    datos: dict[str, pd.DataFrame | str],
    nombre_archivo: str | None = None,
) -> str:
    """Exporta datos a un archivo Excel local.

    Implementa R30 (exportar en Excel) y R31 (fuente identificable).

    Args:
        datos: Diccionario con claves:
            - "hojas": dict {nombre_hoja: DataFrame} o lista de DataFrames.
            - "fuente": str con identificador de la fuente de los datos.
            - "titulo": str opcional para el título del reporte.
        nombre_archivo: Nombre opcional del archivo. Si es None, se genera uno con timestamp.

    Returns:
        Ruta del archivo Excel generado.
    """
    carpeta = asegurar_carpeta_reportes()
    if nombre_archivo is None:
        nombre_archivo = _nombre_archivo("reporte", "xlsx")
    ruta = carpeta / nombre_archivo

    wb = Workbook()

    # Estilos
    font_titulo = Font(bold=True, size=14, color="1F3864")
    font_encabezado = Font(bold=True, size=10, color="FFFFFF")
    font_fuente = Font(italic=True, size=9, color="555555")
    fill_encabezado = "1F3864"
    borde_delgado = Border(
        left=Side(style="thin", color="999999"),
        right=Side(style="thin", color="999999"),
        top=Side(style="thin", color="999999"),
        bottom=Side(style="thin", color="999999"),
    )

    hoja_activa = wb.active
    hoja_activa.title = "Resumen"

    # Título
    titulo = datos.get("titulo", "Reporte de Fill Rate")
    hoja_activa["A1"] = titulo
    hoja_activa["A1"].font = font_titulo

    # Fuente de datos (R31)
    fuente = datos.get("fuente", "no indicado")
    hoja_activa["A2"] = f"Fuente: {fuente}"
    hoja_activa["A2"].font = font_fuente

    # Fecha de generación
    fecha_gen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hoja_activa["A3"] = f"Generado: {fecha_gen}"
    hoja_activa["A3"].font = font_fuente

    # Escribir hojas de datos
    hojas = datos.get("hojas", {})
    if isinstance(hojas, dict):
        items_hojas = list(hojas.items())
    else:
        items_hojas = [(f"Hoja {i+1}", df) for i, df in enumerate(hojas)]

    fila_inicio = 5
    for nombre_hoja, df in items_hojas:
        if isinstance(df, str):
            # Si es un string, escribirlo como texto
            hoja_activa.cell(row=fila_inicio, column=1, value=nombre_hoja)
            hoja_activa.cell(row=fila_inicio, column=1).font = font_encabezado
            hoja_activa.cell(row=fila_inicio + 1, column=1, value=df)
            fila_inicio += 3
            continue

        if not isinstance(df, pd.DataFrame):
            continue

        # Escribir encabezados
        for j, columna in enumerate(df.columns, start=1):
            celda = hoja_activa.cell(row=fila_inicio, column=j, value=str(columna))
            celda.font = font_encabezado
            celda.border = borde_delgado

        # Escribir datos
        for i, (_, fila) in enumerate(df.iterrows(), start=fila_inicio + 1):
            for j, valor in enumerate(fila, start=1):
                celda = hoja_activa.cell(row=i, column=j, value=valor)
                celda.border = borde_delgado

        # Ajustar ancho de columnas
        for j in range(1, len(df.columns) + 1):
            letra = get_column_letter(j)
            hoja_activa.column_dimensions[letra].width = 18

        fila_inicio += len(df) + 3

    wb.save(str(ruta))
    return str(ruta)


def exportar_pdf(
    datos: dict[str, Any],
    nombre_archivo: str | None = None,
) -> str:
    """Exporta datos a un archivo PDF local.

    Implementa R30 (exportar en PDF) y R31 (fuente identificable).

    Args:
        datos: Diccionario con claves:
            - "titulo": str para el título del reporte.
            - "fuente": str con identificador de la fuente de los datos.
            - "contenido": list de diccionarios con "texto" o "tabla".
        nombre_archivo: Nombre opcional del archivo. Si es None, se genera uno con timestamp.

    Returns:
        Ruta del archivo PDF generado.
    """
    carpeta = asegurar_carpeta_reportes()
    if nombre_archivo is None:
        nombre_archivo = _nombre_archivo("reporte", "pdf")
    ruta = carpeta / nombre_archivo

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)

    # Título
    titulo = datos.get("titulo", "Reporte de Fill Rate")
    pdf.cell(0, 10, titulo, new_x="LMARGIN", new_y="NEXT", align="C")

    # Fuente de datos (R31)
    fuente = datos.get("fuente", "no indicado")
    pdf.set_font("Helvetica", "I", 8)
    pdf.cell(0, 6, f"Fuente: {fuente}", new_x="LMARGIN", new_y="NEXT", align="L")

    # Fecha
    fecha_gen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 6, f"Generado: {fecha_gen}", new_x="LMARGIN", new_y="NEXT", align="L")

    pdf.ln(5)

    # Contenido
    contenido = datos.get("contenido", [])
    for item in contenido:
        tipo = item.get("tipo", "texto")

        if tipo == "texto":
            pdf.set_font("Helvetica", "", 10)
            texto = item.get("texto", "")
            pdf.multi_cell(0, 6, texto)
            pdf.ln(2)

        elif tipo == "tabla":
            encabezados = item.get("encabezados", [])
            filas = item.get("filas", [])
            if not encabezados or not filas:
                continue

            pdf.set_font("Helvetica", "B", 9)
            ancho_col = 190 / len(encabezados) if encabezados else 190

            # Encabezados de tabla
            for enc in encabezados:
                pdf.cell(ancho_col, 7, str(enc), border=1, align="C")
            pdf.ln()

            # Filas de datos
            pdf.set_font("Helvetica", "", 9)
            for fila in filas:
                for valor in fila:
                    pdf.cell(ancho_col, 6, str(valor), border=1, align="C")
                pdf.ln()

            pdf.ln(4)

    pdf.output(str(ruta))
    return str(ruta)


def preparar_datos_exportacion(
    consolidado: dict[str, Any],
    fuente: str = "no indicado",
) -> dict[str, Any]:
    """Prepara los datos calculados para exportación.

    Args:
        consolidado: Diccionario con los resultados calculados (Fill Rate,
                     faltantes, rankings, etc.).
        fuente: Identificador de la fuente de los datos (R31).

    Returns:
        Diccionario listo para pasar a exportar_excel() o exportar_pdf().
    """
    titulo = consolidado.get("titulo", "Reporte de Fill Rate - División Retail")

    hojas = {}

    # Consolidado general
    if "consolidado_general" in consolidado:
        df_cons = pd.DataFrame([consolidado["consolidado_general"]])
        hojas["Consolidado General"] = df_cons

    # Por categoría
    if "por_categoria" in consolidado:
        hojas["Por Categoría"] = consolidado["por_categoria"]

    # Por producto
    if "por_producto" in consolidado:
        hojas["Por Producto"] = consolidado["por_producto"]

    # Por Centro de Carne
    if "por_centro_carne" in consolidado:
        hojas["Por Centro de Carne"] = consolidado["por_centro_carne"]

    # Rankings
    if "ranking_kilos" in consolidado:
        hojas["Ranking Kilos"] = consolidado["ranking_kilos"]

    if "ranking_colones" in consolidado:
        hojas["Ranking Colones"] = consolidado["ranking_colones"]

    # Recurrencia
    if "recurrentes" in consolidado:
        hojas["Faltantes Recurrentes"] = consolidado["recurrentes"]

    return {
        "titulo": titulo,
        "fuente": fuente,
        "hojas": hojas,
    }


def preparar_contenido_pdf(
    consolidado: dict[str, Any],
    fuente: str = "no indicado",
) -> dict[str, Any]:
    """Prepara el contenido para exportación a PDF.

    Args:
        consolidado: Diccionario con los resultados calculados.
        fuente: Identificador de la fuente de los datos (R31).

    Returns:
        Diccionario listo para pasar a exportar_pdf().
    """
    titulo = consolidado.get("titulo", "Reporte de Fill Rate - División Retail")

    contenido = []

    # Resumen ejecutivo
    resumen = consolidado.get("resumen_ejecutivo", "no indicado")
    contenido.append({"tipo": "texto", "texto": f"Resumen ejecutivo: {resumen}"})

    # Consolidado general
    if "consolidado_general" in consolidado:
        cg = consolidado["consolidado_general"]
        filas = [[k, str(v)] for k, v in cg.items()]
        contenido.append({
            "tipo": "tabla",
            "encabezados": ["Indicador", "Valor"],
            "filas": filas,
        })

    # Por categoría
    if "por_categoria" in consolidado and not consolidado["por_categoria"].empty:
        df_cat = consolidado["por_categoria"]
        encabezados = df_cat.columns.tolist()
        filas = df_cat.values.tolist()
        contenido.append({
            "tipo": "tabla",
            "encabezados": [str(e) for e in encabezados],
            "filas": [[str(v) for v in fila] for fila in filas],
        })

    # Rankings
    if "ranking_kilos" in consolidado and not consolidado["ranking_kilos"].empty:
        df_rk = consolidado["ranking_kilos"]
        encabezados = df_rk.columns.tolist()
        filas = df_rk.values.tolist()
        contenido.append({
            "tipo": "tabla",
            "encabezados": [str(e) for e in encabezados],
            "filas": [[str(v) for v in fila] for fila in filas],
        })

    return {
        "titulo": titulo,
        "fuente": fuente,
        "contenido": contenido,
    }


if __name__ == "__main__":
    import pandas as pd

    # Prueba rápida de exportación
    df_prueba = pd.DataFrame(
        {
            "Categoría": ["Res", "Cerdo"],
            "Pedido kg": [140, 110],
            "Entrega kg": [95, 98],
            "Faltante kg": [45, 12],
            "Fill Rate %": [67.86, 89.09],
        }
    )

    datos_excel = preparar_datos_exportacion(
        {
            "titulo": "Reporte de Prueba - Fill Rate",
            "por_categoria": df_prueba,
            "consolidado_general": {
                "Kilos solicitados": 250,
                "Kilos entregados": 193,
                "Kilos faltantes": 57,
                "Fill Rate %": 77.20,
            },
        },
        fuente="Insumos/Fill Rate Noviembre - Diciembre 2025.xlsx - hoja FR NOV 2025",
    )

    ruta_excel = exportar_excel(datos_excel)
    print(f"Excel generado: {ruta_excel}")

    datos_pdf = preparar_contenido_pdf(
        {
            "titulo": "Reporte de Prueba - Fill Rate",
            "resumen_ejecutivo": "Fill Rate general del 77,20 %. Faltantes críticos en categoría Res.",
            "consolidado_general": {
                "Kilos solicitados": 250,
                "Kilos entregados": 193,
                "Kilos faltantes": 57,
                "Fill Rate %": 77.20,
            },
            "por_categoria": df_prueba,
        },
        fuente="Insumos/Fill Rate Noviembre - Diciembre 2025.xlsx - hoja FR NOV 2025",
    )

    ruta_pdf = exportar_pdf(datos_pdf)
    print(f"PDF generado: {ruta_pdf}")
