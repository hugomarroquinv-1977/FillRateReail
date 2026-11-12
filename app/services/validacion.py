"""Servicio de validación de archivos de entrada (R01, R02, R03, R04, R08).

- Lee archivos Excel desde una carpeta local configurada (R01).
- Interpreta nombres como 1-11-26.xlsx con formato día-mes-año (R02).
- Evita reprocesar el mismo contenido como si fuera un día nuevo (R03).
- No modifica los Excel originales (R04).
- Cuenta registros válidos, excluidos y pendientes de revisión (R08).
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd

# Carpeta local configurable donde se guardan los archivos diarios de Fill Rate
CARPETA_DATOS = Path("datos") / "fill_rate"

# Archivo de registro de archivos ya procesados (evita duplicados)
REGISTRO_PROCESADOS = Path("datos") / "procesados.json"

# Patrón para nombres tipo 1-11-26.xlsx (día-mes-año)
PATRON_FECHA_ARCHIVO = re.compile(r"^(\d{1,2})-(\d{1,2})-(\d{2})\.xlsx$")


def interpretar_fecha_nombre(nombre_archivo: str) -> Tuple[datetime | None, str | None]:
    """Interpreta un nombre de archivo con formato día-mes-año (R02).

    Ejemplo: 1-11-26.xlsx -> 1 de noviembre de 2026.

    Args:
        nombre_archivo: Nombre del archivo Excel.

    Returns:
        Tupla (fecha, mensaje_error). Si no coincide el patrón, fecha es None.
    """
    match = PATRON_FECHA_ARCHIVO.match(nombre_archivo)
    if not match:
        return None, f"Nombre '{nombre_archivo}' no cumple formato día-mes-año (ej. 1-11-26.xlsx)"

    dia, mes, ano_corto = int(match.group(1)), int(match.group(2)), int(match.group(3))
    ano = 2000 + ano_corto  # 26 -> 2026

    try:
        fecha = datetime(ano, mes, dia)
        return fecha, None
    except ValueError as exc:
        return None, f"Fecha inválida en '{nombre_archivo}': {exc}"


def cargar_registro_procesados() -> Dict[str, str]:
    """Carga el registro de archivos ya procesados (R03).

    Returns:
        Diccionario {nombre_archivo: hash_contenido}.
    """
    if not REGISTRO_PROCESADOS.exists():
        return {}
    try:
        with open(REGISTRO_PROCESADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def guardar_registro_procesados(registro: Dict[str, str]) -> None:
    """Guarda el registro de archivos procesados (R03)."""
    REGISTRO_PROCESADOS.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRO_PROCESADOS, "w", encoding="utf-8") as f:
        json.dump(registro, f, indent=2, ensure_ascii=False)


def hash_archivo(ruta: Path) -> str:
    """Calcula el hash SHA-256 de un archivo para detectar duplicados (R03)."""
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(8192), b""):
            h.update(bloque)
    return h.hexdigest()


def listar_archivos_excel(carpeta: Path) -> List[Path]:
    """Lista archivos .xlsx en la carpeta configurada (R01).

    Args:
        carpeta: Carpeta local donde se buscan los archivos.

    Returns:
        Lista de rutas de archivos Excel encontrados.
    """
    if not carpeta.exists():
        return []
    return sorted(carpeta.glob("*.xlsx"))


def validar_y_contar_registros(df: pd.DataFrame) -> Tuple[int, int, int]:
    """Cuenta registros válidos, excluidos y pendientes de revisión (R08).

    Un registro es válido si tiene Pedido y Recibido no nulos y Pedido > 0.
    Un registro es excluido si faltan campos obligatorios.
    Un registro es pendiente si tiene Pedido o Recibido inválido pero no nulo.

    Args:
        df: DataFrame con los datos del reporte.

    Returns:
        Tupla (validos, excluidos, pendientes).
    """
    validos = 0
    excluidos = 0
    pendientes = 0

    for _, fila in df.iterrows():
        pedido = fila.get("Pedido")
        recibido = fila.get("Recibido")

        if pd.isna(pedido) or pd.isna(recibido):
            excluidos += 1
            continue

        try:
            pedido_num = float(pedido)
            recibido_num = float(recibido)
        except (ValueError, TypeError):
            pendientes += 1
            continue

        if pedido_num <= 0:
            excluidos += 1
            continue

        validos += 1

    return validos, excluidos, pendientes


def procesar_archivo(ruta: Path, registro: Dict[str, str]) -> dict:
    """Procesa un archivo Excel: valida, cuenta registros y registra si es nuevo (R01-R04, R08).

    Args:
        ruta: Ruta al archivo Excel.
        registro: Diccionario de archivos ya procesados.

    Returns:
        Diccionario con el resultado del procesamiento.
    """
    nombre = ruta.name
    contenido_hash = hash_archivo(ruta)

    # R03: evitar reprocesar el mismo contenido como día nuevo
    if nombre in registro and registro[nombre] == contenido_hash:
        return {
            "archivo": nombre,
            "estado": "ya_procesado",
            "mensaje": "Contenido idéntico al ya procesado previamente.",
            "validos": 0,
            "excluidos": 0,
            "pendientes": 0,
        }

    # R01: leer el archivo Excel
    try:
        df = pd.read_excel(ruta, sheet_name=0, header=None)
    except Exception as exc:  # pylint: disable=broad-except
        return {
            "archivo": nombre,
            "estado": "error_lectura",
            "mensaje": f"No se pudo leer el archivo: {exc}",
            "validos": 0,
            "excluidos": 0,
            "pendientes": 0,
        }

    # Detectar encabezados (primera fila no vacía)
    fila_encabezados = None
    for idx in range(df.shape[0]):
        if not df.iloc[idx].isna().all():
            fila_encabezados = idx
            break

    if fila_encabezados is None:
        return {
            "archivo": nombre,
            "estado": "sin_datos",
            "mensaje": "El archivo no contiene filas con datos.",
            "validos": 0,
            "excluidos": 0,
            "pendientes": 0,
        }

    encabezados = [str(c) if pd.notna(c) else f"Col_{i}" for i, c in enumerate(df.iloc[fila_encabezados].tolist())]
    datos = df.iloc[fila_encabezados + 1 :].copy()
    datos.columns = encabezados
    datos = datos.dropna(how="all").reset_index(drop=True)

    # R08: contar registros válidos, excluidos y pendientes
    validos, excluidos, pendientes = validar_y_contar_registros(datos)

    # R04: no modificamos el archivo original (solo lectura)

    # Registrar este archivo como procesado (R03)
    registro[nombre] = contenido_hash

    return {
        "archivo": nombre,
        "estado": "procesado",
        "mensaje": "Archivo leído y validado correctamente.",
        "validos": validos,
        "excluidos": excluidos,
        "pendientes": pendientes,
        "filas_totales": len(datos),
        "columnas": encabezados,
    }


def validar_carpeta(carpeta: Path = CARPETA_DATOS) -> dict:
    """Valida todos los archivos Excel de una carpeta (R01, R03, R04, R08).

    Args:
        carpeta: Carpeta local con los archivos de Fill Rate.

    Returns:
        Diccionario con resumen de validación y detalle por archivo.
    """
    registro = cargar_registro_procesados()
    archivos = listar_archivos_excel(carpeta)

    resultados = []
    total_validos = 0
    total_excluidos = 0
    total_pendientes = 0

    for archivo in archivos:
        resultado = procesar_archivo(archivo, registro)
        resultados.append(resultado)
        total_validos += resultado.get("validos", 0)
        total_excluidos += resultado.get("excluidos", 0)
        total_pendientes += resultado.get("pendientes", 0)

    guardar_registro_procesados(registro)

    return {
        "carpeta": str(carpeta),
        "archivos_encontrados": len(archivos),
        "total_validos": total_validos,
        "total_excluidos": total_excluidos,
        "total_pendientes": total_pendientes,
        "detalle": resultados,
    }


def imprimir_resumen(resumen: dict) -> None:
    """Imprime en consola el resumen de validación."""
    print("=" * 60)
    print("VALIDACIÓN DE ARCHIVOS DE ENTRADA (R01-R04, R08)")
    print("=" * 60)
    print(f"Carpeta: {resumen['carpeta']}")
    print(f"Archivos encontrados: {resumen['archivos_encontrados']}")
    print()
    print(f"Registros válidos:      {resumen['total_validos']}")
    print(f"Registros excluidos:    {resumen['total_excluidos']}")
    print(f"Registros pendientes:   {resumen['total_pendientes']}")
    print()
    for det in resumen["detalle"]:
        print(f"Archivo: {det['archivo']}")
        print(f"  Estado: {det['estado']}")
        print(f"  Mensaje: {det['mensaje']}")
        if det["estado"] == "procesado":
            print(f"  Válidos: {det['validos']}, Excluidos: {det['excluidos']}, Pendientes: {det['pendientes']}")
            print(f"  Columnas: {det['columnas']}")
        print()


if __name__ == "__main__":
    # Nota: con el insumo real entregado (un solo archivo agrupado),
    # la carpeta datos/fill_rate puede no existir todavía.
    # Se muestra el comportamiento esperado.
    resumen = validar_carpeta(CARPETA_DATOS)
    imprimir_resumen(resumen)
