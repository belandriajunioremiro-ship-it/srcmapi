-- ============================================================
-- SRCM — Sistema de Registro Catastral Municipal
-- Municipio Torbes, Estado Táchira, Venezuela
-- Base de datos: Supabase (PostgreSQL + PostGIS)
-- v2.5 COMPLETA — Unificada (idempotente: re-ejecutable sin perder datos)
--
-- Bloques del código (23 caracteres, sin separadores):
--   E  (2)  Entidad Federal      -> Táchira = 20 ✅ CONFIRMADO
--   M  (2)  Municipio            -> Torbes = 27 ✅ CONFIRMADO (INE/IGVSB)
--   P  (2)  Parroquia            -> San Josecito = 01 ✅ CONFIRMADO
--   S  (2)  Sector / ámbito catastral
--   Ma (3)  Manzana
--   Pa (3)  Parcela
--   SP (3)  Subparcela
--   N  (3)  Nivel
--   U  (3)  Unidad
--
-- DATOS OFICIALES CONFIRMADOS:
--   ✅ Estado:      Táchira (E = 20)
--   ✅ Municipio:   Torbes (M = 27) - INE/IGVSB/Gaceta Municipal
--   ✅ Parroquia:   San Josecito (P = 01) - Única parroquia del municipio
--   ✅ Huso UTM:    18N (EPSG:2201 - REGVEN)
--
-- CAMBIOS v2.5:
--   ✅ Integración completa de la migración v2.5 de cédula catastral
--   ✅ Campos nuevos en INMUEBLES: fecha_recibo, numero_recibo
--   ✅ Campos institucionales en CONFIGURACION_CATASTRAL para PDF
--   ✅ Vista v_pdf_cedula_catastral actualizada con todos los campos oficiales
--
-- CAMBIOS v2.4:
--   ✅ FIX: DROP VIEW IF EXISTS antes de crear las vistas
--   ✅ FIX: idx_inm_codigo_prefix usa bpchar_pattern_ops
--
-- CAMBIOS v2.3:
--   ✅ Validador de código corregido (23 dígitos, no 21)
--   ✅ Vista v_pdf_cedula_catastral: N y U extraen 3 caracteres
--   ✅ handle_new_user robusto (no tumba el signup de Supabase)
--   ✅ Vigencia se recalcula al editar fecha_emision
--   ✅ mapa_catastral() acepta bbox (el mapa solo carga lo visible)
--   ✅ Índices trgm separados para nombre/apellido/cédula
--   ✅ Índices para paginación/orden del backend
--   ✅ Trigger updated_at en configuracion_catastral
-- ============================================================


-- ============================================================
-- 1. EXTENSIONES
-- ============================================================
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- búsqueda parcial (ILIKE '%...%')


-- ============================================================
-- 2. CONFIGURACIÓN CATASTRAL (fila única)
-- ============================================================
CREATE TABLE IF NOT EXISTS configuracion_catastral (
  id                      smallint NOT NULL DEFAULT 1,
  codigo_estado           char(2)  NOT NULL DEFAULT '20',   -- Táchira (CONFIRMADO)
  codigo_municipio        char(2)  NOT NULL,                -- Torbes: 27 CONFIRMADO
  codigo_parroquia        char(2)  NOT NULL DEFAULT '01',   -- San Josecito (CONFIRMADO)
  nombre_estado           text     NOT NULL DEFAULT 'Táchira',
  nombre_municipio        text     NOT NULL DEFAULT 'Torbes',
  nombre_parroquia        text     NOT NULL DEFAULT 'San Josecito',
  ordenanza_referencia    text,
  srid_utm                integer  NOT NULL DEFAULT 2201,   -- REGVEN / UTM 18N (CONFIRMADO)
  valor_m2_terreno        numeric(15,2) NOT NULL DEFAULT 24500.00,
  valor_m2_construccion   numeric(15,2) NOT NULL DEFAULT 85400.00,
  valor_m2_comercio       numeric(15,2) NOT NULL DEFAULT 95000.00,
  alicuota_impuesto       numeric(6,5)  NOT NULL DEFAULT 0.00300,
  vigencia_cedula_meses   integer  NOT NULL DEFAULT 12,
  updated_at              timestamptz NOT NULL DEFAULT now(),

  -- Campos institucionales para cédula catastral (v2.5)
  rif_alcaldia               text NOT NULL DEFAULT 'G-20000395-2',
  direccion_institucional     text NOT NULL DEFAULT 'Municipio Torbes, San Josecito, Vía al Llano, Troncal 5',
  nombre_maxima_autoridad     text NOT NULL DEFAULT 'Dra. Charly Rojas',
  cargo_maxima_autoridad      text NOT NULL DEFAULT 'Alcaldesa Bolivariana y Primera Autoridad Civil del Municipio Torbes, Estado Táchira',
  texto_acta_maxima_autoridad text NOT NULL DEFAULT 'Acta de Sesión Solemne N° 78 de Fecha 02 de Agosto de 2025',
  nombre_director_catastro    text NOT NULL DEFAULT '',
  cargo_director_catastro     text NOT NULL DEFAULT 'Directora de Urbanismo y Catastro',
  texto_resolucion_director   text NOT NULL DEFAULT '',
  notas_legales               text NOT NULL DEFAULT
$$1. Cédula Catastral que se expide a solicitud departe interesada para fines legales.
2. Los precios por m² del terreno y de la construcción están sujetos a cambios.
3. Si modifica dirección de acuerdo al nuevo ordenamiento municipal en municipios Torbes y sus parroquias.
4. Un (01) año de vigencia desde la fecha de expedición cumpliendo con la ORDENANZA SOBRE CATASTRO.
5. NO AUTORIZA permiso para construir, ni para Variables Urbanas. No acredita propiedad.$$,

  CONSTRAINT configuracion_catastral_pkey PRIMARY KEY (id),
  CONSTRAINT configuracion_catastral_singleton CHECK (id = 1)
);

INSERT INTO configuracion_catastral (
  codigo_estado, codigo_municipio, codigo_parroquia,
  nombre_estado, nombre_municipio, nombre_parroquia,
  srid_utm, ordenanza_referencia
) VALUES (
  '20', '27', '01',
  'Táchira', 'Torbes', 'San Josecito',
  2201, 'Gaceta Municipal de Torbes - Ordenanza de Catastro vigente'
)
ON CONFLICT (id) DO NOTHING;


-- ============================================================
-- 3. CONFIGURACIÓN DEL SISTEMA (Parámetros Globales)
-- ============================================================
-- ⚠️ Mantener SINCRONIZADA con configuracion_catastral:
--    el generador de código usa configuracion_catastral y el
--    validador usa configuracion_sistema. Si difieren, todo
--    INSERT de inmueble fallará.
CREATE TABLE IF NOT EXISTS configuracion_sistema (
  id                integer PRIMARY KEY DEFAULT 1,
  estado_codigo     varchar(2) NOT NULL DEFAULT '20',
  municipio_codigo  varchar(2) NOT NULL DEFAULT '27',
  parroquia_codigo  varchar(2) NOT NULL DEFAULT '01',
  nombre_municipio  text NOT NULL DEFAULT 'Municipio Torbes',

  CONSTRAINT un_solo_registro CHECK (id = 1)
);

INSERT INTO configuracion_sistema
  (id, estado_codigo, municipio_codigo, parroquia_codigo, nombre_municipio)
VALUES
  (1, '20', '27', '01', 'Municipio Torbes')
ON CONFLICT (id) DO NOTHING;


-- ============================================================
-- 4. SECUENCIA para expedientes
-- ============================================================
-- NOTA: el consecutivo NO reinicia cada año (queda 000012/2026,
-- 000013/2027...). Si se requiere reinicio anual, gestionarlo
-- desde el backend al inicio de cada año.
CREATE SEQUENCE IF NOT EXISTS seq_expediente START 1;


-- ============================================================
-- 5. USUARIOS (2 roles: administrador, inspector)
-- ============================================================
CREATE TABLE IF NOT EXISTS usuarios (
  id          uuid NOT NULL,
  cedula      text NOT NULL,
  nombre      text NOT NULL,
  apellido    text NOT NULL,
  rol         text NOT NULL DEFAULT 'inspector',
  activo      boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT usuarios_pkey PRIMARY KEY (id),
  CONSTRAINT usuarios_cedula_key UNIQUE (cedula),
  CONSTRAINT usuarios_rol_check CHECK (rol IN ('administrador', 'inspector'))
);


-- ============================================================
-- 6. PROPIETARIOS
-- ============================================================
CREATE TABLE IF NOT EXISTS propietarios (
  id          uuid NOT NULL DEFAULT gen_random_uuid(),
  cedula_rif  text NOT NULL,
  nombre      text NOT NULL,
  apellido    text NOT NULL,
  telefono    text,
  email       text,
  direccion   text,
  created_at  timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT propietarios_pkey PRIMARY KEY (id),
  CONSTRAINT propietarios_cedula_rif_key UNIQUE (cedula_rif)
);


-- ============================================================
-- 7. INMUEBLES
-- ============================================================
CREATE TABLE IF NOT EXISTS inmuebles (
  id                        uuid NOT NULL DEFAULT gen_random_uuid(),

  -- Código catastral (bloques individuales + código completo)
  sector                    char(2) NOT NULL,
  manzana                   char(3) NOT NULL,
  parcela                   char(3) NOT NULL,
  subparcela                char(3) NOT NULL DEFAULT '000',
  nivel                     char(3) NOT NULL DEFAULT '000',
  unidad                    char(3) NOT NULL DEFAULT '000',
  codigo_catastral          char(23),                  -- generado por trigger
  expediente_numero         text,                      -- "N°.../año" (cédula)

  -- Propietario / administrador
  propietario_id            uuid REFERENCES propietarios(id) ON DELETE RESTRICT,
  direccion                 text NOT NULL,

  -- Documento de propiedad
  documento_tipo             text,
  documento_numero           text,
  documento_tomo             text,
  documento_folio            text,
  documento_protocolo        text,
  documento_fecha            date,

  -- Tenencia
  tenencia                    text NOT NULL DEFAULT 'propio'
                               CHECK (tenencia IN ('propio', 'ejido', 'arrendado')),
  contrato_arrendamiento_num   text,
  contrato_arrendamiento_fecha date,

  -- Linderos según documento (mts)
  lindero_norte_doc            text,
  lindero_norte_mts            numeric(10,2),
  lindero_sur_doc              text,
  lindero_sur_mts              numeric(10,2),
  lindero_este_doc             text,
  lindero_este_mts             numeric(10,2),
  lindero_oeste_doc            text,
  lindero_oeste_mts             numeric(10,2),

  -- Linderos según levantamiento topográfico / GPS (mts)
  lindero_norte_top            text,
  lindero_norte_top_mts        numeric(10,2),
  lindero_sur_top              text,
  lindero_sur_top_mts          numeric(10,2),
  lindero_este_top             text,
  lindero_este_top_mts         numeric(10,2),
  lindero_oeste_top            text,
  lindero_oeste_top_mts        numeric(10,2),

  -- Servicio de factibilidad
  aguas_blancas               boolean NOT NULL DEFAULT false,
  aguas_servidas              boolean NOT NULL DEFAULT false,
  electricidad                boolean NOT NULL DEFAULT false,
  contador                    boolean NOT NULL DEFAULT false,

  -- Vivienda / uso
  existe_vivienda              boolean NOT NULL DEFAULT false,
  tipo_vivienda                text,
  descripcion_uso              text NOT NULL DEFAULT 'residencial',
  numero_plantas               integer,
  uso_segun_zonificacion       text,

  -- Áreas y valores
  area_terreno_m2                   numeric(12,2),
  valor_unit_terreno                numeric(15,2),
  area_construccion_m2              numeric(12,2),
  valor_unit_construccion           numeric(15,2),
  area_comercio_m2                  numeric(12,2),
  valor_unit_comercio               numeric(15,2),

  valor_terreno                     numeric(18,2) GENERATED ALWAYS AS
      (COALESCE(area_terreno_m2, 0) * COALESCE(valor_unit_terreno, 0)) STORED,
  valor_construccion                numeric(18,2) GENERATED ALWAYS AS
      (COALESCE(area_construccion_m2, 0) * COALESCE(valor_unit_construccion, 0)) STORED,
  valor_comercio                    numeric(18,2) GENERATED ALWAYS AS
      (COALESCE(area_comercio_m2, 0) * COALESCE(valor_unit_comercio, 0)) STORED,
  valor_catastral_total             numeric(18,2) GENERATED ALWAYS AS
      (COALESCE(area_terreno_m2, 0) * COALESCE(valor_unit_terreno, 0)
       + COALESCE(area_construccion_m2, 0) * COALESCE(valor_unit_construccion, 0)
       + COALESCE(area_comercio_m2, 0) * COALESCE(valor_unit_comercio, 0)) STORED,

  -- Características del inmueble
  via_acceso                    text CHECK (via_acceso IN ('asfalto', 'pavimento', 'tierra', 'otro')),
  estructura_techo              text CHECK (estructura_techo IN ('placa', 'machimbre', 'acerolit', 'asbesto', 'otro')),
  estructura_paredes            text CHECK (estructura_paredes IN ('adobe', 'ladrillo', 'bloque', 'friso_liso', 'otro')),
  piso                          text CHECK (piso IN ('ceramica', 'cemento', 'terracota', 'otro')),
  dormitorios                   integer,
  banos                         integer,
  sala                          boolean NOT NULL DEFAULT false,
  cocina                        boolean NOT NULL DEFAULT false,
  ambiente_otro                 text,
  caracteristica_general        text CHECK (caracteristica_general IN
                                 ('aislada', 'continua', 'pareada', 'condominio', 'otro')),

  observaciones                 text,

  -- Geoespacial (marcado en mapa, estilo Google Maps)
  geom                          geometry(Polygon, 4326) NOT NULL,
  utm_norte                     numeric(12,2),
  utm_este                      numeric(12,2),
  superficie_gis_m2             numeric(12,2),
  perimetro_gis_m               numeric(12,2),

  registrado_por                uuid REFERENCES auth.users(id),
  estado_sync                   text NOT NULL DEFAULT 'synced'
                                 CHECK (estado_sync IN ('synced', 'pendiente', 'error')),
  fecha_emision                 date NOT NULL DEFAULT CURRENT_DATE,
  vigente_hasta                 date,

  -- Campos para cédula catastral (v2.5)
  fecha_recibo                  date NOT NULL DEFAULT CURRENT_DATE,
  numero_recibo                 text,

  created_at                    timestamptz NOT NULL DEFAULT now(),
  updated_at                    timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT inmuebles_pkey PRIMARY KEY (id),
  CONSTRAINT inmuebles_codigo_catastral_key UNIQUE (codigo_catastral),
  CONSTRAINT inmuebles_sector_manzana_parcela_key UNIQUE (sector, manzana, parcela, subparcela, nivel, unidad)
);


-- ============================================================
-- 8. HITOS PREDIALES (vértices del polígono / linderos GPS)
-- ============================================================
CREATE TABLE IF NOT EXISTS hitos_prediales (
  id              uuid NOT NULL DEFAULT gen_random_uuid(),
  inmueble_id     uuid NOT NULL REFERENCES inmuebles(id) ON DELETE CASCADE,
  indice_vertice  integer NOT NULL,
  descripcion     text,
  lat             numeric(10,7) NOT NULL,
  lon             numeric(10,7) NOT NULL,
  utm_norte       numeric(12,2),
  utm_este        numeric(12,2),
  foto_url        text,
  created_at      timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT hitos_prediales_pkey PRIMARY KEY (id),
  CONSTRAINT hitos_prediales_inmueble_vertice_key UNIQUE (inmueble_id, indice_vertice)
);


-- ============================================================
-- 9. FOTOS DEL INMUEBLE
-- ============================================================
CREATE TABLE IF NOT EXISTS fotos_inmueble (
  id           uuid NOT NULL DEFAULT gen_random_uuid(),
  inmueble_id  uuid NOT NULL REFERENCES inmuebles(id) ON DELETE CASCADE,
  url          text NOT NULL,
  descripcion  text,
  created_at   timestamptz NOT NULL DEFAULT now(),

  CONSTRAINT fotos_inmueble_pkey PRIMARY KEY (id)
);


-- ============================================================
-- 10. ÍNDICES
-- ============================================================
-- Espaciales y relacionales
CREATE INDEX IF NOT EXISTS idx_inmuebles_geom        ON inmuebles USING gist (geom);
CREATE INDEX IF NOT EXISTS idx_inmuebles_sector      ON inmuebles USING btree (sector);
CREATE INDEX IF NOT EXISTS idx_inmuebles_propietario ON inmuebles USING btree (propietario_id);
CREATE INDEX IF NOT EXISTS idx_hitos_inmueble        ON hitos_prediales USING btree (inmueble_id);
CREATE INDEX IF NOT EXISTS idx_fotos_inmueble        ON fotos_inmueble USING btree (inmueble_id);

-- Paginación / filtros / búsqueda / orden (backend)
CREATE INDEX IF NOT EXISTS idx_inm_valor_total   ON inmuebles USING btree (valor_catastral_total);
CREATE INDEX IF NOT EXISTS idx_inm_fecha_emision ON inmuebles USING btree (fecha_emision);
CREATE INDEX IF NOT EXISTS idx_inm_expediente    ON inmuebles USING btree (expediente_numero);
-- Búsqueda por prefijo de código catastral (LIKE '20112701%')
-- ✅ FIX v2.3: la columna es char(23) → usar bpchar_pattern_ops
--    (text_pattern_ops no acepta el tipo character → error 42804)
CREATE INDEX IF NOT EXISTS idx_inm_codigo_prefix ON inmuebles (codigo_catastral bpchar_pattern_ops);
-- Búsqueda parcial de dirección (ILIKE '%los almendros%')
CREATE INDEX IF NOT EXISTS idx_inm_direccion_trgm ON inmuebles USING gin (direccion gin_trgm_ops);
-- Búsqueda parcial de propietarios (índices SEPARADOS: cada uno
-- sirve a su respectivo ILIKE en las queries OR del backend)
CREATE INDEX IF NOT EXISTS idx_prop_nombre_trgm   ON propietarios USING gin (nombre     gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_prop_apellido_trgm ON propietarios USING gin (apellido   gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_prop_cedula_trgm   ON propietarios USING gin (cedula_rif gin_trgm_ops);
-- Búsqueda de nombre completo (solo se usa si la query compara
-- contra la expresión exacta nombre || ' ' || apellido)
CREATE INDEX IF NOT EXISTS idx_prop_nombre_completo_trgm ON propietarios
  USING gin ((nombre || ' ' || apellido) gin_trgm_ops);
-- Cola de sincronización offline (solo filas pendientes/error)
CREATE INDEX IF NOT EXISTS idx_inm_sync_pendiente ON inmuebles (created_at)
  WHERE estado_sync <> 'synced';


-- ============================================================
-- 11. FUNCIONES
-- ============================================================

-- ------------------------------------------------------------
-- 11.1 Actualiza updated_at automáticamente
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
 $$;


-- ------------------------------------------------------------
-- 11.2 Genera el código catastral completo de 23 caracteres
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION generar_codigo_catastral(
  p_sector      char(2),
  p_manzana     char(3),
  p_parcela     char(3),
  p_subparcela  char(3) DEFAULT '000',
  p_nivel       char(3) DEFAULT '000',
  p_unidad      char(3) DEFAULT '000'
) RETURNS char(23)
LANGUAGE plpgsql AS $$ DECLARE
  v_cfg configuracion_catastral%ROWTYPE;
BEGIN
  SELECT * INTO v_cfg FROM configuracion_catastral WHERE id = 1;
  RETURN v_cfg.codigo_estado || v_cfg.codigo_municipio || v_cfg.codigo_parroquia
         || p_sector || p_manzana || p_parcela || p_subparcela || p_nivel || p_unidad;
END;
 $$;


-- ------------------------------------------------------------
-- 11.3 Formatea el código catastral con guiones (solo presentación)
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION formatear_codigo_catastral(p_codigo char(23))
RETURNS text LANGUAGE sql IMMUTABLE AS $$   SELECT substring(p_codigo from 1 for 2) || '-' || substring(p_codigo from 3 for 2) || '-'
      || substring(p_codigo from 5 for 2) || '-' || substring(p_codigo from 7 for 2) || '-'
      || substring(p_codigo from 9 for 3) || '-' || substring(p_codigo from 12 for 3) || '-'
      || substring(p_codigo from 15 for 3) || '-' || substring(p_codigo from 18 for 3) || '-'
      || substring(p_codigo from 21 for 3);
 $$;


-- ------------------------------------------------------------
-- 11.4 Validar el Código Catastral (Dinámico)
-- ✅ FIX CRÍTICO: validaba 21 dígitos; el formato
--    E(2)+M(2)+P(2)+S(2)+Ma(3)+Pa(3)+SP(3)+N(3)+U(3) = 23.
--    Esto rechazaba TODOS los INSERT/UPDATE de inmuebles.
-- ✅ Este trigger corre DESPUÉS del generador (los BEFORE
--    disparan en orden alfabético de nombre: ...antes_guardar (a)
--    → ...prevenir_solape (p) → ...validar_codigo (v)). NO
--    renombrar los triggers de forma que altere ese orden.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION validar_codigo_catastral_dinamico()
RETURNS trigger AS $$ DECLARE
    prefijo_esperado varchar(6);
BEGIN
    SELECT estado_codigo || municipio_codigo || parroquia_codigo
      INTO prefijo_esperado
      FROM public.configuracion_sistema WHERE id = 1;

    IF NOT (NEW.codigo_catastral LIKE prefijo_esperado || '%') THEN
        RAISE EXCEPTION 'Código inválido. Para este municipio, el código debe comenzar estrictamente por: %', prefijo_esperado;
    END IF;

    IF length(NEW.codigo_catastral) != 23 OR NEW.codigo_catastral ~ '[^0-9]' THEN
        RAISE EXCEPTION 'El código catastral debe tener exactamente 23 dígitos numéricos.';
    END IF;

    RETURN NEW;
END;
 $$ LANGUAGE plpgsql;


-- ------------------------------------------------------------
-- 11.5 Trigger: calcula código catastral, expediente, vigencia,
--      área/perímetro GIS y coordenadas UTM antes de insertar
--      o actualizar un inmueble.
-- ✅ FIX: la vigencia se recalcula también cuando cambia
--    fecha_emision en un UPDATE (antes quedaba desactualizada).
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION antes_de_guardar_inmueble()
RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE
  v_cfg configuracion_catastral%ROWTYPE;
  v_centroide geometry;
  v_utm geometry;
BEGIN
  SELECT * INTO v_cfg FROM configuracion_catastral WHERE id = 1;

  NEW.codigo_catastral := generar_codigo_catastral(
    NEW.sector, NEW.manzana, NEW.parcela, NEW.subparcela, NEW.nivel, NEW.unidad
  );

  IF NEW.expediente_numero IS NULL THEN
    NEW.expediente_numero := lpad(nextval('seq_expediente')::text, 6, '0')
      || '/' || extract(year FROM now())::text;
  END IF;

  IF TG_OP = 'INSERT'
     OR NEW.vigente_hasta IS NULL
     OR (TG_OP = 'UPDATE' AND NEW.fecha_emision IS DISTINCT FROM OLD.fecha_emision)
  THEN
    NEW.vigente_hasta := NEW.fecha_emision
      + make_interval(months => v_cfg.vigencia_cedula_meses);
  END IF;

  -- Geometría: superficie, perímetro (geography, en m2/m) y UTM
  NEW.superficie_gis_m2 := round(ST_Area(NEW.geom::geography)::numeric, 2);
  NEW.perimetro_gis_m   := round(ST_Perimeter(NEW.geom::geography)::numeric, 2);

  v_centroide := ST_Centroid(NEW.geom);
  v_utm := ST_Transform(v_centroide, v_cfg.srid_utm);
  NEW.utm_este  := round(ST_X(v_utm)::numeric, 2);
  NEW.utm_norte := round(ST_Y(v_utm)::numeric, 2);

  RETURN NEW;
END;
 $$;


-- ------------------------------------------------------------
-- 11.6 Trigger: calcula UTM (REGVEN) para cada vértice/hito
--      predial capturado en campo, vía PostGIS ST_Transform.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION antes_de_guardar_hito()
RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE
  v_srid integer;
  v_utm  geometry;
BEGIN
  SELECT srid_utm INTO v_srid FROM configuracion_catastral WHERE id = 1;
  v_utm := ST_Transform(ST_SetSRID(ST_MakePoint(NEW.lon, NEW.lat), 4326), v_srid);
  NEW.utm_este  := round(ST_X(v_utm)::numeric, 2);
  NEW.utm_norte := round(ST_Y(v_utm)::numeric, 2);
  RETURN NEW;
END;
 $$;


-- ------------------------------------------------------------
-- 11.7 Impide que dos predios se solapen (más de 1 m²)
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION prevenir_solape_predios()
RETURNS trigger LANGUAGE plpgsql AS $$ DECLARE
  v_conflicto record;
BEGIN
  SELECT codigo_catastral,
         ST_Area(ST_Intersection(NEW.geom, geom)::geography) AS area_solape
  INTO v_conflicto
  FROM inmuebles
  WHERE id <> COALESCE(NEW.id, gen_random_uuid())
    AND ST_Intersects(geom, NEW.geom)
  ORDER BY area_solape DESC
  LIMIT 1;

  IF v_conflicto.area_solape IS NOT NULL AND v_conflicto.area_solape > 1 THEN
    RAISE EXCEPTION 'solape_topologico: el polígono se superpone % m² con el predio %',
      round(v_conflicto.area_solape::numeric, 1), v_conflicto.codigo_catastral;
  END IF;

  RETURN NEW;
END;
 $$;


-- ------------------------------------------------------------
-- 11.8 Crea el perfil en "usuarios" al registrarse en Supabase Auth
-- ✅ FIX ROBUSTO:
--    - cédula provisional única (TMP-xxxx) si no vino en metadata,
--      para no chocar con el UNIQUE y tumbar el signup completo
--    - ON CONFLICT sin target: cubre choque por id Y por cédula
--    - bloque EXCEPTION: un error de perfil NUNCA debe impedir
--      que el usuario se cree en Supabase Auth
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER AS $$ BEGIN
  INSERT INTO usuarios (id, nombre, apellido, cedula, rol)
  VALUES (
    NEW.id,
    COALESCE(NULLIF(NEW.raw_user_meta_data->>'nombre',   ''), 'Sin nombre'),
    COALESCE(NULLIF(NEW.raw_user_meta_data->>'apellido', ''), 'Sin apellido'),
    COALESCE(NULLIF(NEW.raw_user_meta_data->>'cedula', ''),
             'TMP-' || left(NEW.id::text, 8)),
    COALESCE(NULLIF(NEW.raw_user_meta_data->>'rol', ''), 'inspector')
  )
  ON CONFLICT DO NOTHING;
  RETURN NEW;
EXCEPTION WHEN OTHERS THEN
  RETURN NEW;
END;
 $$;


-- ------------------------------------------------------------
-- 11.9 Añade el rol al JWT (usado por las políticas RLS)
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION custom_access_token_hook(event jsonb)
RETURNS jsonb LANGUAGE plpgsql AS $$ DECLARE
  claims jsonb;
  v_rol  text;
BEGIN
  SELECT rol INTO v_rol FROM usuarios WHERE id = (event->>'user_id')::uuid;

  claims := event->'claims';
  claims := jsonb_set(claims, '{role}', to_jsonb(COALESCE(v_rol, 'inspector')));
  event := jsonb_set(event, '{claims}', claims);
  RETURN event;
END;
 $$;


-- ------------------------------------------------------------
-- 11.10 GeoJSON del mapa
-- ✅ NUEVO: acepta bbox opcional (minLon, minLat, maxLon, maxLat)
--    para que el mapa solo cargue los predios visibles en pantalla.
--    Con NULLs carga todo (retrocompatible con la llamada sin args).
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION mapa_catastral(
  p_minlon float DEFAULT NULL,
  p_minlat float DEFAULT NULL,
  p_maxlon float DEFAULT NULL,
  p_maxlat float DEFAULT NULL
)
RETURNS jsonb LANGUAGE sql STABLE AS $$   SELECT jsonb_build_object(
    'type', 'FeatureCollection',
    'features', COALESCE(jsonb_agg(jsonb_build_object(
      'type', 'Feature',
      'geometry', ST_AsGeoJSON(geom)::jsonb,
      'properties', jsonb_build_object(
        'id', id,
        'codigo', formatear_codigo_catastral(codigo_catastral),
        'direccion', direccion,
        'sector', sector,
        'superficie', superficie_gis_m2
      )
    )), '[]'::jsonb)
  )
  FROM inmuebles
  WHERE (p_minlon IS NULL
         OR geom && ST_MakeEnvelope(p_minlon, p_minlat, p_maxlon, p_maxlat, 4326));
 $$;


-- ------------------------------------------------------------
-- 11.11 Estadísticas generales del catastro
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION estadisticas_catastro()
RETURNS jsonb LANGUAGE sql STABLE AS $$   SELECT jsonb_build_object(
    'total_predios', count(*),
    'superficie_total_m2', COALESCE(sum(superficie_gis_m2), 0),
    'valor_catastral_total', COALESCE(sum(valor_catastral_total), 0),
    'predios_con_vivienda', count(*) FILTER (WHERE existe_vivienda = true),
    'valor_promedio_por_predio', COALESCE(avg(valor_catastral_total), 0)
  )
  FROM inmuebles;
 $$;


-- ------------------------------------------------------------
-- 11.12 Predios agrupados por sector
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION predios_por_sector()
RETURNS jsonb LANGUAGE sql STABLE AS $$
  SELECT jsonb_object_agg(sector, datos_sector)
  FROM (
    SELECT
      sector,
      jsonb_build_object(
        'total_predios', count(*),
        'superficie_total_m2', COALESCE(sum(superficie_gis_m2), 0),
        'valor_catastral_total', COALESCE(sum(valor_catastral_total), 0)
      ) as datos_sector
    FROM inmuebles
    GROUP BY sector
    ORDER BY sector
  ) subquery;
 $$;


-- ------------------------------------------------------------
-- 11.13 Detecta solapamientos para un polígono dado (antes de insertar)
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION detectar_solapamientos(p_geom geometry(Polygon, 4326))
RETURNS jsonb LANGUAGE sql STABLE AS $$   SELECT jsonb_agg(jsonb_build_object(
    'codigo_catastral', codigo_catastral,
    'direccion', direccion,
    'area_solape_m2', round(ST_Area(ST_Intersection(geom, p_geom)::geography)::numeric, 2)
  ))
  FROM inmuebles
  WHERE ST_Intersects(geom, p_geom)
    AND ST_Area(ST_Intersection(geom, p_geom)::geography) > 1;
 $$;


-- ============================================================
-- 12. TRIGGERS
-- ============================================================

-- updated_at automático en todas las tablas con timestamp
CREATE TRIGGER trg_usuarios_updated_at
  BEFORE UPDATE ON usuarios
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_propietarios_updated_at
  BEFORE UPDATE ON propietarios
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_configuracion_catastral_updated_at
  BEFORE UPDATE ON configuracion_catastral
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_inmuebles_updated_at
  BEFORE UPDATE ON inmuebles
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Generación de código catastral, expediente, vigencia y cálculos GIS
CREATE TRIGGER trg_inmuebles_antes_guardar
  BEFORE INSERT OR UPDATE ON inmuebles
  FOR EACH ROW EXECUTE FUNCTION antes_de_guardar_inmueble();

-- Validación del código catastral (después de generarlo)
CREATE TRIGGER trg_inmuebles_validar_codigo
  BEFORE INSERT OR UPDATE ON inmuebles
  FOR EACH ROW EXECUTE FUNCTION validar_codigo_catastral_dinamico();

-- Prevención de solapamientos
CREATE TRIGGER trg_inmuebles_prevenir_solape
  BEFORE INSERT OR UPDATE ON inmuebles
  FOR EACH ROW EXECUTE FUNCTION prevenir_solape_predios();

-- Cálculo de UTM para hitos prediales
CREATE TRIGGER trg_hitos_antes_guardar
  BEFORE INSERT OR UPDATE ON hitos_prediales
  FOR EACH ROW EXECUTE FUNCTION antes_de_guardar_hito();

-- Creación de perfil de usuario al registrarse en Supabase Auth
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();


-- ============================================================
-- 13. HOOKS DE SUPABASE AUTH
-- ============================================================
-- Este hook inyecta el rol en el JWT (se configura en Supabase:
-- Authentication → Hooks → Custom Access Token Hook)
-- La función custom_access_token_hook ya está definida arriba (11.9)


-- ============================================================
-- 14. VISTAS
-- ============================================================
-- ⚠️ IMPORTANTE: DROP VIEW IF EXISTS antes de CREATE VIEW.
--    PostgreSQL no permite ALTER VIEW; insertar/renombrar/reordenar columnas exige recrear la vista.
--    Nota: si algún objeto llegara a depender de estas vistas,
--    el DROP fallará (avisa antes de usar CASCADE).
-- ============================================================

-- ------------------------------------------------------------
-- 14.1 Vista completa para la Cédula Catastral (PDF)
-- ------------------------------------------------------------
DROP VIEW IF EXISTS public.v_cedula_catastral;

CREATE VIEW v_cedula_catastral AS
SELECT
  i.id                        AS inmueble_id,
  i.codigo_catastral,
  formatear_codigo_catastral(i.codigo_catastral) AS codigo_catastral_formato,
  i.expediente_numero,
  i.fecha_emision,
  i.vigente_hasta,

  pr.cedula_rif               AS propietario_cedula_rif,
  pr.nombre                   AS propietario_nombre,
  pr.apellido                 AS propietario_apellido,

  i.direccion,
  i.documento_tipo, i.documento_numero, i.documento_tomo,
  i.documento_folio, i.documento_protocolo, i.documento_fecha,

  i.tenencia, i.contrato_arrendamiento_num, i.contrato_arrendamiento_fecha,

  i.lindero_norte_doc, i.lindero_norte_mts,
  i.lindero_sur_doc, i.lindero_sur_mts,
  i.lindero_este_doc, i.lindero_este_mts,
  i.lindero_oeste_doc, i.lindero_oeste_mts,

  i.lindero_norte_top, i.lindero_norte_top_mts,
  i.lindero_sur_top, i.lindero_sur_top_mts,
  i.lindero_este_top, i.lindero_este_top_mts,
  i.lindero_oeste_top, i.lindero_oeste_top_mts,

  i.aguas_blancas, i.aguas_servidas, i.electricidad, i.contador,
  i.existe_vivienda, i.tipo_vivienda, i.descripcion_uso,
  i.numero_plantas, i.uso_segun_zonificacion,

  i.area_terreno_m2, i.valor_unit_terreno, i.valor_terreno,
  i.area_construccion_m2, i.valor_unit_construccion, i.valor_construccion,
  i.area_comercio_m2, i.valor_unit_comercio, i.valor_comercio,
  i.valor_catastral_total,

  i.via_acceso, i.estructura_techo, i.estructura_paredes, i.piso,
  i.dormitorios, i.banos, i.sala, i.cocina, i.ambiente_otro,
  i.caracteristica_general, i.observaciones,

  i.utm_norte AS utm_norte_centroide,
  i.utm_este  AS utm_este_centroide

FROM inmuebles i
LEFT JOIN propietarios pr ON pr.id = i.propietario_id;


-- ------------------------------------------------------------
-- 14.2 Vista para PDF con Configuración Dinámica (v2.5 actualizada)
-- ✅ FIX CRÍTICO (v2.2): N y U extraían 2 caracteres; correcto es 3.
--    Posiciones en el código de 23: S=7-8, Ma=9-11, Pa=12-14,
--    SP=15-17, N=18-20, U=21-23.
-- ✅ v2.5: Vista actualizada con todos los campos del formato oficial
-- ------------------------------------------------------------
DROP VIEW IF EXISTS public.v_pdf_cedula_catastral;

CREATE VIEW v_pdf_cedula_catastral AS
SELECT
  i.id AS inmueble_id,
  i.codigo_catastral,

  cfg.estado_codigo    AS e,
  cfg.municipio_codigo AS m,
  cfg.parroquia_codigo AS p,
  SUBSTRING(i.codigo_catastral FROM 7  FOR 2) AS s,
  SUBSTRING(i.codigo_catastral FROM 9  FOR 3) AS ma,
  SUBSTRING(i.codigo_catastral FROM 12 FOR 3) AS pa,
  SUBSTRING(i.codigo_catastral FROM 15 FOR 3) AS sp,
  SUBSTRING(i.codigo_catastral FROM 18 FOR 3) AS n,
  SUBSTRING(i.codigo_catastral FROM 21 FOR 3) AS u,

  -- Expediente / recibo / fechas
  i.expediente_numero,
  i.numero_recibo,
  i.fecha_recibo,
  i.fecha_emision,
  i.vigente_hasta,

  -- Propietario
  p.cedula_rif,
  p.nombre || ' ' || p.apellido AS propietario_nombre,

  -- Inmueble / documento
  i.direccion,
  i.documento_tipo, i.documento_numero, i.documento_tomo,
  i.documento_folio, i.documento_protocolo, i.documento_fecha,
  i.tenencia,

  -- Linderos según documento
  i.lindero_norte_doc, i.lindero_norte_mts,
  i.lindero_sur_doc, i.lindero_sur_mts,
  i.lindero_este_doc, i.lindero_este_mts,
  i.lindero_oeste_doc, i.lindero_oeste_mts,

  -- Linderos según levantamiento topográfico
  i.lindero_norte_top, i.lindero_norte_top_mts,
  i.lindero_sur_top, i.lindero_sur_top_mts,
  i.lindero_este_top, i.lindero_este_top_mts,
  i.lindero_oeste_top, i.lindero_oeste_top_mts,

  -- Factibilidad de servicios
  i.aguas_blancas, i.aguas_servidas, i.electricidad, i.contador,

  -- Vivienda / uso
  i.existe_vivienda, i.tipo_vivienda, i.descripcion_uso,
  i.numero_plantas, i.uso_segun_zonificacion,

  -- Áreas y valores (unitarios + calculados, por categoría y total)
  i.area_terreno_m2, i.valor_unit_terreno, i.valor_terreno,
  i.area_construccion_m2, i.valor_unit_construccion, i.valor_construccion,
  i.area_comercio_m2, i.valor_unit_comercio, i.valor_comercio,
  i.valor_catastral_total,

  -- Características físicas
  i.via_acceso, i.estructura_techo, i.estructura_paredes, i.piso,
  i.dormitorios, i.banos, i.sala, i.cocina, i.ambiente_otro,
  i.caracteristica_general,

  i.observaciones,

  -- Coordenadas UTM del centroide
  i.utm_norte,
  i.utm_este,

  -- Datos institucionales (para encabezado y firmas del PDF)
  cat.nombre_estado, cat.nombre_municipio, cat.nombre_parroquia,
  cat.rif_alcaldia, cat.direccion_institucional,
  cat.nombre_maxima_autoridad, cat.cargo_maxima_autoridad,
  cat.texto_acta_maxima_autoridad,
  cat.nombre_director_catastro, cat.cargo_director_catastro,
  cat.texto_resolucion_director,
  cat.notas_legales

FROM public.inmuebles i
CROSS JOIN public.configuracion_sistema  cfg
CROSS JOIN public.configuracion_catastral cat
LEFT JOIN public.propietarios p ON i.propietario_id = p.id
WHERE cfg.id = 1 AND cat.id = 1;


-- ============================================================
-- 15. VERIFICACIÓN POST-INSTALACIÓN (correr a mano, opcional)
-- ============================================================
-- 1) Código generado debe tener 23 caracteres:
--    SELECT generar_codigo_catastral('01','001','001');
--    → '20112701001001000000000'
--
-- 2) La vista PDF debe extraer todos los bloques correctamente:
--    SELECT e, m, p, s, ma, pa, sp, n, u FROM v_pdf_cedula_catastral LIMIT 1;
--
-- 3) Verificar las columnas de la vista PDF (debe incluir
--    expediente_numero entre 'u' y 'cedula_rif'):
--    SELECT column_name FROM information_schema.columns
--    WHERE table_name = 'v_pdf_cedula_catastral'
--    ORDER BY ordinal_position;
--
-- 4) Mapa completo (retrocompatible, sin bbox):
--    SELECT mapa_catastral();
--
-- 5) Mapa solo con predios visibles (bbox San Josecito aprox):
--    SELECT mapa_catastral(-72.25, 7.70, -72.15, 7.80);
--
-- 6) Estadísticas:
--    SELECT estadisticas_catastro();
--
-- 7) Predios por sector:
--    SELECT predios_por_sector();
--
-- 8) Verificar que los índices quedaron creados:
--    SELECT indexname FROM pg_indexes
--    WHERE tablename = 'inmuebles'
--      AND indexname IN ('idx_inm_codigo_prefix','idx_inm_direccion_trgm');
--
-- 8) Verificar campos institucionales de configuración catastral:
--    SELECT nombre_maxima_autoridad, cargo_maxima_autoridad, notas_legales
--    FROM configuracion_catastral WHERE id = 1;
--
-- 9) Completar manualmente los datos del director de catastro:
--    UPDATE configuracion_catastral SET
--      nombre_director_catastro  = 'NOMBRE REAL DE LA DIRECTORA',
--      texto_resolucion_director = 'Resolución N° 018/2025 de fecha 15 de Agosto de 2025'
--    WHERE id = 1;
-- ============================================================
-- FIN v2.5 COMPLETA
-- ============================================================
