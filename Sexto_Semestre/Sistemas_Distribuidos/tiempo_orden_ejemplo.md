# Ejemplo Práctico: Tiempo y Orden en Sistemas Distribuidos

## Objetivos de Aprendizaje

- Implementar relojes lógicos de Lamport en un sistema distribuido simple
- Visualizar la relación "sucedió antes" entre eventos distribuidos
- Detectar causalidad entre mensajes utilizando relojes vectoriales

## Requisitos Previos

- Python 3.6 o superior
- Conocimientos básicos de programación en Python
- Entendimiento conceptual de relojes lógicos y vectoriales

## Implementación de Relojes Lógicos de Lamport

### Descripción

En este ejemplo, implementaremos un sistema simple que simula la comunicación entre tres procesos distribuidos utilizando relojes lógicos de Lamport para establecer un orden parcial de eventos.

### Código Base

```python
# lamport_clocks.py
import random
import time
from threading import Thread, Lock

class Process:
    def __init__(self, process_id, num_processes):
        self.process_id = process_id
        self.clock = 0
        self.lock = Lock()
        self.message_queue = []
        self.log = []
        self.num_processes = num_processes
    
    def local_event(self):
        with self.lock:
            self.clock += 1
            event = f"Proceso {self.process_id}: Evento local en tiempo {self.clock}"
            self.log.append((self.clock, event))
            print(event)
    
    def send_message(self, receiver_id):
        with self.lock:
            self.clock += 1
            message = {
                "sender": self.process_id,
                "clock": self.clock,
                "content": f"Mensaje de {self.process_id} a {receiver_id}"
            }
            event = f"Proceso {self.process_id}: Envío a P{receiver_id} en tiempo {self.clock}"
            self.log.append((self.clock, event))
            print(event)
            return message
    
    def receive_message(self, message):
        with self.lock:
            sender_clock = message["clock"]
            self.clock = max(self.clock, sender_clock) + 1
            event = f"Proceso {self.process_id}: Recibido de P{message['sender']} en tiempo {self.clock}"
            self.log.append((self.clock, event))
            print(event)
    
    def run(self, processes):
        for _ in range(5):  # Cada proceso ejecuta 5 acciones
            time.sleep(random.uniform(0.1, 0.5))
            action = random.choice(["local", "send"])
            
            if action == "local":
                self.local_event()
            else:
                # Elegir un proceso aleatorio para enviar un mensaje
                receiver_id = random.choice([i for i in range(self.num_processes) if i != self.process_id])
                message = self.send_message(receiver_id)
                processes[receiver_id].message_queue.append(message)
        
        # Procesar mensajes recibidos
        while self.message_queue:
            message = self.message_queue.pop(0)
            self.receive_message(message)

def main():
    num_processes = 3
    processes = [Process(i, num_processes) for i in range(num_processes)]
    
    # Crear hilos para cada proceso
    threads = []
    for i in range(num_processes):
        thread = Thread(target=processes[i].run, args=(processes,))
        threads.append(thread)
        thread.start()
    
    # Esperar a que todos los hilos terminen
    for thread in threads:
        thread.join()
    
    # Mostrar el log de eventos ordenados por tiempo lógico
    print("\nLog de eventos ordenados por tiempo lógico:")
    all_events = []
    for p in processes:
        all_events.extend(p.log)
    
    for clock, event in sorted(all_events):
        print(f"[Tiempo {clock}] {event}")

if __name__ == "__main__":
    main()
```

### Ejecución y Resultados Esperados

Al ejecutar este código, verás cómo tres procesos generan eventos locales y se envían mensajes entre sí. Cada proceso mantiene su propio reloj lógico que se incrementa en eventos locales y se actualiza al recibir mensajes, siguiendo las reglas de Lamport:

1. Antes de ejecutar un evento, un proceso incrementa su contador.
2. Al enviar un mensaje, el proceso incluye su valor de contador actual.
3. Al recibir un mensaje, el proceso actualiza su contador al máximo entre su valor actual y el valor recibido, y luego lo incrementa.

El resultado final muestra todos los eventos ordenados según sus marcas de tiempo lógicas, estableciendo un orden parcial consistente con la relación "sucedió antes".

## Ejercicio: Implementación de Relojes Vectoriales

### Descripción

Ahora extenderemos el ejemplo para implementar relojes vectoriales, que nos permiten detectar la causalidad entre eventos (no solo establecer un orden parcial).

### Instrucciones

1. Modifica la clase `Process` para que utilice un vector de relojes en lugar de un único contador.
2. Implementa las reglas de actualización para relojes vectoriales:
   - En un evento local, el proceso incrementa solo su propia posición en el vector.
   - Al enviar un mensaje, el proceso incluye su vector de relojes completo.
   - Al recibir un mensaje, el proceso actualiza su vector tomando el máximo elemento por elemento entre su vector actual y el recibido, y luego incrementa su propia posición.
3. Añade una función para detectar si dos eventos están causalmente relacionados, son concurrentes o si uno sucedió antes que otro.

### Código Base para el Ejercicio

```python
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
```

### Desafío Adicional

Una vez implementados los relojes vectoriales, añade una función que analice el log de eventos y muestre:

1. Pares de eventos que están causalmente relacionados
2. Pares de eventos que son concurrentes
3. Una visualización simple de la relación "sucedió antes" como un grafo dirigido

## Aplicaciones Prácticas

Los relojes lógicos y vectoriales tienen numerosas aplicaciones en sistemas distribuidos:

1. **Ordenamiento de eventos**: Determinar un orden consistente de operaciones en bases de datos distribuidas.
2. **Detección de causalidad**: Identificar dependencias entre eventos en sistemas de mensajería.
3. **Depuración distribuida**: Rastrear la secuencia de eventos que llevaron a un error.
4. **Consistencia eventual**: Implementar mecanismos de reconciliación en sistemas con replicación.

## Preguntas de Reflexión

1. ¿Por qué los relojes físicos no son suficientes para ordenar eventos en sistemas distribuidos?
2. ¿En qué situaciones los relojes de Lamport no proporcionan suficiente información y se necesitan relojes vectoriales?
3. ¿Cómo afecta el tamaño del sistema (número de procesos) a la escalabilidad de los relojes vectoriales?
4. ¿Qué estrategias podrían implementarse para reducir la sobrecarga de los relojes vectoriales en sistemas grandes?

## Referencias

1. Lamport, L. (1978). Time, clocks, and the ordering of events in a distributed system. Communications of the ACM, 21(7), 558-565.
2. Mattern, F. (1989). Virtual time and global states of distributed systems. Parallel and Distributed Algorithms, 215-226.
3. Fidge, C. J. (1988). Timestamps in message-passing systems that preserve the partial ordering. Proceedings of the 11th Australian Computer Science Conference, 10, 56-66.
