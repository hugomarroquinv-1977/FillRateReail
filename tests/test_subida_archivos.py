"""Pruebas de la carga de archivos desde la web y de la detección de fechas.

Casos cubiertos:
- El archivo subido se guarda con nombre canónico (con espacio, año de 4 dígitos).
- Nombres con guion bajo (efecto de secure_filename) también se reconocen.
- Nombres con año de 2 dígitos se normalizan a 4 dígitos.
- El archivo subido tiene prioridad y actualiza la fecha del tablero.
- Nombres inválidos son rechazados sin guardar nada.
"""

import io

import pytest

from app.services.analisis_diario import (
    guardar_archivo_cargado,
    interpretar_fecha_nombre_archivo,
    listar_archivos_disponibles,
    listar_archivos_pedido,
    obtener_estado_ultima_fecha,
)

CONTENIDO_FALSO = b"contenido de prueba"


@pytest.mark.parametrize(
    "nombre,esperado",
    [
        ("Pedido 09-11-2026.xlsx", (2026, 11, 9)),
        ("Pedido 9-11-26.xlsx", (2026, 11, 9)),
        ("Pedido_09-11-2026.xlsx", (2026, 11, 9)),
        ("Pedido 01-01-25.xlsx", (2025, 1, 1)),
    ],
)
def test_interpretar_fecha_variantes(nombre, esperado):
    fecha = interpretar_fecha_nombre_archivo(nombre)
    assert fecha is not None
    assert (fecha.year, fecha.month, fecha.day) == esperado


@pytest.mark.parametrize(
    "nombre",
    ["reporte.xlsx", "Pedido 09-11.xlsx", "Pedido 09-11-2026.xls", "Pedido 32-11-2026.xlsx"],
)
def test_interpretar_fecha_invalida(nombre):
    assert interpretar_fecha_nombre_archivo(nombre) is None


def test_guardar_normaliza_nombre(tmp_path):
    carpeta_insumos = tmp_path / "Insumos"
    carpeta_carga = tmp_path / "carga"
    carpeta_carga.mkdir()

    ruta = guardar_archivo_cargado(CONTENIDO_FALSO, "Pedido_09-11-26.xlsx")

    assert ruta.name == "Pedido 09-11-2026.xlsx"
    assert ruta.read_bytes() == CONTENIDO_FALSO
    assert ruta.parent.name == "carga_temporal"

    archivos = listar_archivos_pedido(carpeta_insumos, ruta.parent)
    assert len(archivos) == 1
    assert archivos[0][0].strftime("%d-%m-%Y") == "09-11-2026"


def test_archivo_subido_tiene_prioridad(tmp_path):
    carpeta_insumos = tmp_path / "Insumos"
    carpeta_carga = tmp_path / "carga"
    carpeta_insumos.mkdir()
    carpeta_carga.mkdir()

    # Misma fecha en ambos orígenes
    (carpeta_insumos / "Pedido 07-11-2026.xlsx").write_bytes(b"repo")
    (carpeta_carga / "Pedido_07-11-2026.xlsx").write_bytes(b"subido")

    archivos = listar_archivos_pedido(carpeta_insumos, carpeta_carga)
    assert len(archivos) == 1
    assert archivos[0][1].parent == carpeta_carga

    detalle = listar_archivos_disponibles(carpeta_insumos, carpeta_carga)
    assert detalle[0]["origen"] == "Carga web"


def test_fecha_mas_reciente_es_el_archivo_subido(tmp_path):
    carpeta_insumos = tmp_path / "Insumos"
    carpeta_carga = tmp_path / "carga"
    carpeta_insumos.mkdir()
    carpeta_carga.mkdir()

    (carpeta_insumos / "Pedido 07-11-2026.xlsx").write_bytes(b"repo")
    (carpeta_carga / "Pedido 09-11-2026.xlsx").write_bytes(b"subido")

    archivos = listar_archivos_pedido(carpeta_insumos, carpeta_carga)
    assert archivos[0][0].strftime("%d-%m-%Y") == "09-11-2026"
    assert archivos[0][1].name == "Pedido 09-11-2026.xlsx"


def test_guardar_nombre_invalido_falla(tmp_path, monkeypatch):
    import app.services.analisis_diario as svc

    monkeypatch.setattr(svc, "CARGA_TEMPORAL_PATH", tmp_path / "carga")

    with pytest.raises(ValueError):
        guardar_archivo_cargado(CONTENIDO_FALSO, "reporte.xlsx")


def test_endpoint_subida_rechaza_nombre_invalido():
    from app import create_app

    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    respuesta = client.post(
        "/subir-archivo",
        data={"archivo": (io.BytesIO(CONTENIDO_FALSO), "reporte.xlsx")},
        content_type="multipart/form-data",
    )
    assert respuesta.status_code == 400
    assert "inválido" in respuesta.get_json()["error"]


def test_estado_ultima_fecha_incluye_archivo_y_origen(tmp_path):
    carpeta_insumos = tmp_path / "Insumos"
    carpeta_carga = tmp_path / "carga"
    carpeta_insumos.mkdir()
    carpeta_carga.mkdir()

    from pathlib import Path

    origen = Path("Insumos") / "Pedido 07-11-2026.xlsx"
    if not origen.exists():
        pytest.skip("No hay archivo real de insumos para la prueba")

    (carpeta_carga / "Pedido 09-11-2026.xlsx").write_bytes(origen.read_bytes())

    estado = obtener_estado_ultima_fecha(carpeta_insumos, carpeta_carga)
    assert estado is not None
    assert estado["fecha"] == "09-11-2026"
    assert estado["archivo"] == "Pedido 09-11-2026.xlsx"
    assert estado["origen"] == "Carga web"
    assert estado["total_archivos"] == 1
