# 🚀 SRCM v3.0 - Arquitectura de Múltiples Propietarios (Co-propietarios)

Este documento proyecta y diseña la actualización arquitectónica necesaria para soportar **múltiples propietarios** (co-propietarios) en un mismo terreno.

Actualmente (v2.5), la base de datos tiene una relación **1:N** (1 Propietario tiene muchos Inmuebles, pero 1 Inmueble solo puede tener 1 Propietario).
Para soportar co-propietarios, debemos migrar a una relación **Muchos-a-Muchos (M:N)** utilizando una tabla intermedia (inmueble_propietario).

---

## 📂 1. Cambios a nivel de Base de Datos (PostgreSQL)

1. **Crear Tabla Intermedia (inmueble_propietario)**:
   Esta tabla conectará UUIDs de inmuebles con UUIDs de propietarios, e incluirá campos adicionales como es_principal y porcentaje_propiedad.
2. **Eliminar Llave Foránea en inmuebles**:
   La columna propietario_id de la tabla inmuebles será eliminada.
3. **Actualizar la Vista _pdf_cedula_catastral**:
   La cédula catastral PDF suele mostrar al "Representante" o listar a todos. Se actualizará la vista para hacer JOIN con la tabla intermedia filtrando por es_principal = true, de modo que el PDF siga renderizando un dueño titular sin romperse.

---

## 🐍 2. Cambios a nivel de Python (FastAPI + SQLAlchemy)

### A. Modelos (pp/models/inmueble.py)
Se debe crear el modelo de la tabla intermedia y actualizar las relaciones:

`python
class InmueblePropietario(Base):
    __tablename__ = "inmueble_propietario"
    inmueble_id = Column(UUID(as_uuid=True), ForeignKey("inmuebles.id", ondelete="CASCADE"), primary_key=True)
    propietario_id = Column(UUID(as_uuid=True), ForeignKey("propietarios.id", ondelete="CASCADE"), primary_key=True)
    es_principal = Column(Boolean, default=False)
    porcentaje = Column(Numeric(5,2), default=100.00)

class Inmueble(Base):
    # ELIMINAR: propietario_id = Column(UUID...)
    
    # NUEVO:
    propietarios = relationship("Propietario", secondary="inmueble_propietario", backref="inmuebles")
`

### B. Esquemas Pydantic (pp/schemas/inmueble.py)
En lugar de recibir un solo propietario_id, el payload de creación recibirá una lista:

`python
class PropietarioInmuebleCreate(BaseModel):
    propietario_id: UUID4
    es_principal: bool
    porcentaje: float

class InmuebleCreate(InmuebleBase):
    propietarios: List[PropietarioInmuebleCreate]
`

### C. Servicios y Endpoints (pp/services/inmueble_service.py)
Al guardar el inmueble, iteramos sobre la lista para insertarlos en la tabla intermedia:

`python
db_inmueble = Inmueble(**inmueble_data)
db.add(db_inmueble)
db.flush() # Para obtener el ID

for prop in propietarios_data:
    relacion = InmueblePropietario(
        inmueble_id=db_inmueble.id,
        propietario_id=prop.propietario_id,
        es_principal=prop.es_principal,
        porcentaje=prop.porcentaje
    )
    db.add(relacion)
db.commit()
`

---

## 💾 3. Script SQL Completo (Proyección v3.0)
Si la Alcaldía decide implementar esto mañana, el script que ejecuta todo el cambio sin romper los datos existentes se encuentra en el archivo adjunto: SQL_V3_COPROPIETARIOS.sql.