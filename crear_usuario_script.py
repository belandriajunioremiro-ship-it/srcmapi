"""
Script para crear el usuario en la tabla usuarios de la base de datos
"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# El ID del usuario de Supabase Auth (extraído del token)
USER_ID = "91f625d2-82eb-479f-a45f-1a02ae3d1e45"

def crear_usuario_en_bd():
    """
    Crea el registro del usuario en la tabla usuarios usando service_role_key
    """
    url = f"{SUPABASE_URL}/rest/v1/usuarios"
    
    headers = {
        "apikey": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "id": USER_ID,
        "cedula": "V-20394453",
        "nombre": "Junior",
        "apellido": "Belandria",
        "rol": "administrador",
        "activo": True
    }
    
    print("Creando usuario en tabla usuarios...")
    print(f"ID: {USER_ID}")
    print(f"Cedula: V-20394453")
    print(f"Nombre: Junior Belandria")
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        print("Usuario creado exitosamente en tabla usuarios")
        return True
    elif response.status_code == 409:
        print("El usuario ya existe en tabla usuarios")
        return True
    else:
        print(f"Error al crear usuario: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    crear_usuario_en_bd()
