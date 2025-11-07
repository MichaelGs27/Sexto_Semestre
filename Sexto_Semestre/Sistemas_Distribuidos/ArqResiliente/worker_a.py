# worker_a.py
import time
import random

def process_text_to_upper(text):
    # Simular trabajo y posible fallo
    if random.random() < 0.3: # 30% de probabilidad de fallar
        print("WORKER A: ¡Oh no! He fallado.")
        raise ConnectionError("No se pudo conectar con el worker A")
    print("WORKER A: Procesando texto a mayúsculas.")
    time.sleep(2) # Simular latencia de red
    return text.upper()