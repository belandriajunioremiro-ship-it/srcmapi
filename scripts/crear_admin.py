"""
Promueve un usuario existente (por cédula) a rol 'administrador'.

Uso (con el entorno virtual activado, desde la raíz del proyecto):

    python scripts/crear_admin.py V-12345678

El usuario debe existir previamente en la tabla `usuarios` (es decir, ya
debe haberse registrado al menos una vez vía Supabase Auth, lo cual dispara
el trigger handle_new_user que crea su fila con rol 'inspector' por defecto).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402


def main():
    if len(sys.argv) != 2:
        print("Uso: python scripts/crear_admin.py <cedula>")
        sys.exit(1)

    cedula = sys.argv[1]
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter(Usuario.cedula == cedula).first()
        if not usuario:
            print(f"No se encontró ningún usuario con cédula '{cedula}'.")
            print("Recuerda: el usuario debe haberse registrado antes vía Supabase Auth.")
            sys.exit(1)

        usuario.rol = "administrador"
        db.commit()
        print(f"OK: {usuario.nombre} {usuario.apellido} ({cedula}) ahora es administrador.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
