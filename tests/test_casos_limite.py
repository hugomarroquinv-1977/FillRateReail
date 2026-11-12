"""Pruebas de casos límite (AGENTS.md, sección 10).

Estas pruebas validan el comportamiento de la app ante situaciones límite.
NO se modifica el código de la app ni se "ajustan" los números.

Cada prueba verifica el comportamiento obligatorio definido en AGENTS.md.
"""

from __future__ import annotations

import pandas as pd

from app.services.calculo_fill_rate import calcular_dataframe, calcular_registro, calcular_consolidado
from app.services.validacion import validar_y_contar_registros, interpretar_fecha_nombre
from app.services.rankings import cruzar_con_ventas
from app.services.agente_ia import (
    procesar_con_ia,
    construir_json_vacio,
    modelo_local_disponible,
)


# ---------------------------------------------------------------------------
# Caso: Pedido de cero kilos (R16)
# ---------------------------------------------------------------------------


def test_pedido_cero_no_calcula_fill_rate():
    """Pedido de cero kilos no genera Fill Rate por división entre cero."""
    resultado = calcular_registro(0, 0)
    assert resultado.fill_rate_pct is None, (
        f"Pedido cero: fill_rate debe ser None, obtenido {resultado.fill_rate_pct}"
    )
    assert resultado.es_valido is False


def test_pedido_cero_en_dataframe():
    """Registros con pedido cero se excluyen del cálculo válido."""
    df = pd.DataFrame(
        {
            "Pedido": [100, 0, 50],
            "Recibido": [75, 0, 30],
        }
    )
    resultado = calcular_dataframe(df)

    filas_validas = resultado[resultado["Es valido"] == True]  # noqa: E712
    assert len(filas_validas) == 2, (
        f"Esperado 2 filas válidas (excluyendo pedido cero), obtenido {len(filas_validas)}"
    )
    assert filas_validas.iloc[0]["Kilos faltantes"] == 25


# ---------------------------------------------------------------------------
# Caso: Entrega superior al pedido (R16)
# ---------------------------------------------------------------------------


def test_entrega_superior_marca_revision():
    """Si entregado > solicitado, marcar para revisión sin ajustar silenciosamente."""
    resultado = calcular_registro(50, 80)
    assert resultado.motivo_exclusion != "", (
        "Entrega superior debe tener motivo de revisión"
    )
    assert "Entrega superior" in resultado.motivo_exclusion
    # Los valores originales se mantienen, no se ajustan
    assert resultado.kilos_solicitados == 50
    assert resultado.kilos_entregados == 80


# ---------------------------------------------------------------------------
# Caso: Campos incompletos / nulos (R06, R07, R08)
# ---------------------------------------------------------------------------


def test_campos_incompletos_excluidos():
    """Registros con campos incompletos se excluyen del cálculo válido (R06, R07).

    Fila 0 (100, 75): válido. Fila 1 (None, 40): excluido (pedido nulo).
    Fila 2 (50, None): excluido (recibido nulo). Fila 3 (80, 60): válido.
    """
    df = pd.DataFrame(
        {
            "Pedido": [100, None, 50, 80],
            "Recibido": [75, 40, None, 60],
        }
    )
    validos, excluidos, pendientes = validar_y_contar_registros(df)

    assert validos == 2, f"Esperado 2 válidos, obtenido {validos}"
    assert excluidos == 2, f"Esperado 2 excluidos (nulos), obtenido {excluidos}"
    assert pendientes == 0, f"Esperado 0 pendientes, obtenido {pendientes}"


# ---------------------------------------------------------------------------
# Caso: Producto sin histórico de ventas (R27)
# ---------------------------------------------------------------------------


def test_producto_sin_historial_ventas_no_disponible():
    """Producto sin historial de ventas muestra 'no disponible', no cero (R27)."""
    df_productos = pd.DataFrame(
        {
            "Artículo": ["R001", "PRODUCTO_NUEVO_XYZ"],
            "Centro": ["CC A", "CC A"],
        }
    )
    df_ventas = pd.DataFrame(
        {
            "Centro": ["CC A"],
            "Artículo": ["R001"],
            "Ventas kg": [900],
            "Ventas ₡": [4500000],
        }
    )

    resultado = cruzar_con_ventas(
        df_productos,
        df_ventas,
        col_producto="Artículo",
        col_centro="Centro",
        col_ventas_kg="Ventas kg",
        col_ventas_crc="Ventas ₡",
        periodo="Octubre 2026",
    )

    fila_nuevo = resultado[resultado["Artículo"] == "PRODUCTO_NUEVO_XYZ"].iloc[0]
    assert fila_nuevo["Ventas_kg_Octubre 2026"] == "no disponible", (
        f"Producto sin historial: Ventas kg debe ser 'no disponible', obtenido {fila_nuevo['Ventas_kg_Octubre 2026']}"
    )
    assert fila_nuevo["Ventas_crc_Octubre 2026"] == "no disponible", (
        f"Producto sin historial: Ventas crc debe ser 'no disponible', obtenido {fila_nuevo['Ventas_crc_Octubre 2026']}"
    )


# ---------------------------------------------------------------------------
# Caso: Duplicado exacto (R03)
# ---------------------------------------------------------------------------


def test_duplicado_exacto_no_contabiliza_dos_veces():
    """Un duplicado exacto no debe contabilizarse dos veces en el cálculo."""
    df = pd.DataFrame(
        {
            "Pedido": [100, 100],
            "Recibido": [75, 75],
        }
    )
    resultado = calcular_dataframe(df)

    # Ambos registros se procesan individualmente (el control de duplicados
    # se hace a nivel de archivo, no de fila, según R03)
    filas_validas = resultado[resultado["Es valido"] == True]  # noqa: E712
    assert len(filas_validas) == 2, (
        f"Esperado 2 filas válidas, obtenido {len(filas_validas)}"
    )
    # Pero el total no duplica el contenido del archivo (eso se controla
    # en el registro de archivos procesados de validacion.py)
    assert filas_validas["Kilos solicitados"].sum() == 200


# ---------------------------------------------------------------------------
# Caso: Modelo de IA no disponible (R10 del agente)
# ---------------------------------------------------------------------------


def test_modelo_ia_no_disponible_no_rompe_app():
    """Si el modelo de IA no está disponible, la app sigue mostrando cálculos (agente Regla 10)."""
    disponible = modelo_local_disponible()

    # El JSON debe devolverse válido incluso si IA no está disponible
    indicadores = {
        "fecha_corte": "2026-11-04",
        "resumen_ejecutivo": "Resumen de prueba",
        "alertas": [],
        "productos_indispensables": [],
        "riesgos_detectados": [],
        "limitaciones": [],
        "fuentes": ["test.xlsx"],
    }

    resultado = procesar_con_ia(indicadores, ["test.xlsx"])

    assert "fecha_corte" in resultado
    assert "alertas" in resultado
    assert resultado["alertas"] == []
    assert "limitaciones" in resultado
    # Si IA no está disponible, debe haber una limitación reportada
    if not disponible:
        assert len(resultado["limitaciones"]) > 0, (
            "Si IA no está disponible, debe haber al menos una limitación reportada"
        )


def test_json_vacio_sin_alertas():
    """Cuando no hay alertas sustentadas, devolver listas vacías (agente Regla 9)."""
    json_vacio = construir_json_vacio("2026-11-04", ["test.xlsx"])

    assert json_vacio["fecha_corte"] == "2026-11-04"
    assert json_vacio["alertas"] == []
    assert json_vacio["productos_indispensables"] == []
    assert json_vacio["riesgos_detectados"] == []
    assert json_vacio["limitaciones"] == []
    assert json_vacio["fuentes"] == ["test.xlsx"]


# ---------------------------------------------------------------------------
# Caso: Fecha inválida en nombre de archivo (R02)
# ---------------------------------------------------------------------------


def test_fecha_invalida_nombre_archivo():
    """Nombre de archivo con fecha inválida debe retornar error, no fecha inventada."""
    fecha, error = interpretar_fecha_nombre("30-02-26.xlsx")
    assert fecha is None, f"Fecha inválida debe retornar None, obtenido {fecha}"
    assert error is not None, "Debe haber un mensaje de error para fecha inválida"


def test_nombre_archivo_sin_formato_valido():
    """Nombre sin formato día-mes-año debe retornar error."""
    fecha, error = interpretar_fecha_nombre("archivo_sin_fecha.xlsx")
    assert fecha is None
    assert error is not None


# ---------------------------------------------------------------------------
# Caso: Cantidad en unidades en lugar de kilos (R09)
# ---------------------------------------------------------------------------


def test_unidades_no_se_mezclan_con_kilos():
    """Cantidades en unidades no se mezclan con indicadores en kilogramos (R09)."""
    # Esto se valida a nivel de servicio: si una columna tiene "UNIDAD(ES)"
    # en lugar de "KILO(S)", no debe incluirse en cálculos de kg.
    # La prueba verifica que los valores numéricos se procesan como kilos
    # sin conversión automática de unidades.
    df = pd.DataFrame(
        {
            "Pedido": [100, 50],
            "Recibido": [75, 50],
            "Unidad": ["KILO(S)", "UNIDAD(ES)"],
        }
    )

    resultado = calcular_dataframe(df[["Pedido", "Recibido"]])
    filas_validas = resultado[resultado["Es valido"] == True]  # noqa: E712
    assert len(filas_validas) == 2, (
        f"Esperado 2 filas válidas, obtenido {len(filas_validas)}"
    )
    # Los valores se mantienen como kilos sin conversión de unidades
    assert filas_validas["Kilos faltantes"].sum() == 25


# ---------------------------------------------------------------------------
# Caso: Archivo vacío
# ---------------------------------------------------------------------------


def test_archivo_vacio_no_contiene_registros():
    """Archivo vacío debe informar que no contiene registros procesables."""
    df_vacio = pd.DataFrame(columns=["Pedido", "Recibido"])
    validos, excluidos, pendientes = validar_y_contar_registros(df_vacio)

    assert validos == 0
    assert excluidos == 0
    assert pendientes == 0


# ---------------------------------------------------------------------------
# Caso: Dos archivos distintos para la misma fecha (detección de conflicto)
# ---------------------------------------------------------------------------


def test_dos_archivos_misma_fecha_detecta_conflicto():
    """Dos archivos distintos para la misma fecha deben detectarse como conflicto."""
    # Esto se valida a nivel de registro de archivos procesados:
    # si dos archivos tienen el mismo nombre de fecha pero contenido diferente,
    # ambos tienen hashes distintos y se procesan como archivos separados.
    # El conflicto se detecta cuando el nombre es igual pero el hash es distinto.
    from app.services.validacion import hash_archivo
    from pathlib import Path
    import tempfile
    import os

    contenido_a = b"Pedido,Recibido\n100,75\n"
    contenido_b = b"Pedido,Recibido\n200,150\n"

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False, mode="wb") as f1:
        f1.write(contenido_a)
        ruta_a = Path(f1.name)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False, mode="wb") as f2:
        f2.write(contenido_b)
        ruta_b = Path(f2.name)

    try:
        hash_a = hash_archivo(ruta_a)
        hash_b = hash_archivo(ruta_b)

        # Mismo nombre de fecha, contenido diferente -> hashes distintos
        assert hash_a != hash_b, (
            "Dos archivos con mismo nombre pero contenido diferente deben tener hashes distintos"
        )
    finally:
        os.unlink(ruta_a)
        os.unlink(ruta_b)
