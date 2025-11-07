import threading
import time
import random

# Constantes del Reloj de Lamport
CLOCK = 0
CLOCK_LOCK = threading.Lock()

# Estado del proceso: 'RELEASED', 'WANTED', 'HELD'
STATE = 'RELEASED'

# Conjunto de procesos a los que se les debe enviar un mensaje de peticion
DEFERRED_REPLIES = []

# Conjunto de procesos a los que se les ha enviado una peticion (para saber cuondo entrar a la seccion crotica)
REQUEST_SENT_TO = set()

# Lock para la seccion crotica (solo se usa para simular el acceso, el algoritmo se encarga de la exclusion)
CS_LOCK = threading.Lock() 
PROCESS_ID = -1

# Lista global de todos los objetos Process para mensajeroa
ALL_PROCESSES = []

def get_current_time():
    global CLOCK
    with CLOCK_LOCK:
        CLOCK += 1
        return CLOCK

def send_request(target_id):
    global CLOCK
    time_sent = get_current_time()
    
    print(f"P{PROCESS_ID}: Enviando REQUEST a P{target_id} en tiempo {time_sent}")
    
    # Simular latencia y enviar a la funcion de recepcion
    time.sleep(random.uniform(0.01, 0.1))
    ALL_PROCESSES[target_id].receive_request(PROCESS_ID, time_sent)

def receive_request(sender_id, sender_time):
    global CLOCK, STATE, DEFERRED_REPLIES
    
    # 1. Actualizar reloj de Lamport (Regla de Lamport)
    with CLOCK_LOCK:
        CLOCK = max(CLOCK, sender_time) + 1
        current_time = CLOCK

    print(f"P{PROCESS_ID}: Recibido REQUEST de P{sender_id} en tiempo {sender_time}. Mi tiempo actual: {current_time}")

    # 2. Decidir si enviar REPLY o diferirlo
    
    # Criterio de prioridad: Si el receptor esto en RELEASED O si el receptor tiene un timestamp MAYOR que el emisor
    # (El timestamp (tiempo, ID) se usa para el desempate)
    my_priority = (current_time, PROCESS_ID)
    sender_priority = (sender_time, sender_id)
    
    if STATE == 'RELEASED' or (STATE == 'WANTED' and my_priority > sender_priority):
        # Enviar REPLY inmediatamente
        send_reply(sender_id)
        
    else: # Si el receptor esto en HELD (Seccion Crotica) o tiene MAYOR prioridad
        # Diferir el REPLY
        DEFERRED_REPLIES.append(sender_id)
        print(f"P{PROCESS_ID}: Difiriendo REPLY a P{sender_id}. Mi estado es {STATE}.")

def send_reply(target_id):
    global CLOCK
    reply_time = get_current_time()
    print(f"P{PROCESS_ID}: Enviando REPLY a P{target_id} en tiempo {reply_time}")
    
    # Simular latencia y enviar a la funcion de recepcion
    time.sleep(random.uniform(0.01, 0.1))
    ALL_PROCESSES[target_id].receive_reply(PROCESS_ID, reply_time)

def receive_reply(sender_id, reply_time):
    global REQUEST_SENT_TO
    
    with CLOCK_LOCK:
        global CLOCK
        CLOCK = max(CLOCK, reply_time) + 1
        
    print(f"P{PROCESS_ID}: Recibido REPLY de P{sender_id}. Tiempo: {CLOCK}")
    
    # Remover al remitente de la lista de pendientes
    REQUEST_SENT_TO.discard(sender_id)

    # Verificar si se puede entrar a la seccion crotica (solo si es el oltimo REPLY)
    if not REQUEST_SENT_TO and STATE == 'WANTED':
        enter_critical_section()

def enter_critical_section():
    global STATE
    STATE = 'HELD'
    get_current_time() # Toca el reloj antes de entrar
    print(f"\n---> P{PROCESS_ID} ENTRA a la SECCIoN CRoTICA. Tiempo: {CLOCK} <---")
    
    # Simular trabajo en la Seccion Crotica
    time.sleep(random.uniform(1.0, 2.0))
    
    exit_critical_section()

def exit_critical_section():
    global STATE, DEFERRED_REPLIES
    STATE = 'RELEASED'
    get_current_time() # Toca el reloj al salir
    print(f"\n---> P{PROCESS_ID} SALE de la SECCIoN CRoTICA. Tiempo: {CLOCK} <---")
    
    # Enviar REPLY a todos los procesos diferidos
    for sender_id in DEFERRED_REPLIES:
        send_reply(sender_id)
        
    DEFERRED_REPLIES = []

def request_critical_section(all_processes):
    global STATE, REQUEST_SENT_TO, PROCESS_ID
    
    # 1. Marcar estado como WANTED y obtener tiempo de peticion
    STATE = 'WANTED'
    get_current_time() 
    
    # 2. Inicializar el conjunto de procesos pendientes (todos menos uno mismo)
    REQUEST_SENT_TO = set(p.id for p in all_processes if p.id != PROCESS_ID)
    
    print(f"\nP{PROCESS_ID}: Pide acceso a la Seccion Crotica. Tiempo de peticion: {CLOCK}")
    
    # 3. Enviar REQUEST a todos los demos procesos
    for process in all_processes:
        if process.id != PROCESS_ID:
            send_request(process.id)

class ProcessRunner:
    def __init__(self, id, all_processes):
        self.id = id
        self.thread = threading.Thread(target=process_activity, args=(self, all_processes))
        
    def start(self):
        self.thread.start()

    def join(self):
        self.thread.join()

def process_activity(process, all_processes):
    global PROCESS_ID, ALL_PROCESSES
    PROCESS_ID = process.id
    ALL_PROCESSES = all_processes
    
    # Simular que los procesos piden acceso a la SC en momentos aleatorios
    time.sleep(random.uniform(0, 3))
    
    # Un proceso pide la SC
    request_critical_section(all_processes)
    # Dormir para permitir que otros procesos compitan
    time.sleep(5) 

# --- Simulacion principal ---
if __name__ == "__main__":
    NUM_PROCESSES = 3
    
    # Se usa una simulacion de objetos para manejar el envoo de mensajes entre hilos
    ALL_PROCESSES = [
        type('MockProcess', (object,), {
            'id': i,
            'receive_request': lambda self, sender_id, sender_time: receive_request(sender_id, sender_time),
            'receive_reply': lambda self, sender_id, reply_time: receive_reply(sender_id, reply_time),
        })() 
        for i in range(NUM_PROCESSES)
    ]

    # Ejecutar hilos
    runners = [ProcessRunner(i, ALL_PROCESSES) for i in range(NUM_PROCESSES)]
    
    print("Iniciando simulacion de Exclusion Mutua (Ricart-Agrawala) con 3 procesos...")
    
    for runner in runners:
        runner.start()
        
    for runner in runners:
        runner.join()
        
    print("\nSimulacion de Ricart-Agrawala Finalizada.")
