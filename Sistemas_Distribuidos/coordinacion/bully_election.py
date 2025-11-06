import threading
import time
import random

class Process:
    def __init__(self, process_id, num_processes):
        self.id = process_id
        self.num_processes = num_processes
        self.leader = -1
        self.active = True
        self.lock = threading.Lock()

    def set_leader(self, leader_id):
        with self.lock:
            self.leader = leader_id
            print(f"P{self.id}: Nuevo líder establecido: P{self.leader}")

    def start_election(self, all_processes):
        with self.lock:
            if not self.active:
                return

            print(f"\n--- P{self.id} INICIA ELECCIÓN ---")
            
            # 1. Enviar mensaje 'Election' a todos los procesos con ID superior
            higher_processes = [p for p in all_processes if p.id > self.id]
            if not higher_processes:
                # 2. Si es el de mayor ID (y está activo), se declara líder
                self.set_leader(self.id)
                self.announce_leader(all_processes)
                return

            print(f"P{self.id}: Enviando mensajes ELECTION a procesos más altos: {[p.id for p in higher_processes]}")
            
            # 3. Esperar respuesta ('OK')
            received_ok = False
            for p in higher_processes:
                if p.receive_election(self):
                    received_ok = True
                    break 

            if not received_ok:
                # 4. Si no recibe 'OK', se declara líder
                self.set_leader(self.id)
                self.announce_leader(all_processes)
            else:
                print(f"P{self.id}: Recibió OK. Esperando mensaje COORDINATOR.")


    def receive_election(self, sender):
        with self.lock:
            if not self.active:
                return False

            print(f"P{self.id}: Recibido ELECTION de P{sender.id}. Respondiendo OK.")
            sender.receive_ok(self)
            
            if self.leader != self.id: 
                pass 
            return True

    def receive_ok(self, sender):
        with self.lock:
            if self.active:
                print(f"P{self.id}: Recibido OK de P{sender.id}.")

    def announce_leader(self, all_processes):
        print(f"P{self.id}: Enviando mensaje COORDINATOR (Líder: P{self.id}) a todos.")
        for p in all_processes:
            p.receive_coordinator(self.id)

    def receive_coordinator(self, leader_id):
        with self.lock:
            if self.active:
                self.set_leader(leader_id)

    def fail(self):
        with self.lock:
            self.active = False
            print(f"--- P{self.id} HA FALLADO (Inactivo) ---")

def main():
    NUM_PROCESSES = 5
    processes = [Process(i, NUM_PROCESSES) for i in range(NUM_PROCESSES)]
    all_processes = processes[:]
    
    processes[NUM_PROCESSES - 1].set_leader(NUM_PROCESSES - 1)
    
    print("\n--- INICIO DE SIMULACIÓN ALGORITMO BULLY ---")
    
    # 1. Simular Fallo del Líder (P4)
    time.sleep(1)
    processes[NUM_PROCESSES - 1].fail()
    
    # 2. Iniciar elección (ej: P1 detecta el fallo)
    time.sleep(1)
    initiator_id = 1
    processes[initiator_id].start_election(all_processes)
    
    # 3. Simular un segundo fallo durante la elección (ej: P3)
    time.sleep(2)
    processes[3].fail()
    
    # 4. Simular una segunda elección (ej: P0 detecta el fallo)
    time.sleep(1)
    processes[0].start_election(all_processes)


if __name__ == "__main__":
    main()
