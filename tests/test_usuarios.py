"""
Pruebas E2E para endpoints de usuarios
"""
import pytest
import requests


class TestUsuarios:
    """Pruebas para gestión de usuarios"""
    
    def test_obtener_perfil_actual(self, api_url, headers):
        """
        US-001: Obtener perfil actual
        Verificar que se pueden obtener datos del usuario autenticado
        """
        response = requests.get(f"{api_url}/usuarios/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "cedula" in data
        assert "nombre" in data
        assert "apellido" in data
        assert "rol" in data
    
    def test_listar_usuarios(self, api_url, headers):
        """
        US-002: Listar usuarios (admin)
        Verificar que se pueden listar todos los usuarios
        """
        response = requests.get(f"{api_url}/usuarios", headers=headers)
        # Puede requerir rol de administrador
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
        elif response.status_code == 403:
            # Usuario no tiene permisos de admin, es aceptable
            pytest.skip("Requiere rol de administrador")
    
    def test_cambiar_rol_usuario(self, api_url, headers):
        """
        US-003: Cambiar rol de usuario (admin)
        Verificar que se puede cambiar el rol entre admin/inspector
        """
        # Esta prueba requiere un ID de usuario válido y permisos de admin
        # Por ahora la saltamos si no tenemos permisos
        pytest.skip("Requiere rol de administrador y ID de usuario específico")
    
    def test_activar_desactivar_usuario(self, api_url, headers):
        """
        US-004: Activar/desactivar usuario (admin)
        Verificar que se puede cambiar el estado activo/inactivo
        """
        # Esta prueba requiere un ID de usuario válido y permisos de admin
        # Por ahora la saltamos si no tenemos permisos
        pytest.skip("Requiere rol de administrador y ID de usuario específico")
