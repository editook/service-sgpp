import urllib.request
import json

BASE_URL = "https://service-sgpp.fly.dev/api/v1"

# 1. Login
data = b"username=admin&password=admin123"
req = urllib.request.Request(f"{BASE_URL}/auth/login", data=data)
req.add_header("Content-Type", "application/x-www-form-urlencoded")

try:
    with urllib.request.urlopen(req) as f:
        response = json.loads(f.read().decode('utf-8'))
        token = response["access_token"]
except urllib.error.HTTPError as e:
    print("Login failed:", e.read().decode())
    exit(1)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "codigo_unico": "CASO-TEST-1",
    "nombre_evaluado": "Juan Perez",
    "tipo_delito": "Otro",
    "coeficiente_id": 1,
    "perito_id": 1,
    "departamento": "La Paz",
    "fecha_ingreso": "2026-03-01",
    "plazo_dias": 10,
    "fecha_requerimiento": None,
    "tipo_requerimiento": None,
    "estado_proceso": None,
    "estado_proceso_detalle": None,
    "estado_pericia": None,
    "estado_pericia_fecha_programada": None,
    "estado_pericia_detalle_representacion": None,
    "estado_pericia_fecha_evaluacion": None,
    "estado_pericia_tiempo_entrega": None,
    "estado_pericia_fecha_entrega": None,
    "sujeto_procesal": None,
    "sujeto_procesal_detalle": None,
    "tipo_delito_detalle": None,
    "sexo": None,
    "edad": None,
    "tiene_consultor_tecnico": False
}

req_case = urllib.request.Request(f"{BASE_URL}/cases/", data=json.dumps(payload).encode('utf-8'), headers=headers)
try:
    with urllib.request.urlopen(req_case) as f:
        print(f"Success: {f.read().decode()}")
except urllib.error.HTTPError as e:
    print(f"Error {e.code}: {e.read().decode()}")
