-- ============================================================
-- SRCM - MIGRACION v3.0 (Soporte a Múltiples Propietarios)
-- Ejecutar en Supabase -> SQL Editor
-- ============================================================

BEGIN;

-- 1. Crear tabla intermedia de Muchos a Muchos
CREATE TABLE IF NOT EXISTS public.inmueble_propietario (
    inmueble_id UUID NOT NULL REFERENCES public.inmuebles(id) ON DELETE CASCADE,
    propietario_id UUID NOT NULL REFERENCES public.propietarios(id) ON DELETE CASCADE,
    es_principal BOOLEAN NOT NULL DEFAULT false,
    porcentaje_propiedad NUMERIC(5,2) DEFAULT 100.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    
    CONSTRAINT inmueble_propietario_pkey PRIMARY KEY (inmueble_id, propietario_id)
);

-- 2. Migrar los datos existentes (Mover el dueño actual a la nueva tabla como principal al 100%)
INSERT INTO public.inmueble_propietario (inmueble_id, propietario_id, es_principal, porcentaje_propiedad)
SELECT id, propietario_id, true, 100.00
FROM public.inmuebles
WHERE propietario_id IS NOT NULL;

-- 3. Eliminar la columna vieja de la tabla de inmuebles
ALTER TABLE public.inmuebles DROP COLUMN propietario_id;

-- 4. Reconstruir la Vista de la Cédula Catastral (v_pdf_cedula_catastral)
DROP VIEW IF EXISTS public.v_pdf_cedula_catastral CASCADE;

CREATE VIEW public.v_pdf_cedula_catastral AS
SELECT 
    i.id AS inmueble_id,
    i.codigo_catastral,
    i.expediente_numero,
    -- Datos del propietario principal
    p.nombre || ' ' || p.apellido AS propietario_nombre,
    p.cedula_rif AS propietario_cedula_rif,
    i.direccion AS direccion_inmueble,
    i.documento_tipo,
    i.documento_numero,
    i.documento_tomo,
    i.documento_fecha,
    i.tenencia,
    i.documento_folio,
    i.documento_protocolo,
    -- (Aquí continuarían todos los campos geográficos y físicos que ya tiene la vista actual...)
    i.area_terreno_m2
FROM public.inmuebles i
-- NUEVO JOIN: Buscamos solo al propietario marcado como principal para el PDF
LEFT JOIN public.inmueble_propietario ip ON i.id = ip.inmueble_id AND ip.es_principal = true
LEFT JOIN public.propietarios p ON ip.propietario_id = p.id;

COMMIT;