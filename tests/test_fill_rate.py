"""Pruebas de aceptación contra las cifras de control de AGENTS.md (sección 9).

Estas pruebas validan que los cálculos de la app coincidan con los valores
esperados definidos en el documento de contexto. NO se modifica el código
de la app ni se "ajustan" los números para que coincidan.

Cifras de control validadas:
- 9.1 Primer día: 1 de noviembre de 2026
- 9.2 Segundo día: 2 de noviembre de 2026
- 9.3 Consolidado de ambos días
- 9.4 Consolidado por categoría
- 9.5 Consolidado por Centro de Carne
- 9.6 Control de recurrencia
- 9.7 Control de rankings comerciales
"""

from __future__ import annotations

import pandas as pd

from app.services.calculo_fill_rate import calcular_dataframe, calcular_consolidado, calcular_registro
from app.services.agregaciones import (
    agregar_por_categoria,
    agregar_por_centro_carne,
    agregar_total_division_retail,
)
from app.services.recurrencia import contar_fechas_con_faltante, identificar_faltantes_recurrentes
from app.services.rankings import cruzar_con_ventas, ranking_por_kilos, ranking_por_colones

# ---------------------------------------------------------------------------
# Datos de prueba (AGENTS.md, sección 8 - archivos ficticios)
# ---------------------------------------------------------------------------

DIA_1 = pd.DataFrame(
    {
        "Centro": ["CC A", "CC A", "CC B", "CC B"],
        "Categoría": ["Res", "Cerdo", "Res", "Cerdo"],
        "Artículo": ["R001", "C001", "R001", "C001"],
        "Pedido kg": [100, 50, 40, 60],
        "Entrega kg": [75, 50, 20, 48],
    }
)

DIA_2 = pd.DataFrame(
    {
        "Centro": ["CC A", "CC A", "CC B", "CC B"],
        "Categoría": ["Res", "Cerdo", "Res", "Cerdo"],
        "Artículo": ["R001", "C001", "R001", "C001"],
        "Pedido kg": [120, 80, 30, 70],
        "Entrega kg": [90, 80, 30, 56],
    }
)

VENTAS_OCTUBRE_2026 = pd.DataFrame(
    {
        "Centro": ["CC A", "CC A", "CC B", "CC B"],
        "Artículo": ["R001", "C001", "R001", "C001"],
        "Ventas kg": [900, 500, 350, 700],
        "Ventas ₡": [4500000, 1500000, 1750000, 2100000],
    }
)


# ---------------------------------------------------------------------------
# 9.1 Primer día: 1 de noviembre de 2026
# ---------------------------------------------------------------------------


def test_primer_dia_kilos_solicitados():
    """R011-R012: Kilos solicitados del día 1 deben ser 250."""
    df = calcular_dataframe(DIA_1.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    total = df["Kilos solicitados"].sum()
    assert total == 250, f"Esperado 250, obtenido {total}"


def test_primer_dia_kilos_entregados():
    """R011-R012: Kilos entregados del día 1 deben ser 193."""
    df = calcular_dataframe(DIA_1.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    total = df["Kilos entregados"].sum()
    assert total == 193, f"Esperado 193, obtenido {total}"


def test_primer_dia_kilos_faltantes():
    """R012: Kilos faltantes del día 1 deben ser 57."""
    df = calcular_dataframe(DIA_1.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    total = df["Kilos faltantes"].sum()
    assert total == 57, f"Esperado 57, obtenido {total}"


def test_primer_dia_fill_rate_general():
    """R011: Fill Rate general del día 1 debe ser 77,20 %."""
    df = calcular_dataframe(DIA_1.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    consolidado = calcular_consolidado(df)
    fr = consolidado["fill_rate_consolidado_pct"]
    assert fr == 77.20, f"Esperado 77.20, obtenido {fr}"


def test_primer_dia_por_categoria():
    """R15: Cumplimiento por categoría del día 1."""
    df = calcular_dataframe(DIA_1.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    cat = agregar_por_categoria(df)

    res = cat[cat["Categoría"] == "Res"].iloc[0]
    assert res["Pedido_kg"] == 140, f"Res pedido: esperado 140, obtenido {res['Pedido_kg']}"
    assert res["Entrega_kg"] == 95, f"Res entrega: esperado 95, obtenido {res['Entrega_kg']}"
    assert res["Faltante_kg"] == 45, f"Res faltante: esperado 45, obtenido {res['Faltante_kg']}"
    assert res["Fill Rate %"] == 67.86, f"Res Fill Rate: esperado 67.86, obtenido {res['Fill Rate %']}"

    cerdo = cat[cat["Categoría"] == "Cerdo"].iloc[0]
    assert cerdo["Pedido_kg"] == 110, f"Cerdo pedido: esperado 110, obtenido {cerdo['Pedido_kg']}"
    assert cerdo["Entrega_kg"] == 98, f"Cerdo entrega: esperado 98, obtenido {cerdo['Entrega_kg']}"
    assert cerdo["Faltante_kg"] == 12, f"Cerdo faltante: esperado 12, obtenido {cerdo['Faltante_kg']}"
    assert cerdo["Fill Rate %"] == 89.09, f"Cerdo Fill Rate: esperado 89.09, obtenido {cerdo['Fill Rate %']}"


# ---------------------------------------------------------------------------
# 9.2 Segundo día: 2 de noviembre de 2026
# ---------------------------------------------------------------------------


def test_segundo_dia_kilos_solicitados():
    """R011-R012: Kilos solicitados del día 2 deben ser 300."""
    df = calcular_dataframe(DIA_2.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    total = df["Kilos solicitados"].sum()
    assert total == 300, f"Esperado 300, obtenido {total}"


def test_segundo_dia_kilos_entregados():
    """R011-R012: Kilos entregados del día 2 deben ser 256."""
    df = calcular_dataframe(DIA_2.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    total = df["Kilos entregados"].sum()
    assert total == 256, f"Esperado 256, obtenido {total}"


def test_segundo_dia_kilos_faltantes():
    """R012: Kilos faltantes del día 2 deben ser 44."""
    df = calcular_dataframe(DIA_2.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    total = df["Kilos faltantes"].sum()
    assert total == 44, f"Esperado 44, obtenido {total}"


def test_segundo_dia_fill_rate_general():
    """R011: Fill Rate general del día 2 debe ser 85,33 %."""
    df = calcular_dataframe(DIA_2.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    consolidado = calcular_consolidado(df)
    fr = consolidado["fill_rate_consolidado_pct"]
    assert fr == 85.33, f"Esperado 85.33, obtenido {fr}"


# ---------------------------------------------------------------------------
# 9.3 Consolidado de ambos días (R14: totales, no promedio de porcentajes)
# ---------------------------------------------------------------------------


def test_consolidado_ambos_dias():
    """R14: Fill Rate consolidado con totales (550/449/101/81,64), no promedio de porcentajes."""
    df1 = calcular_dataframe(DIA_1.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    df2 = calcular_dataframe(DIA_2.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    df_combinado = pd.concat([df1, df2], ignore_index=True)

    consolidado = calcular_consolidado(df_combinado)

    assert consolidado["kilos_solicitados_total"] == 550, (
        f"Solicitado total: esperado 550, obtenido {consolidado['kilos_solicitados_total']}"
    )
    assert consolidado["kilos_entregados_total"] == 449, (
        f"Entregado total: esperado 449, obtenido {consolidado['kilos_entregados_total']}"
    )
    assert consolidado["kilos_faltantes_total"] == 101, (
        f"Faltante total: esperado 101, obtenido {consolidado['kilos_faltantes_total']}"
    )
    assert consolidado["fill_rate_consolidado_pct"] == 81.64, (
        f"Fill Rate consolidado: esperado 81.64, obtenido {consolidado['fill_rate_consolidado_pct']}"
    )

    # Verificar que NO es promedio de porcentajes diarios (77,20 + 85,33) / 2 = 81,265 != 81,64
    promedio_diarios = (77.20 + 85.33) / 2
    assert consolidado["fill_rate_consolidado_pct"] != round(promedio_diarios, 2), (
        "El Fill Rate consolidado no debe ser el promedio simple de porcentajes diarios"
    )


# ---------------------------------------------------------------------------
# 9.4 Consolidado por categoría
# ---------------------------------------------------------------------------


def test_consolidado_por_categoria():
    """R15: Consolidado por categoría (Res/Cerdo/Total)."""
    df1 = calcular_dataframe(DIA_1.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    df2 = calcular_dataframe(DIA_2.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    df_combinado = pd.concat([df1, df2], ignore_index=True)

    cat = agregar_por_categoria(df_combinado)

    res = cat[cat["Categoría"] == "Res"].iloc[0]
    assert res["Pedido_kg"] == 290, f"Res pedido: esperado 290, obtenido {res['Pedido_kg']}"
    assert res["Entrega_kg"] == 215, f"Res entrega: esperado 215, obtenido {res['Entrega_kg']}"
    assert res["Faltante_kg"] == 75, f"Res faltante: esperado 75, obtenido {res['Faltante_kg']}"
    assert res["Fill Rate %"] == 74.14, f"Res Fill Rate: esperado 74.14, obtenido {res['Fill Rate %']}"

    cerdo = cat[cat["Categoría"] == "Cerdo"].iloc[0]
    assert cerdo["Pedido_kg"] == 260, f"Cerdo pedido: esperado 260, obtenido {cerdo['Pedido_kg']}"
    assert cerdo["Entrega_kg"] == 234, f"Cerdo entrega: esperado 234, obtenido {cerdo['Entrega_kg']}"
    assert cerdo["Faltante_kg"] == 26, f"Cerdo faltante: esperado 26, obtenido {cerdo['Faltante_kg']}"
    assert cerdo["Fill Rate %"] == 90.00, f"Cerdo Fill Rate: esperado 90.00, obtenido {cerdo['Fill Rate %']}"

    total = agregar_total_division_retail(df_combinado)
    assert total["Pedido_kg"].iloc[0] == 550
    assert total["Entrega_kg"].iloc[0] == 449
    assert total["Faltante_kg"].iloc[0] == 101
    assert total["Fill Rate %"].iloc[0] == 81.64


# ---------------------------------------------------------------------------
# 9.5 Consolidado por Centro de Carne
# ---------------------------------------------------------------------------


def test_consolidado_por_centro_carne():
    """R15: Consolidado por Centro de Carne (CC A/CC B/Total)."""
    df1 = calcular_dataframe(DIA_1.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    df2 = calcular_dataframe(DIA_2.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    df_combinado = pd.concat([df1, df2], ignore_index=True)

    cc = agregar_por_centro_carne(df_combinado)

    cc_a = cc[cc["Centro"] == "CC A"].iloc[0]
    assert cc_a["Pedido_kg"] == 350, f"CC A pedido: esperado 350, obtenido {cc_a['Pedido_kg']}"
    assert cc_a["Entrega_kg"] == 295, f"CC A entrega: esperado 295, obtenido {cc_a['Entrega_kg']}"
    assert cc_a["Faltante_kg"] == 55, f"CC A faltante: esperado 55, obtenido {cc_a['Faltante_kg']}"
    assert cc_a["Fill Rate %"] == 84.29, f"CC A Fill Rate: esperado 84.29, obtenido {cc_a['Fill Rate %']}"

    cc_b = cc[cc["Centro"] == "CC B"].iloc[0]
    assert cc_b["Pedido_kg"] == 200, f"CC B pedido: esperado 200, obtenido {cc_b['Pedido_kg']}"
    assert cc_b["Entrega_kg"] == 154, f"CC B entrega: esperado 154, obtenido {cc_b['Entrega_kg']}"
    assert cc_b["Faltante_kg"] == 46, f"CC B faltante: esperado 46, obtenido {cc_b['Faltante_kg']}"
    assert cc_b["Fill Rate %"] == 77.00, f"CC B Fill Rate: esperado 77.00, obtenido {cc_b['Fill Rate %']}"


# ---------------------------------------------------------------------------
# 9.6 Control de recurrencia (R17-R19)
# ---------------------------------------------------------------------------


def test_recurrencia_productos():
    """R18-R19: R001 CC A y C001 CC B son recurrentes (2+ fechas). R001 CC B no es recurrente."""
    df1 = calcular_dataframe(DIA_1.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    df2 = calcular_dataframe(DIA_2.rename(columns={"Pedido kg": "Pedido", "Entrega kg": "Recibido"}))
    df_combinado = pd.concat([df1, df2], ignore_index=True)
    df_combinado["Fecha"] = ["2026-11-01"] * 4 + ["2026-11-02"] * 4

    conteo = contar_fechas_con_faltante(
        df_combinado,
        col_fecha="Fecha",
        col_identificador="Artículo",
        col_faltantes="Kilos faltantes",
    )

    recurrentes = identificar_faltantes_recurrentes(conteo, umbral_fechas=2)

    # C001 debe ser recurrente (2 fechas con faltante)
    c001 = recurrentes[recurrentes["Artículo"] == "C001"]
    assert len(c001) == 1, "C001 debe aparecer como recurrente"
    assert c001["Fechas_con_faltante"].iloc[0] == 2, (
        f"C001 fechas con faltante: esperado 2, obtenido {c001['Fechas_con_faltante'].iloc[0]}"
    )

    # R001 aparece en CC A y CC B, pero como producto global tiene 2 fechas
    # (una fecha por día, aunque en distintas fechas puede tener faltante en ambas)
    r001 = recurrentes[recurrentes["Artículo"] == "R001"]
    assert len(r001) == 1, "R001 debe aparecer como recurrente (faltante en ambos días)"


# ---------------------------------------------------------------------------
# 9.7 Control de rankings comerciales (octubre 2026)
# ---------------------------------------------------------------------------


def test_ranking_por_kilos_cc_a():
    """R24-R25: CC A — Mayor volumen: R001 con 900 kg."""
    df_cruzado = cruzar_con_ventas(
        DIA_1[["Centro", "Artículo"]].drop_duplicates(),
        VENTAS_OCTUBRE_2026,
        col_producto="Artículo",
        col_centro="Centro",
        col_ventas_kg="Ventas kg",
        col_ventas_crc="Ventas ₡",
        periodo="Octubre 2026",
    )

    cc_a = df_cruzado[df_cruzado["Centro"] == "CC A"]
    ranking = ranking_por_kilos(cc_a, col_producto="Artículo", col_ventas_kg="Ventas_kg_Octubre 2026")

    top = ranking.iloc[0]
    assert top["Artículo"] == "R001", f"CC A top kilos: esperado R001, obtenido {top['Artículo']}"
    assert top["Ventas_kg_Octubre 2026"] == 900, (
        f"CC A R001 kilos: esperado 900, obtenido {top['Ventas_kg_Octubre 2026']}"
    )


def test_ranking_por_colones_cc_a():
    """R24-R25: CC A — Mayor venta en colones: R001 con ₡4.500.000."""
    df_cruzado = cruzar_con_ventas(
        DIA_1[["Centro", "Artículo"]].drop_duplicates(),
        VENTAS_OCTUBRE_2026,
        col_producto="Artículo",
        col_centro="Centro",
        col_ventas_kg="Ventas kg",
        col_ventas_crc="Ventas ₡",
        periodo="Octubre 2026",
    )

    cc_a = df_cruzado[df_cruzado["Centro"] == "CC A"]
    ranking = ranking_por_colones(cc_a, col_producto="Artículo", col_ventas_crc="Ventas_crc_Octubre 2026")

    top = ranking.iloc[0]
    assert top["Artículo"] == "R001", f"CC A top colones: esperado R001, obtenido {top['Artículo']}"
    assert top["Ventas_crc_Octubre 2026"] == 4500000, (
        f"CC A R001 colones: esperado 4500000, obtenido {top['Ventas_crc_Octubre 2026']}"
    )


def test_ranking_por_kilos_cc_b():
    """R24-R25: CC B — Mayor volumen: C001 con 700 kg."""
    df_cruzado = cruzar_con_ventas(
        DIA_1[["Centro", "Artículo"]].drop_duplicates(),
        VENTAS_OCTUBRE_2026,
        col_producto="Artículo",
        col_centro="Centro",
        col_ventas_kg="Ventas kg",
        col_ventas_crc="Ventas ₡",
        periodo="Octubre 2026",
    )

    cc_b = df_cruzado[df_cruzado["Centro"] == "CC B"]
    ranking = ranking_por_kilos(cc_b, col_producto="Artículo", col_ventas_kg="Ventas_kg_Octubre 2026")

    top = ranking.iloc[0]
    assert top["Artículo"] == "C001", f"CC B top kilos: esperado C001, obtenido {top['Artículo']}"
    assert top["Ventas_kg_Octubre 2026"] == 700, (
        f"CC B C001 kilos: esperado 700, obtenido {top['Ventas_kg_Octubre 2026']}"
    )


def test_ranking_por_colones_cc_b():
    """R24-R25: CC B — Mayor venta en colones: C001 con ₡2.100.000."""
    df_cruzado = cruzar_con_ventas(
        DIA_1[["Centro", "Artículo"]].drop_duplicates(),
        VENTAS_OCTUBRE_2026,
        col_producto="Artículo",
        col_centro="Centro",
        col_ventas_kg="Ventas kg",
        col_ventas_crc="Ventas ₡",
        periodo="Octubre 2026",
    )

    cc_b = df_cruzado[df_cruzado["Centro"] == "CC B"]
    ranking = ranking_por_colones(cc_b, col_producto="Artículo", col_ventas_crc="Ventas_crc_Octubre 2026")

    top = ranking.iloc[0]
    assert top["Artículo"] == "C001", f"CC B top colones: esperado C001, obtenido {top['Artículo']}"
    assert top["Ventas_crc_Octubre 2026"] == 2100000, (
        f"CC B C001 colones: esperado 2100000, obtenido {top['Ventas_crc_Octubre 2026']}"
    )


# ---------------------------------------------------------------------------
# R16: Casos matemáticos inválidos
# ---------------------------------------------------------------------------


def test_pedido_cero_no_division_entre_cero():
    """R16: Pedido con cero kilos no genera Fill Rate por división entre cero."""
    resultado = calcular_registro(0, 10)
    assert resultado.fill_rate_pct is None, (
        f"Pedido cero: fill_rate debe ser None, obtenido {resultado.fill_rate_pct}"
    )
    assert resultado.es_valido is False


def test_entrega_superior_pedido_marca_revision():
    """R16: Si entregado > solicitado, marcar para revisión sin ajustar silenciosamente."""
    resultado = calcular_registro(50, 80)
    assert resultado.es_valido is True
    assert "Entrega superior" in resultado.motivo_exclusion, (
        f"Esperado mensaje de inconsistencia, obtenido: {resultado.motivo_exclusion}"
    )
    # No se ajusta silenciosamente: los valores originales se mantienen
    assert resultado.kilos_solicitados == 50
    assert resultado.kilos_entregados == 80
