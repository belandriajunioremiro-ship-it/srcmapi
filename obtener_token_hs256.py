"""
Script para obtener un token JWT de Supabase Auth con algoritmo HS256
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

def obtener_token_hs256(email, password):
    """
    Obtiene un token JWT de Supabase Auth usando email y password
    Intenta obtener token HS256 o regular
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
        
        # Decodificar el header para ver el algoritmo
        from jose import jwt
        headers_token = jwt.get_unverified_header(access_token)
        algorithm = headers_token.get("alg", "unknown")
        
        print("Token obtenido exitosamente")
        print(f"Algoritmo: {algorithm}")
        print(f"Access Token (primeros 50 chars): {access_token[:50]}...")
        return access_token, algorithm
    else:
        print(f"Error al obtener token: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None

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
    
    token, algorithm = obtener_token_hs256(email, password)
    
    if token:
        print()
        print("Copia este token y agregalo a tu archivo .env:")
        print(f"TEST_AUTH_TOKEN={token}")
        
        # Tambien guardarlo en un archivo para facilitar
        with open("token_obtenido_hs256.txt", "w") as f:
            f.write(token)
        print("Token guardado en 'token_obtenido_hs256.txt'")
        print(f"Algoritmo del token: {algorithm}")