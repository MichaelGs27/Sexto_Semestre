# vector_clocks.py
import random
import time
from threading import Thread, Lock

class Process:
    def __init__(self, process_id, num_processes):
        self.process_id = process_id
        # TODO: Inicializar el vector de relojes con ceros
        self.vector_clock = [0] * num_processes
        self.lock = Lock()
        self.message_queue = []
        self.log = []
        self.num_processes = num_processes
    
    def local_event(self):
        with self.lock:
            # TODO: Incrementar solo la posición correspondiente al proceso actual
            self.vector_clock[self.process_id] += 1
            event = f"Proceso {self.process_id}: Evento local con vector {self.vector_clock}"
            self.log.append((self.vector_clock.copy(), event))
            print(event)
    
    def send_message(self, receiver_id):
        with self.lock:
            # TODO: Incrementar la posición del proceso actual en el vector
            self.vector_clock[self.process_id] += 1
            message = {
                "sender": self.process_id,
                "vector_clock": self.vector_clock.copy(),
                "content": f"Mensaje de {self.process_id} a {receiver_id}"
            }
            event = f"Proceso {self.process_id}: Envío a P{receiver_id} con vector {self.vector_clock}"
            self.log.append((self.vector_clock.copy(), event))
            print(event)
            return message
    
    def receive_message(self, message):
        with self.lock:
            # TODO: Actualizar el vector de relojes según las reglas
            # 1. Tomar el máximo elemento por elemento
            # 2. Incrementar la posición del proceso actual
            received_vector = message["vector_clock"]
            for i in range(self.num_processes):
                self.vector_clock[i] = max(self.vector_clock[i], received_vector[i])
            self.vector_clock[self.process_id] += 1
            
            event = f"Proceso {self.process_id}: Recibido de P{message['sender']} con vector {self.vector_clock}"
            self.log.append((self.vector_clock.copy(), event))
            print(event)
    
    def run(self, processes):
        # Mismo código que en el ejemplo anterior
        pass

# TODO: Implementar una función para comparar dos vectores de relojes
def compare_vectors(vector1, vector2):
    """
    Compara dos vectores de relojes y determina su relación causal.
    Retorna: 
        -1 si vector1 -> vector2 (vector1 sucedió antes que vector2)
        1 si vector2 -> vector1 (vector2 sucedió antes que vector1)
        0 si son concurrentes
    """
    less_than = False
    greater_than = False
    
    for v1, v2 in zip(vector1, vector2):
        if v1 < v2:
            less_than = True
        elif v1 > v2:
            greater_than = True
        
        if less_than and greater_than:
            return 0  # Concurrentes
    
    if less_than:
        return -1  # vector1 sucedió antes que vector2
    if greater_than:
        return 1   # vector2 sucedió antes que vector1
    return 0       # Iguales (mismo evento)

def main():
    # Código similar al ejemplo anterior, pero añadiendo análisis de causalidad
    pass

if __name__ == "__main__":
    main()