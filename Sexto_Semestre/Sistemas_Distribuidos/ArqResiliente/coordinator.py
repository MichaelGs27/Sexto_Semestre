# coordinator.py
# Importamos la "función-servicio" directamente
from worker_a import process_text_to_upper

def handle_request(text):
    print("COORDINATOR: Recibí una petición. Necesito ayuda de Worker A.")
    try:
        result_a = process_text_to_upper(text)
        print(f"COORDINATOR: Éxito. Resultado: {result_a}")
        return result_a
    except ConnectionError as e:
        print(f"COORDINATOR: La operación falló porque Worker A no responde. Error: {e}")
        return "ERROR: El servicio no está disponible."

# Simular una petición de un cliente
print("--- Intentando procesar 'hola mundo' ---")
handle_request("hola mundo")
