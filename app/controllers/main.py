"""Controlador principal de la aplicación FillRateRetail."""

from flask import Blueprint, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def inicio():
    """Pantalla de inicio / tablero gerencial."""
    datos_tablero = {
        "fill_rate_general": "77,20",
        "kilos_faltantes_totales": "57",
        "kilos_solicitados_totales": "250",
        "kilos_entregados_totales": "193",
        "datos_por_categoria": [
            {"categoria": "Res", "pedido_kg": "140", "entrega_kg": "95", "faltante_kg": "45", "fill_rate_pct": "67,86"},
            {"categoria": "Cerdo", "pedido_kg": "110", "entrega_kg": "98", "faltante_kg": "12", "fill_rate_pct": "89,09"},
        ],
        "datos_por_centro": [
            {"centro": "CC A", "pedido_kg": "350", "entrega_kg": "295", "faltante_kg": "55", "fill_rate_pct": "84,29"},
            {"centro": "CC B", "pedido_kg": "200", "entrega_kg": "154", "faltante_kg": "46", "fill_rate_pct": "77,00"},
        ],
        "datos_recurrentes": [
            {"producto": "RIB EYE STEAK", "codigo": "R001", "categoria": "Res", "faltante_total_kg": "55", "dias_con_faltante": "2"},
            {"producto": "CACHETE DE CERDO", "codigo": "C001", "categoria": "Cerdo", "faltante_total_kg": "26", "dias_con_faltante": "2"},
        ],
        "alertas_ia": [],
        "alerta_ia_no_disponible": "El motor de IA local no está configurado. Los cálculos determinísticos siguen disponibles.",
    }

    return render_template("inicio.html", **datos_tablero)


@main_bp.route("/resultados")
def resultados():
    """Pantalla de resultados detallados con tabla y detalle por registro."""
    import json

    datos_resultados = {
        "total_registros": "8",
        "registros_con_faltante": "4",
        "fill_rate_promedio": "81,25",
        "kilos_faltantes_totales": "101",
        "datos_registros": [
            {
                "fecha": "2026-11-01",
                "centro_carne": "CC A",
                "categoria": "Res",
                "producto": "RIB EYE STEAK",
                "codigo": "R001",
                "pedido_kg": "100",
                "entrega_kg": "75",
                "faltante_kg": "25",
                "fill_rate_pct": "75,00",
                "detalle_json": {
                    "fecha": "2026-11-01",
                    "centro_carne": "CC A",
                    "categoria": "Res",
                    "producto": "RIB EYE STEAK",
                    "codigo": "R001",
                    "pedido_kg": "100",
                    "entrega_kg": "75",
                    "faltante_kg": "25",
                    "fill_rate_pct": "75,00",
                },
            },
            {
                "fecha": "2026-11-01",
                "centro_carne": "CC A",
                "categoria": "Cerdo",
                "producto": "CACHETE DE CERDO",
                "codigo": "C001",
                "pedido_kg": "50",
                "entrega_kg": "50",
                "faltante_kg": "0",
                "fill_rate_pct": "100,00",
                "detalle_json": {
                    "fecha": "2026-11-01",
                    "centro_carne": "CC A",
                    "categoria": "Cerdo",
                    "producto": "CACHETE DE CERDO",
                    "codigo": "C001",
                    "pedido_kg": "50",
                    "entrega_kg": "50",
                    "faltante_kg": "0",
                    "fill_rate_pct": "100,00",
                },
            },
            {
                "fecha": "2026-11-01",
                "centro_carne": "CC B",
                "categoria": "Res",
                "producto": "RIB EYE STEAK",
                "codigo": "R001",
                "pedido_kg": "40",
                "entrega_kg": "20",
                "faltante_kg": "20",
                "fill_rate_pct": "50,00",
                "detalle_json": {
                    "fecha": "2026-11-01",
                    "centro_carne": "CC B",
                    "categoria": "Res",
                    "producto": "RIB EYE STEAK",
                    "codigo": "R001",
                    "pedido_kg": "40",
                    "entrega_kg": "20",
                    "faltante_kg": "20",
                    "fill_rate_pct": "50,00",
                },
            },
            {
                "fecha": "2026-11-01",
                "centro_carne": "CC B",
                "categoria": "Cerdo",
                "producto": "CACHETE DE CERDO",
                "codigo": "C001",
                "pedido_kg": "60",
                "entrega_kg": "48",
                "faltante_kg": "12",
                "fill_rate_pct": "80,00",
                "detalle_json": {
                    "fecha": "2026-11-01",
                    "centro_carne": "CC B",
                    "categoria": "Cerdo",
                    "producto": "CACHETE DE CERDO",
                    "codigo": "C001",
                    "pedido_kg": "60",
                    "entrega_kg": "48",
                    "faltante_kg": "12",
                    "fill_rate_pct": "80,00",
                },
            },
            {
                "fecha": "2026-11-02",
                "centro_carne": "CC A",
                "categoria": "Res",
                "producto": "RIB EYE STEAK",
                "codigo": "R001",
                "pedido_kg": "120",
                "entrega_kg": "90",
                "faltante_kg": "30",
                "fill_rate_pct": "75,00",
                "detalle_json": {
                    "fecha": "2026-11-02",
                    "centro_carne": "CC A",
                    "categoria": "Res",
                    "producto": "RIB EYE STEAK",
                    "codigo": "R001",
                    "pedido_kg": "120",
                    "entrega_kg": "90",
                    "faltante_kg": "30",
                    "fill_rate_pct": "75,00",
                },
            },
            {
                "fecha": "2026-11-02",
                "centro_carne": "CC A",
                "categoria": "Cerdo",
                "producto": "CACHETE DE CERDO",
                "codigo": "C001",
                "pedido_kg": "80",
                "entrega_kg": "80",
                "faltante_kg": "0",
                "fill_rate_pct": "100,00",
                "detalle_json": {
                    "fecha": "2026-11-02",
                    "centro_carne": "CC A",
                    "categoria": "Cerdo",
                    "producto": "CACHETE DE CERDO",
                    "codigo": "C001",
                    "pedido_kg": "80",
                    "entrega_kg": "80",
                    "faltante_kg": "0",
                    "fill_rate_pct": "100,00",
                },
            },
            {
                "fecha": "2026-11-02",
                "centro_carne": "CC B",
                "categoria": "Res",
                "producto": "RIB EYE STEAK",
                "codigo": "R001",
                "pedido_kg": "30",
                "entrega_kg": "30",
                "faltante_kg": "0",
                "fill_rate_pct": "100,00",
                "detalle_json": {
                    "fecha": "2026-11-02",
                    "centro_carne": "CC B",
                    "categoria": "Res",
                    "producto": "RIB EYE STEAK",
                    "codigo": "R001",
                    "pedido_kg": "30",
                    "entrega_kg": "30",
                    "faltante_kg": "0",
                    "fill_rate_pct": "100,00",
                },
            },
            {
                "fecha": "2026-11-02",
                "centro_carne": "CC B",
                "categoria": "Cerdo",
                "producto": "CACHETE DE CERDO",
                "codigo": "C001",
                "pedido_kg": "70",
                "entrega_kg": "56",
                "faltante_kg": "14",
                "fill_rate_pct": "80,00",
                "detalle_json": {
                    "fecha": "2026-11-02",
                    "centro_carne": "CC B",
                    "categoria": "Cerdo",
                    "producto": "CACHETE DE CERDO",
                    "codigo": "C001",
                    "pedido_kg": "70",
                    "entrega_kg": "56",
                    "faltante_kg": "14",
                    "fill_rate_pct": "80,00",
                },
            },
        ],
        "alerta_ia_no_disponible": "El motor de IA local no está configurado. Los cálculos determinísticos siguen disponibles.",
    }

    return render_template("resultados.html", **datos_resultados)
