"""
Script para obtener un token JWT de Supabase Auth
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def obtener_token(email, password):
    """
    Obtiene un token JWT de Supabase Auth usando email y password
    """
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")
        print("Token obtenido exitosamente")
        print(f"Access Token: {access_token}")
        return access_token
    else:
        print(f"Error al obtener token: {response.status_code}")
        print(f"Response: {response.text}")
        return None

if __name__ == "__main__":
    print("Obtener Token JWT de Supabase Auth")
    print(f"Supabase URL: {SUPABASE_URL}")
    print()
    
    # Usar credenciales proporcionadas
    email = "belandriajunioremiro@gmail.com"
    password = "20394453"
    
    print(f"Email: {email}")
    print(f"Contrasena: {'*' * len(password)}")
    print()
    
    token = obtener_token(email, password)
    
    if token:
        print()
        print("Copia este token y agregalo a tu archivo .env:")
        print(f"TEST_AUTH_TOKEN={token}")
        
        # Tambien guardarlo en un archivo para facilitar
        with open("token_obtenido.txt", "w") as f:
            f.write(token)
        print("Token guardado en 'token_obtenido.txt'")
