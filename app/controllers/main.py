"""Controlador principal de la aplicación FillRateRetail."""

from flask import Blueprint, render_template, jsonify, request

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def inicio():
    """Pantalla principal con 3 tabs de análisis de Fill Rate."""
    from app.services.analisis_diario import (
        obtener_estado_ultima_fecha,
        obtener_estado_mes_ano,
        obtener_analisis_categoria,
    )
    from datetime import datetime

    # Obtener fecha actual para seleccionar mes/año por defecto
    ahora = datetime.now()

    # Vista 1: Última fecha disponible
    estado_ultimo = obtener_estado_ultima_fecha()

    # Vista 2: Mes actual acumulado
    estado_mes = obtener_estado_mes_ano(ahora.month, ahora.year)

    # Vista 3: Análisis por categoría
    analisis_categoria = obtener_analisis_categoria()

    return render_template(
        "inicio.html",
        estado_ultimo=estado_ultimo,
        estado_mes=estado_mes,
        analisis_categoria=analisis_categoria,
        mes_actual=ahora.month,
        ano_actual=ahora.year,
    )


@main_bp.route("/analisis/mes")
def analisis_mes():
    """Pantalla de análisis acumulado por mes con selector."""
    from app.services.analisis_diario import (
        obtener_estado_mes_ano,
        obtener_analisis_categoria,
    )

    mes = request.args.get("mes", type=int)
    ano = request.args.get("ano", type=int)

    if not mes or not ano:
        from datetime import datetime
        ahora = datetime.now()
        mes = ahora.month
        ano = ahora.year

    estado_mes = obtener_estado_mes_ano(mes, ano)
    analisis_categoria = obtener_analisis_categoria()

    meses = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
    ]

    anos = list(range(2024, 2027))

    return render_template(
        "analisis_mes.html",
        estado_mes=estado_mes,
        analisis_categoria=analisis_categoria,
        mes_seleccionado=mes,
        ano_seleccionado=ano,
        meses=meses,
        anos=anos,
    )


@main_bp.route("/analisis/categoria")
def analisis_categoria_view():
    """Pantalla de análisis de faltante por categoría."""
    from app.services.analisis_diario import obtener_analisis_categoria

    analisis = obtener_analisis_categoria()

    return render_template(
        "analisis_categoria.html",
        analisis_categoria=analisis,
    )


@main_bp.route("/api/actualizar", methods=["POST"])
def actualizar_analisis():
    """Endpoint para actualizar el análisis diario.
    Lee nuevamente los archivos de insumos/ y devuelve los datos actualizados.
    """
    from app.services.analisis_diario import (
        obtener_estado_ultima_fecha,
        obtener_estado_mes_ano,
        obtener_analisis_categoria,
    )
    from datetime import datetime

    ahora = datetime.now()

    estado_ultimo = obtener_estado_ultima_fecha()
    estado_mes = obtener_estado_mes_ano(ahora.month, ahora.year)
    analisis_categoria = obtener_analisis_categoria()

    return jsonify({
        "estado_ultimo": estado_ultimo,
        "estado_mes": estado_mes,
        "analisis_categoria": analisis_categoria,
        "timestamp": ahora.strftime("%d-%m-%Y %H:%M:%S"),
    })
