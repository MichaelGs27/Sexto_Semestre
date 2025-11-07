# coordinator.py
from auth_server import generate_token
from worker_c import count_words_jwt

# 1. Simular login y obtener token
mi_token = generate_token(user_id="estudiante123")
print(f"COORDINATOR: Obtenido token: {mi_token[:30]}...")

# 2. Usar el token para llamar al worker
try:
    resultado = count_words_jwt("un texto de ejemplo", token=mi_token)
    print(f"Resultado de Worker C: {resultado} palabras")
except PermissionError as e:
    print(f"COORDINATOR: La llamada falló. Razón: {e}")
