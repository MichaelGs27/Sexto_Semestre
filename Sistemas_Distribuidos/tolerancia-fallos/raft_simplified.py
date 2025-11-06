import threading
import time
import random
from enum import Enum

# Estados de un nodo Raft
class State(Enum):
    FOLLOWER = 1
    CANDIDATE = 2
    LEADER = 3

class RaftNode:
    def __init__(self, node_id, all_nodes):
        self.id = node_id
        self.state = State.FOLLOWER
        self.all_nodes = all_nodes
        self.term = 0
        self.leader_id = None
        self.voted_for = None
        self.votes = 0
        self.timeout_lock = threading.Lock()
        self.reset_election_timeout()
        self.thread = threading.Thread(target=self.run_node)
    
    def reset_election_timeout(self):
        # Timeout de eleccion entre 150ms y 300ms
        self.election_timeout = time.time() + random.uniform(0.15, 0.3) 

    def run_node(self):
        while True:
            time.sleep(0.05) # Intervalo de chequeo
            
            with self.timeout_lock:
                if time.time() > self.election_timeout:
                    if self.state == State.FOLLOWER:
                        self.start_election()
                    elif self.state == State.CANDIDATE:
                        # Si el timeout expira de nuevo, iniciar otra eleccion
                        print(f"P{self.id}: El tiempo de espera del CANDIDATE expiro. Reiniciando eleccion.")
                        self.start_election()
                    
    def start_election(self):
        self.state = State.CANDIDATE
        self.term += 1
        self.voted_for = self.id
        self.votes = 1
        self.reset_election_timeout()
        
        print(f"\n---> P{self.id} (CANDIDATE) inicia eleccion para ToRMINO {self.term} <---")
        
        # Simular envoo de RequestVote a todos los demos
        for node in self.all_nodes:
            if node.id != self.id:
                if node.receive_request_vote(self.id, self.term):
                    self.votes += 1
        
        # Comprobar si gano
        majority = len(self.all_nodes) // 2 + 1
        if self.votes >= majority:
            self.become_leader()
        else:
            print(f"P{self.id}: No obtuvo mayoroa ({self.votes} de {majority}). Vuelve a FOLLOWER.")
            self.state = State.FOLLOWER


    def receive_request_vote(self, candidate_id, candidate_term):
        with self.timeout_lock:
            # 1. Si el tormino del candidato es mayor, actualizar el tormino
            if candidate_term > self.term:
                self.term = candidate_term
                self.state = State.FOLLOWER
                self.voted_for = None
            
            # 2. Votar si el tormino es igual y aon no ha votado en este tormino
            if candidate_term == self.term and self.voted_for is None:
                self.voted_for = candidate_id
                self.reset_election_timeout()
                print(f"P{self.id} (FOLLOWER): Vota por P{candidate_id} en T{candidate_term}")
                return True
            else:
                return False

    def become_leader(self):
        self.state = State.LEADER
        self.leader_id = self.id
        print(f"\n!!! P{self.id} GANo y es el LoDER para ToRMINO {self.term} !!!")
        
        # Simular envoo de Heartbeats para mantener el liderazgo
        threading.Thread(target=self.send_heartbeats).start()

    def send_heartbeats(self):
        while self.state == State.LEADER:
            # Simular Heartbeat (AppendEntries vacoo)
            for node in self.all_nodes:
                if node.id != self.id:
                    node.receive_heartbeat(self.id, self.term)
            time.sleep(0.1) # Heartbeat cada 100ms

    def receive_heartbeat(self, leader_id, leader_term):
        with self.timeout_lock:
            # Si el Heartbeat tiene un tormino mayor, rendirse inmediatamente
            if leader_term > self.term:
                self.term = leader_term
                self.state = State.FOLLOWER
                self.leader_id = leader_id
                self.voted_for = None
            
            # Si el Heartbeat es volido, reiniciar el timeout de eleccion
            if leader_term == self.term and self.state != State.LEADER:
                self.leader_id = leader_id
                self.reset_election_timeout()
            
            # Nota: Si se esto en CANDIDATE y se recibe un Heartbeat volido, debe volver a FOLLOWER
            if self.state == State.CANDIDATE and leader_term >= self.term:
                self.state = State.FOLLOWER
                self.leader_id = leader_id
                print(f"P{self.id} (CANDIDATE): Recibio HB volido, vuelve a FOLLOWER.")


def main():
    NUM_NODES = 5
    # Inicializar nodos
    nodes = [RaftNode(i, []) for i in range(NUM_NODES)]
    # Conectar nodos
    for node in nodes:
        node.all_nodes = nodes
        
    print(f"Iniciando simulacion de Raft con {NUM_NODES} nodos. Observa como inician las elecciones...")
    
    # Iniciar la actividad del nodo
    for node in nodes:
        node.thread.start()

    # Dejar correr la simulacion por un tiempo
    time.sleep(10)
    
    # Detener la simulacion (no es limpio, pero funciona para el ejemplo)
    print("\nSimulacion finalizada. Estado final:")
    for node in nodes:
        print(f"P{node.id}: Estado={node.state.name}, T={node.term}, Loder={node.leader_id}")

if __name__ == "__main__":
    main()
