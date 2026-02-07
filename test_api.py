#!/usr/bin/env python3
"""
Script de pruebas para gestión de administradores.
Ejecutar: python test_admins.py
"""
import sys
import requests
import json
from datetime import datetime

# Cambiar si usas localhost
BASE_URL = "https://pisoskermy-backend.onrender.com"
# Para desarrollo local descomentar:
# BASE_URL = "http://localhost:5000"

TOKEN = None
CURRENT_ADMIN_ID = None


def log(message, level='INFO'):
    """Log con colores."""
    colors = {
        'INFO': '\033[94m',    # Azul
        'OK': '\033[92m',      # Verde
        'WARN': '\033[93m',    # Amarillo
        'FAIL': '\033[91m',    # Rojo
        'RESET': '\033[0m'
    }
    color = colors.get(level, colors['INFO'])
    reset = colors['RESET']
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{color}[{timestamp}] {message}{reset}")


def check_response(response, expected_status, endpoint):
    """Verifica que la respuesta sea la esperada."""
    if response.status_code != expected_status:
        log(f"FAIL: {endpoint} - Expected {expected_status}, got {response.status_code}", 'FAIL')
        try:
            log(f"Response: {response.json()}", 'FAIL')
        except:
            log(f"Response: {response.text}", 'FAIL')
        return False
    log(f"OK: {endpoint} - {expected_status}", 'OK')
    return True


def test_login(email, password):
    """Probar login y obtener token."""
    global TOKEN, CURRENT_ADMIN_ID
    
    log("Probando login")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        'email': email,
        'password': password
    })
    
    if not check_response(r, 200, "POST /api/auth/login"):
        return False
    
    data = r.json()
    TOKEN = data['token']
    CURRENT_ADMIN_ID = data['admin']['id']
    
    log(f"OK: Token obtenido para {data['admin']['email']}", 'OK')
    log(f"OK: Admin ID: {CURRENT_ADMIN_ID}", 'OK')
    return True


def test_list_admins():
    """Probar listado de admins."""
    log("Probando listado de admins")
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    r = requests.get(f"{BASE_URL}/api/auth/admins", headers=headers)
    if not check_response(r, 200, "GET /api/auth/admins"):
        return False
    
    admins = r.json()['admins']
    log(f"OK: Se encontraron {len(admins)} admins", 'OK')
    
    for admin in admins:
        status = "ACTIVO" if admin['is_active'] else "INACTIVO"
        log(f"  - {admin['name']} ({admin['email']}) - {status}", 'INFO')
    
    return True


def test_create_admin():
    """Probar creación de admin."""
    log("Probando creación de admin")
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    # Crear admin de prueba
    test_email = f"test_{datetime.now().timestamp()}@pisoskermy.com"
    r = requests.post(f"{BASE_URL}/api/auth/admins", headers=headers, json={
        'email': test_email,
        'name': 'Admin de Prueba',
        'password': 'prueba123'
    })
    
    if not check_response(r, 201, "POST /api/auth/admins"):
        return False
    
    admin = r.json()['admin']
    log(f"OK: Admin creado - {admin['email']}", 'OK')
    return admin['id']


def test_update_admin(admin_id):
    """Probar actualización de admin."""
    log(f"Probando actualización de admin {admin_id}")
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    r = requests.put(f"{BASE_URL}/api/auth/admins/{admin_id}", headers=headers, json={
        'name': 'Admin Actualizado',
    })
    
    if not check_response(r, 200, f"PUT /api/auth/admins/{admin_id}"):
        return False
    
    admin = r.json()['admin']
    if admin['name'] != 'Admin Actualizado':
        log("FAIL: El nombre no se actualizó correctamente", 'FAIL')
        return False
    
    log(f"OK: Admin actualizado - {admin['name']}", 'OK')
    return True


def test_change_password(admin_id):
    """Probar cambio de password."""
    log(f"Probando cambio de password para admin {admin_id}")
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    r = requests.put(f"{BASE_URL}/api/auth/admins/{admin_id}/password", headers=headers, json={
        'password': 'nuevaPassword456'
    })
    
    if not check_response(r, 200, f"PUT /api/auth/admins/{admin_id}/password"):
        return False
    
    log("OK: Password actualizado", 'OK')
    return True


def test_toggle_admin(admin_id):
    """Probar activar/desactivar admin."""
    log(f"Probando toggle de admin {admin_id}")
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    # Desactivar
    r = requests.put(f"{BASE_URL}/api/auth/admins/{admin_id}/toggle", headers=headers)
    if not check_response(r, 200, f"PUT /api/auth/admins/{admin_id}/toggle (desactivar)"):
        return False
    
    admin = r.json()['admin']
    if admin['is_active']:
        log("FAIL: El admin debería estar inactivo", 'FAIL')
        return False
    log("OK: Admin desactivado", 'OK')
    
    # Reactivar
    r = requests.put(f"{BASE_URL}/api/auth/admins/{admin_id}/toggle", headers=headers)
    if not check_response(r, 200, f"PUT /api/auth/admins/{admin_id}/toggle (activar)"):
        return False
    
    admin = r.json()['admin']
    if not admin['is_active']:
        log("FAIL: El admin debería estar activo", 'FAIL')
        return False
    log("OK: Admin activado", 'OK')
    
    return True


def test_cannot_deactivate_self():
    """Probar que no puede desactivarse a sí mismo."""
    log("Probando que no puede desactivarse a sí mismo")
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    r = requests.put(f"{BASE_URL}/api/auth/admins/{CURRENT_ADMIN_ID}/toggle", headers=headers)
    
    if r.status_code != 400:
        log(f"FAIL: Debería retornar 400, pero retornó {r.status_code}", 'FAIL')
        return False
    
    error = r.json().get('error', '')
    if 'tu propia cuenta' not in error.lower():
        log(f"FAIL: Mensaje de error incorrecto: {error}", 'FAIL')
        return False
    
    log("OK: Correctamente rechazado - no puede desactivarse a sí mismo", 'OK')
    return True


def test_validations():
    """Probar validaciones."""
    log("Probando validaciones")
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    # Email inválido
    r = requests.post(f"{BASE_URL}/api/auth/admins", headers=headers, json={
        'email': 'invalido',
        'name': 'Test',
        'password': 'test123'
    })
    if r.status_code != 400:
        log(f"FAIL: Email inválido debería retornar 400, retornó {r.status_code}", 'FAIL')
        return False
    log("OK: Email inválido rechazado", 'OK')
    
    # Password muy corto
    r = requests.post(f"{BASE_URL}/api/auth/admins", headers=headers, json={
        'email': 'test@test.com',
        'name': 'Test',
        'password': '123'
    })
    if r.status_code != 400:
        log(f"FAIL: Password corto debería retornar 400, retornó {r.status_code}", 'FAIL')
        return False
    log("OK: Password corto rechazado", 'OK')
    
    # Nombre vacío
    r = requests.post(f"{BASE_URL}/api/auth/admins", headers=headers, json={
        'email': 'test@test.com',
        'name': '',
        'password': 'test123'
    })
    if r.status_code != 400:
        log(f"FAIL: Nombre vacío debería retornar 400, retornó {r.status_code}", 'FAIL')
        return False
    log("OK: Nombre vacío rechazado", 'OK')
    
    return True


def test_audit_log():
    """Verificar que las acciones quedaron en bitácora."""
    log("Verificando bitácora de auditoría")
    headers = {'Authorization': f'Bearer {TOKEN}'}
    
    r = requests.get(f"{BASE_URL}/api/auth/audit?per_page=10", headers=headers)
    if not check_response(r, 200, "GET /api/auth/audit"):
        return False
    
    logs = r.json()['logs']
    
    # Buscar acciones de admin
    admin_actions = [
        log for log in logs 
        if log['entity'] == 'admin' and log['action'] in [
            'CREATE_ADMIN', 'UPDATE_ADMIN', 'CHANGE_PASSWORD', 
            'ACTIVATE_ADMIN', 'DEACTIVATE_ADMIN'
        ]
    ]
    
    if len(admin_actions) == 0:
        log("WARN: No se encontraron acciones de admin en la bitácora", 'WARN')
    else:
        log(f"OK: Se encontraron {len(admin_actions)} acciones de admin en bitácora", 'OK')
        for audit in admin_actions[:3]:  # Mostrar solo las últimas 3
            log(f"  - {audit['action']} por {audit['admin_email']}", 'INFO')
    
    return True


def main():
    log("=== Iniciando pruebas de gestión de admins ===", 'INFO')
    log(f"Base URL: {BASE_URL}", 'INFO')
    
    # Solicitar credenciales
    print()
    email = input("Email del admin: ").strip()
    password = input("Password del admin: ").strip()
    print()
    
    results = []
    test_admin_id = None
    
    # Login
    results.append(("Login", test_login(email, password)))
    
    if not TOKEN:
        log("FAIL: No se pudo obtener el token. Las pruebas se detienen.", 'FAIL')
        sys.exit(1)
    
    # Pruebas de listado
    results.append(("Listar admins", test_list_admins()))
    
    # Pruebas de creación
    test_admin_id = test_create_admin()
    results.append(("Crear admin", test_admin_id is not None))
    
    if test_admin_id:
        # Pruebas de actualización
        results.append(("Actualizar admin", test_update_admin(test_admin_id)))
        
        # Pruebas de password
        results.append(("Cambiar password", test_change_password(test_admin_id)))
        
        # Pruebas de toggle
        results.append(("Toggle admin", test_toggle_admin(test_admin_id)))
    
    # Pruebas de seguridad
    results.append(("No desactivar self", test_cannot_deactivate_self()))
    
    # Pruebas de validación
    results.append(("Validaciones", test_validations()))
    
    # Auditoría
    results.append(("Bitácora", test_audit_log()))
    
    # Resumen
    log("\n=== Resumen de pruebas ===", 'INFO')
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    
    for name, ok in results:
        status = 'OK' if ok else 'FAIL'
        log(f"{name}: {status}", 'OK' if ok else 'FAIL')
    
    log(f"\nTotal: {passed}/{total} pruebas pasaron", 'OK' if passed == total else 'FAIL')
    
    # Limpiar admin de prueba
    if test_admin_id:
        log(f"\nNOTA: Se creó admin de prueba con ID {test_admin_id}", 'INFO')
        log("Puedes desactivarlo o eliminarlo manualmente si lo deseas", 'INFO')
    
    if passed == total:
        log("\nTodas las pruebas pasaron. La gestión de admins está funcionando correctamente.", 'OK')
        sys.exit(0)
    else:
        log("\nAlgunas pruebas fallaron. Revisar los errores arriba.", 'FAIL')
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        log("\n\nPruebas canceladas por el usuario", 'WARN')
        sys.exit(1)
    except Exception as e:
        log(f"\n\nError inesperado: {e}", 'FAIL')
        import traceback
        traceback.print_exc()
        sys.exit(1)