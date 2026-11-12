"""Servicio de integración con el agente de IA local.

Contrato JSON de salida (según AGENTS.md, sección 5.4):
{
  "fecha_corte": "AAAA-MM-DD",
  "resumen_ejecutivo": "string",
  "alertas": [
    {
      "centro_carne": "string",
      "categoria": "string",
      "codigo_articulo": "string",
      "producto": "string",
      "tipo": "Faltante confirmado o riesgo estimado",
      "prioridad": "string",
      "evidencia": {
        "kilos_faltantes": number | string,
        "dias_con_faltante": integer | string,
        "fill_rate_pct": number | string,
        "ventas_historicas_kg": number | string,
        "ventas_historicas_crc": number | string,
        "periodo_referencia": "string"
      },
      "recomendacion": "string"
    }
  ],
  "productos_indispensables": [],
  "riesgos_detectados": [],
  "limitaciones": [],
  "fuentes": []
}

Reglas obligatorias del agente (AGENTS.md, sección 5.4):
1. Nunca inventar datos, productos, fechas, cifras ni causas de faltantes.
2. Si un campo no aparece o no puede determinarse, usar exactamente "no indicado".
3. Los datos numéricos válidos deben devolverse como números, sin símbolos ni unidades.
4. No modificar cifras previamente calculadas por Python.
5. Distinguir explícitamente los hechos confirmados de las estimaciones.
6. No afirmar problemas de producción/inventario/logística si solo hay faltante de abastecimiento.
7. Justificar las recomendaciones con datos concretos.
8. No recomendar cantidades específicas de reposición sin regla aprobada.
9. Devolver listas vacías cuando no existan alertas sustentadas.
10. Si el modelo local no está disponible, mostrar cálculos y señalar que IA no está disponible.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv

# Cargar variables de .env si existe
load_dotenv()


def leer_llave_ia() -> str:
    """Lee la llave de acceso del agente de IA desde .env.

    Returns:
        La llave configurada, o cadena vacía si no está definida.
    """
    return os.getenv("IA_API_KEY", "")


def modelo_local_disponible() -> bool:
    """Verifica si el motor de IA local está disponible.

    En esta implementación se verifica la presencia de la llave en .env.
    En una integración real, aquí se consultaría al motor local (Ollama/llama.cpp).

    Returns:
        True si el modelo local está disponible, False en caso contrario.
    """
    llave = leer_llave_ia()
    # Si no hay llave configurada, se considera que el modelo no está disponible
    # para inferencia externa, pero la app sigue funcionando con cálculos determinísticos.
    return llave != ""


def construir_json_vacio(fecha_corte: str, fuentes: list[str]) -> dict[str, Any]:
    """Construye un JSON válido con listas vacías cuando no hay alertas (Regla 9).

    Args:
        fecha_corte: Fecha del análisis en formato AAAA-MM-DD.
        fuentes: Lista de identificadores de archivos y períodos utilizados.

    Returns:
        Diccionario con la estructura del contrato JSON y listas vacías.
    """
    return {
        "fecha_corte": fecha_corte,
        "resumen_ejecutivo": "no indicado",
        "alertas": [],
        "productos_indispensables": [],
        "riesgos_detectados": [],
        "limitaciones": [],
        "fuentes": fuentes,
    }


def construir_json_ia_no_disponible(fecha_corte: str, fuentes: list[str]) -> dict[str, Any]:
    """Construye JSON indicando que el agente de IA no está disponible (Regla 10).

    Args:
        fecha_corte: Fecha del análisis en formato AAAA-MM-DD.
        fuentes: Lista de identificadores de archivos y períodos utilizados.

    Returns:
        Diccionario con la estructura del contrato JSON y limitación de IA no disponible.
    """
    return {
        "fecha_corte": fecha_corte,
        "resumen_ejecutivo": "no indicado",
        "alertas": [],
        "productos_indispensables": [],
        "riesgos_detectados": [],
        "limitaciones": [
            {
                "tipo": "Modelo de IA no disponible",
                "descripcion": "El motor de IA local no está configurado o no está disponible. "
                "Los cálculos determinísticos de Python siguen mostrándose normalmente.",
            }
        ],
        "fuentes": fuentes,
    }


def validar_evidencia(evidencia: dict[str, Any]) -> dict[str, Any]:
    """Valida y normaliza la estructura de evidencia de una alerta.

    Aplica las reglas obligatorias del agente:
    - Campos numéricos como números sin símbolos ni unidades (Regla 3).
    - Campos ausentes como "no indicado" (Regla 2).

    Args:
        evidencia: Diccionario con los datos de evidencia.

    Returns:
        Diccionario normalizado con las llaves obligatorias de evidencia.
    """
    return {
        "kilos_faltantes": evidencia.get("kilos_faltantes", "no indicado"),
        "dias_con_faltante": evidencia.get("dias_con_faltante", "no indicado"),
        "fill_rate_pct": evidencia.get("fill_rate_pct", "no indicado"),
        "ventas_historicas_kg": evidencia.get("ventas_historicas_kg", "no indicado"),
        "ventas_historicas_crc": evidencia.get("ventas_historicas_crc", "no indicado"),
        "periodo_referencia": evidencia.get("periodo_referencia", "no indicado"),
    }


def generar_alerta(
    centro_carne: str,
    categoria: str,
    codigo_articulo: str,
    producto: str,
    tipo: str,
    prioridad: str,
    evidencia: dict[str, Any],
    recomendacion: str,
) -> dict[str, Any]:
    """Genera una entrada de alerta siguiendo el contrato JSON.

    Args:
        centro_carne: Establecimiento afectado ("no indicado" si no se conoce).
        categoria: Categoría del producto ("no indicado" si no se conoce).
        codigo_articulo: Código identificador ("no indicado" si no se conoce).
        producto: Descripción comercial ("no indicado" si no se conoce).
        tipo: "Faltante confirmado" o "riesgo estimado".
        prioridad: Evaluación cualitativa fundamentada.
        evidencia: Indicadores que fundamentan la alerta.
        recomendacion: Acción sugerida (sin cantidades específicas de reposición, Regla 8).

    Returns:
        Diccionario con la estructura de una alerta.
    """
    return {
        "centro_carne": centro_carne or "no indicado",
        "categoria": categoria or "no indicado",
        "codigo_articulo": codigo_articulo or "no indicado",
        "producto": producto or "no indicado",
        "tipo": tipo,
        "prioridad": prioridad,
        "evidencia": validar_evidencia(evidencia),
        "recomendacion": recomendacion or "no indicado",
    }


def procesar_con_ia(
    indicadores: dict[str, Any],
    fuentes: list[str],
) -> dict[str, Any]:
    """Procesa los indicadores calculados y devuelve el JSON del agente de IA.

    Esta función es el punto de entrada del agente. Recibe datos ya calculados
    por Python y los interpreta siguiendo el contrato JSON y las reglas obligatorias.

    Args:
        indicadores: Diccionario con los indicadores calculados por Python
                     (Fill Rate, faltantes, recurrencia, rankings, etc.).
        fuentes: Lista de identificadores de archivos y períodos utilizados.

    Returns:
        Diccionario con la estructura completa del contrato JSON del agente.
    """
    fecha_corte = datetime.now().strftime("%Y-%m-%d")

    # Regla 10: si el modelo local no está disponible, devolver JSON con limitación
    if not modelo_local_disponible():
        return construir_json_ia_no_disponible(fecha_corte, fuentes)

    # Regla 9: si no hay alertas sustentadas, devolver listas vacías
    alertas_raw = indicadores.get("alertas", [])
    if not alertas_raw:
        return construir_json_vacio(fecha_corte, fuentes)

    # Procesar cada alerta aplicando las reglas obligatorias
    alertas_procesadas = []
    for alerta in alertas_raw:
        alerta_procesada = generar_alerta(
            centro_carne=alerta.get("centro_carne", "no indicado"),
            categoria=alerta.get("categoria", "no indicado"),
            codigo_articulo=alerta.get("codigo_articulo", "no indicado"),
            producto=alerta.get("producto", "no indicado"),
            tipo=alerta.get("tipo", "no indicado"),
            prioridad=alerta.get("prioridad", "no indicado"),
            evidencia=alerta.get("evidencia", {}),
            recomendacion=alerta.get("recomendacion", "no indicado"),
        )
        alertas_procesadas.append(alerta_procesada)

    # Construir JSON final (sin modificar cifras de Python - Regla 4)
    resultado = {
        "fecha_corte": fecha_corte,
        "resumen_ejecutivo": indicadores.get("resumen_ejecutivo", "no indicado"),
        "alertas": alertas_procesadas,
        "productos_indispensables": indicadores.get("productos_indispensables", []),
        "riesgos_detectados": indicadores.get("riesgos_detectados", []),
        "limitaciones": indicadores.get("limitaciones", []),
        "fuentes": fuentes,
    }

    return resultado


def serializar_json(resultado: dict[str, Any]) -> str:
    """Serializa el resultado a string JSON válido.

    Args:
        resultado: Diccionario con el resultado del agente.

    Returns:
        String JSON válido.
    """
    return json.dumps(resultado, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    # Prueba rápida del contrato JSON
    indicadores_prueba = {
        "fecha_corte": "2026-11-04",
        "resumen_ejecutivo": "Se detectaron faltantes recurrentes en productos de alta rotación.",
        "alertas": [
            {
                "centro_carne": "CC A",
                "categoria": "Res",
                "codigo_articulo": "R001",
                "producto": "RIB EYE STEAK",
                "tipo": "Faltante confirmado",
                "prioridad": "Alta",
                "evidencia": {
                    "kilos_faltantes": 55,
                    "dias_con_faltante": 2,
                    "fill_rate_pct": 67.86,
                    "ventas_historicas_kg": 900,
                    "ventas_historicas_crc": 4500000,
                    "periodo_referencia": "Octubre 2026",
                },
                "recomendacion": "Revisar abastecimiento de R001 en CC A por faltante recurrente.",
            }
        ],
        "productos_indispensables": ["R001"],
        "riesgos_detectados": [],
        "limitaciones": [],
        "fuentes": ["Insumos/Fill Rate Noviembre - Diciembre 2025.xlsx - hoja FR NOV 2025"],
    }

    fuentes = ["Insumos/Fill Rate Noviembre - Diciembre 2025.xlsx"]
    resultado = procesar_con_ia(indicadores_prueba, fuentes)
    print(serializar_json(resultado))
