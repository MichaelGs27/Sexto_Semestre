# Ejemplo Práctico: Coordinación Distribuida

## Objetivos de Aprendizaje

- Implementar un algoritmo básico de elección de líder en un sistema distribuido
- Comprender los mecanismos de exclusión mutua distribuida
- Desarrollar un sistema simple de detección de fallos

## Requisitos Previos

- Python 3.6 o superior
- Biblioteca ZeroMQ (`pip install pyzmq`)
- Conocimientos básicos de programación en Python
- Entendimiento conceptual de coordinación distribuida

## Implementación de un Algoritmo de Elección de Líder (Bully)

### Descripción

En este ejemplo, implementaremos una versión simplificada del algoritmo Bully para elección de líder. Este algoritmo permite que un grupo de procesos elija a uno de ellos como coordinador basándose en sus identificadores.

### Principios del Algoritmo Bully

1. Cada proceso tiene un identificador único.
2. El proceso con el ID más alto se convierte en el líder.
3. Cuando un proceso detecta que el líder actual no responde, inicia una elección.
4. Durante una elección, un proceso envía mensajes a todos los procesos con IDs mayores.
5. Si ningún proceso con ID mayor responde, el proceso se declara líder.
6. Si algún proceso con ID mayor responde, ese proceso toma el control de la elección.

### Código Base

```python
# bully_algorithm.py
import time
import random
import threading
import zmq
from datetime import datetime

class Process:
    def __init__(self, process_id, total_processes, base_port=5550):
        self.id = process_id
        self.total_processes = total_processes
        self.base_port = base_port
        self.leader_id = None
        self.active = True
        self.election_in_progress = False
        
        # Configuración de ZeroMQ
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind(f"tcp://*:{self.base_port + self.id}")
        
        self.senders = {}
        for i in range(total_processes):
            if i != self.id:
                sender = self.context.socket(zmq.PUSH)
                sender.connect(f"tcp://localhost:{self.base_port + i}")
                self.senders[i] = sender
        
        # Iniciar hilos
        self.receiver_thread = threading.Thread(target=self.receive_messages)
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeats)
        self.election_thread = None
    
    def start(self):
        print(f"Proceso {self.id} iniciado")
        self.receiver_thread.start()
        self.heartbeat_thread.start()
        
        # Si soy el proceso con ID más alto, inicio como líder
        if self.id == self.total_processes - 1:
            self.become_leader()
        else:
            # Esperar un momento para que todos los procesos se inicien
            time.sleep(2)
            self.start_election()
    
    def receive_messages(self):
        while self.active:
            try:
                message = self.receiver.recv_json(flags=zmq.NOBLOCK)
                self.process_message(message)
            except zmq.ZMQError:
                pass
            time.sleep(0.1)
    
    def process_message(self, message):
        msg_type = message.get("type")
        sender_id = message.get("sender_id")
        
        if msg_type == "ELECTION":
            print(f"Proceso {self.id} recibió mensaje de elección de {sender_id}")
            # Responder al remitente que hay un proceso con ID mayor
            self.send_message(sender_id, {"type": "RESPONSE", "sender_id": self.id})
            # Iniciar mi propia elección
            if not self.election_in_progress:
                self.start_election()
        
        elif msg_type == "RESPONSE":
            print(f"Proceso {self.id} recibió respuesta de {sender_id}")
            self.election_in_progress = False
        
        elif msg_type == "COORDINATOR":
            print(f"Proceso {self.id} recibió anuncio de coordinador: {sender_id}")
            self.leader_id = sender_id
            self.election_in_progress = False
        
        elif msg_type == "HEARTBEAT":
            # Solo procesar heartbeats si vienen del líder actual
            if sender_id == self.leader_id:
                print(f"Proceso {self.id} recibió heartbeat del líder {sender_id}")
    
    def send_message(self, target_id, message):
        if target_id in self.senders:
            self.senders[target_id].send_json(message)
    
    def broadcast_message(self, message):
        for target_id in self.senders:
            self.send_message(target_id, message)
    
    def start_election(self):
        print(f"Proceso {self.id} inicia elección")
        self.election_in_progress = True
        self.leader_id = None
        
        # Enviar mensaje de elección a todos los procesos con ID mayor
        higher_processes_exist = False
        for i in range(self.id + 1, self.total_processes):
            if i in self.senders:
                higher_processes_exist = True
                self.send_message(i, {"type": "ELECTION", "sender_id": self.id})
        
        # Si no hay procesos con ID mayor, me convierto en líder
        if not higher_processes_exist:
            self.become_leader()
        else:
            # Esperar respuestas por un tiempo
            def wait_for_responses():
                time.sleep(2)  # Esperar 2 segundos por respuestas
                if self.election_in_progress:
                    # Si aún estamos en elección, no recibimos respuestas de procesos mayores
                    self.become_leader()
            
            self.election_thread = threading.Thread(target=wait_for_responses)
            self.election_thread.start()
    
    def become_leader(self):
        print(f"Proceso {self.id} se convierte en líder")
        self.leader_id = self.id
        self.election_in_progress = False
        
        # Anunciar a todos los procesos
        self.broadcast_message({"type": "COORDINATOR", "sender_id": self.id})
    
    def send_heartbeats(self):
        while self.active:
            if self.leader_id == self.id:  # Si soy el líder
                print(f"Líder {self.id} enviando heartbeat")
                self.broadcast_message({"type": "HEARTBEAT", "sender_id": self.id})
            time.sleep(1)
    
    def simulate_failure(self):
        print(f"Proceso {self.id} simulando fallo")
        self.active = False
        time.sleep(5)  # Simular fallo por 5 segundos
        self.active = True
        print(f"Proceso {self.id} recuperado")
        # Reiniciar hilos
        if not self.receiver_thread.is_alive():
            self.receiver_thread = threading.Thread(target=self.receive_messages)
            self.receiver_thread.start()
        if not self.heartbeat_thread.is_alive():
            self.heartbeat_thread = threading.Thread(target=self.send_heartbeats)
            self.heartbeat_thread.start()

def main():
    total_processes = 4
    processes = []
    
    # Crear procesos
    for i in range(total_processes):
        processes.append(Process(i, total_processes))
    
    # Iniciar procesos
    for p in processes:
        p.start()
    
    # Esperar un tiempo para que se establezca el líder
    time.sleep(5)
    
    # Simular fallo del líder después de un tiempo
    time.sleep(10)
    leader_index = total_processes - 1  # El proceso con ID más alto
    print(f"\nSimulando fallo del líder (Proceso {leader_index})...")
    processes[leader_index].simulate_failure()
    
    # Mantener el programa en ejecución
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Terminando procesos...")
        for p in processes:
            p.active = False

if __name__ == "__main__":
    main()
```

### Ejecución y Resultados Esperados

Al ejecutar este código, verás:

1. Los procesos se inician y el proceso con el ID más alto se convierte en líder.
2. El líder envía heartbeats periódicos a todos los demás procesos.
3. Después de un tiempo, se simula un fallo del líder.
4. Los demás procesos detectan el fallo e inician una nueva elección.
5. Un nuevo líder es elegido (el proceso con el siguiente ID más alto).

Este ejemplo muestra cómo los sistemas distribuidos pueden auto-organizarse para mantener un coordinador incluso cuando ocurren fallos.

## Ejercicio: Implementación de Exclusión Mutua Distribuida

### Descripción

En este ejercicio, implementaremos un algoritmo simple de exclusión mutua distribuida utilizando el algoritmo de Ricart-Agrawala, que permite a múltiples procesos acceder a un recurso compartido de manera segura.

### Instrucciones

1. Extiende el código base para implementar el algoritmo de Ricart-Agrawala:
   - Cada proceso debe poder solicitar acceso a un recurso compartido.
   - Cuando un proceso quiere acceder al recurso, envía una solicitud a todos los demás.
   - Los demás procesos responden según sus propias solicitudes y relojes lógicos.
   - Un proceso puede acceder al recurso cuando ha recibido respuestas de todos los demás.

### Código Base para el Ejercicio

```python
# distributed_mutex.py
import time
import random
import threading
import zmq
from datetime import datetime

class Process:
    def __init__(self, process_id, total_processes, base_port=5550):
        self.id = process_id
        self.total_processes = total_processes
        self.base_port = base_port
        self.clock = 0  # Reloj lógico de Lamport
        self.active = True
        
        # Estado para exclusión mutua
        self.requesting_resource = False
        self.request_timestamp = 0
        self.replies_received = set()
        self.deferred_replies = []
        
        # Configuración de ZeroMQ
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind(f"tcp://*:{self.base_port + self.id}")
        
        self.senders = {}
        for i in range(total_processes):
            if i != self.id:
                sender = self.context.socket(zmq.PUSH)
                sender.connect(f"tcp://localhost:{self.base_port + i}")
                self.senders[i] = sender
        
        # Iniciar hilo receptor
        self.receiver_thread = threading.Thread(target=self.receive_messages)
        self.receiver_thread.daemon = True
    
    def start(self):
        print(f"Proceso {self.id} iniciado")
        self.receiver_thread.start()
    
    def receive_messages(self):
        while self.active:
            try:
                message = self.receiver.recv_json(flags=zmq.NOBLOCK)
                self.process_message(message)
            except zmq.ZMQError:
                pass
            time.sleep(0.1)
    
    def process_message(self, message):
        msg_type = message.get("type")
        sender_id = message.get("sender_id")
        timestamp = message.get("timestamp", 0)
        
        # Actualizar reloj lógico
        self.clock = max(self.clock, timestamp) + 1
        
        if msg_type == "REQUEST":
            # TODO: Implementar lógica para procesar solicitudes de recurso
            # Si no estoy solicitando el recurso o mi solicitud tiene mayor timestamp,
            # enviar REPLY inmediatamente
            # Si no, diferir la respuesta
            pass
        
        elif msg_type == "REPLY":
            # TODO: Implementar lógica para procesar respuestas
            # Añadir el remitente a las respuestas recibidas
            # Verificar si ya podemos acceder al recurso
            pass
    
    def send_message(self, target_id, message):
        # Añadir timestamp al mensaje
        message["timestamp"] = self.clock
        if target_id in self.senders:
            self.senders[target_id].send_json(message)
    
    def broadcast_message(self, message):
        for target_id in self.senders:
            self.send_message(target_id, message)
    
    def request_resource(self):
        # TODO: Implementar solicitud de recurso
        # 1. Actualizar estado y timestamp
        # 2. Enviar solicitud a todos los procesos
        # 3. Esperar respuestas
        pass
    
    def release_resource(self):
        # TODO: Implementar liberación de recurso
        # 1. Actualizar estado
        # 2. Enviar respuestas diferidas
        pass
    
    def use_resource(self):
        print(f"Proceso {self.id} solicitando recurso...")
        self.request_resource()
        
        # Esperar hasta obtener el recurso
        while self.requesting_resource:
            time.sleep(0.1)
        
        print(f"Proceso {self.id} accediendo al recurso")
        time.sleep(random.uniform(1, 3))  # Simular uso del recurso
        
        print(f"Proceso {self.id} liberando recurso")
        self.release_resource()

def main():
    total_processes = 3
    processes = []
    
    # Crear procesos
    for i in range(total_processes):
        processes.append(Process(i, total_processes))
    
    # Iniciar procesos
    for p in processes:
        p.start()
    
    # Esperar un momento para que todos los procesos se inicien
    time.sleep(2)
    
    # Simular solicitudes de recurso
    for _ in range(2):  # Cada proceso intenta acceder al recurso 2 veces
        threads = []
        for p in processes:
            t = threading.Thread(target=p.use_resource)
            threads.append(t)
            t.start()
            time.sleep(random.uniform(0.5, 1.5))  # Pequeño retraso entre solicitudes
        
        for t in threads:
            t.join()
    
    # Mantener el programa en ejecución un momento más
    time.sleep(5)
    print("Terminando procesos...")
    for p in processes:
        p.active = False

if __name__ == "__main__":
    main()
```

### Desafío Adicional

Una vez implementado el algoritmo básico de exclusión mutua, añade las siguientes mejoras:

1. Implementa un mecanismo de detección de interbloqueos (deadlocks).
2. Añade un timeout para las solicitudes de recurso, para evitar esperas indefinidas.
3. Implementa una cola de prioridad para las solicitudes basada en los timestamps.

## Implementación de un Servicio de Coordinación Simple (Estilo ZooKeeper)

### Descripción

Para complementar los ejemplos anteriores, aquí hay un ejemplo simplificado de cómo implementar un servicio de coordinación básico inspirado en ZooKeeper o etcd.

```python
# simple_coordinator.py
import time
import threading
import zmq
import json
from collections import defaultdict

class CoordinationService:
    def __init__(self, port=5555):
        self.port = port
        self.data = {}  # Almacén clave-valor
        self.watches = defaultdict(set)  # Observadores por clave
        self.lock = threading.Lock()
        self.active = True
        
        # Configuración de ZeroMQ
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind(f"tcp://*:{self.port}")
        
        # Iniciar hilo de servicio
        self.service_thread = threading.Thread(target=self.run_service)
        self.service_thread.daemon = True
    
    def start(self):
        print(f"Servicio de coordinación iniciado en puerto {self.port}")
        self.service_thread.start()
    
    def run_service(self):
        while self.active:
            try:
                message = self.socket.recv_json()
                response = self.process_request(message)
                self.socket.send_json(response)
            except Exception as e:
                print(f"Error en el servicio: {e}")
                self.socket.send_json({"status": "error", "message": str(e)})
    
    def process_request(self, request):
        operation = request.get("operation")
        path = request.get("path")
        
        with self.lock:
            if operation == "GET":
                return self.get_data(path)
            elif operation == "SET":
                value = request.get("value")
                watch = request.get("watch", False)
                return self.set_data(path, value, watch)
            elif operation == "DELETE":
                return self.delete_data(path)
            elif operation == "WATCH":
                client_id = request.get("client_id")
                return self.add_watch(path, client_id)
            elif operation == "LIST":
                return self.list_children(path)
            else:
                return {"status": "error", "message": "Operación no soportada"}
    
    def get_data(self, path):
        if path in self.data:
            return {"status": "ok", "value": self.data[path]}
        else:
            return {"status": "error", "message": "Ruta no encontrada"}
    
    def set_data(self, path, value, watch=False):
        old_value = self.data.get(path)
        self.data[path] = value
        
        # Notificar a los observadores
        if path in self.watches and old_value != value:
            self.notify_watches(path, value)
        
        return {"status": "ok"}
    
    def delete_data(self, path):
        if path in self.data:
            del self.data[path]
            
            # Notificar a los observadores
            if path in self.watches:
                self.notify_watches(path, None)
            
            return {"status": "ok"}
        else:
            return {"status": "error", "message": "Ruta no encontrada"}
    
    def add_watch(self, path, client_id):
        self.watches[path].add(client_id)
        return {"status": "ok"}
    
    def list_children(self, path):
        # Listar todas las claves que comienzan con path/
        if not path.endswith('/'):
            path += '/'
        
        children = [k[len(path):].split('/')[0] for k in self.data.keys() 
                   if k.startswith(path) and k != path]
        
        # Eliminar duplicados
        children = list(set(children))
        
        return {"status": "ok", "children": children}
    
    def notify_watches(self, path, value):
        # En una implementación real, esto enviaría notificaciones a los clientes
        print(f"Notificando cambio en {path}: {value} a {self.watches[path]}")

class CoordinationClient:
    def __init__(self, client_id, server_port=5555):
        self.client_id = client_id
        self.server_port = server_port
        
        # Configuración de ZeroMQ
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(f"tcp://localhost:{self.server_port}")
    
    def get(self, path):
        request = {
            "operation": "GET",
            "path": path
        }
        self.socket.send_json(request)
        return self.socket.recv_json()
    
    def set(self, path, value, watch=False):
        request = {
            "operation": "SET",
            "path": path,
            "value": value,
            "watch": watch
        }
        self.socket.send_json(request)
        return self.socket.recv_json()
    
    def delete(self, path):
        request = {
            "operation": "DELETE",
            "path": path
        }
        self.socket.send_json(request)
        return self.socket.recv_json()
    
    def watch(self, path):
        request = {
            "operation": "WATCH",
            "path": path,
            "client_id": self.client_id
        }
        self.socket.send_json(request)
        return self.socket.recv_json()
    
    def list_children(self, path):
        request = {
            "operation": "LIST",
            "path": path
        }
        self.socket.send_json(request)
        return self.socket.recv_json()

def main():
    # Iniciar servicio de coordinación
    service = CoordinationService()
    service.start()
    
    # Esperar a que el servicio esté listo
    time.sleep(1)
    
    # Crear algunos clientes
    clients = [CoordinationClient(f"client-{i}") for i in range(3)]
    
    # Cliente 1 crea algunos datos
    print("Cliente 1 creando datos...")
    clients[0].set("/config", {"max_connections": 100})
    clients[0].set("/status", "running")
    clients[0].set("/locks/resource1", "free")
    
    # Cliente 2 lee datos
    print("\nCliente 2 leyendo datos...")
    print(f"Config: {clients[1].get('/config')}")
    print(f"Status: {clients[1].get('/status')}")
    
    # Cliente 3 observa un recurso y lo adquiere
    print("\nCliente 3 observando y adquiriendo recurso...")
    clients[2].watch("/locks/resource1")
    print(f"Estado inicial del recurso: {clients[2].get('/locks/resource1')}")
    clients[2].set("/locks/resource1", "locked_by_client3")
    
    # Cliente 1 lista los recursos disponibles
    print("\nCliente 1 listando recursos...")
    print(f"Recursos: {clients[0].list_children('/locks')}")
    
    # Mantener el programa en ejecución un momento
    time.sleep(2)
    print("\nTerminando servicio...")
    service.active = False

if __name__ == "__main__":
    main()
```

### Aplicaciones Prácticas

Los mecanismos de coordinación distribuida tienen numerosas aplicaciones:

1. **Elección de líder**: Designar un nodo para tareas especiales como balanceo de carga o agregación.
2. **Exclusión mutua**: Garantizar acceso seguro a recursos compartidos en sistemas distribuidos.
3. **Servicios de configuración**: Mantener configuraciones consistentes entre múltiples nodos.
4. **Descubrimiento de servicios**: Permitir que los nodos encuentren y se comuniquen entre sí.
5. **Gestión de bloqueos distribuidos**: Coordinar el acceso a recursos compartidos.

## Preguntas de Reflexión

1. ¿Qué ventajas y desventajas tiene el algoritmo Bully para elección de líder?
2. ¿Cómo afecta la latencia de red al rendimiento de los algoritmos de exclusión mutua distribuida?
3. ¿En qué situaciones es preferible utilizar un servicio de coordinación centralizado (como ZooKeeper) frente a algoritmos distribuidos puros?
4. ¿Cómo se podría mejorar la tolerancia a fallos en los ejemplos presentados?

## Referencias

1. Ricart, G., & Agrawala, A. K. (1981). An optimal algorithm for mutual exclusion in computer networks. Communications of the ACM, 24(1), 9-17.
2. Garcia-Molina, H. (1982). Elections in a distributed computing system. IEEE Transactions on Computers, 100(1), 48-59.
3. Hunt, P., Konar, M., Junqueira, F. P., & Reed, B. (2010). ZooKeeper: Wait-free coordination for internet-scale systems. USENIX Annual Technical Conference.
