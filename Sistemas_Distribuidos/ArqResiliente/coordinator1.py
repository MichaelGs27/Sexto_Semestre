# coordinator.py con Circuit Breaker
import pybreaker
from worker_a import process_text_to_upper

# Crear un "cortocircuito". Si falla 2 veces en 60s, se abre por 30s.
breaker = pybreaker.CircuitBreaker(fail_max=2, reset_timeout=30)

# Anotar la función que queremos proteger
@breaker
def call_worker_a(text):
    return process_text_to_upper(text)

def handle_request(text):
    print("COORDINATOR: Recibí una petición. Intentaré llamar a Worker A a través del Circuit Breaker.")
    try:
        result_a = call_worker_a(text)
        print(f"COORDINATOR: Éxito. Resultado: {result_a}")
        return result_a
    except pybreaker.CircuitBreakerError:
        print("COORDINATOR: El Circuit Breaker está abierto. No llamaré a Worker A. Devolviendo respuesta alternativa.")
        return "Servicio no disponible temporalmente, intente más tarde. (Respuesta de Fallback)"
    except ConnectionError:
         print("COORDINATOR: Worker A falló, pero el Circuit Breaker lo registró.")
         return "ERROR: El servicio falló en este intento."

# Simular múltiples peticiones para ver el breaker en acción
for i in range(10):
    print(f"\n--- Intento #{i+1} ---")
    handle_request("hola mundo")
