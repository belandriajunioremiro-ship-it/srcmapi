"""
Genera el PDF de la Cédula Catastral en el propio backend (más seguro y
consistente que generarlo en el frontend: los datos y el cálculo de
vigencia/valores salen directo de la base de datos, y el usuario nunca
puede manipular lo que ve el PDF).

Usa la vista `v_pdf_cedula_catastral` (ya definida en el script SQL) como
fuente de datos, más `formatear_codigo_catastral` para el código con
guiones. Renderiza con Jinja2 y convierte a PDF con WeasyPrint.
"""
import io
import base64
from datetime import date
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import Any

import qrcode
from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy import text
from sqlalchemy.orm import Session
from weasyprint import HTML

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"


def _fmt_num(value, decimals=2, thousands=True):
    if value is None:
        return "—"
    try:
        n = float(value)
    except (TypeError, ValueError):
        return "—"
    if thousands:
        return f"{n:,.{decimals}f}"
    return f"{n:.{decimals}f}"


def _fmt_area(value):
    return _fmt_num(value, decimals=2, thousands=False)


def _fmt_money(value):
    return _fmt_num(value, decimals=2, thousands=True)


def _fmt_mts(value):
    return _fmt_num(value, decimals=2, thousands=False)


_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)
_env.filters["fmt_money"] = _fmt_money
_env.filters["fmt_area"] = _fmt_area
_env.filters["fmt_mts"] = _fmt_mts
_env.filters["fmt_num"] = _fmt_num


def generar_qr(nombre: str, codigo_catastral: str, expediente: str) -> str:
    """Genera un código QR con los datos de la cédula y lo devuelve como data URI base64."""
    contenido = (
        f"CÉDULA CATASTRAL\n"
        f"Propietario: {nombre}\n"
        f"Código Catastral: {codigo_catastral}\n"
        f"Expediente: {expediente}\n"
        f"Municipio Torbes - Estado Táchira"
    )
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(contenido)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#000000", back_color="#ffffff")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def obtener_datos_cedula(db: Session, inmueble_id: str) -> dict[str, Any] | None:
    """
    Trae la fila de la vista v_pdf_cedula_catastral para un inmueble,
    junto con el código formateado (con guiones) de v_cedula_catastral.
    """
    row = db.execute(
        text(
            """
            SELECT pdf.*, fmt.codigo_catastral_formato
            FROM v_pdf_cedula_catastral pdf
            JOIN v_cedula_catastral fmt ON fmt.inmueble_id = pdf.inmueble_id
            WHERE pdf.inmueble_id = :inmueble_id
            """
        ),
        {"inmueble_id": str(inmueble_id)},
    ).mappings().first()

    return dict(row) if row else None


def generar_pdf_cedula(db: Session, inmueble_id: str) -> bytes:
    """Devuelve los bytes del PDF de la cédula catastral de un inmueble."""
    datos = obtener_datos_cedula(db, inmueble_id)
    if datos is None:
        raise ValueError("Inmueble no encontrado")

    # Generar QR
    qr_code = generar_qr(
        datos.get("propietario_nombre", ""),
        datos.get("codigo_catastral_formato", ""),
        datos.get("expediente_numero", ""),
    )

    template = _env.get_template("cedula_catastral.html")
    html_str = template.render(
        d=datos,
        logos=f"file:///{STATIC_DIR}/logos",
        fecha_generacion=date.today().strftime("%d/%m/%Y"),
        qr_code=qr_code,
    )

    pdf_buffer = io.BytesIO()
    HTML(string=html_str, base_url=str(TEMPLATES_DIR)).write_pdf(pdf_buffer)
    return pdf_buffer.getvalue()

