#!/usr/bin/env python3
"""
Script de pruebas para verificar que todas las APIs funcionan correctamente.

Ejecutar desde la raiz del repo con el servidor corriendo:

    python test_api.py

Prerequisitos:
- docker compose up -d (la API debe estar corriendo en http://localhost:5000)
- Haber creado al menos un admin con create_first_admin.py
"""
import requests
import sys
from pathlib import Path

BASE_URL = 'http://localhost:5000'
TOKEN = None


def log(msg, level='INFO'):
    colors = {
        'INFO':  '\033[94m',
        'OK':    '\033[92m',
        'FAIL':  '\033[91m',
        'WARN':  '\033[93m',
        'RESET': '\033[0m',
    }
    print(f"{colors.get(level, '')}{level}: {msg}{colors['RESET']}")


def check_response(response, expected_status, test_name):
    if response.status_code == expected_status:
        log(f"{test_name} - OK", 'OK')
        return True
    else:
        log(f"{test_name} - FAIL (esperado {expected_status}, obtuvo {response.status_code})", 'FAIL')
        log(f"Respuesta: {response.text}", 'WARN')
        return False


def test_health():
    log("Probando /health")
    r = requests.get(f"{BASE_URL}/health")
    return check_response(r, 200, "GET /health")


def test_login(email, password):
    global TOKEN
    log(f"Probando login con {email}")
    r = requests.post(f"{BASE_URL}/api/auth/login", json={
        'email': email,
        'password': password,
    })
    if check_response(r, 200, "POST /api/auth/login"):
        TOKEN = r.json()['token']
        log(f"Token obtenido: {TOKEN[:20]}...", 'OK')
        return True
    return False


def test_auth_me():
    log("Probando /api/auth/me")
    headers = {'Authorization': f'Bearer {TOKEN}'}
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    return check_response(r, 200, "GET /api/auth/me")


def test_categories():
    log("Probando categorias")
    headers = {'Authorization': f'Bearer {TOKEN}'}

    # Crear
    r = requests.post(f"{BASE_URL}/api/admin/categories", headers=headers, json={'name': 'Test Category'})
    if not check_response(r, 201, "POST /api/admin/categories"):
        return False
    cat_id = r.json()['id']

    # Listar admin
    r = requests.get(f"{BASE_URL}/api/admin/categories", headers=headers)
    if not check_response(r, 200, "GET /api/admin/categories"):
        return False

    # Listar publico
    r = requests.get(f"{BASE_URL}/api/categories")
    if not check_response(r, 200, "GET /api/categories"):
        return False

    # Actualizar
    r = requests.put(f"{BASE_URL}/api/admin/categories/{cat_id}", headers=headers, json={'name': 'Updated Category'})
    if not check_response(r, 200, f"PUT /api/admin/categories/{cat_id}"):
        return False

    # Eliminar
    r = requests.delete(f"{BASE_URL}/api/admin/categories/{cat_id}", headers=headers)
    return check_response(r, 200, f"DELETE /api/admin/categories/{cat_id}")


def test_tags():
    log("Probando etiquetas")
    headers = {'Authorization': f'Bearer {TOKEN}'}

    r = requests.post(f"{BASE_URL}/api/admin/tags", headers=headers, json={'name': 'Test Tag'})
    if not check_response(r, 201, "POST /api/admin/tags"):
        return False
    tag_id = r.json()['id']

    r = requests.get(f"{BASE_URL}/api/admin/tags", headers=headers)
    if not check_response(r, 200, "GET /api/admin/tags"):
        return False

    r = requests.get(f"{BASE_URL}/api/tags")
    if not check_response(r, 200, "GET /api/tags"):
        return False

    r = requests.put(f"{BASE_URL}/api/admin/tags/{tag_id}", headers=headers, json={'name': 'Updated Tag'})
    if not check_response(r, 200, f"PUT /api/admin/tags/{tag_id}"):
        return False

    r = requests.delete(f"{BASE_URL}/api/admin/tags/{tag_id}", headers=headers)
    return check_response(r, 200, f"DELETE /api/admin/tags/{tag_id}")


def test_providers():
    log("Probando proveedores")
    headers = {'Authorization': f'Bearer {TOKEN}'}

    r = requests.post(f"{BASE_URL}/api/admin/providers", headers=headers, json={
        'name': 'Test Provider',
        'contact': 'test@example.com',
        'phone': '12345',
        'description': 'Test description'
    })
    if not check_response(r, 201, "POST /api/admin/providers"):
        return False
    prov_id = r.json()['id']

    r = requests.get(f"{BASE_URL}/api/admin/providers", headers=headers)
    if not check_response(r, 200, "GET /api/admin/providers"):
        return False

    r = requests.put(f"{BASE_URL}/api/admin/providers/{prov_id}", headers=headers, json={'phone': '99999'})
    if not check_response(r, 200, f"PUT /api/admin/providers/{prov_id}"):
        return False

    r = requests.delete(f"{BASE_URL}/api/admin/providers/{prov_id}", headers=headers)
    return check_response(r, 200, f"DELETE /api/admin/providers/{prov_id}")


def test_products():
    log("Probando productos")
    headers = {'Authorization': f'Bearer {TOKEN}'}

    # Crear categoria y tag para asociar al producto
    r1 = requests.post(f"{BASE_URL}/api/admin/categories", headers=headers, json={'name': 'Prod Cat'})
    r2 = requests.post(f"{BASE_URL}/api/admin/tags", headers=headers, json={'name': 'Prod Tag'})
    cat_id = r1.json()['id']
    tag_id = r2.json()['id']

    # Crear producto
    r = requests.post(f"{BASE_URL}/api/admin/products", headers=headers, json={
        'name': 'Test Product',
        'description': 'Description',
        'price': 1500.50,
        'category_ids': [cat_id],
        'tag_ids': [tag_id],
        'provider_ids': []
    })
    if not check_response(r, 201, "POST /api/admin/products"):
        return False
    prod_id = r.json()['id']
    product = r.json()

    # Verificar que el admin ve el precio
    if 'price' not in product:
        log("FAIL: El admin no ve el precio en la respuesta", 'FAIL')
        return False
    log("OK: El admin ve el precio en la respuesta", 'OK')

    # Listar productos (admin)
    r = requests.get(f"{BASE_URL}/api/admin/products", headers=headers)
    if not check_response(r, 200, "GET /api/admin/products"):
        return False

    # Listar productos (publico) - verificar que NO se ve el precio
    r = requests.get(f"{BASE_URL}/api/products")
    if not check_response(r, 200, "GET /api/products"):
        return False
    products_public = r.json()['products']
    if products_public and 'price' in products_public[0]:
        log("FAIL: El cliente publico puede ver el precio", 'FAIL')
        return False
    log("OK: El cliente publico NO ve el precio", 'OK')

    # Actualizar
    r = requests.put(f"{BASE_URL}/api/admin/products/{prod_id}", headers=headers, json={'name': 'Updated Product'})
    if not check_response(r, 200, f"PUT /api/admin/products/{prod_id}"):
        return False

    # Eliminar
    r = requests.delete(f"{BASE_URL}/api/admin/products/{prod_id}", headers=headers)
    if not check_response(r, 200, f"DELETE /api/admin/products/{prod_id}"):
        return False

    # Limpiar
    requests.delete(f"{BASE_URL}/api/admin/categories/{cat_id}", headers=headers)
    requests.delete(f"{BASE_URL}/api/admin/tags/{tag_id}", headers=headers)
    return True


def test_site_content():
    log("Probando contenido del sitio")
    headers = {'Authorization': f'Bearer {TOKEN}'}

    # Leer (publico) - debe crear automaticamente si no existe
    r = requests.get(f"{BASE_URL}/api/site-content/about_us")
    if not check_response(r, 200, "GET /api/site-content/about_us"):
        return False

    # Actualizar (admin)
    r = requests.put(f"{BASE_URL}/api/admin/site-content/about_us", headers=headers, json={
        'title': 'Sobre Nosotros',
        'content': 'Este es el contenido de prueba'
    })
    if not check_response(r, 200, "PUT /api/admin/site-content/about_us"):
        return False

    # Leer de nuevo (publico) - debe tener el contenido actualizado
    r = requests.get(f"{BASE_URL}/api/site-content/about_us")
    if not check_response(r, 200, "GET /api/site-content/about_us (updated)"):
        return False
    content = r.json()
    if content['title'] != 'Sobre Nosotros':
        log("FAIL: El contenido no se actualizo correctamente", 'FAIL')
        return False
    log("OK: El contenido se actualizo correctamente", 'OK')
    return True


def test_audit_log():
    log("Probando bitacora de auditoria")
    headers = {'Authorization': f'Bearer {TOKEN}'}

    r = requests.get(f"{BASE_URL}/api/auth/audit", headers=headers)
    if not check_response(r, 200, "GET /api/auth/audit"):
        return False

    logs = r.json()['logs']
    if len(logs) == 0:
        log("WARN: No hay entradas en la bitacora (deberia haber al menos el LOGIN)", 'WARN')
    else:
        log(f"OK: Hay {len(logs)} entradas en la bitacora", 'OK')
    return True


def main():
    log("=== Iniciando pruebas del backend ===", 'INFO')
    log(f"Base URL: {BASE_URL}", 'INFO')

    # Credenciales del admin (cambiar si usaste otras en create_first_admin.py)
    email = input("Email del admin: ").strip()
    password = input("Password del admin: ").strip()

    results = []

    results.append(("Health check", test_health()))
    results.append(("Login", test_login(email, password)))

    if not TOKEN:
        log("FAIL: No se pudo obtener el token. Las pruebas restantes se omiten.", 'FAIL')
        sys.exit(1)

    results.append(("Auth me", test_auth_me()))
    results.append(("Categories", test_categories()))
    results.append(("Tags", test_tags()))
    results.append(("Providers", test_providers()))
    results.append(("Products", test_products()))
    results.append(("Site Content", test_site_content()))
    results.append(("Audit Log", test_audit_log()))

    log("\n=== Resumen de pruebas ===", 'INFO')
    passed = sum(1 for _, ok in results if ok)
    total = len(results)

    for name, ok in results:
        status = 'OK' if ok else 'FAIL'
        log(f"{name}: {status}", 'OK' if ok else 'FAIL')

    log(f"\nTotal: {passed}/{total} pruebas pasaron", 'OK' if passed == total else 'FAIL')

    if passed == total:
        log("Todas las pruebas pasaron. El backend esta listo.", 'OK')
        sys.exit(0)
    else:
        log("Algunas pruebas fallaron. Revisar los errores arriba.", 'FAIL')
        sys.exit(1)


if __name__ == '__main__':
    main()