from app.models.inmueble import Inmueble
from app.schemas.inmueble import InmuebleListItem, InmuebleOut
from app.services.geo_service import wkb_to_geojson
from app.utils.catastro_codigo import formatear_codigo_catastral


def inmueble_a_out(inmueble: Inmueble) -> InmuebleOut:
    data = InmuebleOut.model_validate(inmueble)
    data.codigo_catastral_formato = formatear_codigo_catastral(
        inmueble.codigo_catastral
    )
    return data


def inmueble_a_list_item(inmueble: Inmueble) -> InmuebleListItem:
    data = InmuebleListItem.model_validate(inmueble)
    data.codigo_catastral_formato = formatear_codigo_catastral(
        inmueble.codigo_catastral
    )
    return data
