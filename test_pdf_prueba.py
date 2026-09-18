"""
Script para generar PDFs de prueba de la cédula catastral con datos realistas
del Municipio Torbes, San Josecito, Estado Táchira.

Cada ejecución genera un PDF diferente (incrementa el número de expediente)
para simular cédulas catastrales reales del municipio.

Uso:
    python test_pdf_prueba.py          # Genera 1 PDF
    python test_pdf_prueba.py --n 5    # Genera 5 PDFs diferentes
"""
import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path
from io import BytesIO
import base64

import qrcode
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

TEMPLATES_DIR = Path(__file__).resolve().parent / "app" / "templates"
STATIC_DIR = Path(__file__).resolve().parent / "static"


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

NOMBRES = [
    ("Carlos", "Mora Rivas"), ("María", "Blanco Hernández"), ("José", "Pérez García"),
    ("Carmen", "Torres Ramírez"), ("Miguel", "González Díaz"), ("Rosa", "Moreno Jiménez"),
    ("Antonio", "Ruiz Rojas"), ("Yolanda", "Medina Castro"), ("Luis", "Vargas Arias"),
    ("Patricia", "Contreras Delgado"), ("Fernando", "Guerrero Navarro"), ("Gladys", "Ortiz Pardo"),
    ("Andrés", "Quintero Salazar"), ("Ana", "Urbina Villanueva"), ("Eduardo", "Zambrano Colmenares"),
    ("Mercedes", "Escalante Fernández"), ("Roberto", "Gómez López"), ("Zuleima", "Martínez Rodríguez"),
    ("Francisco", "Suárez Vivas"), ("Norka", "Chacón Mora"), ("Jorge", "Rivas Blanco"),
    ("Belkis", "Hernández Pérez"), ("Alberto", "García Sánchez"), ("Mireya", "Torres González"),
    ("Rafael", "Díaz Moreno"), ("Doris", "Jiménez Ruiz"), ("Héctor", "Rojas Medina"),
    ("Nilda", "Castro Vargas"), ("César", "Arias Contreras"), ("Hilda", "Delgado Guerrero"),
]

SECTORES = [
    {"cod": "01", "nombre": "Centro San Josecito", "via": "Calle Bolívar", "tipo": "asfalto"},
    {"cod": "02", "nombre": "Vía al Llano", "via": "Vía al Llano", "tipo": "asfalto"},
    {"cod": "03", "nombre": "La Loma", "via": "Carrera La Loma", "tipo": "pavimento"},
    {"cod": "04", "nombre": "El Cerrito", "via": "Calle El Cerrito", "tipo": "tierra"},
    {"cod": "05", "nombre": "La Quebrada", "via": "Calle La Quebrada", "tipo": "tierra"},
    {"cod": "06", "nombre": "Troncal 5 Norte", "via": "Troncal 5, Sector Norte", "tipo": "asfalto"},
    {"cod": "07", "nombre": "El Paraíso", "via": "Calle El Paraíso", "tipo": "pavimento"},
    {"cod": "08", "nombre": "San Rafael", "via": "Calle San Rafael", "tipo": "pavimento"},
    {"cod": "09", "nombre": "Bella Vista", "via": "Calle Bella Vista", "tipo": "asfalto"},
    {"cod": "10", "nombre": "El Progreso", "via": "Calle El Progreso", "tipo": "tierra"},
]

LINDEROS = [
    "Terreno de la familia Mora", "Calle principal del sector", "Quebrada La Loma",
    "Terreno de la familia Rivas", "Camino vecinal", "Carretera Troncal 5",
    "Predio municipal", "Casa de la familia Blanco", "Terreno de la familia Hernández",
    "Caño San José", "Vía al cementerio", "Terreno de la alcaldía",
    "Cancha deportiva", "Escuela Bolivariana", "Terreno de la familia García",
]

_contador = 0


def siguiente_expediente():
    global _contador
    _contador += 1
    return f"{_contador:06d}/2025"


def generar_qr(nombre, codigo_catastral, expediente):
    contenido = (
        f"CEDULA CATASTRAL\n"
        f"Propietario: {nombre}\n"
        f"Codigo Catastral: {codigo_catastral}\n"
        f"Expediente: {expediente}\n"
        f"Municipio Torbes - Estado Tachira"
    )
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M,
                        box_size=10, border=2)
    qr.add_data(contenido)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#000000", back_color="#ffffff")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"


def generar_datos_realistas():
    nombre, apellido = random.choice(NOMBRES)
    sector = random.choice(SECTORES)
    manzana = f"{random.randint(1,50):03d}"
    parcela = f"{random.randint(1,200):03d}"

    n_ced = random.randint(5, 30)
    resto = random.randint(10000, 99999)
    cedula = f"V-{n_ced}.{resto % 100}.{resto // 100}"

    area_terreno = round(random.uniform(200, 2000), 2)
    tiene_construccion = random.random() > 0.15
    area_construccion = round(random.uniform(80, area_terreno * 0.7), 2) if tiene_construccion else None
    tiene_comercio = random.random() < 0.2
    area_comercio = round(random.uniform(10, 80), 2) if tiene_comercio else None

    valor_unit_terreno = round(random.uniform(20000, 45000), 2)
    valor_unit_construccion = round(random.uniform(65000, 120000), 2) if area_construccion else None
    valor_unit_comercio = round(random.uniform(80000, 150000), 2) if area_comercio else None

    valor_terreno = round(area_terreno * valor_unit_terreno, 2)
    valor_construccion = round(area_construccion * valor_unit_construccion, 2) if area_construccion and valor_unit_construccion else 0
    valor_comercio = round(area_comercio * valor_unit_comercio, 2) if area_comercio and valor_unit_comercio else 0
    valor_total = round(valor_terreno + valor_construccion + valor_comercio, 2)

    tenencia = random.choices(["propio", "ejido", "arrendado"], weights=[70, 20, 10])[0]

    mts_n = round(random.uniform(15, 55), 2)
    mts_s = round(random.uniform(15, 55), 2)
    mts_e = round(random.uniform(10, 45), 2)
    mts_o = round(random.uniform(10, 45), 2)

    fecha_emision = date(2025, random.randint(1, 9), random.randint(1, 28))
    fecha_recibo = fecha_emision - timedelta(days=random.randint(0, 30))
    expediente = siguiente_expediente()

    doc_tipos = ["Título de Propiedad", "Título Supletorio", "Compra-Venta",
                 "Declaración Sucesoral", "Donación"]

    return {
        "nombre_estado": "Táchira",
        "nombre_municipio": "Torbes",
        "nombre_parroquia": "San Josecito",
        "rif_alcaldia": "G-20000395-2",
        "direccion_institucional": "Municipio Torbes, San Josecito, Vía al Llano, Troncal 5",
        "e": "20", "m": "27", "p": "01",
        "s": sector["cod"],
        "ma": manzana, "pa": parcela,
        "sp": "000", "n": "000", "u": "000",
        "codigo_catastral_formato": f"20-27-01-{sector['cod']}-{manzana}-{parcela}-000-000-000",
        "expediente_numero": expediente,
        "numero_recibo": f"REC-2025-{random.randint(1,999):04d}",
        "fecha_recibo": fecha_recibo,
        "fecha_emision": fecha_emision,
        "vigente_hasta": fecha_emision + timedelta(days=365),
        "propietario_nombre": f"{nombre} {apellido}",
        "cedula_rif": cedula,
        "direccion": f"{sector['via']}, #{random.randint(1,300)}, Sector {sector['nombre']}, San Josecito",
        "documento_tipo": random.choice(doc_tipos),
        "documento_numero": f"{random.randint(100,9999)}",
        "documento_tomo": random.choice(["I", "II", "III", "IV"]),
        "documento_folio": f"{random.randint(1,500)}",
        "documento_protocolo": f"{random.randint(1,5):02d}",
        "documento_fecha": date(random.randint(2005, 2024), random.randint(1, 12), random.randint(1, 28)),
        "tenencia": tenencia,
        "lindero_norte_doc": random.choice(LINDEROS),
        "lindero_norte_mts": mts_n,
        "lindero_sur_doc": random.choice(LINDEROS),
        "lindero_sur_mts": mts_s,
        "lindero_este_doc": random.choice(LINDEROS),
        "lindero_este_mts": mts_e,
        "lindero_oeste_doc": random.choice(LINDEROS),
        "lindero_oeste_mts": mts_o,
        "lindero_norte_top": f"Vértice GPS Norte",
        "lindero_norte_top_mts": round(mts_n + random.uniform(-1.5, 1.5), 2),
        "lindero_sur_top": f"Vértice GPS Sur",
        "lindero_sur_top_mts": round(mts_s + random.uniform(-1.5, 1.5), 2),
        "lindero_este_top": f"Vértice GPS Este",
        "lindero_este_top_mts": round(mts_e + random.uniform(-1.5, 1.5), 2),
        "lindero_oeste_top": f"Vértice GPS Oeste",
        "lindero_oeste_top_mts": round(mts_o + random.uniform(-1.5, 1.5), 2),
        "aguas_blancas": random.random() > 0.25,
        "aguas_servidas": random.random() > 0.3,
        "electricidad": random.random() > 0.15,
        "contador": random.random() > 0.4,
        "existe_vivienda": tiene_construccion,
        "tipo_vivienda": random.choice(["casa", "casa", "quinta", "apartamento"]) if tiene_construccion else None,
        "descripcion_uso": random.choices(["residencial", "comercial", "mixto"], weights=[65, 15, 20])[0],
        "numero_plantas": random.choice([1, 1, 2, 2, 3]) if tiene_construccion else None,
        "uso_segun_zonificacion": "residencial",
        "area_terreno_m2": area_terreno,
        "valor_unit_terreno": valor_unit_terreno,
        "area_construccion_m2": area_construccion,
        "valor_unit_construccion": valor_unit_construccion,
        "area_comercio_m2": area_comercio,
        "valor_unit_comercio": valor_unit_comercio,
        "valor_terreno": valor_terreno,
        "valor_construccion": valor_construccion,
        "valor_comercio": valor_comercio,
        "valor_catastral_total": valor_total,
        "via_acceso": sector["tipo"],
        "estructura_techo": random.choice(["placa", "placa", "machimbre", "acerolit"]) if tiene_construccion else None,
        "estructura_paredes": random.choice(["bloque", "bloque", "ladrillo", "friso_liso"]) if tiene_construccion else None,
        "piso": random.choice(["ceramica", "ceramica", "cemento", "terracota"]) if tiene_construccion else None,
        "dormitorios": random.randint(1, 5) if tiene_construccion else None,
        "banos": random.randint(1, 3) if tiene_construccion else None,
        "sala": tiene_construccion,
        "cocina": tiene_construccion,
        "ambiente_otro": random.choice(["Comedor", "Sala de estar", "Terraza", "Estudio"]),
        "caracteristica_general": random.choice(["aislada", "continua", "pareada"]),
        "observaciones": random.choice([
            "Inmueble en buen estado de conservación",
            "Requiere mantenimiento en la cubierta",
            "Ampliación en proceso de legalización",
            "Predio con uso mixto residencial-comercial",
            "Terreno con pendiente moderada",
            "Colinda con quebrada seasonal",
            "Vivienda de interés social",
        ]),
        "utm_norte": round(random.uniform(860000, 870000), 2),
        "utm_este": round(random.uniform(250000, 260000), 2),
        "notas_legales": None,
        "nombre_maxima_autoridad": "Dra. Charly Rojas",
        "cargo_maxima_autoridad": "Alcaldesa Bolivariana y Primera Autoridad Civil del Municipio Torbes, Estado Táchira",
        "texto_acta_maxima_autoridad": "Acta de Sesión Solemne N° 78 de Fecha 02 de Agosto de 2025",
        "nombre_director_catastro": "",
        "cargo_director_catastro": "Directora de Urbanismo y Catastro",
        "texto_resolucion_director": "Resolución N° 018/2025 de fecha 15 de Agosto de 2025",
    }


def generar_pdf_prueba(indice=1):
    datos = generar_datos_realistas()

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["fmt_money"] = _fmt_money
    env.filters["fmt_area"] = _fmt_area
    env.filters["fmt_mts"] = _fmt_mts
    env.filters["fmt_num"] = _fmt_num

    qr_code = generar_qr(
        datos["propietario_nombre"],
        datos.get("codigo_catastral_formato", ""),
        datos.get("expediente_numero", ""),
    )

    template = env.get_template("cedula_catastral.html")
    html_str = template.render(
        d=datos,
        logos=f"file:///{STATIC_DIR}/logos",
        fecha_generacion=date.today().strftime("%d/%m/%Y"),
        qr_code=qr_code,
    )

    output_dir = Path(__file__).resolve().parent / "pdfs_prueba"
    output_dir.mkdir(exist_ok=True)

    nombre_archivo = f"cedula_{datos['expediente_numero'].replace('/', '_')}_{datos['s']}-{datos['ma']}-{datos['pa']}.pdf"
    output_path = output_dir / nombre_archivo

    HTML(string=html_str, base_url=str(TEMPLATES_DIR)).write_pdf(output_path)

    print(f"  [{indice}] {datos['propietario_nombre']:30s} | {datos['codigo_catastral_formato']:30s} | Exp: {datos['expediente_numero']:12s} | {nombre_archivo}")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generar PDFs de prueba con datos realistas de Torbes")
    parser.add_argument("--n", type=int, default=1, help="Cantidad de PDFs a generar")
    args = parser.parse_args()

    try:
        print(f"\nGenerando {args.n} cédula(s) catastral(es) de prueba con datos de Torbes...\n")
        print(f"{'':>4} {'Propietario':30s} | {'Código Catastral':30s} | {'Expediente':12s} | Archivo")
        print("-" * 120)

        for i in range(1, args.n + 1):
            generar_pdf_prueba(i)

        output_dir = Path(__file__).resolve().parent / "pdfs_prueba"
        print(f"\nPDFs generados en: {output_dir}")
        print("Abre los archivos para ver cédulas catastrales con datos realistas de San Josecito, Municipio Torbes.")

    except Exception as e:
        print(f"Error al generar PDF: {e}")
        print("\nSi falta GTK3 runtime, instálalo desde:")
        print("https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases")
