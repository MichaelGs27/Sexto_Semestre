# Ejemplo Práctico: Datos y Particionamiento

## Objetivos de Aprendizaje

- Implementar un algoritmo de hashing consistente para distribuir datos
- Comprender los mecanismos de replicación y sharding en sistemas distribuidos
- Experimentar con un sistema de almacenamiento distribuido simple
- Analizar el comportamiento del sistema al añadir o eliminar nodos

## Requisitos Previos

- Python 3.6 o superior
- Biblioteca Flask (`pip install flask`)
- Biblioteca Requests (`pip install requests`)
- Conocimientos básicos de programación en Python
- Entendimiento conceptual de particionamiento de datos

## Implementación de Hashing Consistente

### Descripción

En este ejemplo, implementaremos un algoritmo de hashing consistente para distribuir datos entre múltiples nodos. El hashing consistente minimiza la redistribución de datos cuando se añaden o eliminan nodos del sistema.

### Código Base

```python
# consistent_hashing.py
import hashlib
import bisect
import random
import time
import threading
import json
from flask import Flask, request, jsonify
import requests
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ConsistentHash:
    """Implementación de hashing consistente con nodos virtuales."""
    
    def __init__(self, nodes=None, replicas=100):
        """
        Inicializa el hash consistente.
        
        Args:
            nodes: Lista de nodos iniciales (opcional)
            replicas: Número de nodos virtuales por nodo real
        """
        self.replicas = replicas
        self.ring = {}  # Hash -> Nodo
        self.sorted_keys = []  # Lista ordenada de hashes
        
        if nodes:
            for node in nodes:
                self.add_node(node)
    
    def add_node(self, node):
        """Añade un nodo al anillo."""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            bisect.insort(self.sorted_keys, key)
        
        logger.info(f"Nodo {node} añadido al anillo")
    
    def remove_node(self, node):
        """Elimina un nodo del anillo."""
        for i in range(self.replicas):
            key = self._hash(f"{node}:{i}")
            if key in self.ring:
                del self.ring[key]
                self.sorted_keys.remove(key)
        
        logger.info(f"Nodo {node} eliminado del anillo")
    
    def get_node(self, key):
        """
        Obtiene el nodo responsable de una clave.
        
        Args:
            key: Clave a buscar
            
        Returns:
            Nodo responsable de la clave
        """
        if not self.ring:
            return None
        
        hash_key = self._hash(key)
        
        # Encontrar el primer nodo con hash mayor o igual
        idx = bisect.bisect_left(self.sorted_keys, hash_key) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]
    
    def get_nodes(self, key, count):
        """
        Obtiene varios nodos responsables de una clave (para replicación).
        
        Args:
            key: Clave a buscar
            count: Número de nodos a retornar
            
        Returns:
            Lista de nodos responsables de la clave
        """
        if not self.ring:
            return []
        
        count = min(count, len(set(self.ring.values())))
        
        hash_key = self._hash(key)
        
        # Encontrar el primer nodo
        idx = bisect.bisect_left(self.sorted_keys, hash_key) % len(self.sorted_keys)
        
        # Recolectar nodos únicos
        nodes = []
        seen = set()
        
        while len(nodes) < count:
            node = self.ring[self.sorted_keys[idx]]
            if node not in seen:
                seen.add(node)
                nodes.append(node)
            
            idx = (idx + 1) % len(self.sorted_keys)
        
        return nodes
    
    def _hash(self, key):
        """Calcula el hash de una clave."""
        return int(hashlib.md5(str(key).encode()).hexdigest(), 16)
    
    def get_node_keys(self):
        """Retorna un diccionario de nodos y sus claves virtuales."""
        node_keys = {}
        for key, node in self.ring.items():
            if node not in node_keys:
                node_keys[node] = []
            node_keys[node].append(key)
        return node_keys
    
    def get_distribution(self):
        """Retorna la distribución de claves virtuales por nodo."""
        distribution = {}
        for node in set(self.ring.values()):
            distribution[node] = sum(1 for n in self.ring.values() if n == node)
        return distribution

class StorageNode:
    """Nodo de almacenamiento que utiliza hashing consistente."""
    
    def __init__(self, node_id, port, peer_ports=None, replicas=3):
        self.node_id = node_id
        self.port = port
        self.peer_ports = peer_ports or []
        self.replicas = replicas
        
        # Inicializar hashing consistente
        nodes = [f"node:{p}" for p in [port] + self.peer_ports]
        self.ch = ConsistentHash(nodes)
        
        # Almacenamiento local
        self.data = {}
        self.lock = threading.Lock()
        
        # Inicializar la aplicación Flask
        self.app = Flask(f"node-{node_id}")
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/get/<key>', methods=['GET'])
        def get_value(key):
            # Determinar si este nodo es responsable de la clave
            responsible_nodes = self.ch.get_nodes(key, self.replicas)
            is_responsible = f"node:{self.port}" in responsible_nodes
            
            with self.lock:
                if is_responsible and key in self.data:
                    return jsonify({
                        'key': key,
                        'value': self.data[key],
                        'node': self.port
                    })
                elif is_responsible:
                    # Intentar obtener de otros nodos responsables
                    for node in responsible_nodes:
                        if node != f"node:{self.port}":
                            port = int(node.split(':')[1])
                            try:
                                response = requests.get(f"http://localhost:{port}/get_local/{key}", timeout=0.5)
                                if response.status_code == 200:
                                    data = response.json()
                                    # Almacenar localmente para futuras consultas
                                    self.data[key] = data['value']
                                    return jsonify({
                                        'key': key,
                                        'value': data['value'],
                                        'node': self.port,
                                        'source': port
                                    })
                            except requests.exceptions.RequestException:
                                pass
                    
                    return jsonify({'error': 'Key not found'}), 404
                else:
                    # Redirigir al nodo responsable
                    responsible_node = self.ch.get_node(key)
                    port = int(responsible_node.split(':')[1])
                    
                    try:
                        response = requests.get(f"http://localhost:{port}/get/{key}", timeout=0.5)
                        return jsonify(response.json()), response.status_code
                    except requests.exceptions.RequestException:
                        return jsonify({'error': 'Failed to contact responsible node'}), 500
        
        @self.app.route('/get_local/<key>', methods=['GET'])
        def get_local_value(key):
            """Endpoint para obtener un valor localmente (sin redirección)."""
            with self.lock:
                if key in self.data:
                    return jsonify({
                        'key': key,
                        'value': self.data[key],
                        'node': self.port
                    })
                else:
                    return jsonify({'error': 'Key not found'}), 404
        
        @self.app.route('/put', methods=['POST'])
        def put_value():
            data = request.json
            key = data.get('key')
            value = data.get('value')
            
            # Determinar los nodos responsables
            responsible_nodes = self.ch.get_nodes(key, self.replicas)
            
            # Almacenar localmente si somos responsables
            if f"node:{self.port}" in responsible_nodes:
                with self.lock:
                    self.data[key] = value
            
            # Replicar a otros nodos responsables
            success_count = 1 if f"node:{self.port}" in responsible_nodes else 0
            failed_nodes = []
            
            for node in responsible_nodes:
                if node != f"node:{self.port}":
                    port = int(node.split(':')[1])
                    try:
                        response = requests.post(
                            f"http://localhost:{port}/put_local",
                            json={'key': key, 'value': value},
                            timeout=0.5
                        )
                        if response.status_code == 200:
                            success_count += 1
                        else:
                            failed_nodes.append(port)
                    except requests.exceptions.RequestException:
                        failed_nodes.append(port)
            
            # Verificar si se alcanzó el quórum de escritura
            if success_count >= (self.replicas + 1) // 2:
                return jsonify({
                    'status': 'success',
                    'key': key,
                    'replicated': success_count,
                    'failed_nodes': failed_nodes
                })
            else:
                return jsonify({
                    'status': 'partial_failure',
                    'key': key,
                    'replicated': success_count,
                    'failed_nodes': failed_nodes
                }), 500
        
        @self.app.route('/put_local', methods=['POST'])
        def put_local_value():
            """Endpoint para almacenar un valor localmente (sin redirección)."""
            data = request.json
            key = data.get('key')
            value = data.get('value')
            
            with self.lock:
                self.data[key] = value
            
            return jsonify({
                'status': 'success',
                'key': key
            })
        
        @self.app.route('/join', methods=['POST'])
        def join_ring():
            """Endpoint para que un nuevo nodo se una al anillo."""
            data = request.json
            new_node = data.get('node')
            
            with self.lock:
                self.ch.add_node(new_node)
                # Recalcular qué claves deben moverse al nuevo nodo
                keys_to_move = []
                for key in list(self.data.keys()):
                    responsible_nodes = self.ch.get_nodes(key, self.replicas)
                    if f"node:{self.port}" not in responsible_nodes:
                        keys_to_move.append(key)
                
                # Mover claves al nuevo nodo
                moved_keys = []
                for key in keys_to_move:
                    try:
                        port = int(new_node.split(':')[1])
                        response = requests.post(
                            f"http://localhost:{port}/put_local",
                            json={'key': key, 'value': self.data[key]},
                            timeout=0.5
                        )
                        if response.status_code == 200:
                            moved_keys.append(key)
                    except requests.exceptions.RequestException:
                        pass
                
                # Eliminar claves movidas
                for key in moved_keys:
                    del self.data[key]
            
            return jsonify({
                'status': 'success',
                'node_added': new_node,
                'keys_moved': len(moved_keys)
            })
        
        @self.app.route('/leave', methods=['POST'])
        def leave_ring():
            """Endpoint para que un nodo salga del anillo."""
            data = request.json
            leaving_node = data.get('node')
            
            with self.lock:
                self.ch.remove_node(leaving_node)
            
            return jsonify({
                'status': 'success',
                'node_removed': leaving_node
            })
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            """Endpoint para obtener el estado del nodo."""
            with self.lock:
                return jsonify({
                    'node_id': self.node_id,
                    'port': self.port,
                    'data_count': len(self.data),
                    'ring_size': len(self.ch.ring),
                    'distribution': self.ch.get_distribution()
                })
    
    def run(self):
        """Inicia el servidor Flask."""
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

def main():
    parser = argparse.ArgumentParser(description='Storage Node with Consistent Hashing')
    parser.add_argument('--id', type=int, required=True, help='ID del nodo')
    parser.add_argument('--port', type=int, required=True, help='Puerto del nodo')
    parser.add_argument('--peers', type=str, help='Puertos de los nodos pares (separados por comas)')
    parser.add_argument('--replicas', type=int, default=3, help='Número de réplicas por clave')
    
    args = parser.parse_args()
    
    peer_ports = []
    if args.peers:
        peer_ports = [int(p) for p in args.peers.split(',')]
    
    node = StorageNode(args.id, args.port, peer_ports, args.replicas)
    node.run()

if __name__ == "__main__":
    main()
```

### Ejecución y Resultados Esperados

Para ejecutar este ejemplo, necesitarás abrir varias terminales y ejecutar el script con diferentes parámetros para cada nodo:

```bash
# Terminal 1 - Nodo 1
python consistent_hashing.py --id 1 --port 5001 --peers 5002,5003

# Terminal 2 - Nodo 2
python consistent_hashing.py --id 2 --port 5002 --peers 5001,5003

# Terminal 3 - Nodo 3
python consistent_hashing.py --id 3 --port 5003 --peers 5001,5002
```

Una vez que los nodos estén en ejecución, puedes interactuar con ellos:

```bash
# Almacenar un valor
curl -X POST -H "Content-Type: application/json" -d '{"key":"user1", "value":"Alice"}' http://localhost:5001/put

# Recuperar el valor (desde cualquier nodo)
curl http://localhost:5002/get/user1

# Verificar el estado de un nodo
curl http://localhost:5001/status
```

Para simular la adición de un nuevo nodo:

```bash
# Terminal 4 - Nodo 4
python consistent_hashing.py --id 4 --port 5004 --peers 5001,5002,5003

# Notificar a los nodos existentes
curl -X POST -H "Content-Type: application/json" -d '{"node":"node:5004"}' http://localhost:5001/join
curl -X POST -H "Content-Type: application/json" -d '{"node":"node:5004"}' http://localhost:5002/join
curl -X POST -H "Content-Type: application/json" -d '{"node":"node:5004"}' http://localhost:5003/join
```

Para simular la salida de un nodo:

```bash
# Notificar a los nodos restantes
curl -X POST -H "Content-Type: application/json" -d '{"node":"node:5003"}' http://localhost:5001/leave
curl -X POST -H "Content-Type: application/json" -d '{"node":"node:5003"}' http://localhost:5002/leave
curl -X POST -H "Content-Type: application/json" -d '{"node":"node:5004"}' http://localhost:5004/leave
```

Observarás que:

1. Las claves se distribuyen uniformemente entre los nodos.
2. Cuando se añade o elimina un nodo, solo una fracción de las claves se redistribuye.
3. La replicación garantiza que los datos estén disponibles incluso si algunos nodos fallan.

## Ejercicio: Implementación de Sharding

### Descripción

En este ejercicio, extenderemos el sistema para implementar sharding basado en rangos de claves, una técnica común en bases de datos distribuidas.

### Instrucciones

1. Modifica el código base para implementar sharding basado en rangos de claves.
2. Cada nodo será responsable de un rango específico de claves.
3. Implementa un mecanismo para balancear la carga cuando un nodo se sobrecarga.

### Código Base para el Ejercicio

```python
# range_sharding.py
import time
import random
import threading
import json
from flask import Flask, request, jsonify
import requests
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ShardManager:
    """Gestor de shards basado en rangos de claves."""
    
    def __init__(self, num_shards=10):
        """
        Inicializa el gestor de shards.
        
        Args:
            num_shards: Número de shards
        """
        self.num_shards = num_shards
        self.shard_to_node = {}  # shard_id -> node_port
        self.node_to_shards = {}  # node_port -> [shard_id]
    
    def assign_shard(self, shard_id, node_port):
        """Asigna un shard a un nodo."""
        self.shard_to_node[shard_id] = node_port
        
        if node_port not in self.node_to_shards:
            self.node_to_shards[node_port] = []
        
        if shard_id not in self.node_to_shards[node_port]:
            self.node_to_shards[node_port].append(shard_id)
        
        logger.info(f"Shard {shard_id} asignado al nodo {node_port}")
    
    def remove_node(self, node_port):
        """Elimina un nodo y reasigna sus shards."""
        if node_port not in self.node_to_shards:
            return []
        
        shards_to_reassign = self.node_to_shards[node_port].copy()
        del self.node_to_shards[node_port]
        
        for shard_id in shards_to_reassign:
            if shard_id in self.shard_to_node and self.shard_to_node[shard_id] == node_port:
                del self.shard_to_node[shard_id]
        
        return shards_to_reassign
    
    def get_node_for_key(self, key):
        """Obtiene el nodo responsable de una clave."""
        shard_id = self.get_shard_for_key(key)
        return self.shard_to_node.get(shard_id)
    
    def get_shard_for_key(self, key):
        """Determina el shard para una clave."""
        # Usar un hash simple para distribuir las claves
        hash_val = hash(str(key)) % self.num_shards
        return hash_val
    
    def get_all_nodes(self):
        """Retorna todos los nodos activos."""
        return list(self.node_to_shards.keys())
    
    def get_shards_for_node(self, node_port):
        """Retorna los shards asignados a un nodo."""
        return self.node_to_shards.get(node_port, [])
    
    def balance_shards(self):
        """Balancea los shards entre los nodos disponibles."""
        if not self.node_to_shards:
            return []
        
        # Calcular el número ideal de shards por nodo
        nodes = list(self.node_to_shards.keys())
        ideal_shards_per_node = self.num_shards / len(nodes)
        
        # Identificar nodos sobrecargados y subcargados
        overloaded = []
        underloaded = []
        
        for node, shards in self.node_to_shards.items():
            if len(shards) > ideal_shards_per_node + 1:
                overloaded.append((node, len(shards)))
            elif len(shards) < ideal_shards_per_node:
                underloaded.append((node, len(shards)))
        
        # Ordenar por carga
        overloaded.sort(key=lambda x: x[1], reverse=True)
        underloaded.sort(key=lambda x: x[1])
        
        # Mover shards de nodos sobrecargados a subcargados
        moves = []  # [(shard_id, from_node, to_node)]
        
        for over_node, _ in overloaded:
            while len(self.node_to_shards[over_node]) > ideal_shards_per_node and underloaded:
                under_node, _ = underloaded[0]
                
                # Seleccionar un shard para mover
                shard_to_move = self.node_to_shards[over_node][0]
                
                # Actualizar asignaciones
                self.node_to_shards[over_node].remove(shard_to_move)
                if under_node not in self.node_to_shards:
                    self.node_to_shards[under_node] = []
                self.node_to_shards[under_node].append(shard_to_move)
                self.shard_to_node[shard_to_move] = under_node
                
                # Registrar el movimiento
                moves.append((shard_to_move, over_node, under_node))
                
                # Actualizar estado de carga
                if len(self.node_to_shards[under_node]) >= ideal_shards_per_node:
                    underloaded.pop(0)
        
        return moves

class ShardNode:
    """Nodo que implementa sharding basado en rangos."""
    
    def __init__(self, node_id, port, coordinator_port=None, replicas=1):
        self.node_id = node_id
        self.port = port
        self.coordinator_port = coordinator_port
        self.replicas = replicas
        
        # Almacenamiento local por shard
        self.data = {}  # shard_id -> {key: value}
        self.lock = threading.Lock()
        
        # Inicializar la aplicación Flask
        self.app = Flask(f"node-{node_id}")
        self.setup_routes()
        
        # Registrarse con el coordinador si existe
        if coordinator_port:
            self.register_with_coordinator()
    
    def setup_routes(self):
        @self.app.route('/get/<key>', methods=['GET'])
        def get_value(key):
            # TODO: Implementar obtención de valor
            # 1. Determinar el shard para la clave
            # 2. Verificar si somos responsables de ese shard
            # 3. Si lo somos, buscar el valor localmente
            # 4. Si no, redirigir al nodo responsable
            pass
        
        @self.app.route('/put', methods=['POST'])
        def put_value():
            # TODO: Implementar almacenamiento de valor
            # 1. Determinar el shard para la clave
            # 2. Verificar si somos responsables de ese shard
            # 3. Si lo somos, almacenar el valor localmente
            # 4. Si no, redirigir al nodo responsable
            pass
        
        @self.app.route('/assign_shard', methods=['POST'])
        def assign_shard():
            # TODO: Implementar asignación de shard
            # 1. Recibir el ID del shard a asignar
            # 2. Inicializar el almacenamiento para ese shard si no existe
            # 3. Confirmar la asignación
            pass
        
        @self.app.route('/transfer_shard', methods=['POST'])
        def transfer_shard():
            # TODO: Implementar transferencia de shard
            # 1. Recibir el ID del shard y el nodo destino
            # 2. Enviar todos los datos de ese shard al nodo destino
            # 3. Confirmar la transferencia
            pass
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            # TODO: Implementar obtención de estado
            # 1. Retornar información sobre los shards asignados
            # 2. Incluir estadísticas de uso
            pass
    
    def register_with_coordinator(self):
        """Registra este nodo con el coordinador."""
        try:
            response = requests.post(
                f"http://localhost:{self.coordinator_port}/register_node",
                json={'node_port': self.port},
                timeout=1
            )
            if response.status_code == 200:
                logger.info(f"Nodo {self.port} registrado con el coordinador")
            else:
                logger.error(f"Error registrando nodo: {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error conectando con el coordinador: {e}")
    
    def run(self):
        """Inicia el servidor Flask."""
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

class ShardCoordinator:
    """Coordinador de shards."""
    
    def __init__(self, port, num_shards=10):
        self.port = port
        self.shard_manager = ShardManager(num_shards)
        self.lock = threading.Lock()
        
        # Inicializar la aplicación Flask
        self.app = Flask(f"coordinator")
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/register_node', methods=['POST'])
        def register_node():
            # TODO: Implementar registro de nodo
            # 1. Recibir el puerto del nodo
            # 2. Asignar shards al nodo según sea necesario
            # 3. Confirmar el registro
            pass
        
        @self.app.route('/remove_node', methods=['POST'])
        def remove_node():
            # TODO: Implementar eliminación de nodo
            # 1. Recibir el puerto del nodo a eliminar
            # 2. Reasignar sus shards a otros nodos
            # 3. Confirmar la eliminación
            pass
        
        @self.app.route('/balance', methods=['POST'])
        def balance_shards():
            # TODO: Implementar balanceo de shards
            # 1. Calcular una distribución más equilibrada
            # 2. Mover shards entre nodos según sea necesario
            # 3. Confirmar el balanceo
            pass
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            # TODO: Implementar obtención de estado
            # 1. Retornar información sobre la asignación de shards
            # 2. Incluir estadísticas de distribución
            pass
    
    def run(self):
        """Inicia el servidor Flask."""
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

def main():
    parser = argparse.ArgumentParser(description='Sharding Node')
    parser.add_argument('--id', type=int, required=True, help='ID del nodo')
    parser.add_argument('--port', type=int, required=True, help='Puerto del nodo')
    parser.add_argument('--coordinator', type=int, help='Puerto del coordinador')
    parser.add_argument('--is-coordinator', action='store_true', help='Si este nodo es el coordinador')
    parser.add_argument('--num-shards', type=int, default=10, help='Número de shards')
    
    args = parser.parse_args()
    
    if args.is_coordinator:
        coordinator = ShardCoordinator(args.port, args.num_shards)
        coordinator.run()
    else:
        node = ShardNode(args.id, args.port, args.coordinator)
        node.run()

if __name__ == "__main__":
    main()
```

### Desafío Adicional

Una vez implementado el sistema de sharding, añade las siguientes mejoras:

1. Implementa replicación de shards para mejorar la disponibilidad.
2. Añade soporte para transacciones que afectan a múltiples shards.
3. Implementa un mecanismo de recuperación para cuando un nodo falla.

## Implementación de un Cliente para una Base de Datos NoSQL

### Descripción

Para complementar los ejemplos anteriores, aquí hay un ejemplo de cómo implementar un cliente simple para interactuar con una base de datos NoSQL distribuida (en este caso, MongoDB).

```python
# nosql_client.py
import pymongo
import time
import random
import argparse
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MongoDBClient:
    """Cliente para interactuar con MongoDB."""
    
    def __init__(self, hosts, replicaset=None, w=1, r=1):
        """
        Inicializa el cliente de MongoDB.
        
        Args:
            hosts: Lista de hosts (host:port)
            replicaset: Nombre del replica set (opcional)
            w: Nivel de write concern
            r: Nivel de read concern
        """
        self.hosts = hosts
        self.replicaset = replicaset
        self.w = w
        self.r = r
        
        # Construir URI de conexión
        if replicaset:
            self.uri = f"mongodb://{','.join(hosts)}/?replicaSet={replicaset}"
        else:
            self.uri = f"mongodb://{','.join(hosts)}/"
        
        # Conectar a MongoDB
        self.client = MongoClient(self.uri, w=self.w, readPreference='secondaryPreferred')
        
        logger.info(f"Cliente MongoDB inicializado con URI: {self.uri}")
    
    def create_database(self, db_name):
        """Crea una base de datos."""
        return self.client[db_name]
    
    def create_collection(self, db_name, collection_name, sharded=False):
        """Crea una colección."""
        db = self.client[db_name]
        
        # Crear colección
        if collection_name not in db.list_collection_names():
            db.create_collection(collection_name)
        
        # Habilitar sharding si es necesario
        if sharded:
            try:
                self.client.admin.command('enableSharding', db_name)
                self.client.admin.command('shardCollection', f"{db_name}.{collection_name}", key={'_id': 'hashed'})
                logger.info(f"Sharding habilitado para {db_name}.{collection_name}")
            except OperationFailure as e:
                logger.error(f"Error habilitando sharding: {e}")
        
        return db[collection_name]
    
    def insert_document(self, db_name, collection_name, document):
        """Inserta un documento."""
        db = self.client[db_name]
        collection = db[collection_name]
        
        try:
            result = collection.insert_one(document)
            return result.inserted_id
        except Exception as e:
            logger.error(f"Error insertando documento: {e}")
            return None
    
    def find_document(self, db_name, collection_name, query):
        """Busca documentos que coincidan con la consulta."""
        db = self.client[db_name]
        collection = db[collection_name]
        
        try:
            return list(collection.find(query))
        except Exception as e:
            logger.error(f"Error buscando documentos: {e}")
            return []
    
    def update_document(self, db_name, collection_name, query, update):
        """Actualiza documentos que coincidan con la consulta."""
        db = self.client[db_name]
        collection = db[collection_name]
        
        try:
            result = collection.update_many(query, update)
            return result.modified_count
        except Exception as e:
            logger.error(f"Error actualizando documentos: {e}")
            return 0
    
    def delete_document(self, db_name, collection_name, query):
        """Elimina documentos que coincidan con la consulta."""
        db = self.client[db_name]
        collection = db[collection_name]
        
        try:
            result = collection.delete_many(query)
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error eliminando documentos: {e}")
            return 0
    
    def get_sharding_status(self):
        """Obtiene el estado del sharding."""
        try:
            return self.client.admin.command('listShards')
        except Exception as e:
            logger.error(f"Error obteniendo estado de sharding: {e}")
            return None
    
    def get_replication_status(self):
        """Obtiene el estado de la replicación."""
        try:
            return self.client.admin.command('replSetGetStatus')
        except Exception as e:
            logger.error(f"Error obteniendo estado de replicación: {e}")
            return None
    
    def close(self):
        """Cierra la conexión."""
        self.client.close()

def simulate_workload(client, db_name, collection_name, num_operations=100):
    """Simula una carga de trabajo en la base de datos."""
    # Crear colección si no existe
    client.create_collection(db_name, collection_name, sharded=True)
    
    # Realizar operaciones
    for i in range(num_operations):
        operation = random.choice(['insert', 'find', 'update', 'delete'])
        
        if operation == 'insert':
            document = {
                'user_id': f"user_{random.randint(1, 1000)}",
                'value': random.randint(1, 100),
                'timestamp': time.time()
            }
            client.insert_document(db_name, collection_name, document)
        
        elif operation == 'find':
            user_id = f"user_{random.randint(1, 1000)}"
            client.find_document(db_name, collection_name, {'user_id': user_id})
        
        elif operation == 'update':
            user_id = f"user_{random.randint(1, 1000)}"
            client.update_document(
                db_name, 
                collection_name, 
                {'user_id': user_id}, 
                {'$set': {'value': random.randint(1, 100)}}
            )
        
        elif operation == 'delete':
            user_id = f"user_{random.randint(1, 1000)}"
            client.delete_document(db_name, collection_name, {'user_id': user_id})
        
        # Pequeña pausa para no saturar
        time.sleep(0.01)

def main():
    parser = argparse.ArgumentParser(description='MongoDB Client')
    parser.add_argument('--hosts', type=str, required=True, help='Hosts de MongoDB (separados por comas)')
    parser.add_argument('--replicaset', type=str, help='Nombre del replica set')
    parser.add_argument('--db', type=str, default='test', help='Nombre de la base de datos')
    parser.add_argument('--collection', type=str, default='test', help='Nombre de la colección')
    parser.add_argument('--operations', type=int, default=100, help='Número de operaciones a simular')
    
    args = parser.parse_args()
    
    hosts = args.hosts.split(',')
    
    client = MongoDBClient(hosts, args.replicaset)
    
    # Simular carga de trabajo
    simulate_workload(client, args.db, args.collection, args.operations)
    
    # Mostrar estado
    sharding_status = client.get_sharding_status()
    if sharding_status:
        logger.info(f"Estado de sharding: {sharding_status}")
    
    replication_status = client.get_replication_status()
    if replication_status:
        logger.info(f"Estado de replicación: {replication_status}")
    
    client.close()

if __name__ == "__main__":
    main()
```

Para ejecutar este ejemplo, necesitarás tener acceso a un clúster de MongoDB:

```bash
python nosql_client.py --hosts localhost:27017,localhost:27018,localhost:27019 --replicaset rs0 --db test --collection users --operations 1000
```

## Aplicaciones Prácticas

Las técnicas de particionamiento de datos tienen numerosas aplicaciones:

1. **Bases de datos distribuidas**: Escalar horizontalmente para manejar grandes volúmenes de datos.
2. **Sistemas de caché**: Distribuir la carga entre múltiples nodos para mejorar el rendimiento.
3. **Sistemas de almacenamiento de objetos**: Distribuir archivos entre múltiples servidores.
4. **Procesamiento de big data**: Particionar datos para procesamiento paralelo.
5. **Microservicios**: Particionar datos por dominio o funcionalidad.

## Preguntas de Reflexión

1. ¿Qué ventajas ofrece el hashing consistente frente a otras técnicas de particionamiento?
2. ¿Cómo afecta el número de nodos virtuales en el hashing consistente a la distribución de datos?
3. ¿En qué situaciones es preferible el sharding basado en rangos frente al hashing consistente?
4. ¿Qué estrategias existen para manejar consultas que abarcan múltiples shards?

## Referencias

1. Karger, D., Lehman, E., Leighton, T., Panigrahy, R., Levine, M., & Lewin, D. (1997). Consistent hashing and random trees: Distributed caching protocols for relieving hot spots on the World Wide Web. Proceedings of the 29th Annual ACM Symposium on Theory of Computing, 654-663.
2. DeCandia, G., Hastorun, D., Jampani, M., Kakulapati, G., Lakshman, A., Pilchin, A., ... & Vogels, W. (2007). Dynamo: Amazon's highly available key-value store. ACM SIGOPS Operating Systems Review, 41(6), 205-220.
3. Corbett, J. C., Dean, J., Epstein, M., Fikes, A., Frost, C., Furman, J. J., ... & Woodford, D. (2013). Spanner: Google's globally distributed database. ACM Transactions on Computer Systems, 31(3), 1-22.
