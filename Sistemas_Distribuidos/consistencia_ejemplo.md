# Ejemplo Práctico: Modelos de Consistencia

## Objetivos de Aprendizaje

- Comprender los diferentes modelos de consistencia en sistemas distribuidos
- Implementar un sistema con consistencia eventual y resolución de conflictos
- Experimentar con quórums para lograr diferentes niveles de consistencia

## Requisitos Previos

- Python 3.6 o superior
- Biblioteca Flask (`pip install flask`)
- Biblioteca Requests (`pip install requests`)
- Conocimientos básicos de programación en Python
- Entendimiento conceptual de consistencia en sistemas distribuidos

## Implementación de un Sistema con Consistencia Eventual

### Descripción

En este ejemplo, implementaremos un sistema de almacenamiento clave-valor distribuido con consistencia eventual. El sistema constará de múltiples nodos que pueden recibir operaciones de lectura y escritura, y que se sincronizarán periódicamente.

### Código Base

```python
# eventual_consistency.py
import time
import json
import threading
import requests
from flask import Flask, request, jsonify
import random
import argparse
from datetime import datetime

class Node:
    def __init__(self, node_id, port, peer_ports=None):
        self.node_id = node_id
        self.port = port
        self.peer_ports = peer_ports or []
        self.data = {}  # Almacén clave-valor
        self.vector_clocks = {}  # Vector clocks para cada clave
        self.lock = threading.Lock()
        
        # Inicializar la aplicación Flask
        self.app = Flask(f"node-{node_id}")
        self.setup_routes()
        
        # Iniciar hilo de sincronización
        self.sync_thread = threading.Thread(target=self.sync_with_peers)
        self.sync_thread.daemon = True
        self.sync_thread.start()
    
    def setup_routes(self):
        @self.app.route('/get/<key>', methods=['GET'])
        def get_value(key):
            with self.lock:
                if key in self.data:
                    return jsonify({
                        "key": key,
                        "value": self.data[key],
                        "vector_clock": self.vector_clocks.get(key, {})
                    })
                else:
                    return jsonify({"error": "Key not found"}), 404
        
        @self.app.route('/put', methods=['POST'])
        def put_value():
            data = request.json
            key = data.get('key')
            value = data.get('value')
            client_vector_clock = data.get('vector_clock', {})
            
            with self.lock:
                # Actualizar vector clock
                current_vector_clock = self.vector_clocks.get(key, {})
                
                # Si es una actualización de un cliente
                if not client_vector_clock:
                    # Incrementar el contador para este nodo
                    current_vector_clock[str(self.node_id)] = current_vector_clock.get(str(self.node_id), 0) + 1
                else:
                    # Fusionar vector clocks (tomar el máximo para cada componente)
                    for node_id, count in client_vector_clock.items():
                        current_vector_clock[node_id] = max(current_vector_clock.get(node_id, 0), count)
                    
                    # Incrementar el contador para este nodo
                    current_vector_clock[str(self.node_id)] = current_vector_clock.get(str(self.node_id), 0) + 1
                
                # Actualizar datos y vector clock
                self.data[key] = value
                self.vector_clocks[key] = current_vector_clock
                
                return jsonify({
                    "status": "success",
                    "key": key,
                    "value": value,
                    "vector_clock": current_vector_clock
                })
        
        @self.app.route('/sync', methods=['POST'])
        def receive_sync():
            sync_data = request.json
            
            with self.lock:
                for key, item in sync_data.items():
                    remote_value = item['value']
                    remote_vector_clock = item['vector_clock']
                    
                    # Si la clave no existe localmente, simplemente la añadimos
                    if key not in self.data:
                        self.data[key] = remote_value
                        self.vector_clocks[key] = remote_vector_clock
                    else:
                        # Comparar vector clocks para resolver conflictos
                        local_vector_clock = self.vector_clocks[key]
                        
                        # Verificar si hay un conflicto
                        if self.is_concurrent(local_vector_clock, remote_vector_clock):
                            # Resolver conflicto (en este caso, elegimos arbitrariamente)
                            # En un sistema real, podríamos usar una estrategia más sofisticada
                            if self.node_id > int(list(remote_vector_clock.keys())[0]):
                                # Mantener valor local
                                pass
                            else:
                                # Usar valor remoto
                                self.data[key] = remote_value
                            
                            # Fusionar vector clocks
                            merged_clock = self.merge_vector_clocks(local_vector_clock, remote_vector_clock)
                            self.vector_clocks[key] = merged_clock
                        elif self.happens_before(local_vector_clock, remote_vector_clock):
                            # El valor remoto es más reciente
                            self.data[key] = remote_value
                            self.vector_clocks[key] = remote_vector_clock
                        # Si el valor local es más reciente, no hacemos nada
            
            return jsonify({"status": "sync_received"})
    
    def is_concurrent(self, vc1, vc2):
        """Determina si dos eventos son concurrentes según sus vector clocks."""
        less = False
        greater = False
        
        for node_id in set(vc1.keys()) | set(vc2.keys()):
            count1 = vc1.get(node_id, 0)
            count2 = vc2.get(node_id, 0)
            
            if count1 < count2:
                less = True
            elif count1 > count2:
                greater = True
            
            if less and greater:
                return True  # Concurrentes
        
        return False  # Uno sucede antes que el otro
    
    def happens_before(self, vc1, vc2):
        """Determina si vc1 sucedió antes que vc2."""
        less = False
        
        for node_id in set(vc1.keys()) | set(vc2.keys()):
            count1 = vc1.get(node_id, 0)
            count2 = vc2.get(node_id, 0)
            
            if count1 > count2:
                return False
            if count1 < count2:
                less = True
        
        return less  # vc1 sucedió antes que vc2 si al menos un contador es menor
    
    def merge_vector_clocks(self, vc1, vc2):
        """Fusiona dos vector clocks tomando el máximo para cada componente."""
        result = vc1.copy()
        
        for node_id, count in vc2.items():
            result[node_id] = max(result.get(node_id, 0), count)
        
        return result
    
    def sync_with_peers(self):
        """Sincroniza periódicamente con otros nodos."""
        while True:
            time.sleep(5)  # Sincronizar cada 5 segundos
            
            with self.lock:
                sync_data = {}
                for key in self.data:
                    sync_data[key] = {
                        'value': self.data[key],
                        'vector_clock': self.vector_clocks.get(key, {})
                    }
            
            # Enviar datos a todos los peers
            for port in self.peer_ports:
                try:
                    requests.post(f"http://localhost:{port}/sync", json=sync_data, timeout=1)
                except requests.exceptions.RequestException as e:
                    print(f"Error sincronizando con nodo en puerto {port}: {e}")
    
    def run(self):
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

def main():
    parser = argparse.ArgumentParser(description='Nodo con consistencia eventual')
    parser.add_argument('--id', type=int, required=True, help='ID del nodo')
    parser.add_argument('--port', type=int, required=True, help='Puerto del nodo')
    parser.add_argument('--peers', type=str, help='Puertos de los nodos pares (separados por comas)')
    
    args = parser.parse_args()
    
    peer_ports = []
    if args.peers:
        peer_ports = [int(p) for p in args.peers.split(',')]
    
    node = Node(args.id, args.port, peer_ports)
    node.run()

if __name__ == "__main__":
    main()
```

### Ejecución y Resultados Esperados

Para ejecutar este ejemplo, necesitarás abrir varias terminales y ejecutar el script con diferentes parámetros para cada nodo:

```bash
# Terminal 1 - Nodo 1
python eventual_consistency.py --id 1 --port 5001 --peers 5002,5003

# Terminal 2 - Nodo 2
python eventual_consistency.py --id 2 --port 5002 --peers 5001,5003

# Terminal 3 - Nodo 3
python eventual_consistency.py --id 3 --port 5003 --peers 5001,5002
```

Luego, puedes interactuar con los nodos usando curl o cualquier cliente HTTP:

```bash
# Escribir un valor en el nodo 1
curl -X POST -H "Content-Type: application/json" -d '{"key":"user1", "value":"Alice"}' http://localhost:5001/put

# Leer el valor desde el nodo 2 (puede no estar disponible inmediatamente)
curl http://localhost:5002/get/user1

# Escribir un valor diferente para la misma clave en el nodo 3
curl -X POST -H "Content-Type: application/json" -d '{"key":"user1", "value":"Bob"}' http://localhost:5003/put

# Esperar unos segundos para la sincronización y luego verificar el valor en todos los nodos
curl http://localhost:5001/get/user1
curl http://localhost:5002/get/user1
curl http://localhost:5003/get/user1
```

Observarás que:

1. Inicialmente, los nodos pueden tener valores diferentes para la misma clave.
2. Después de la sincronización, todos los nodos convergen al mismo valor.
3. Los vector clocks se utilizan para resolver conflictos y determinar qué valor debe prevalecer.

## Ejercicio: Implementación de un Sistema con Quórums

### Descripción

En este ejercicio, extenderemos el sistema anterior para implementar un modelo de consistencia basado en quórums. En lugar de permitir que cualquier nodo actualice los datos libremente, requeriremos que un número mínimo de nodos (quórum) confirme las operaciones de lectura y escritura.

### Instrucciones

1. Modifica el código base para implementar quórums de lectura y escritura.
2. Configura el sistema para que:
   - Las escrituras requieran confirmación de al menos W nodos.
   - Las lecturas consulten a al menos R nodos y devuelvan el valor más reciente.
   - W + R > N (donde N es el número total de nodos) para garantizar consistencia.

### Código Base para el Ejercicio

```python
# quorum_consistency.py
import time
import json
import threading
import requests
from flask import Flask, request, jsonify
import random
import argparse
from datetime import datetime
import concurrent.futures

class QuorumNode:
    def __init__(self, node_id, port, peer_ports=None, read_quorum=2, write_quorum=2):
        self.node_id = node_id
        self.port = port
        self.peer_ports = peer_ports or []
        self.data = {}  # Almacén clave-valor
        self.timestamps = {}  # Timestamps para cada clave
        self.lock = threading.Lock()
        self.read_quorum = read_quorum
        self.write_quorum = write_quorum
        
        # Inicializar la aplicación Flask
        self.app = Flask(f"node-{node_id}")
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/get/<key>', methods=['GET'])
        def get_value(key):
            # Implementación directa (sin quórum)
            with self.lock:
                if key in self.data:
                    return jsonify({
                        "key": key,
                        "value": self.data[key],
                        "timestamp": self.timestamps.get(key, 0)
                    })
                else:
                    return jsonify({"error": "Key not found"}), 404
        
        @self.app.route('/put', methods=['POST'])
        def put_value():
            # Implementación directa (sin quórum)
            data = request.json
            key = data.get('key')
            value = data.get('value')
            timestamp = data.get('timestamp', time.time())
            
            with self.lock:
                # Solo actualizar si el timestamp es más reciente
                current_timestamp = self.timestamps.get(key, 0)
                if timestamp > current_timestamp:
                    self.data[key] = value
                    self.timestamps[key] = timestamp
                
                return jsonify({
                    "status": "success",
                    "key": key,
                    "value": value,
                    "timestamp": timestamp
                })
        
        @self.app.route('/read_request/<key>', methods=['GET'])
        def read_request(key):
            """Endpoint para solicitudes de lectura de otros nodos."""
            with self.lock:
                if key in self.data:
                    return jsonify({
                        "key": key,
                        "value": self.data[key],
                        "timestamp": self.timestamps.get(key, 0)
                    })
                else:
                    return jsonify({"error": "Key not found"}), 404
        
        @self.app.route('/write_request', methods=['POST'])
        def write_request():
            """Endpoint para solicitudes de escritura de otros nodos."""
            data = request.json
            key = data.get('key')
            value = data.get('value')
            timestamp = data.get('timestamp', time.time())
            
            with self.lock:
                # Solo actualizar si el timestamp es más reciente
                current_timestamp = self.timestamps.get(key, 0)
                if timestamp > current_timestamp:
                    self.data[key] = value
                    self.timestamps[key] = timestamp
                    return jsonify({"status": "success"})
                else:
                    return jsonify({"status": "outdated"})
        
        @self.app.route('/client_read/<key>', methods=['GET'])
        def client_read(key):
            """Endpoint para lecturas de clientes con quórum."""
            # TODO: Implementar lectura con quórum
            # 1. Solicitar el valor a todos los nodos (incluyendo a sí mismo)
            # 2. Esperar respuestas del quórum de lectura
            # 3. Devolver el valor más reciente según el timestamp
            pass
        
        @self.app.route('/client_write', methods=['POST'])
        def client_write():
            """Endpoint para escrituras de clientes con quórum."""
            # TODO: Implementar escritura con quórum
            # 1. Generar un timestamp para la operación
            # 2. Enviar la solicitud de escritura a todos los nodos (incluyendo a sí mismo)
            # 3. Esperar confirmaciones del quórum de escritura
            # 4. Devolver éxito o fracaso según las confirmaciones recibidas
            pass
    
    def read_from_peers(self, key):
        """Solicita el valor de una clave a todos los nodos pares."""
        results = []
        
        # Leer del nodo local
        with self.lock:
            if key in self.data:
                results.append({
                    "key": key,
                    "value": self.data[key],
                    "timestamp": self.timestamps.get(key, 0),
                    "node_id": self.node_id
                })
        
        # Leer de los nodos pares
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_port = {
                executor.submit(self.read_from_node, port, key): port
                for port in self.peer_ports
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    if result and "error" not in result:
                        results.append(result)
                except Exception as e:
                    print(f"Error leyendo de nodo en puerto {port}: {e}")
        
        return results
    
    def read_from_node(self, port, key):
        """Lee una clave de un nodo específico."""
        try:
            response = requests.get(f"http://localhost:{port}/read_request/{key}", timeout=1)
            if response.status_code == 200:
                data = response.json()
                data["node_id"] = port  # Añadir ID del nodo para referencia
                return data
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def write_to_peers(self, key, value, timestamp):
        """Escribe un valor en todos los nodos pares."""
        results = []
        
        # Escribir en el nodo local
        with self.lock:
            current_timestamp = self.timestamps.get(key, 0)
            if timestamp > current_timestamp:
                self.data[key] = value
                self.timestamps[key] = timestamp
                results.append({"status": "success", "node_id": self.node_id})
            else:
                results.append({"status": "outdated", "node_id": self.node_id})
        
        # Escribir en los nodos pares
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_port = {
                executor.submit(self.write_to_node, port, key, value, timestamp): port
                for port in self.peer_ports
            }
            
            for future in concurrent.futures.as_completed(future_to_port):
                port = future_to_port[future]
                try:
                    result = future.result()
                    if result:
                        result["node_id"] = port
                        results.append(result)
                except Exception as e:
                    print(f"Error escribiendo en nodo en puerto {port}: {e}")
        
        return results
    
    def write_to_node(self, port, key, value, timestamp):
        """Escribe un valor en un nodo específico."""
        try:
            response = requests.post(
                f"http://localhost:{port}/write_request",
                json={"key": key, "value": value, "timestamp": timestamp},
                timeout=1
            )
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.exceptions.RequestException:
            return None
    
    def run(self):
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

def main():
    parser = argparse.ArgumentParser(description='Nodo con consistencia de quórum')
    parser.add_argument('--id', type=int, required=True, help='ID del nodo')
    parser.add_argument('--port', type=int, required=True, help='Puerto del nodo')
    parser.add_argument('--peers', type=str, help='Puertos de los nodos pares (separados por comas)')
    parser.add_argument('--read-quorum', type=int, default=2, help='Tamaño del quórum de lectura')
    parser.add_argument('--write-quorum', type=int, default=2, help='Tamaño del quórum de escritura')
    
    args = parser.parse_args()
    
    peer_ports = []
    if args.peers:
        peer_ports = [int(p) for p in args.peers.split(',')]
    
    node = QuorumNode(args.id, args.port, peer_ports, args.read_quorum, args.write_quorum)
    node.run()

if __name__ == "__main__":
    main()
```

### Desafío Adicional

Una vez implementado el sistema con quórums, añade las siguientes mejoras:

1. Implementa un mecanismo de "read repair" que actualice los nodos desactualizados durante las operaciones de lectura.
2. Añade soporte para diferentes niveles de consistencia que el cliente pueda especificar (ONE, QUORUM, ALL).
3. Implementa un mecanismo de "hinted handoff" para manejar nodos temporalmente no disponibles.

## Implementación de un CRDT Simple (Contador Incrementable)

### Descripción

Los CRDTs (Conflict-free Replicated Data Types) son estructuras de datos que pueden ser replicadas en múltiples nodos y fusionadas sin conflictos. Aquí implementaremos un contador G-Counter (Grow-only Counter) como ejemplo simple de CRDT.

```python
# crdt_counter.py
import time
import json
import threading
import requests
from flask import Flask, request, jsonify
import argparse

class GCounter:
    """
    G-Counter (Grow-only Counter) CRDT.
    Permite incrementos concurrentes sin conflictos.
    """
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.values = [0] * num_nodes
    
    def increment(self, amount=1):
        """Incrementa el contador para este nodo."""
        self.values[self.node_id] += amount
    
    def merge(self, other_counter):
        """Fusiona con otro contador tomando el máximo para cada posición."""
        for i in range(len(self.values)):
            self.values[i] = max(self.values[i], other_counter.values[i])
    
    def value(self):
        """Obtiene el valor total del contador."""
        return sum(self.values)
    
    def to_dict(self):
        """Convierte el contador a un diccionario para serialización."""
        return {"values": self.values}
    
    @classmethod
    def from_dict(cls, data, node_id):
        """Crea un contador a partir de un diccionario deserializado."""
        counter = cls(node_id, len(data["values"]))
        counter.values = data["values"]
        return counter

class CRDTNode:
    def __init__(self, node_id, port, num_nodes, peer_ports=None):
        self.node_id = node_id
        self.port = port
        self.num_nodes = num_nodes
        self.peer_ports = peer_ports or []
        self.counter = GCounter(node_id, num_nodes)
        self.lock = threading.Lock()
        
        # Inicializar la aplicación Flask
        self.app = Flask(f"node-{node_id}")
        self.setup_routes()
        
        # Iniciar hilo de sincronización
        self.sync_thread = threading.Thread(target=self.sync_with_peers)
        self.sync_thread.daemon = True
        self.sync_thread.start()
    
    def setup_routes(self):
        @self.app.route('/increment', methods=['POST'])
        def increment():
            data = request.json
            amount = data.get('amount', 1)
            
            with self.lock:
                self.counter.increment(amount)
            
            return jsonify({
                "status": "success",
                "new_value": self.counter.value()
            })
        
        @self.app.route('/value', methods=['GET'])
        def get_value():
            with self.lock:
                return jsonify({
                    "value": self.counter.value(),
                    "components": self.counter.values
                })
        
        @self.app.route('/sync', methods=['POST'])
        def receive_sync():
            data = request.json
            
            with self.lock:
                remote_counter = GCounter.from_dict(data, self.node_id)
                self.counter.merge(remote_counter)
            
            return jsonify({"status": "sync_received"})
    
    def sync_with_peers(self):
        """Sincroniza periódicamente con otros nodos."""
        while True:
            time.sleep(5)  # Sincronizar cada 5 segundos
            
            with self.lock:
                counter_data = self.counter.to_dict()
            
            # Enviar datos a todos los peers
            for port in self.peer_ports:
                try:
                    requests.post(f"http://localhost:{port}/sync", json=counter_data, timeout=1)
                except requests.exceptions.RequestException as e:
                    print(f"Error sincronizando con nodo en puerto {port}: {e}")
    
    def run(self):
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

def main():
    parser = argparse.ArgumentParser(description='Nodo CRDT (G-Counter)')
    parser.add_argument('--id', type=int, required=True, help='ID del nodo')
    parser.add_argument('--port', type=int, required=True, help='Puerto del nodo')
    parser.add_argument('--num-nodes', type=int, required=True, help='Número total de nodos')
    parser.add_argument('--peers', type=str, help='Puertos de los nodos pares (separados por comas)')
    
    args = parser.parse_args()
    
    peer_ports = []
    if args.peers:
        peer_ports = [int(p) for p in args.peers.split(',')]
    
    node = CRDTNode(args.id, args.port, args.num_nodes, peer_ports)
    node.run()

if __name__ == "__main__":
    main()
```

Para ejecutar este ejemplo, abre varias terminales:

```bash
# Terminal 1 - Nodo 0
python crdt_counter.py --id 0 --port 5001 --num-nodes 3 --peers 5002,5003

# Terminal 2 - Nodo 1
python crdt_counter.py --id 1 --port 5002 --num-nodes 3 --peers 5001,5003

# Terminal 3 - Nodo 2
python crdt_counter.py --id 2 --port 5003 --num-nodes 3 --peers 5001,5002
```

Luego, puedes incrementar el contador en diferentes nodos:

```bash
# Incrementar en el nodo 0
curl -X POST -H "Content-Type: application/json" -d '{"amount": 5}' http://localhost:5001/increment

# Incrementar en el nodo 1
curl -X POST -H "Content-Type: application/json" -d '{"amount": 3}' http://localhost:5002/increment

# Verificar el valor en todos los nodos (después de la sincronización)
curl http://localhost:5001/value
curl http://localhost:5002/value
curl http://localhost:5003/value
```

Observarás que:

1. Cada nodo mantiene su propio componente del contador.
2. El valor total es la suma de todos los componentes.
3. Después de la sincronización, todos los nodos convergen al mismo valor total.
4. No hay conflictos, incluso si múltiples nodos incrementan simultáneamente.

## Aplicaciones Prácticas

Los modelos de consistencia tienen numerosas aplicaciones en sistemas distribuidos:

1. **Bases de datos distribuidas**: Diferentes sistemas ofrecen diferentes garantías de consistencia según sus casos de uso.
2. **Sistemas de caché**: La consistencia eventual es común en sistemas de caché distribuidos como Memcached o Redis.
3. **Almacenamiento en la nube**: Servicios como Amazon S3 ofrecen consistencia eventual para optimizar la disponibilidad.
4. **Aplicaciones colaborativas**: Los CRDTs se utilizan en aplicaciones como Google Docs para permitir la edición concurrente.
5. **Sistemas de mensajería**: La consistencia causal es importante en sistemas de mensajería para preservar el orden de los mensajes relacionados.

## Preguntas de Reflexión

1. ¿Qué compensaciones (trade-offs) existen entre consistencia fuerte y disponibilidad en sistemas distribuidos?
2. ¿En qué situaciones es aceptable o incluso preferible la consistencia eventual frente a la consistencia fuerte?
3. ¿Cómo afecta el tamaño de los quórums de lectura y escritura al rendimiento y disponibilidad del sistema?
4. ¿Qué tipos de aplicaciones son más adecuadas para utilizar CRDTs y por qué?

## Referencias

1. Vogels, W. (2009). Eventually consistent. Communications of the ACM, 52(1), 40-44.
2. DeCandia, G., Hastorun, D., Jampani, M., Kakulapati, G., Lakshman, A., Pilchin, A., ... & Vogels, W. (2007). Dynamo: Amazon's highly available key-value store. ACM SIGOPS Operating Systems Review, 41(6), 205-220.
3. Shapiro, M., Preguiça, N., Baquero, C., & Zawirski, M. (2011). Conflict-free replicated data types. In Symposium on Self-Stabilizing Systems (pp. 386-400). Springer, Berlin, Heidelberg.
