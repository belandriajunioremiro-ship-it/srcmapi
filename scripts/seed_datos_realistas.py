"""
Script para poblar la base de datos con datos realistas del Municipio Torbes,
San Josecito, Estado Táchira, Venezuela.

Genera propietarios e inmuebles con datos verosímiles (nombres, direcciones,
sectores, linderos, valores) basados en la realidad del municipio.

Uso:
    cd srcm-backend
    python -m scripts.seed_datos_realistas

Cada ejecución agrega N nuevos registros (incremental). Los expedientes y
códigos catastrales los genera la BD automáticamente vía triggers.
"""
import sys
import os
import random
import uuid
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from app.db.session import SessionLocal

NOMBRES_MASC = [
    "Carlos", "Miguel", "José", "Antonio", "Luis", "Pedro", "Rafael",
    "Fernando", "Andrés", "Eduardo", "Roberto", "Francisco", "Jorge",
    "Alberto", "Manuel", "Ricardo", "Héctor", "César", "Ángel", "Daniel",
    "Gustavo", "Armando", "Víctor", "Mario", "Jaime", "Óscar", "Ramón",
    "Elías", "Néstor", "Germán",
]

NOMBRES_FEM = [
    "María", "Carmen", "Rosa", "Yolanda", "Ana", "Luisa", "Patricia",
    "Gladys", "Mercedes", "Zuleima", "Yenis", "Yajaira", "Omaira",
    "Norka", "Belkis", "Mireya", "Doris", "Nilda", "Hilda", "Coromoto",
    "Deisy", "Yolibeth", "Zoraida", "Elena", "Isabel", "Teresa",
    "Gabriela", "Andreina", "Daniela", "Carolina",
]

APELLIDOS = [
    "Mora", "Rivas", "Blanco", "Hernández", "Pérez", "García", "Sánchez",
    "Torres", "Ramírez", "González", "Díaz", "Moreno", "Jiménez", "Ruiz",
    "Rojas", "Medina", "Castro", "Vargas", "Arias", "Contreras", "Delgado",
    "Guerrero", "Navarro", "Ortiz", "Pardo", "Quintero", "Salazar",
    "Urbina", "Villanueva", "Zambrano", "Colmenares", "Escalante",
    "Fernández", "Gómez", "López", "Martínez", "Rodríguez", "Suárez",
    "Vivas", "Chacón",
]

SECTORES = [
    {"codigo": "01", "nombre": "Centro San Josecito", "dir_base": "Calle Bolívar", "tipo_via": "asfalto"},
    {"codigo": "02", "nombre": "Vía al Llano", "dir_base": "Vía al Llano", "tipo_via": "asfalto"},
    {"codigo": "03", "nombre": "La Loma", "dir_base": "Carrera La Loma", "tipo_via": "pavimento"},
    {"codigo": "04", "nombre": "El Cerrito", "dir_base": "Calle El Cerrito", "tipo_via": "tierra"},
    {"codigo": "05", "nombre": "La Quebrada", "dir_base": "Calle La Quebrada", "tipo_via": "tierra"},
    {"codigo": "06", "nombre": "Troncal 5 Norte", "dir_base": "Troncal 5, Sector Norte", "tipo_via": "asfalto"},
    {"codigo": "07", "nombre": "El Paraíso", "dir_base": "Calle El Paraíso", "tipo_via": "pavimento"},
    {"codigo": "08", "nombre": "San Rafael", "dir_base": "Calle San Rafael", "tipo_via": "pavimento"},
    {"codigo": "09", "nombre": "Bella Vista", "dir_base": "Calle Bella Vista", "tipo_via": "asfalto"},
    {"codigo": "10", "nombre": "El Progreso", "dir_base": "Calle El Progreso", "tipo_via": "tierra"},
]

LINDEROS_REFERENCIA = [
    "Terreno de la familia Mora", "Calle principal del sector",
    "Quebrada La Loma", "Terreno de la familia Rivas",
    "Camino vecinal", "Carretera Troncal 5",
    "Predio municipal", "Terreno baldío",
    "Casa de la familia Blanco", "Terreno de la familia Hernández",
    "Caño San José", "Límite con finca El Paraíso",
    "Vía al cementerio", "Terreno de la alcaldía",
    "Cancha deportiva", "Escuela Bolivariana",
    "Terreno de la familia García", "Callejón El Progreso",
]

DOCUMENTOS = [
    {"tipo": "Título de Propiedad", "tomo": "I", "folio": None, "protocolo": "01"},
    {"tipo": "Título Supletorio", "tomo": "II", "folio": None, "protocolo": "02"},
    {"tipo": "Compra-Venta", "tomo": "III", "folio": None, "protocolo": "01"},
    {"tipo": "Declaración Sucesoral", "tomo": "I", "folio": None, "protocolo": "03"},
    {"tipo": "Donación", "tomo": "IV", "folio": None, "protocolo": "01"},
]

USOS = ["residencial", "comercial", "mixto", "institucional"]
TIPOS_VIVIENDA = ["casa", "casa", "casa", "quinta", "apartamento", "rancho"]
ESTRUCTURAS_TECHO = ["placa", "placa", "placa", "machimbre", "acerolit"]
ESTRUCTURAS_PAREDES = ["bloque", "bloque", "bloque", "ladrillo", "adobe", "friso_liso"]
PISOS = ["ceramica", "ceramica", "ceramica", "cemento", "terracota"]
CARACTERISTICAS = ["aislada", "aislada", "continua", "pareada"]

COORDENADAS_CENTRO = (-72.228, 7.810)


def generar_cedula():
    n = random.randint(5, 30)
    resto = random.randint(10000, 99999)
    return f"V-{n}.{resto % 100}.{resto // 100}"


def generar_telefono():
    prefijos = ["0412", "0414", "0416", "0424", "0426"]
    return f"{random.choice(prefijos)}-{random.randint(100,999)}-{random.randint(1000,9999)}"


def generar_rif():
    tipos = ["V", "J", "G"]
    t = random.choice(tipos)
    n = random.randint(10, 30)
    resto = random.randint(10000, 99999)
    digito = random.randint(0, 9)
    return f"{t}-{n}.{resto % 100}.{resto // 100}-{digito}"


def generar_poligono_alrededor(lon, lat, tamano_grados=0.0005):
    import random as r
    offsets = [
        (0, 0),
        (tamano_grados * r.uniform(0.7, 1.3), tamano_grados * r.uniform(0.3, 0.7)),
        (tamano_grados * r.uniform(0.5, 1.0), tamano_grados * r.uniform(0.8, 1.4)),
        (-tamano_grados * r.uniform(0.1, 0.4), tamano_grados * r.uniform(0.8, 1.3)),
        (0, 0),
    ]
    coords = [[round(lon + dx, 7), round(lat + dy, 7)] for dx, dy in offsets]
    return {"type": "Polygon", "coordinates": [coords]}


def seed(cantidad_propietarios=10, cantidad_inmuebles=15):
    db = SessionLocal()
    try:
        existentes = db.execute(
            text("SELECT cedula_rif FROM propietarios")
        ).scalars().all()
        cedulas_existentes = set(existentes)

        propietarios_creados = []

        for i in range(cantidad_propietarios):
            intentos = 0
            while intentos < 50:
                es_juridico = random.random() < 0.15
                if es_juridico:
                    cedula = generar_rif()
                    nombre = random.choice(["Constructora", "Inversiones", "Comercializadora", "Desarrollos", "Inmobiliaria"])
                    apellido = random.choice(APELLIDOS) + " C.A."
                else:
                    cedula = generar_cedula()
                    es_masc = random.random() < 0.55
                    nombre = random.choice(NOMBRES_MASC if es_masc else NOMBRES_FEM)
                    apellido = random.choice(APELLIDOS) + " " + random.choice(APELLIDOS)

                if cedula not in cedulas_existentes:
                    break
                intentos += 1
            else:
                continue

            sector = random.choice(SECTORES)
            dir_prop = f"{sector['dir_base']}, #{random.randint(1,200)}, {sector['nombre']}, San Josecito"

            db.execute(text("""
                INSERT INTO propietarios (cedula_rif, nombre, apellido, telefono, email, direccion)
                VALUES (:cedula, :nombre, :apellido, :telefono, :email, :direccion)
                ON CONFLICT (cedula_rif) DO NOTHING
            """), {
                "cedula": cedula,
                "nombre": nombre,
                "apellido": apellido,
                "telefono": generar_telefono(),
                "email": f"{nombre.lower().replace(' ', '')}{random.randint(1,99)}@gmail.com",
                "direccion": dir_prop,
            })

            cedulas_existentes.add(cedula)
            propietarios_creados.append(cedula)
            print(f"  Propietario: {nombre} {apellido} - {cedula}")

        db.commit()
        print(f"\n{len(propietarios_creados)} propietarios creados.\n")

        prop_ids = [row[0] for row in db.execute(text("SELECT id FROM propietarios")).fetchall()]
        if not prop_ids:
            print("No hay propietarios. Abortando inmuebles.")
            return

        inmuebles_creados = 0
        for i in range(cantidad_inmuebles):
            sector = random.choice(SECTORES)
            prop_id = random.choice(prop_ids)

            manzana = f"{random.randint(1,50):03d}"
            parcela = f"{random.randint(1,200):03d}"
            subparcela = random.choice(["000", "000", "000", f"{random.randint(1,10):03d}"])
            nivel = random.choice(["000", "000", "001", "002"])
            unidad = random.choice(["000", "000", "001"])

            dir_inm = f"{sector['dir_base']}, #{random.randint(1,300)}, Sector {sector['nombre']}, San Josecito"

            doc = random.choice(DOCUMENTOS)
            doc_num = f"{random.randint(100,9999)}"
            doc_folio = f"{random.randint(1,500)}"
            doc_fecha = date(random.randint(2005, 2024), random.randint(1, 12), random.randint(1, 28))

            tenencia = random.choices(["propio", "ejido", "arrendado"], weights=[70, 20, 10])[0]

            area_terreno = round(random.uniform(200, 2000), 2)
            area_construccion = round(random.uniform(0, area_terreno * 0.8), 2) if random.random() > 0.15 else None
            area_comercio = round(random.uniform(0, 50), 2) if random.random() < 0.2 else None

            valor_unit_terreno = round(random.uniform(20000, 45000), 2)
            valor_unit_construccion = round(random.uniform(65000, 120000), 2) if area_construccion else None
            valor_unit_comercio = round(random.uniform(80000, 150000), 2) if area_comercio else None

            lind_norte = random.choice(LINDEROS_REFERENCIA)
            lind_sur = random.choice(LINDEROS_REFERENCIA)
            lind_este = random.choice(LINDEROS_REFERENCIA)
            lind_oeste = random.choice(LINDEROS_REFERENCIA)

            mts_norte = round(random.uniform(10, 60), 2)
            mts_sur = round(random.uniform(10, 60), 2)
            mts_este = round(random.uniform(10, 50), 2)
            mts_oeste = round(random.uniform(10, 50), 2)

            tiene_vivienda = area_construccion is not None and area_construccion > 0

            lat_offset = random.uniform(-0.008, 0.008)
            lon_offset = random.uniform(-0.008, 0.008)
            geom = generar_poligono_alrededor(
                COORDENADAS_CENTRO[0] + lon_offset,
                COORDENADAS_CENTRO[1] + lat_offset,
                tamano_grados=random.uniform(0.0003, 0.001)
            )

            uso = random.choices(USOS, weights=[65, 15, 15, 5])[0]
            tipo_viv = random.choice(TIPOS_VIVIENDA) if tiene_vivienda else None
            n_plantas = random.choice([1, 1, 1, 2, 2, 3]) if tiene_vivienda else None
            dormitorios = random.randint(1, 5) if tiene_vivienda else None
            n_banos = random.randint(1, 3) if tiene_vivienda else None

            fecha_emision = date(2024, random.randint(1, 12), random.randint(1, 28))
            fecha_recibo = fecha_emision - timedelta(days=random.randint(0, 30))
            numero_recibo = f"REC-{fecha_emision.year}-{random.randint(1,999):04d}"

            try:
                db.execute(text("""
                    INSERT INTO inmuebles (
                        sector, manzana, parcela, subparcela, nivel, unidad,
                        propietario_id, direccion,
                        documento_tipo, documento_numero, documento_tomo,
                        documento_folio, documento_protocolo, documento_fecha,
                        tenencia,
                        lindero_norte_doc, lindero_norte_mts,
                        lindero_sur_doc, lindero_sur_mts,
                        lindero_este_doc, lindero_este_mts,
                        lindero_oeste_doc, lindero_oeste_mts,
                        lindero_norte_top, lindero_norte_top_mts,
                        lindero_sur_top, lindero_sur_top_mts,
                        lindero_este_top, lindero_este_top_mts,
                        lindero_oeste_top, lindero_oeste_top_mts,
                        aguas_blancas, aguas_servidas, electricidad, contador,
                        existe_vivienda, tipo_vivienda, descripcion_uso,
                        numero_plantas, uso_segun_zonificacion,
                        area_terreno_m2, valor_unit_terreno,
                        area_construccion_m2, valor_unit_construccion,
                        area_comercio_m2, valor_unit_comercio,
                        via_acceso, estructura_techo, estructura_paredes, piso,
                        dormitorios, banos, sala, cocina,
                        ambiente_otro, caracteristica_general,
                        observaciones, geom,
                        fecha_emision, fecha_recibo, numero_recibo,
                        estado_sync
                    ) VALUES (
                        :sector, :manzana, :parcela, :subparcela, :nivel, :unidad,
                        :propietario_id, :direccion,
                        :documento_tipo, :documento_numero, :documento_tomo,
                        :documento_folio, :documento_protocolo, :documento_fecha,
                        :tenencia,
                        :lindero_norte_doc, :lindero_norte_mts,
                        :lindero_sur_doc, :lindero_sur_mts,
                        :lindero_este_doc, :lindero_este_mts,
                        :lindero_oeste_doc, :lindero_oeste_mts,
                        :lindero_norte_top, :lindero_norte_top_mts,
                        :lindero_sur_top, :lindero_sur_top_mts,
                        :lindero_este_top, :lindero_este_top_mts,
                        :lindero_oeste_top, :lindero_oeste_top_mts,
                        :aguas_blancas, :aguas_servidas, :electricidad, :contador,
                        :existe_vivienda, :tipo_vivienda, :descripcion_uso,
                        :numero_plantas, :uso_segun_zonificacion,
                        :area_terreno_m2, :valor_unit_terreno,
                        :area_construccion_m2, :valor_unit_construccion,
                        :area_comercio_m2, :valor_unit_comercio,
                        :via_acceso, :estructura_techo, :estructura_paredes, :piso,
                        :dormitorios, :banos, :sala, :cocina,
                        :ambiente_otro, :caracteristica_general,
                        :observaciones,
                        ST_GeomFromGeoJSON(:geom)::geometry(Polygon, 4326),
                        :fecha_emision, :fecha_recibo, :numero_recibo,
                        'synced'
                    )
                """), {
                    "sector": sector["codigo"],
                    "manzana": manzana,
                    "parcela": parcela,
                    "subparcela": subparcela,
                    "nivel": nivel,
                    "unidad": unidad,
                    "propietario_id": prop_id,
                    "direccion": dir_inm,
                    "documento_tipo": doc["tipo"],
                    "documento_numero": doc_num,
                    "documento_tomo": doc["tomo"],
                    "documento_folio": doc_folio,
                    "documento_protocolo": doc["protocolo"],
                    "documento_fecha": doc_fecha,
                    "tenencia": tenencia,
                    "lindero_norte_doc": lind_norte,
                    "lindero_norte_mts": mts_norte,
                    "lindero_sur_doc": lind_sur,
                    "lindero_sur_mts": mts_sur,
                    "lindero_este_doc": lind_este,
                    "lindero_este_mts": mts_este,
                    "lindero_oeste_doc": lind_oeste,
                    "lindero_oeste_mts": mts_oeste,
                    "lindero_norte_top": f"Vértice GPS Norte ({lind_norte})",
                    "lindero_norte_top_mts": round(mts_norte + random.uniform(-2, 2), 2),
                    "lindero_sur_top": f"Vértice GPS Sur ({lind_sur})",
                    "lindero_sur_top_mts": round(mts_sur + random.uniform(-2, 2), 2),
                    "lindero_este_top": f"Vértice GPS Este ({lind_este})",
                    "lindero_este_top_mts": round(mts_este + random.uniform(-2, 2), 2),
                    "lindero_oeste_top": f"Vértice GPS Oeste ({lind_oeste})",
                    "lindero_oeste_top_mts": round(mts_oeste + random.uniform(-2, 2), 2),
                    "aguas_blancas": random.random() > 0.25,
                    "aguas_servidas": random.random() > 0.3,
                    "electricidad": random.random() > 0.15,
                    "contador": random.random() > 0.4,
                    "existe_vivienda": tiene_vivienda,
                    "tipo_vivienda": tipo_viv,
                    "descripcion_uso": uso,
                    "numero_plantas": n_plantas,
                    "uso_segun_zonificacion": uso,
                    "area_terreno_m2": area_terreno,
                    "valor_unit_terreno": valor_unit_terreno,
                    "area_construccion_m2": area_construccion,
                    "valor_unit_construccion": valor_unit_construccion,
                    "area_comercio_m2": area_comercio,
                    "valor_unit_comercio": valor_unit_comercio,
                    "via_acceso": sector["tipo_via"],
                    "estructura_techo": random.choice(ESTRUCTURAS_TECHO) if tiene_vivienda else None,
                    "estructura_paredes": random.choice(ESTRUCTURAS_PAREDES) if tiene_vivienda else None,
                    "piso": random.choice(PISOS) if tiene_vivienda else None,
                    "dormitorios": dormitorios,
                    "banos": n_banos,
                    "sala": tiene_vivienda,
                    "cocina": tiene_vivienda,
                    "ambiente_otro": random.choice(["Comedor", "Sala de estar", "Terraza", "Estudio", None]),
                    "caracteristica_general": random.choice(CARACTERISTICAS) if tiene_vivienda else None,
                    "observaciones": random.choice([
                        None,
                        "Inmueble en buen estado de conservación",
                        "Requiere mantenimiento en la cubierta",
                        "Ampliación en proceso de legalización",
                        "Predio con uso mixto residencial-comercial",
                        "Terreno con pendiente moderada",
                        "Colinda con quebrada seasonal",
                        "Vivienda de interés social",
                    ]),
                    "geom": __import__("json").dumps(geom),
                    "fecha_emision": fecha_emision,
                    "fecha_recibo": fecha_recibo,
                    "numero_recibo": numero_recibo,
                })

                inmuebles_creados += 1
                print(f"  Inmueble: Sector {sector['codigo']} ({sector['nombre']}), Mz:{manzana} Pc:{parcela} - {dir_inm}")

            except Exception as exc:
                db.rollback()
                print(f"  [ERROR] Inmueble sector {sector['codigo']}, Mz:{manzana} Pc:{parcela}: {exc}")
                continue

        db.commit()
        print(f"\n{inmuebles_creados} inmuebles creados exitosamente.")
        print("Los códigos catastrales, expedientes y vigencias los generó la BD automáticamente.")

        total_prop = db.execute(text("SELECT count(*) FROM propietarios")).scalar()
        total_inm = db.execute(text("SELECT count(*) FROM inmuebles")).scalar()
        print(f"\nTotal en BD: {total_prop} propietarios, {total_inm} inmuebles")

    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Poblar BD con datos realistas de Torbes")
    parser.add_argument("--propietarios", type=int, default=10, help="Cantidad de propietarios a crear")
    parser.add_argument("--inmuebles", type=int, default=15, help="Cantidad de inmuebles a crear")
    args = parser.parse_args()

    print(f"Generando {args.propietarios} propietarios y {args.inmuebles} inmuebles...")
    seed(args.propietarios, args.inmuebles)
