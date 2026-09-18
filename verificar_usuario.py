"""
Script para verificar si el usuario existe en la base de datos
"""
import os
from dotenv import load_dotenv
import requests

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

USER_ID = "91f625d2-82eb-479f-a45f-1a02ae3d1e45"

def verificar_usuario():
    """
    Verifica si el usuario existe en la tabla usuarios
    """
    url = f"{SUPABASE_URL}/rest/v1/usuarios?id=eq.{USER_ID}"
    
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json"
    }
    
    print("Verificando usuario en tabla usuarios...")
    print(f"ID: {USER_ID}")
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        usuarios = response.json()
        if len(usuarios) > 0:
            print(f"Usuario encontrado: {usuarios[0]}")
            return True
        else:
            print("Usuario no encontrado en tabla usuarios")
            return False
    else:
        print(f"Error al verificar usuario: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    verificar_usuario()
