"""Servicio de cálculo de Fill Rate y kilos faltantes (R11, R12, R13, R14, R16).

- R11: Fill Rate (%) = (Kilos entregados / Kilos solicitados) × 100,
  solo cuando kilos solicitados > 0 y los datos son válidos.
- R12: Kilos faltantes = Kilos solicitados − Kilos entregados.
  El faltante se muestra exclusivamente en kilogramos.
- R13: Formato de indicadores (Fill Rate porcentaje, faltantes en kg,
  ventas históricas en colones y kg por separado).
- R14: Fill Rate consolidado con totales, no promedio de porcentajes.
- R16: Pedidos con cantidad cero no generan Fill Rate por división entre cero.
       Si entregado > solicitado, marcar para revisión sin ajustar silenciosamente.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass
class ResultadoCalculo:
    """Resultado del cálculo de Fill Rate para un registro."""

    kilos_solicitados: float
    kilos_entregados: float
    kilos_faltantes: float
    fill_rate_pct: Optional[float]
    es_valido: bool
    motivo_exclusion: str = ""


def calcular_registro(kilos_solicitados: float, kilos_entregados: float) -> ResultadoCalculo:
    """Calcula Fill Rate y kilos faltantes para un registro individual.

    Implementa R11, R12, R13 y R16.

    Args:
        kilos_solicitados: Cantidad pedida en kilogramos.
        kilos_entregados: Cantidad entregada en kilogramos.

    Returns:
        ResultadoCalculo con los valores calculados.
    """
    # R16: si kilos solicitados es cero o menor, no calcular Fill Rate por división entre cero
    if kilos_solicitados <= 0:
        return ResultadoCalculo(
            kilos_solicitados=kilos_solicitados,
            kilos_entregados=kilos_entregados,
            kilos_faltantes=kilos_solicitados - kilos_entregados,
            fill_rate_pct=None,
            es_valido=False,
            motivo_exclusion="Kilos solicitados menor o igual a cero (división entre cero prohibida)",
        )

    # R16: si entregado excede solicitado, marcar para revisión sin ajustar silenciosamente
    motivo = ""
    if kilos_entregados > kilos_solicitados:
        motivo = "Entrega superior al pedido (inconsistencia para revisión)"

    # R11: Fill Rate = (entregados / solicitados) × 100
    fill_rate = (kilos_entregados / kilos_solicitados) * 100

    # R12: Faltantes = solicitados − entregados (exclusivamente en kilogramos)
    faltantes = kilos_solicitados - kilos_entregados

    return ResultadoCalculo(
        kilos_solicitados=kilos_solicitados,
        kilos_entregados=kilos_entregados,
        kilos_faltantes=faltantes,
        fill_rate_pct=round(fill_rate, 2),
        es_valido=True,
        motivo_exclusion=motivo,
    )


def calcular_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica el cálculo de Fill Rate a todo un DataFrame.

    Implementa R11, R12, R13 y R16 para cada fila.

    Args:
        df: DataFrame con columnas 'Pedido' y 'Recibido' (o equivalentes mapeadas).

    Returns:
        DataFrame con columnas añadidas: 'Kilos solicitados', 'Kilos entregados',
        'Kilos faltantes', 'Fill Rate %', 'Es valido', 'Motivo exclusion'.
    """
    resultados = []

    for _, fila in df.iterrows():
        pedido = fila.get("Pedido")
        recibido = fila.get("Recibido")

        if pd.isna(pedido) or pd.isna(recibido):
            resultados.append(
                {
                    "Kilos solicitados": None,
                    "Kilos entregados": None,
                    "Kilos faltantes": None,
                    "Fill Rate %": None,
                    "Es valido": False,
                    "Motivo exclusion": "Campos incompletos (Pedido o Recibido nulos)",
                }
            )
            continue

        try:
            pedido_num = float(pedido)
            recibido_num = float(recibido)
        except (ValueError, TypeError):
            resultados.append(
                {
                    "Kilos solicitados": None,
                    "Kilos entregados": None,
                    "Kilos faltantes": None,
                    "Fill Rate %": None,
                    "Es valido": False,
                    "Motivo exclusion": "Valores no numéricos en Pedido o Recibido",
                }
            )
            continue

        calc = calcular_registro(pedido_num, recibido_num)
        resultados.append(
            {
                "Kilos solicitados": calc.kilos_solicitados,
                "Kilos entregados": calc.kilos_entregados,
                "Kilos faltantes": calc.kilos_faltantes,
                "Fill Rate %": calc.fill_rate_pct,
                "Es valido": calc.es_valido,
                "Motivo exclusion": calc.motivo_exclusion,
            }
        )

    df_resultado = df.copy()
    for col in [
        "Kilos solicitados",
        "Kilos entregados",
        "Kilos faltantes",
        "Fill Rate %",
        "Es valido",
        "Motivo exclusion",
    ]:
        df_resultado[col] = [r[col] for r in resultados]

    return df_resultado


def calcular_consolidado(df: pd.DataFrame) -> dict:
    """Calcula el Fill Rate consolidado usando totales (R14).

    Implementa R14: el cumplimiento general se calcula con totales de kilos
    solicitados y entregados, NO promediando porcentajes individuales.

    Args:
        df: DataFrame con columnas calculadas (de salida de calcular_dataframe).

    Returns:
        Diccionario con totales y Fill Rate consolidado.
    """
    df_valido = df[df["Es valido"] == True].copy()  # noqa: E712

    total_solicitado = df_valido["Kilos solicitados"].sum()
    total_entregado = df_valido["Kilos entregados"].sum()
    total_faltante = total_solicitado - total_entregado

    if total_solicitado > 0:
        fill_rate_consolidado = round((total_entregado / total_solicitado) * 100, 2)
    else:
        fill_rate_consolidado = None

    return {
        "kilos_solicitados_total": round(total_solicitado, 2),
        "kilos_entregados_total": round(total_entregado, 2),
        "kilos_faltantes_total": round(total_faltante, 2),
        "fill_rate_consolidado_pct": fill_rate_consolidado,
        "registros_validos": len(df_valido),
    }


if __name__ == "__main__":
    # Prueba rápida con datos de ejemplo del contexto (datos de prueba ficticios)
    import pandas as pd

    df_prueba = pd.DataFrame(
        {
            "Pedido": [100, 50, 40, 60, 120, 80, 30, 70],
            "Recibido": [75, 50, 20, 48, 90, 80, 30, 56],
        }
    )

    df_resultado = calcular_dataframe(df_prueba)
    print(df_resultado.to_string(index=False))

    print()
    print("--- Consolidado (R14) ---")
    consolidado = calcular_consolidado(df_resultado)
    for k, v in consolidado.items():
        print(f"  {k}: {v}")
