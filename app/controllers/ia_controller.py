"""Controlador del agente de IA.

Expone un endpoint que recibe indicadores calculados por Python y devuelve
el JSON del agente de IA siguiendo el contrato definido en AGENTS.md.
"""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.services.agente_ia import procesar_con_ia, serializar_json

ia_bp = Blueprint("ia", __name__)


@ia_bp.route("/analizar", methods=["POST"])
def analizar():
    """Endpoint que recibe indicadores y devuelve el JSON del agente de IA.

    Cuerpo de la solicitud (JSON):
    {
        "indicadores": { ... },  # Datos calculados por Python
        "fuentes": ["archivo1.xlsx", ...]
    }

    Respuesta: JSON válido con el contrato del agente de IA.
    """
    datos = request.get_json(silent=True) or {}

    indicadores = datos.get("indicadores", {})
    fuentes = datos.get("fuentes", [])

    if not isinstance(fuentes, list):
        fuentes = [fuentes] if fuentes else []

    resultado = procesar_con_ia(indicadores, fuentes)

    return jsonify(resultado)


@ia_bp.route("/estado", methods=["GET"])
def estado_ia():
    """Endpoint que indica si el agente de IA está disponible.

    Respuesta:
    {
        "ia_disponible": true/false,
        "mensaje": "..."
    }
    """
    from app.services.agente_ia import modelo_local_disponible, leer_llave_ia

    disponible = modelo_local_disponible()
    llave = leer_llave_ia()

    return jsonify(
        {
            "ia_disponible": disponible,
            "mensaje": (
                "Agente de IA disponible"
                if disponible
                else "Modelo local no configurado. IA no disponible, cálculos determinísticos siguen activos."
            ),
            "llave_configurada": llave != "",
        }
    )
