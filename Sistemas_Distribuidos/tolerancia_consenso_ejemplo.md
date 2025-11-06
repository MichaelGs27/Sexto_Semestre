# Ejemplo Práctico: Tolerancia a Fallos y Consenso

## Objetivos de Aprendizaje

- Comprender los conceptos de tolerancia a fallos en sistemas distribuidos
- Implementar un algoritmo simplificado de consenso basado en Raft
- Experimentar con la detección y manejo de fallos de nodos
- Analizar el comportamiento del sistema bajo diferentes escenarios de partición de red

## Requisitos Previos

- Python 3.6 o superior
- Biblioteca ZeroMQ (`pip install pyzmq`)
- Biblioteca Flask (`pip install flask`)
- Biblioteca Requests (`pip install requests`)
- Conocimientos básicos de programación en Python
- Entendimiento conceptual de tolerancia a fallos y consenso

## Implementación de un Sistema Tolerante a Fallos con Consenso Simplificado

### Descripción

En este ejemplo, implementaremos una versión simplificada del algoritmo de consenso Raft. Raft es un algoritmo diseñado para ser más comprensible que Paxos, manteniendo las mismas garantías de seguridad y liveness. Nuestro sistema permitirá:

1. Elección de líder
2. Replicación de logs
3. Detección de fallos
4. Manejo de particiones de red

### Código Base

```python
# simple_raft.py
import time
import random
import threading
import json
import argparse
import zmq
from enum import Enum
from flask import Flask, request, jsonify
import requests
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NodeState(Enum):
    FOLLOWER = 0
    CANDIDATE = 1
    LEADER = 2

class RaftNode:
    def __init__(self, node_id, port, peer_ports=None):
        self.node_id = node_id
        self.port = port
        self.peer_ports = peer_ports or []
        self.state = NodeState.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.log = []  # Lista de entradas de log (term, command)
        self.commit_index = -1  # Índice del último log confirmado
        self.last_applied = -1  # Índice del último log aplicado al estado
        
        # Variables volátiles para líderes
        self.next_index = {}  # Índice del siguiente log a enviar a cada servidor
        self.match_index = {}  # Índice del log más alto replicado en cada servidor
        
        # Variables para timeouts
        self.election_timeout = random.uniform(150, 300) / 1000  # 150-300ms
        self.last_heartbeat = time.time()
        
        # Estado de la máquina (key-value store simple)
        self.state_machine = {}
        
        # Locks para acceso concurrente
        self.lock = threading.Lock()
        
        # Inicializar la aplicación Flask
        self.app = Flask(f"node-{node_id}")
        self.setup_routes()
        
        # Iniciar hilos
        self.election_thread = threading.Thread(target=self.run_election_timer)
        self.election_thread.daemon = True
        self.election_thread.start()
        
        self.heartbeat_thread = None  # Solo se inicia si somos líder
    
    def setup_routes(self):
        @self.app.route('/request_vote', methods=['POST'])
        def request_vote():
            data = request.json
            term = data.get('term')
            candidate_id = data.get('candidate_id')
            last_log_index = data.get('last_log_index')
            last_log_term = data.get('last_log_term')
            
            with self.lock:
                # Si el término del candidato es menor que el nuestro, rechazar
                if term < self.current_term:
                    return jsonify({
                        'term': self.current_term,
                        'vote_granted': False
                    })
                
                # Si el término es mayor, actualizar nuestro término y convertirnos en follower
                if term > self.current_term:
                    self.current_term = term
                    self.state = NodeState.FOLLOWER
                    self.voted_for = None
                
                # Determinar si concedemos el voto
                vote_granted = False
                if (self.voted_for is None or self.voted_for == candidate_id) and self.is_log_up_to_date(last_log_index, last_log_term):
                    vote_granted = True
                    self.voted_for = candidate_id
                    self.last_heartbeat = time.time()  # Reiniciar timeout al votar
                
                return jsonify({
                    'term': self.current_term,
                    'vote_granted': vote_granted
                })
        
        @self.app.route('/append_entries', methods=['POST'])
        def append_entries():
            data = request.json
            term = data.get('term')
            leader_id = data.get('leader_id')
            prev_log_index = data.get('prev_log_index')
            prev_log_term = data.get('prev_log_term')
            entries = data.get('entries', [])
            leader_commit = data.get('leader_commit')
            
            with self.lock:
                # Si el término del líder es menor que el nuestro, rechazar
                if term < self.current_term:
                    return jsonify({
                        'term': self.current_term,
                        'success': False
                    })
                
                # Reiniciar timeout al recibir mensaje válido del líder
                self.last_heartbeat = time.time()
                
                # Si el término es mayor, actualizar nuestro término
                if term > self.current_term:
                    self.current_term = term
                    self.voted_for = None
                
                # Convertirnos en follower si no lo somos ya
                self.state = NodeState.FOLLOWER
                
                # Verificar consistencia del log
                log_ok = (prev_log_index == -1) or (
                    prev_log_index < len(self.log) and 
                    (prev_log_index == -1 or self.log[prev_log_index][0] == prev_log_term)
                )
                
                if not log_ok:
                    return jsonify({
                        'term': self.current_term,
                        'success': False
                    })
                
                # Procesar entradas de log
                if entries:
                    # Si hay conflictos, eliminar entradas conflictivas y añadir nuevas
                    new_index = prev_log_index + 1
                    if new_index < len(self.log):
                        self.log = self.log[:new_index]
                    
                    # Añadir nuevas entradas
                    self.log.extend(entries)
                
                # Actualizar commit_index si es necesario
                if leader_commit > self.commit_index:
                    self.commit_index = min(leader_commit, len(self.log) - 1)
                    self.apply_committed_entries()
                
                return jsonify({
                    'term': self.current_term,
                    'success': True
                })
        
        @self.app.route('/client_request', methods=['POST'])
        def client_request():
            data = request.json
            command = data.get('command')
            
            with self.lock:
                # Si no somos el líder, redirigir al líder si lo conocemos
                if self.state != NodeState.LEADER:
                    return jsonify({
                        'success': False,
                        'leader': self.voted_for,
                        'message': 'Not the leader'
                    })
                
                # Añadir comando al log
                self.log.append((self.current_term, command))
                logger.info(f"Node {self.node_id} appended command to log: {command}")
                
                return jsonify({
                    'success': True,
                    'message': 'Command accepted'
                })
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            with self.lock:
                return jsonify({
                    'node_id': self.node_id,
                    'state': self.state.name,
                    'current_term': self.current_term,
                    'voted_for': self.voted_for,
                    'log_length': len(self.log),
                    'commit_index': self.commit_index,
                    'state_machine': self.state_machine
                })
    
    def is_log_up_to_date(self, last_log_index, last_log_term):
        """Determina si el log del candidato está al menos tan actualizado como el nuestro."""
        my_last_index = len(self.log) - 1
        my_last_term = self.log[my_last_index][0] if my_last_index >= 0 else 0
        
        if last_log_term != my_last_term:
            return last_log_term > my_last_term
        return last_log_index >= my_last_index
    
    def apply_committed_entries(self):
        """Aplica las entradas de log confirmadas a la máquina de estado."""
        while self.last_applied < self.commit_index:
            self.last_applied += 1
            command = self.log[self.last_applied][1]
            self.apply_command(command)
    
    def apply_command(self, command):
        """Aplica un comando a la máquina de estado."""
        try:
            cmd_type = command.get('type')
            key = command.get('key')
            value = command.get('value')
            
            if cmd_type == 'set':
                self.state_machine[key] = value
                logger.info(f"Node {self.node_id} applied SET {key}={value}")
            elif cmd_type == 'delete':
                if key in self.state_machine:
                    del self.state_machine[key]
                    logger.info(f"Node {self.node_id} applied DELETE {key}")
        except Exception as e:
            logger.error(f"Error applying command: {e}")
    
    def run_election_timer(self):
        """Ejecuta el temporizador de elección para detectar cuando el líder falla."""
        while True:
            time.sleep(0.05)  # Comprobar cada 50ms
            
            with self.lock:
                # Si somos líder, no necesitamos temporizador de elección
                if self.state == NodeState.LEADER:
                    continue
                
                # Si ha pasado el tiempo de elección sin heartbeat, iniciar elección
                if time.time() - self.last_heartbeat > self.election_timeout:
                    self.start_election()
    
    def start_election(self):
        """Inicia una elección de líder."""
        with self.lock:
            self.state = NodeState.CANDIDATE
            self.current_term += 1
            self.voted_for = self.node_id  # Votar por nosotros mismos
            self.last_heartbeat = time.time()  # Reiniciar timeout
            
            # Establecer nuevo timeout aleatorio
            self.election_timeout = random.uniform(150, 300) / 1000
            
            logger.info(f"Node {self.node_id} starting election for term {self.current_term}")
        
        # Solicitar votos a todos los pares
        votes_received = 1  # Incluye nuestro propio voto
        
        for port in self.peer_ports:
            try:
                last_log_index = len(self.log) - 1
                last_log_term = self.log[last_log_index][0] if last_log_index >= 0 else 0
                
                response = requests.post(
                    f"http://localhost:{port}/request_vote",
                    json={
                        'term': self.current_term,
                        'candidate_id': self.node_id,
                        'last_log_index': last_log_index,
                        'last_log_term': last_log_term
                    },
                    timeout=0.1
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    with self.lock:
                        # Si recibimos un término mayor, convertirnos en follower
                        if data['term'] > self.current_term:
                            self.current_term = data['term']
                            self.state = NodeState.FOLLOWER
                            self.voted_for = None
                            return
                        
                        # Contar votos
                        if data['vote_granted']:
                            votes_received += 1
            except requests.exceptions.RequestException:
                # Ignorar errores de conexión
                pass
        
        # Verificar si ganamos la elección
        with self.lock:
            # Solo convertirnos en líder si seguimos siendo candidatos
            if self.state == NodeState.CANDIDATE:
                # Si tenemos mayoría de votos, convertirnos en líder
                if votes_received > (len(self.peer_ports) + 1) / 2:
                    self.become_leader()
    
    def become_leader(self):
        """Convierte este nodo en líder."""
        with self.lock:
            if self.state != NodeState.CANDIDATE:
                return
            
            self.state = NodeState.LEADER
            logger.info(f"Node {self.node_id} became leader for term {self.current_term}")
            
            # Inicializar índices para cada seguidor
            for port in self.peer_ports:
                self.next_index[port] = len(self.log)
                self.match_index[port] = -1
            
            # Iniciar hilo de heartbeat
            if self.heartbeat_thread is None or not self.heartbeat_thread.is_alive():
                self.heartbeat_thread = threading.Thread(target=self.send_heartbeats)
                self.heartbeat_thread.daemon = True
                self.heartbeat_thread.start()
    
    def send_heartbeats(self):
        """Envía heartbeats periódicos a todos los seguidores."""
        while True:
            with self.lock:
                if self.state != NodeState.LEADER:
                    return
                
                for port in self.peer_ports:
                    self.send_append_entries(port)
            
            time.sleep(0.05)  # Enviar heartbeats cada 50ms
    
    def send_append_entries(self, follower_port):
        """Envía AppendEntries RPC a un seguidor específico."""
        try:
            with self.lock:
                if self.state != NodeState.LEADER:
                    return
                
                next_idx = self.next_index.get(follower_port, 0)
                prev_log_index = next_idx - 1
                prev_log_term = self.log[prev_log_index][0] if prev_log_index >= 0 else 0
                
                # Determinar entradas a enviar
                entries = self.log[next_idx:] if next_idx < len(self.log) else []
                
                # Enviar RPC
                response = requests.post(
                    f"http://localhost:{follower_port}/append_entries",
                    json={
                        'term': self.current_term,
                        'leader_id': self.node_id,
                        'prev_log_index': prev_log_index,
                        'prev_log_term': prev_log_term,
                        'entries': entries,
                        'leader_commit': self.commit_index
                    },
                    timeout=0.1
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    with self.lock:
                        # Si recibimos un término mayor, convertirnos en follower
                        if data['term'] > self.current_term:
                            self.current_term = data['term']
                            self.state = NodeState.FOLLOWER
                            self.voted_for = None
                            return
                        
                        # Actualizar índices si la operación fue exitosa
                        if data['success']:
                            if entries:
                                self.next_index[follower_port] = next_idx + len(entries)
                                self.match_index[follower_port] = self.next_index[follower_port] - 1
                                self.update_commit_index()
                        else:
                            # Si falla, decrementar next_index y reintentar
                            self.next_index[follower_port] = max(0, self.next_index[follower_port] - 1)
        except requests.exceptions.RequestException:
            # Ignorar errores de conexión
            pass
    
    def update_commit_index(self):
        """Actualiza el índice de commit basado en la mayoría de réplicas."""
        with self.lock:
            if self.state != NodeState.LEADER:
                return
            
            # Para cada índice de log, verificar si está replicado en la mayoría de servidores
            for n in range(self.commit_index + 1, len(self.log)):
                if self.log[n][0] == self.current_term:  # Solo considerar entradas del término actual
                    # Contar cuántos servidores tienen esta entrada
                    count = 1  # Incluir a nosotros mismos
                    for port in self.peer_ports:
                        if self.match_index.get(port, -1) >= n:
                            count += 1
                    
                    # Si la mayoría tiene esta entrada, actualizar commit_index
                    if count > (len(self.peer_ports) + 1) / 2:
                        self.commit_index = n
                        self.apply_committed_entries()
    
    def run(self):
        """Inicia el servidor Flask."""
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

def main():
    parser = argparse.ArgumentParser(description='Simple Raft Node')
    parser.add_argument('--id', type=int, required=True, help='ID del nodo')
    parser.add_argument('--port', type=int, required=True, help='Puerto del nodo')
    parser.add_argument('--peers', type=str, help='Puertos de los nodos pares (separados por comas)')
    
    args = parser.parse_args()
    
    peer_ports = []
    if args.peers:
        peer_ports = [int(p) for p in args.peers.split(',')]
    
    # Inicializar con un log vacío que contiene una entrada dummy en el término 0
    node = RaftNode(args.id, args.port, peer_ports)
    node.log.append((0, {'type': 'init'}))  # Entrada inicial
    
    node.run()

if __name__ == "__main__":
    main()
```

### Ejecución y Resultados Esperados

Para ejecutar este ejemplo, necesitarás abrir varias terminales y ejecutar el script con diferentes parámetros para cada nodo:

```bash
# Terminal 1 - Nodo 1
python simple_raft.py --id 1 --port 5001 --peers 5002,5003,5004,5005

# Terminal 2 - Nodo 2
python simple_raft.py --id 2 --port 5002 --peers 5001,5003,5004,5005

# Terminal 3 - Nodo 3
python simple_raft.py --id 3 --port 5003 --peers 5001,5002,5004,5005

# Terminal 4 - Nodo 4
python simple_raft.py --id 4 --port 5004 --peers 5001,5002,5003,5005

# Terminal 5 - Nodo 5
python simple_raft.py --id 5 --port 5005 --peers 5001,5002,5003,5004
```

Una vez que los nodos estén en ejecución:

1. Uno de ellos será elegido líder después de un breve período.
2. Puedes verificar el estado de cada nodo:

```bash
curl http://localhost:5001/status
curl http://localhost:5002/status
curl http://localhost:5003/status
curl http://localhost:5004/status
curl http://localhost:5005/status
```

3. Enviar comandos al líder (suponiendo que el nodo 1 es el líder):

```bash
curl -X POST -H "Content-Type: application/json" -d '{"command": {"type": "set", "key": "x", "value": 10}}' http://localhost:5001/client_request
```

4. Simular un fallo del líder cerrando su terminal y observar cómo se elige un nuevo líder.
5. Verificar que el estado se ha replicado correctamente en todos los nodos después de la elección:

```bash
curl http://localhost:5002/status
curl http://localhost:5003/status
curl http://localhost:5004/status
curl http://localhost:5005/status
```

## Ejercicio: Implementación de Detección de Fallos

### Descripción

En este ejercicio, extenderemos el sistema para implementar un mecanismo más robusto de detección de fallos utilizando un enfoque de "sospecha" basado en timeouts adaptativos.

### Instrucciones

1. Añade un componente de detección de fallos que monitoree la salud de otros nodos.
2. Implementa timeouts adaptativos que se ajusten según las condiciones de la red.
3. Añade un mecanismo para que los nodos "sospechosos" puedan defenderse antes de ser considerados fallidos.

### Código Base para el Ejercicio

```python
# failure_detector.py
import time
import threading
import statistics
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdaptiveFailureDetector:
    def __init__(self, node_id, peer_ports, phi_threshold=10, min_timeout=0.1, max_timeout=10.0):
        self.node_id = node_id
        self.peer_ports = peer_ports
        self.phi_threshold = phi_threshold  # Umbral para considerar un nodo como sospechoso
        self.min_timeout = min_timeout
        self.max_timeout = max_timeout
        
        # Estado de los nodos
        self.node_status = {}  # port -> 'alive', 'suspected', 'failed'
        self.last_heartbeat = {}  # port -> timestamp
        self.heartbeat_history = {}  # port -> list of intervals
        
        # Inicializar estado
        for port in peer_ports:
            self.node_status[port] = 'alive'
            self.last_heartbeat[port] = time.time()
            self.heartbeat_history[port] = []
        
        # Lock para acceso concurrente
        self.lock = threading.Lock()
        
        # Iniciar hilos
        self.monitor_thread = threading.Thread(target=self.monitor_nodes)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        self.ping_thread = threading.Thread(target=self.send_pings)
        self.ping_thread.daemon = True
        self.ping_thread.start()
    
    def record_heartbeat(self, port):
        """Registra un heartbeat recibido de un nodo."""
        with self.lock:
            now = time.time()
            if port in self.last_heartbeat:
                interval = now - self.last_heartbeat[port]
                self.heartbeat_history[port].append(interval)
                # Mantener solo los últimos 10 intervalos
                if len(self.heartbeat_history[port]) > 10:
                    self.heartbeat_history[port].pop(0)
            
            self.last_heartbeat[port] = now
            self.node_status[port] = 'alive'
    
    def calculate_phi(self, port):
        """Calcula el valor phi para un nodo basado en su historial de heartbeats."""
        with self.lock:
            if port not in self.last_heartbeat:
                return float('inf')
            
            now = time.time()
            elapsed = now - self.last_heartbeat[port]
            
            # Si no hay suficiente historia, usar un valor conservador
            if len(self.heartbeat_history[port]) < 3:
                expected = self.min_timeout
                variance = self.min_timeout / 2
            else:
                expected = statistics.mean(self.heartbeat_history[port])
                variance = statistics.variance(self.heartbeat_history[port]) if len(self.heartbeat_history[port]) > 1 else expected / 2
            
            # Evitar división por cero
            variance = max(variance, 0.01)
            
            # Calcular phi usando la función de distribución acumulativa
            x = elapsed / expected
            phi = -1 * (x / variance)
            
            return phi
    
    def monitor_nodes(self):
        """Monitorea el estado de los nodos y actualiza su estado."""
        while True:
            time.sleep(0.1)  # Comprobar cada 100ms
            
            with self.lock:
                for port in self.peer_ports:
                    phi = self.calculate_phi(port)
                    
                    if phi > self.phi_threshold:
                        if self.node_status[port] == 'alive':
                            self.node_status[port] = 'suspected'
                            logger.info(f"Node {self.node_id} suspects node at port {port}")
                        elif self.node_status[port] == 'suspected':
                            # Si ha estado sospechoso por mucho tiempo, marcarlo como fallido
                            if time.time() - self.last_heartbeat[port] > self.max_timeout:
                                self.node_status[port] = 'failed'
                                logger.info(f"Node {self.node_id} marks node at port {port} as failed")
    
    def send_pings(self):
        """Envía pings periódicos a todos los nodos."""
        while True:
            time.sleep(0.5)  # Enviar pings cada 500ms
            
            for port in self.peer_ports:
                try:
                    response = requests.get(f"http://localhost:{port}/ping?from={self.node_id}", timeout=0.1)
                    if response.status_code == 200:
                        self.record_heartbeat(port)
                except requests.exceptions.RequestException:
                    # Ignorar errores de conexión
                    pass
    
    def get_alive_nodes(self):
        """Retorna la lista de nodos considerados vivos."""
        with self.lock:
            return [port for port, status in self.node_status.items() if status == 'alive']
    
    def get_failed_nodes(self):
        """Retorna la lista de nodos considerados fallidos."""
        with self.lock:
            return [port for port, status in self.node_status.items() if status == 'failed']

# TODO: Integrar este detector de fallos con el sistema Raft
# 1. Añadir un endpoint /ping en la clase RaftNode
# 2. Inicializar AdaptiveFailureDetector en RaftNode
# 3. Usar get_alive_nodes() para determinar a qué nodos enviar mensajes
# 4. Considerar solo los nodos vivos al calcular la mayoría para elecciones y commits
```

### Desafío Adicional

Una vez implementado el detector de fallos, añade las siguientes mejoras:

1. Implementa un mecanismo de "sospecha mutua" donde los nodos pueden defenderse de ser marcados como fallidos.
2. Añade soporte para la reincorporación de nodos que han fallado y se recuperan.
3. Implementa un mecanismo para simular particiones de red y observa cómo el sistema maneja estas situaciones.

## Implementación de un Servicio Tolerante a Fallos Bizantinos

### Descripción

Para complementar los ejemplos anteriores, aquí hay un ejemplo simplificado de cómo implementar un servicio tolerante a fallos bizantinos utilizando un enfoque de replicación con votación.

```python
# byzantine_service.py
import time
import random
import threading
import json
import argparse
from flask import Flask, request, jsonify
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ByzantineNode:
    def __init__(self, node_id, port, peer_ports=None, byzantine=False, byzantine_strategy=None):
        self.node_id = node_id
        self.port = port
        self.peer_ports = peer_ports or []
        self.byzantine = byzantine
        self.byzantine_strategy = byzantine_strategy or 'random'  # 'random', 'flip', 'delay'
        
        # Estado del nodo
        self.data = {}  # Almacén clave-valor
        self.lock = threading.Lock()
        
        # Inicializar la aplicación Flask
        self.app = Flask(f"node-{node_id}")
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/get/<key>', methods=['GET'])
        def get_value(key):
            with self.lock:
                if self.byzantine and self.byzantine_strategy == 'random':
                    # Nodo bizantino: devolver valor aleatorio
                    return jsonify({
                        'value': random.randint(0, 100),
                        'node_id': self.node_id
                    })
                elif self.byzantine and self.byzantine_strategy == 'flip':
                    # Nodo bizantino: devolver valor opuesto
                    if key in self.data:
                        try:
                            return jsonify({
                                'value': -self.data[key],
                                'node_id': self.node_id
                            })
                        except:
                            pass
                
                # Comportamiento normal
                if key in self.data:
                    return jsonify({
                        'value': self.data[key],
                        'node_id': self.node_id
                    })
                else:
                    return jsonify({
                        'error': 'Key not found',
                        'node_id': self.node_id
                    }), 404
        
        @self.app.route('/set', methods=['POST'])
        def set_value():
            data = request.json
            key = data.get('key')
            value = data.get('value')
            
            with self.lock:
                if self.byzantine and self.byzantine_strategy == 'delay':
                    # Nodo bizantino: retrasar la respuesta
                    time.sleep(2)
                
                self.data[key] = value
                
                return jsonify({
                    'status': 'success',
                    'node_id': self.node_id
                })
        
        @self.app.route('/status', methods=['GET'])
        def get_status():
            with self.lock:
                return jsonify({
                    'node_id': self.node_id,
                    'byzantine': self.byzantine,
                    'strategy': self.byzantine_strategy if self.byzantine else 'normal',
                    'data_size': len(self.data)
                })
    
    def run(self):
        """Inicia el servidor Flask."""
        self.app.run(host='0.0.0.0', port=self.port, debug=False, use_reloader=False)

class ByzantineClient:
    def __init__(self, node_ports, f=1):
        self.node_ports = node_ports
        self.f = f  # Número máximo de nodos bizantinos tolerados
        
        # Para tolerar f nodos bizantinos, necesitamos al menos 3f+1 nodos
        assert len(node_ports) >= 3 * f + 1, f"Se necesitan al menos {3*f+1} nodos para tolerar {f} fallos bizantinos"
    
    def get(self, key):
        """Obtiene un valor con tolerancia a fallos bizantinos."""
        responses = []
        
        for port in self.node_ports:
            try:
                response = requests.get(f"http://localhost:{port}/get/{key}", timeout=1)
                if response.status_code == 200:
                    data = response.json()
                    responses.append((data.get('value'), data.get('node_id')))
            except requests.exceptions.RequestException:
                # Ignorar errores de conexión
                pass
        
        # Si no tenemos suficientes respuestas, no podemos garantizar la corrección
        if len(responses) < 2 * self.f + 1:
            return None, "No hay suficientes respuestas"
        
        # Contar ocurrencias de cada valor
        value_counts = {}
        for value, _ in responses:
            value_counts[value] = value_counts.get(value, 0) + 1
        
        # Encontrar el valor más común
        max_count = 0
        max_value = None
        for value, count in value_counts.items():
            if count > max_count:
                max_count = count
                max_value = value
        
        # Verificar si tenemos una mayoría suficiente
        if max_count >= self.f + 1:
            return max_value, "Consenso alcanzado"
        else:
            return None, "No se pudo alcanzar consenso"
    
    def set(self, key, value):
        """Establece un valor con tolerancia a fallos bizantinos."""
        responses = []
        
        for port in self.node_ports:
            try:
                response = requests.post(
                    f"http://localhost:{port}/set",
                    json={'key': key, 'value': value},
                    timeout=1
                )
                if response.status_code == 200:
                    data = response.json()
                    responses.append((data.get('status'), data.get('node_id')))
            except requests.exceptions.RequestException:
                # Ignorar errores de conexión
                pass
        
        # Si no tenemos suficientes respuestas, no podemos garantizar la corrección
        if len(responses) < 2 * self.f + 1:
            return False, "No hay suficientes respuestas"
        
        # Contar ocurrencias de cada estado
        status_counts = {}
        for status, _ in responses:
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Verificar si tenemos una mayoría suficiente
        if status_counts.get('success', 0) >= 2 * self.f + 1:
            return True, "Operación exitosa"
        else:
            return False, "No se pudo completar la operación"

def main():
    parser = argparse.ArgumentParser(description='Byzantine Fault Tolerant Node')
    parser.add_argument('--id', type=int, required=True, help='ID del nodo')
    parser.add_argument('--port', type=int, required=True, help='Puerto del nodo')
    parser.add_argument('--peers', type=str, help='Puertos de los nodos pares (separados por comas)')
    parser.add_argument('--byzantine', action='store_true', help='Si el nodo debe comportarse de forma bizantina')
    parser.add_argument('--strategy', type=str, default='random', choices=['random', 'flip', 'delay'], help='Estrategia bizantina')
    
    args = parser.parse_args()
    
    peer_ports = []
    if args.peers:
        peer_ports = [int(p) for p in args.peers.split(',')]
    
    node = ByzantineNode(args.id, args.port, peer_ports, args.byzantine, args.strategy)
    node.run()

if __name__ == "__main__":
    main()
```

Para ejecutar este ejemplo, necesitarás abrir varias terminales:

```bash
# Terminal 1 - Nodo normal 1
python byzantine_service.py --id 1 --port 5001 --peers 5002,5003,5004

# Terminal 2 - Nodo normal 2
python byzantine_service.py --id 2 --port 5002 --peers 5001,5003,5004

# Terminal 3 - Nodo normal 3
python byzantine_service.py --id 3 --port 5003 --peers 5001,5002,5004

# Terminal 4 - Nodo bizantino
python byzantine_service.py --id 4 --port 5004 --peers 5001,5002,5003 --byzantine --strategy random
```

Luego, puedes crear un cliente para interactuar con el sistema:

```python
# client_example.py
from byzantine_service import ByzantineClient

client = ByzantineClient([5001, 5002, 5003, 5004], f=1)

# Establecer un valor
success, message = client.set('x', 42)
print(f"Set result: {success}, {message}")

# Obtener el valor
value, message = client.get('x')
print(f"Get result: {value}, {message}")
```

## Aplicaciones Prácticas

Los mecanismos de tolerancia a fallos y consenso tienen numerosas aplicaciones:

1. **Sistemas de almacenamiento distribuido**: Garantizar la consistencia y disponibilidad de datos.
2. **Blockchain y criptomonedas**: Lograr consenso sobre el estado del libro mayor distribuido.
3. **Servicios críticos**: Mantener la disponibilidad y corrección en sistemas de alta fiabilidad.
4. **Computación en la nube**: Coordinar recursos y servicios distribuidos.
5. **Sistemas de control industrial**: Garantizar operaciones seguras incluso ante fallos.

## Preguntas de Reflexión

1. ¿Qué ventajas ofrece Raft sobre otros algoritmos de consenso como Paxos?
2. ¿Cómo afecta el número de nodos al rendimiento y la tolerancia a fallos de un sistema distribuido?
3. ¿Qué estrategias existen para manejar particiones de red en sistemas distribuidos?
4. ¿En qué situaciones es necesaria la tolerancia a fallos bizantinos y cuándo es suficiente la tolerancia a fallos por caída?

## Referencias

1. Ongaro, D., & Ousterhout, J. (2014). In search of an understandable consensus algorithm. USENIX Annual Technical Conference, 305-319.
2. Lamport, L., Shostak, R., & Pease, M. (1982). The Byzantine generals problem. ACM Transactions on Programming Languages and Systems, 4(3), 382-401.
3. Castro, M., & Liskov, B. (1999). Practical Byzantine fault tolerance. OSDI, 99, 173-186.
