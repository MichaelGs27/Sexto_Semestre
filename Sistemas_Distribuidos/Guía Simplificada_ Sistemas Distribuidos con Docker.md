# Guía Simplificada: Sistemas Distribuidos con Docker

## Introducción

Esta guía presenta un enfoque simplificado para demostrar los conceptos fundamentales de sistemas distribuidos utilizando Docker, sin necesidad de desarrollar aplicaciones web complejas con frontend y backend. Nos centraremos en scripts de línea de comandos y herramientas básicas que ilustran claramente los principios de distribución, coordinación y tolerancia a fallos.

## Requisitos Previos

1. **Hardware mínimo recomendado**:
   - 2GB de RAM
   - 5GB de espacio libre en disco
   - Procesador de doble núcleo

2. **Software necesario**:
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/) (incluye Docker Engine y Docker Compose)
   - Terminal o línea de comandos
   - Editor de texto básico

## Parte 1: Instalación y Configuración de Docker

### Paso 1: Instalar Docker Desktop

#### Para Windows:
1. Descarga Docker Desktop desde [la página oficial](https://www.docker.com/products/docker-desktop/)
2. Ejecuta el instalador y sigue las instrucciones
3. Asegúrate de que la opción "WSL 2" esté seleccionada durante la instalación
4. Reinicia tu computadora si es necesario

#### Para macOS:
1. Descarga Docker Desktop desde [la página oficial](https://www.docker.com/products/docker-desktop/)
2. Arrastra Docker a la carpeta de Aplicaciones
3. Abre Docker desde la carpeta de Aplicaciones
4. Sigue las instrucciones de configuración inicial

#### Para Linux:
1. Sigue las instrucciones específicas para tu distribución en [la documentación oficial](https://docs.docker.com/engine/install/)
2. Instala Docker Compose siguiendo [estas instrucciones](https://docs.docker.com/compose/install/)

### Paso 2: Verificar la Instalación

1. Abre una terminal o línea de comandos
2. Ejecuta los siguientes comandos para verificar que Docker está funcionando correctamente:
   ```bash
   docker --version
   docker-compose --version
   docker run hello-world
   ```

## Parte 2: Demostración de Tiempo y Orden en Sistemas Distribuidos

### Paso 3: Crear un Directorio para el Proyecto

1. Crea un directorio para el proyecto:
   ```bash
   mkdir -p sistemas-distribuidos/tiempo-orden
   cd sistemas-distribuidos/tiempo-orden
   ```

### Paso 4: Implementar Relojes Lógicos de Lamport

1. Crea un script Python para simular relojes lógicos de Lamport:
   ```bash
   cat > lamport_clock.py << 'EOF'
   import time
   import random
   import threading
   import os
   
   class Process:
       def __init__(self, process_id):
           self.process_id = process_id
           self.clock = 0
           self.log = []
           self.lock = threading.Lock()
       
       def local_event(self):
           with self.lock:
               self.clock += 1
               event = f"Proceso {self.process_id}: Evento local en tiempo {self.clock}"
               self.log.append((self.clock, event))
               print(event)
       
       def send_message(self, receiver):
           with self.lock:
               self.clock += 1
               message = {"sender": self.process_id, "clock": self.clock}
               event = f"Proceso {self.process_id}: Envío a P{receiver.process_id} en tiempo {self.clock}"
               self.log.append((self.clock, event))
               print(event)
           
           # Simular latencia de red
           time.sleep(random.uniform(0.1, 0.5))
           receiver.receive_message(message)
       
       def receive_message(self, message):
           with self.lock:
               sender_clock = message["clock"]
               self.clock = max(self.clock, sender_clock) + 1
               event = f"Proceso {self.process_id}: Recibido de P{message['sender']} en tiempo {self.clock}"
               self.log.append((self.clock, event))
               print(event)
       
       def print_log(self):
           print(f"\nRegistro de eventos del Proceso {self.process_id}:")
           for clock, event in sorted(self.log, key=lambda x: x[0]):
               print(f"  {event}")
   
   def process_activity(process, other_processes, num_events=5):
       for _ in range(num_events):
           # Simular actividad aleatoria
           time.sleep(random.uniform(0.2, 1.0))
           
           # Decidir aleatoriamente entre evento local o envío de mensaje
           if random.random() < 0.3 or not other_processes:  # 30% probabilidad de evento local
               process.local_event()
           else:
               # Seleccionar un proceso aleatorio para enviar mensaje
               receiver = random.choice(other_processes)
               process.send_message(receiver)
   
   def main():
       # Crear procesos
       num_processes = 3
       processes = [Process(i) for i in range(num_processes)]
       
       # Crear hilos para cada proceso
       threads = []
       for i, process in enumerate(processes):
           other_procs = processes[:i] + processes[i+1:]
           thread = threading.Thread(target=process_activity, args=(process, other_procs))
           threads.append(thread)
       
       # Iniciar todos los hilos
       print("Iniciando simulación de relojes lógicos de Lamport...")
       for thread in threads:
           thread.start()
       
       # Esperar a que todos los hilos terminen
       for thread in threads:
           thread.join()
       
       # Imprimir logs
       print("\n" + "="*50)
       print("RESULTADOS DE LA SIMULACIÓN")
       print("="*50)
       for process in processes:
           process.print_log()
   
   if __name__ == "__main__":
       main()
   EOF
   ```

2. Crea un Dockerfile para ejecutar el script:
   ```bash
   cat > Dockerfile << 'EOF'
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY lamport_clock.py .
   
   CMD ["python", "lamport_clock.py"]
   EOF
   ```

3. Construye y ejecuta el contenedor:
   ```bash
   docker build -t lamport-clock .
   docker run lamport-clock
   ```

### Paso 5: Implementar Relojes Vectoriales

1. Crea un script Python para simular relojes vectoriales:
   ```bash
   cat > vector_clock.py << 'EOF'
   import time
   import random
   import threading
   import os
   from collections import defaultdict
   
   class Process:
       def __init__(self, process_id, num_processes):
           self.process_id = process_id
           self.vector_clock = [0] * num_processes
           self.log = []
           self.lock = threading.Lock()
       
       def local_event(self):
           with self.lock:
               self.vector_clock[self.process_id] += 1
               clock_str = self._format_vector_clock()
               event = f"Proceso {self.process_id}: Evento local con vector {clock_str}"
               self.log.append((self.vector_clock.copy(), event))
               print(event)
       
       def send_message(self, receiver):
           with self.lock:
               self.vector_clock[self.process_id] += 1
               clock_str = self._format_vector_clock()
               event = f"Proceso {self.process_id}: Envío a P{receiver.process_id} con vector {clock_str}"
               self.log.append((self.vector_clock.copy(), event))
               print(event)
               message = {"sender": self.process_id, "vector_clock": self.vector_clock.copy()}
           
           # Simular latencia de red
           time.sleep(random.uniform(0.1, 0.5))
           receiver.receive_message(message)
       
       def receive_message(self, message):
           with self.lock:
               sender_clock = message["vector_clock"]
               # Actualizar el reloj vectorial (tomar el máximo para cada componente)
               for i in range(len(self.vector_clock)):
                   self.vector_clock[i] = max(self.vector_clock[i], sender_clock[i])
               # Incrementar el componente propio
               self.vector_clock[self.process_id] += 1
               
               clock_str = self._format_vector_clock()
               event = f"Proceso {self.process_id}: Recibido de P{message['sender']} con vector {clock_str}"
               self.log.append((self.vector_clock.copy(), event))
               print(event)
       
       def _format_vector_clock(self):
           return "[" + ", ".join(map(str, self.vector_clock)) + "]"
       
       def print_log(self):
           print(f"\nRegistro de eventos del Proceso {self.process_id}:")
           for clock, event in self.log:
               clock_str = "[" + ", ".join(map(str, clock)) + "]"
               print(f"  {event}")
       
       def detect_concurrent_events(self, other_process):
           concurrent_events = []
           
           for clock1, event1 in self.log:
               for clock2, event2 in other_process.log:
                   if self._is_concurrent(clock1, clock2):
                       concurrent_events.append((event1, event2))
           
           return concurrent_events
       
       def _is_concurrent(self, clock1, clock2):
           """Determina si dos relojes vectoriales representan eventos concurrentes."""
           less_than = False
           greater_than = False
           
           for i in range(len(clock1)):
               if clock1[i] < clock2[i]:
                   less_than = True
               elif clock1[i] > clock2[i]:
                   greater_than = True
           
           # Son concurrentes si hay componentes mayores en ambas direcciones
           return less_than and greater_than
   
   def process_activity(process, other_processes, num_events=5):
       for _ in range(num_events):
           # Simular actividad aleatoria
           time.sleep(random.uniform(0.2, 1.0))
           
           # Decidir aleatoriamente entre evento local o envío de mensaje
           if random.random() < 0.3 or not other_processes:  # 30% probabilidad de evento local
               process.local_event()
           else:
               # Seleccionar un proceso aleatorio para enviar mensaje
               receiver = random.choice(other_processes)
               process.send_message(receiver)
   
   def main():
       # Crear procesos
       num_processes = 3
       processes = [Process(i, num_processes) for i in range(num_processes)]
       
       # Crear hilos para cada proceso
       threads = []
       for i, process in enumerate(processes):
           other_procs = processes[:i] + processes[i+1:]
           thread = threading.Thread(target=process_activity, args=(process, other_procs))
           threads.append(thread)
       
       # Iniciar todos los hilos
       print("Iniciando simulación de relojes vectoriales...")
       for thread in threads:
           thread.start()
       
       # Esperar a que todos los hilos terminen
       for thread in threads:
           thread.join()
       
       # Imprimir logs
       print("\n" + "="*50)
       print("RESULTADOS DE LA SIMULACIÓN")
       print("="*50)
       for process in processes:
           process.print_log()
       
       # Detectar eventos concurrentes
       print("\n" + "="*50)
       print("EVENTOS CONCURRENTES DETECTADOS")
       print("="*50)
       for i in range(num_processes):
           for j in range(i+1, num_processes):
               concurrent = processes[i].detect_concurrent_events(processes[j])
               if concurrent:
                   print(f"\nEventos concurrentes entre P{i} y P{j}:")
                   for e1, e2 in concurrent:
                       print(f"  - {e1}")
                       print(f"    {e2}")
   
   if __name__ == "__main__":
       main()
   EOF
   ```

2. Actualiza el Dockerfile para ejecutar el script de relojes vectoriales:
   ```bash
   cat > Dockerfile << 'EOF'
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY vector_clock.py .
   
   CMD ["python", "vector_clock.py"]
   EOF
   ```

3. Construye y ejecuta el contenedor:
   ```bash
   docker build -t vector-clock .
   docker run vector-clock
   ```

## Parte 3: Demostración de Coordinación Distribuida

### Paso 6: Crear un Directorio para Coordinación

1. Crea un directorio para los ejemplos de coordinación:
   ```bash
   cd ..
   mkdir -p coordinacion
   cd coordinacion
   ```

### Paso 7: Implementar Algoritmo de Elección de Líder (Bully)

1. Crea un script Python para simular el algoritmo Bully:
   ```bash
   cat > bully_algorithm.py << 'EOF'
   import time
   import random
   import threading
   import os
   
   class Process:
       def __init__(self, process_id, num_processes):
           self.process_id = process_id
           self.num_processes = num_processes
           self.is_active = True
           self.is_leader = False
           self.current_leader = None
           self.lock = threading.Lock()
           self.election_in_progress = False
           self.responses_received = 0
           self.log = []
       
       def log_event(self, event):
           timestamp = time.time()
           self.log.append((timestamp, event))
           print(f"[{time.strftime('%H:%M:%S')}] {event}")
       
       def start_election(self):
           with self.lock:
               if self.election_in_progress:
                   return
               
               self.election_in_progress = True
               self.responses_received = 0
               self.log_event(f"Proceso {self.process_id}: Inicia elección")
           
           # Enviar mensaje de elección a todos los procesos con ID mayor
           higher_processes = [p for p in range(self.process_id + 1, self.num_processes) if processes[p].is_active]
           
           if not higher_processes:
               # No hay procesos con ID mayor, este proceso se convierte en líder
               self.become_leader()
           else:
               # Enviar mensaje de elección a procesos con ID mayor
               for p_id in higher_processes:
                   self.log_event(f"Proceso {self.process_id}: Envía mensaje de elección a P{p_id}")
                   threading.Thread(target=self.send_election_message, args=(p_id,)).start()
               
               # Esperar respuestas
               threading.Thread(target=self.wait_for_responses, args=(higher_processes,)).start()
       
       def send_election_message(self, target_id):
           # Simular latencia de red
           time.sleep(random.uniform(0.1, 0.3))
           
           # Verificar si el proceso destino está activo
           if processes[target_id].is_active:
               processes[target_id].receive_election_message(self.process_id)
       
       def receive_election_message(self, sender_id):
           with self.lock:
               self.log_event(f"Proceso {self.process_id}: Recibe mensaje de elección de P{sender_id}")
               
               # Responder al remitente
               threading.Thread(target=self.send_ok_message, args=(sender_id,)).start()
               
               # Iniciar una nueva elección
               if not self.election_in_progress:
                   threading.Thread(target=self.start_election).start()
       
       def send_ok_message(self, target_id):
           # Simular latencia de red
           time.sleep(random.uniform(0.1, 0.3))
           
           # Verificar si el proceso destino está activo
           if processes[target_id].is_active:
               processes[target_id].receive_ok_message(self.process_id)
       
       def receive_ok_message(self, sender_id):
           with self.lock:
               self.responses_received += 1
               self.log_event(f"Proceso {self.process_id}: Recibe OK de P{sender_id}")
       
       def wait_for_responses(self, higher_processes):
           # Esperar un tiempo para recibir respuestas
           time.sleep(1.0)
           
           with self.lock:
               if self.responses_received > 0:
                   # Recibió al menos una respuesta, no se convierte en líder
                   self.log_event(f"Proceso {self.process_id}: Recibió {self.responses_received} respuestas, espera mensaje de coordinador")
                   self.election_in_progress = False
               else:
                   # No recibió respuestas, se convierte en líder
                   self.become_leader()
       
       def become_leader(self):
           with self.lock:
               self.is_leader = True
               self.current_leader = self.process_id
               self.election_in_progress = False
               self.log_event(f"Proceso {self.process_id}: Se convierte en LÍDER")
           
           # Anunciar victoria a todos los demás procesos
           for p_id in range(self.num_processes):
               if p_id != self.process_id and processes[p_id].is_active:
                   threading.Thread(target=self.send_coordinator_message, args=(p_id,)).start()
       
       def send_coordinator_message(self, target_id):
           # Simular latencia de red
           time.sleep(random.uniform(0.1, 0.3))
           
           # Verificar si el proceso destino está activo
           if processes[target_id].is_active:
               processes[target_id].receive_coordinator_message(self.process_id)
       
       def receive_coordinator_message(self, leader_id):
           with self.lock:
               self.current_leader = leader_id
               self.is_leader = False
               self.election_in_progress = False
               self.log_event(f"Proceso {self.process_id}: Reconoce a P{leader_id} como LÍDER")
       
       def fail(self):
           with self.lock:
               self.is_active = False
               was_leader = self.is_leader
               self.is_leader = False
               self.log_event(f"Proceso {self.process_id}: FALLA" + (" (era LÍDER)" if was_leader else ""))
           return was_leader
       
       def recover(self):
           with self.lock:
               self.is_active = True
               self.is_leader = False
               self.current_leader = None
               self.log_event(f"Proceso {self.process_id}: RECUPERADO")
           
           # Iniciar elección al recuperarse
           threading.Thread(target=self.start_election).start()
       
       def print_status(self):
           status = "LÍDER" if self.is_leader else f"Sigue a P{self.current_leader}" if self.current_leader is not None else "Sin líder"
           state = "Activo" if self.is_active else "Inactivo"
           return f"Proceso {self.process_id}: {state}, {status}"
   
   def simulate_process_failures(processes):
       # Esperar a que se establezca un líder inicial
       time.sleep(3)
       
       # Simular fallos aleatorios
       for _ in range(3):
           time.sleep(random.uniform(1, 3))
           
           # Seleccionar un proceso aleatorio para fallar
           active_processes = [p for p in range(len(processes)) if processes[p].is_active]
           if active_processes:
               fail_id = random.choice(active_processes)
               was_leader = processes[fail_id].fail()
               
               # Si el líder falló, iniciar una nueva elección desde otro proceso
               if was_leader:
                   time.sleep(1)  # Esperar un poco para simular detección de fallo
                   active_processes = [p for p in range(len(processes)) if processes[p].is_active]
                   if active_processes:
                       initiator = random.choice(active_processes)
                       print(f"\n[SISTEMA] Detectado fallo del líder. P{initiator} inicia nueva elección.")
                       processes[initiator].start_election()
           
           # Recuperar un proceso inactivo aleatorio
           time.sleep(random.uniform(1, 3))
           inactive_processes = [p for p in range(len(processes)) if not processes[p].is_active]
           if inactive_processes:
               recover_id = random.choice(inactive_processes)
               processes[recover_id].recover()
   
   def print_final_status(processes):
       print("\n" + "="*50)
       print("ESTADO FINAL DEL SISTEMA")
       print("="*50)
       for process in processes:
           print(process.print_status())
   
   # Variable global para almacenar los procesos
   processes = []
   
   def main():
       global processes
       
       # Crear procesos
       num_processes = 5
       processes = [Process(i, num_processes) for i in range(num_processes)]
       
       # Iniciar elección desde el proceso 0
       print("Iniciando simulación del algoritmo Bully...")
       threading.Thread(target=processes[0].start_election).start()
       
       # Simular fallos y recuperaciones
       threading.Thread(target=simulate_process_failures, args=(processes,)).start()
       
       # Ejecutar la simulación por un tiempo
       time.sleep(15)
       
       # Imprimir estado final
       print_final_status(processes)
   
   if __name__ == "__main__":
       main()
   EOF
   ```

2. Crea un Dockerfile para ejecutar el algoritmo Bully:
   ```bash
   cat > Dockerfile << 'EOF'
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY bully_algorithm.py .
   
   CMD ["python", "bully_algorithm.py"]
   EOF
   ```

3. Construye y ejecuta el contenedor:
   ```bash
   docker build -t bully-algorithm .
   docker run bully-algorithm
   ```

### Paso 8: Implementar Exclusión Mutua Distribuida

1. Crea un script Python para simular el algoritmo de exclusión mutua de Ricart-Agrawala:
   ```bash
   cat > mutual_exclusion.py << 'EOF'
   import time
   import random
   import threading
   import os
   from collections import defaultdict
   
   class Process:
       def __init__(self, process_id, num_processes):
           self.process_id = process_id
           self.num_processes = num_processes
           self.clock = 0
           self.state = "RELEASED"  # RELEASED, WANTED, HELD
           self.request_timestamp = 0
           self.reply_pending = set()
           self.deferred_replies = set()
           self.lock = threading.Lock()
           self.resource_access_count = 0
           self.log = []
       
       def log_event(self, event):
           timestamp = time.time()
           self.log.append((timestamp, event))
           print(f"[{time.strftime('%H:%M:%S')}] {event}")
       
       def local_event(self):
           with self.lock:
               self.clock += 1
       
       def request_resource(self):
           with self.lock:
               self.state = "WANTED"
               self.clock += 1
               self.request_timestamp = self.clock
               self.reply_pending = set(range(self.num_processes)) - {self.process_id}
               self.log_event(f"Proceso {self.process_id}: Solicita recurso con timestamp {self.request_timestamp}")
           
           # Enviar solicitudes a todos los demás procesos
           for p_id in range(self.num_processes):
               if p_id != self.process_id:
                   threading.Thread(target=self.send_request, args=(p_id,)).start()
           
           # Esperar respuestas
           self.wait_for_replies()
       
       def send_request(self, target_id):
           # Simular latencia de red
           time.sleep(random.uniform(0.1, 0.3))
           
           # Enviar solicitud
           processes[target_id].receive_request(self.process_id, self.request_timestamp)
       
       def receive_request(self, sender_id, timestamp):
           with self.lock:
               # Actualizar reloj lógico
               self.clock = max(self.clock, timestamp) + 1
               
               if self.state == "HELD" or (self.state == "WANTED" and 
                                          (self.request_timestamp < timestamp or 
                                           (self.request_timestamp == timestamp and self.process_id < sender_id))):
                   # Diferir la respuesta
                   self.deferred_replies.add(sender_id)
                   self.log_event(f"Proceso {self.process_id}: Difiere respuesta a P{sender_id}")
               else:
                   # Enviar respuesta inmediatamente
                   threading.Thread(target=self.send_reply, args=(sender_id,)).start()
       
       def send_reply(self, target_id):
           # Simular latencia de red
           time.sleep(random.uniform(0.1, 0.3))
           
           # Enviar respuesta
           processes[target_id].receive_reply(self.process_id)
       
       def receive_reply(self, sender_id):
           with self.lock:
               if sender_id in self.reply_pending:
                   self.reply_pending.remove(sender_id)
                   self.log_event(f"Proceso {self.process_id}: Recibe respuesta de P{sender_id}, pendientes: {len(self.reply_pending)}")
       
       def wait_for_replies(self):
           while True:
               with self.lock:
                   if not self.reply_pending:
                       self.state = "HELD"
                       self.log_event(f"Proceso {self.process_id}: ACCEDE al recurso")
                       break
               time.sleep(0.1)
           
           # Simular uso del recurso
           time.sleep(random.uniform(0.5, 1.5))
           
           # Liberar el recurso
           self.release_resource()
       
       def release_resource(self):
           with self.lock:
               self.state = "RELEASED"
               self.resource_access_count += 1
               self.log_event(f"Proceso {self.process_id}: LIBERA el recurso (accesos totales: {self.resource_access_count})")
               
               # Enviar respuestas diferidas
               deferred = list(self.deferred_replies)
               self.deferred_replies.clear()
           
           # Enviar todas las respuestas diferidas
           for p_id in deferred:
               threading.Thread(target=self.send_reply, args=(p_id,)).start()
       
       def run(self, num_requests=3):
           for _ in range(num_requests):
               # Esperar un tiempo aleatorio antes de solicitar el recurso
               time.sleep(random.uniform(1, 3))
               
               # Solicitar acceso al recurso
               self.request_resource()
   
   # Variable global para almacenar los procesos
   processes = []
   
   def print_statistics(processes):
       print("\n" + "="*50)
       print("ESTADÍSTICAS DE ACCESO AL RECURSO")
       print("="*50)
       for process in processes:
           print(f"Proceso {process.process_id}: {process.resource_access_count} accesos")
   
   def main():
       global processes
       
       # Crear procesos
       num_processes = 5
       processes = [Process(i, num_processes) for i in range(num_processes)]
       
       # Crear hilos para cada proceso
       threads = []
       for process in processes:
           thread = threading.Thread(target=process.run)
           threads.append(thread)
       
       # Iniciar todos los hilos
       print("Iniciando simulación del algoritmo de exclusión mutua de Ricart-Agrawala...")
       for thread in threads:
           thread.start()
       
       # Esperar a que todos los hilos terminen
       for thread in threads:
           thread.join()
       
       # Imprimir estadísticas
       print_statistics(processes)
   
   if __name__ == "__main__":
       main()
   EOF
   ```

2. Actualiza el Dockerfile para ejecutar el algoritmo de exclusión mutua:
   ```bash
   cat > Dockerfile << 'EOF'
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY mutual_exclusion.py .
   
   CMD ["python", "mutual_exclusion.py"]
   EOF
   ```

3. Construye y ejecuta el contenedor:
   ```bash
   docker build -t mutual-exclusion .
   docker run mutual-exclusion
   ```

## Parte 4: Demostración de Consistencia y Replicación

### Paso 9: Crear un Directorio para Consistencia

1. Crea un directorio para los ejemplos de consistencia:
   ```bash
   cd ..
   mkdir -p consistencia
   cd consistencia
   ```

### Paso 10: Implementar un Sistema de Almacenamiento con Quórum

1. Crea un script Python para simular un sistema de almacenamiento con quórum:
   ```bash
   cat > quorum_system.py << 'EOF'
   import time
   import random
   import threading
   import os
   from collections import defaultdict
   
   class StorageNode:
       def __init__(self, node_id):
           self.node_id = node_id
           self.data = {}  # key -> (value, version)
           self.is_active = True
           self.lock = threading.Lock()
           self.log = []
       
       def log_event(self, event):
           timestamp = time.time()
           self.log.append((timestamp, event))
           print(f"[{time.strftime('%H:%M:%S')}] Nodo {self.node_id}: {event}")
       
       def read(self, key):
           if not self.is_active:
               return None, -1
           
           with self.lock:
               if key in self.data:
                   value, version = self.data[key]
                   self.log_event(f"Lee {key}={value} (versión {version})")
                   return value, version
               else:
                   self.log_event(f"Lee {key}=None (no existe)")
                   return None, 0
       
       def write(self, key, value, version):
           if not self.is_active:
               return False
           
           with self.lock:
               current_version = 0
               if key in self.data:
                   _, current_version = self.data[key]
               
               if version > current_version:
                   self.data[key] = (value, version)
                   self.log_event(f"Escribe {key}={value} (versión {version})")
                   return True
               else:
                   self.log_event(f"Rechaza escritura {key}={value} (versión {version}, actual {current_version})")
                   return False
       
       def fail(self):
           with self.lock:
               self.is_active = False
               self.log_event("FALLA")
       
       def recover(self):
           with self.lock:
               self.is_active = True
               self.log_event("RECUPERADO")
   
   class QuorumSystem:
       def __init__(self, num_nodes, read_quorum, write_quorum):
           self.nodes = [StorageNode(i) for i in range(num_nodes)]
           self.read_quorum = read_quorum
           self.write_quorum = write_quorum
           self.num_nodes = num_nodes
           self.log = []
           
           # Verificar que los quórums cumplen la condición R + W > N
           if read_quorum + write_quorum <= num_nodes:
               print(f"ADVERTENCIA: La condición R + W > N no se cumple ({read_quorum} + {write_quorum} <= {num_nodes})")
               print("Esto puede llevar a inconsistencias en los datos.")
       
       def log_event(self, event):
           timestamp = time.time()
           self.log.append((timestamp, event))
           print(f"[{time.strftime('%H:%M:%S')}] Sistema: {event}")
       
       def read_value(self, key):
           active_nodes = [node for node in self.nodes if node.is_active]
           
           if len(active_nodes) < self.read_quorum:
               self.log_event(f"Lectura de {key} FALLIDA: No hay suficientes nodos activos ({len(active_nodes)} < {self.read_quorum})")
               return None
           
           # Seleccionar nodos aleatorios para el quórum de lectura
           read_nodes = random.sample(active_nodes, self.read_quorum)
           
           # Leer de todos los nodos en el quórum
           results = []
           for node in read_nodes:
               value, version = node.read(key)
               results.append((value, version, node))
           
           # Encontrar el valor con la versión más alta
           if not results:
               return None
           
           max_version = max(version for _, version, _ in results)
           if max_version <= 0:
               self.log_event(f"Lectura de {key}: No existe en ningún nodo del quórum")
               return None
           
           # Obtener el valor con la versión más alta
           latest_value = next(value for value, version, _ in results if version == max_version)
           
           # Reparar nodos con versiones antiguas
           for value, version, node in results:
               if version < max_version:
                   threading.Thread(target=self._repair_node, args=(node, key, latest_value, max_version)).start()
           
           self.log_event(f"Lectura de {key}={latest_value} (versión {max_version}) exitosa")
           return latest_value
       
       def _repair_node(self, node, key, value, version):
           """Reparar un nodo con una versión antigua del valor."""
           node.write(key, value, version)
       
       def write_value(self, key, value):
           active_nodes = [node for node in self.nodes if node.is_active]
           
           if len(active_nodes) < self.write_quorum:
               self.log_event(f"Escritura de {key}={value} FALLIDA: No hay suficientes nodos activos ({len(active_nodes)} < {self.write_quorum})")
               return False
           
           # Determinar la versión actual más alta
           max_version = 0
           for node in active_nodes:
               _, version = node.read(key)
               max_version = max(max_version, version)
           
           # Nueva versión
           new_version = max_version + 1
           
           # Seleccionar nodos aleatorios para el quórum de escritura
           write_nodes = random.sample(active_nodes, self.write_quorum)
           
           # Escribir en todos los nodos del quórum
           success_count = 0
           for node in write_nodes:
               if node.write(key, value, new_version):
                   success_count += 1
           
           # La escritura es exitosa si se escribe en todos los nodos del quórum
           success = success_count == self.write_quorum
           
           if success:
               self.log_event(f"Escritura de {key}={value} (versión {new_version}) exitosa en {success_count} nodos")
           else:
               self.log_event(f"Escritura de {key}={value} PARCIAL: Solo {success_count}/{self.write_quorum} nodos")
           
           return success
       
       def simulate_node_failures(self, num_failures=2, duration=3):
           """Simula fallos aleatorios en los nodos."""
           # Seleccionar nodos aleatorios para fallar
           nodes_to_fail = random.sample(self.nodes, min(num_failures, len(self.nodes)))
           
           for node in nodes_to_fail:
               node.fail()
           
           self.log_event(f"{len(nodes_to_fail)} nodos han fallado")
           
           # Programar la recuperación después de la duración especificada
           threading.Timer(duration, self._recover_nodes, args=(nodes_to_fail,)).start()
       
       def _recover_nodes(self, nodes):
           """Recupera los nodos que han fallado."""
           for node in nodes:
               node.recover()
           
           self.log_event(f"{len(nodes)} nodos se han recuperado")
   
   def simulate_client_operations(quorum_system):
       """Simula operaciones de cliente en el sistema de quórum."""
       # Realizar algunas escrituras iniciales
       quorum_system.write_value("contador", 0)
       quorum_system.write_value("nombre", "Sistema Distribuido")
       
       # Simular fallos de nodos después de un tiempo
       threading.Timer(2, quorum_system.simulate_node_failures).start()
       
       # Realizar operaciones de lectura y escritura
       for i in range(10):
           time.sleep(random.uniform(0.5, 1.5))
           
           # Decidir aleatoriamente entre lectura y escritura
           if random.random() < 0.7:  # 70% probabilidad de lectura
               key = random.choice(["contador", "nombre"])
               value = quorum_system.read_value(key)
           else:
               if random.random() < 0.5:
                   # Incrementar contador
                   current = quorum_system.read_value("contador")
                   if current is not None:
                       quorum_system.write_value("contador", current + 1)
               else:
                   # Actualizar nombre
                   suffix = random.randint(1, 100)
                   quorum_system.write_value("nombre", f"Sistema Distribuido {suffix}")
   
   def print_final_state(quorum_system):
       """Imprime el estado final de todos los nodos."""
       print("\n" + "="*50)
       print("ESTADO FINAL DEL SISTEMA")
       print("="*50)
       
       for node in quorum_system.nodes:
           print(f"Nodo {node.node_id} ({'Activo' if node.is_active else 'Inactivo'}):")
           for key, (value, version) in node.data.items():
               print(f"  {key} = {value} (versión {version})")
   
   def main():
       # Crear sistema de quórum con 5 nodos, quórum de lectura 3, quórum de escritura 3
       # Esto cumple R + W > N (3 + 3 > 5)
       quorum_system = QuorumSystem(5, 3, 3)
       
       print("Iniciando simulación de sistema de quórum...")
       
       # Simular operaciones de cliente
       simulate_client_operations(quorum_system)
       
       # Esperar a que terminen todas las operaciones
       time.sleep(10)
       
       # Imprimir estado final
       print_final_state(quorum_system)
   
   if __name__ == "__main__":
       main()
   EOF
   ```

2. Crea un Dockerfile para ejecutar el sistema de quórum:
   ```bash
   cat > Dockerfile << 'EOF'
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY quorum_system.py .
   
   CMD ["python", "quorum_system.py"]
   EOF
   ```

3. Construye y ejecuta el contenedor:
   ```bash
   docker build -t quorum-system .
   docker run quorum-system
   ```

    ### Paso 11: Implementar CRDTs (Conflict-free Replicated Data Types)

1. Crea un script Python para simular CRDTs:
   ```bash
   cat > crdt_counter.py << 'EOF'
   import time
   import random
   import threading
   import os
   from collections import defaultdict
   
   class GCounter:
       """
       Contador creciente (G-Counter) - Un CRDT que solo permite incrementos.
       Cada nodo mantiene un contador local para sí mismo y el valor global
       es la suma de todos los contadores locales.
       """
       def __init__(self, node_id, num_nodes):
           self.node_id = node_id
           self.counters = [0] * num_nodes
           self.log = []
       
       def log_event(self, event):
           timestamp = time.time()
           self.log.append((timestamp, event))
           print(f"[{time.strftime('%H:%M:%S')}] Nodo {self.node_id}: {event}")
       
       def increment(self):
           """Incrementa el contador local de este nodo."""
           self.counters[self.node_id] += 1
           self.log_event(f"Incrementa contador a {self.counters[self.node_id]}")
           return self.value()
       
       def value(self):
           """Obtiene el valor global del contador."""
           return sum(self.counters)
       
       def merge(self, other_counter):
           """Fusiona con otro contador tomando el máximo para cada posición."""
           for i in range(len(self.counters)):
               self.counters[i] = max(self.counters[i], other_counter.counters[i])
           self.log_event(f"Fusiona contadores, nuevo valor: {self.value()}")
   
   class PNCounter:
       """
       Contador positivo/negativo (PN-Counter) - Un CRDT que permite incrementos y decrementos.
       Consiste en dos G-Counters, uno para incrementos y otro para decrementos.
       """
       def __init__(self, node_id, num_nodes):
           self.node_id = node_id
           self.increments = GCounter(node_id, num_nodes)
           self.decrements = GCounter(node_id, num_nodes)
           self.log = []
       
       def log_event(self, event):
           timestamp = time.time()
           self.log.append((timestamp, event))
           print(f"[{time.strftime('%H:%M:%S')}] Nodo {self.node_id}: {event}")
       
       def increment(self):
           """Incrementa el contador."""
           self.increments.increment()
           self.log_event(f"Incrementa contador a {self.value()}")
           return self.value()
       
       def decrement(self):
           """Decrementa el contador."""
           self.decrements.increment()
           self.log_event(f"Decrementa contador a {self.value()}")
           return self.value()
       
       def value(self):
           """Obtiene el valor global del contador."""
           return self.increments.value() - self.decrements.value()
       
       def merge(self, other_counter):
           """Fusiona con otro contador."""
           self.increments.merge(other_counter.increments)
           self.decrements.merge(other_counter.decrements)
           self.log_event(f"Fusiona contadores, nuevo valor: {self.value()}")
   
   class GSet:
       """
       Conjunto creciente (G-Set) - Un CRDT que solo permite añadir elementos.
       """
       def __init__(self, node_id):
           self.node_id = node_id
           self.elements = set()
           self.log = []
       
       def log_event(self, event):
           timestamp = time.time()
           self.log.append((timestamp, event))
           print(f"[{time.strftime('%H:%M:%S')}] Nodo {self.node_id}: {event}")
       
       def add(self, element):
           """Añade un elemento al conjunto."""
           self.elements.add(element)
           self.log_event(f"Añade elemento '{element}', tamaño: {len(self.elements)}")
       
       def contains(self, element):
           """Comprueba si un elemento está en el conjunto."""
           return element in self.elements
       
       def value(self):
           """Obtiene todos los elementos del conjunto."""
           return self.elements.copy()
       
       def merge(self, other_set):
           """Fusiona con otro conjunto tomando la unión."""
           self.elements = self.elements.union(other_set.elements)
           self.log_event(f"Fusiona conjuntos, nuevo tamaño: {len(self.elements)}")
   
   class TwoPhaseSet:
       """
       Conjunto de dos fases (2P-Set) - Un CRDT que permite añadir y eliminar elementos.
       Consiste en dos G-Sets, uno para adiciones y otro para eliminaciones.
       """
       def __init__(self, node_id):
           self.node_id = node_id
           self.additions = GSet(node_id)
           self.removals = GSet(node_id)
           self.log = []
       
       def log_event(self, event):
           timestamp = time.time()
           self.log.append((timestamp, event))
           print(f"[{time.strftime('%H:%M:%S')}] Nodo {self.node_id}: {event}")
       
       def add(self, element):
           """Añade un elemento al conjunto."""
           self.additions.add(element)
           self.log_event(f"Añade elemento '{element}'")
       
       def remove(self, element):
           """Elimina un elemento del conjunto."""
           if self.contains(element):
               self.removals.add(element)
               self.log_event(f"Elimina elemento '{element}'")
       
       def contains(self, element):
           """Comprueba si un elemento está en el conjunto."""
           return self.additions.contains(element) and not self.removals.contains(element)
       
       def value(self):
           """Obtiene todos los elementos actuales del conjunto."""
           return {e for e in self.additions.value() if e not in self.removals.value()}
       
       def merge(self, other_set):
           """Fusiona con otro conjunto."""
           self.additions.merge(other_set.additions)
           self.removals.merge(other_set.removals)
           self.log_event(f"Fusiona conjuntos, nuevo tamaño: {len(self.value())}")
   
   def simulate_network_partition(nodes, partition_duration=3):
       """Simula una partición de red entre los nodos."""
       # Dividir los nodos en dos grupos
       middle = len(nodes) // 2
       group1 = nodes[:middle]
       group2 = nodes[middle:]
       
       print(f"\n[SISTEMA] Iniciando partición de red por {partition_duration} segundos")
       print(f"[SISTEMA] Grupo 1: Nodos {[node.node_id for node in group1]}")
       print(f"[SISTEMA] Grupo 2: Nodos {[node.node_id for node in group2]}")
       
       # Simular operaciones en ambos grupos durante la partición
       def operate_on_group(group, name):
           for _ in range(3):
               time.sleep(random.uniform(0.5, 1.0))
               node = random.choice(group)
               
               # Realizar operación aleatoria
               if isinstance(node, PNCounter):
                   if random.random() < 0.7:
                       node.increment()
                   else:
                       node.decrement()
               elif isinstance(node, TwoPhaseSet):
                   if random.random() < 0.7:
                       element = f"item-{random.randint(1, 10)}"
                       node.add(element)
                   else:
                       if node.value():
                           element = random.choice(list(node.value()))
                           node.remove(element)
       
       # Iniciar hilos para operar en cada grupo
       thread1 = threading.Thread(target=operate_on_group, args=(group1, "Grupo 1"))
       thread2 = threading.Thread(target=operate_on_group, args=(group2, "Grupo 2"))
       
       thread1.start()
       thread2.start()
       
       # Esperar a que terminen las operaciones
       thread1.join()
       thread2.join()
       
       # Esperar el tiempo de la partición
       time.sleep(partition_duration - 3)  # Restar el tiempo de operaciones
       
       print(f"\n[SISTEMA] Finalizando partición de red")
       
       # Sincronizar los nodos después de la partición
       print(f"\n[SISTEMA] Sincronizando nodos después de la partición")
       
       # Realizar fusiones entre todos los nodos
       for i in range(len(nodes)):
           for j in range(len(nodes)):
               if i != j:
                   nodes[i].merge(nodes[j])
   
   def print_final_state(nodes):
       """Imprime el estado final de todos los nodos."""
       print("\n" + "="*50)
       print("ESTADO FINAL DEL SISTEMA")
       print("="*50)
       
       for node in nodes:
           if isinstance(node, PNCounter):
               print(f"Nodo {node.node_id} (PN-Counter): {node.value()}")
               print(f"  Incrementos: {node.increments.counters}")
               print(f"  Decrementos: {node.decrements.counters}")
           elif isinstance(node, TwoPhaseSet):
               print(f"Nodo {node.node_id} (2P-Set): {node.value()}")
               print(f"  Adiciones: {node.additions.value()}")
               print(f"  Eliminaciones: {node.removals.value()}")
   
   def main():
       # Crear nodos con diferentes tipos de CRDTs
       num_nodes = 4
       
       # Crear contadores PN
       pn_counters = [PNCounter(i, num_nodes) for i in range(num_nodes)]
       
       # Realizar algunas operaciones iniciales
       print("Iniciando simulación de PN-Counters...")
       for _ in range(5):
           node = random.choice(pn_counters)
           if random.random() < 0.7:
               node.increment()
           else:
               node.decrement()
       
       # Simular partición de red
       simulate_network_partition(pn_counters)
       
       # Imprimir estado final
       print_final_state(pn_counters)
       
       print("\n" + "="*50)
       
       # Crear conjuntos 2P
       two_phase_sets = [TwoPhaseSet(i) for i in range(num_nodes)]
       
       # Realizar algunas operaciones iniciales
       print("\nIniciando simulación de 2P-Sets...")
       for _ in range(5):
           node = random.choice(two_phase_sets)
           element = f"item-{random.randint(1, 10)}"
           node.add(element)
       
       # Simular partición de red
       simulate_network_partition(two_phase_sets)
       
       # Imprimir estado final
       print_final_state(two_phase_sets)
   
   if __name__ == "__main__":
       main()
   EOF
   ```

2. Actualiza el Dockerfile para ejecutar la simulación de CRDTs:
   ```bash
   cat > Dockerfile << 'EOF'
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY crdt_counter.py .
   
   CMD ["python", "crdt_counter.py"]
   EOF
   ```

3. Construye y ejecuta el contenedor:
   ```bash
   docker build -t crdt-simulation .
   docker run crdt-simulation
   ```

## Parte 5: Demostración de Tolerancia a Fallos y Consenso

### Paso 12: Crear un Directorio para Tolerancia a Fallos

1. Crea un directorio para los ejemplos de tolerancia a fallos:
   ```bash
   cd ..
   mkdir -p tolerancia-fallos
   cd tolerancia-fallos
   ```

### Paso 13: Implementar un Algoritmo de Consenso Simplificado (Raft)

1. Crea un script Python para simular un algoritmo de consenso simplificado basado en Raft:
   ```bash
   cat > raft_simplified.py << 'EOF'
   import time
   import random
   import threading
   import os
   from enum import Enum
   
   class NodeState(Enum):
       FOLLOWER = 1
       CANDIDATE = 2
       LEADER = 3
   
   class LogEntry:
       def __init__(self, term, command):
           self.term = term
           self.command = command
   
   class RaftNode:
       def __init__(self, node_id, num_nodes):
           self.node_id = node_id
           self.num_nodes = num_nodes
           self.state = NodeState.FOLLOWER
           self.current_term = 0
           self.voted_for = None
           self.log = []  # Lista de LogEntry
           self.commit_index = -1
           self.last_applied = -1
           self.next_index = {}  # Para líderes: índice del siguiente log para cada seguidor
           self.match_index = {}  # Para líderes: índice más alto replicado para cada seguidor
           
           self.election_timeout = random.uniform(1.5, 3.0)
           self.last_heartbeat = time.time()
           self.votes_received = 0
           
           self.is_active = True
           self.event_log = []
           
           self.lock = threading.Lock()
       
       def log_event(self, event):
           timestamp = time.time()
           self.event_log.append((timestamp, event))
           print(f"[{time.strftime('%H:%M:%S')}] Nodo {self.node_id} ({self.state.name}): {event}")
       
       def start(self):
           """Inicia el nodo."""
           self.log_event("Iniciando nodo")
           
           # Iniciar hilo para verificar timeouts
           self.timeout_thread = threading.Thread(target=self._check_timeout)
           self.timeout_thread.daemon = True
           self.timeout_thread.start()
       
       def _check_timeout(self):
           """Verifica si ha expirado el timeout de elección."""
           while self.is_active:
               time.sleep(0.1)
               
               with self.lock:
                   if self.state != NodeState.LEADER:
                       if time.time() - self.last_heartbeat > self.election_timeout:
                           self._start_election()
       
       def _start_election(self):
           """Inicia una elección."""
           with self.lock:
               self.state = NodeState.CANDIDATE
               self.current_term += 1
               self.voted_for = self.node_id
               self.votes_received = 1  # Voto por sí mismo
               self.election_timeout = random.uniform(1.5, 3.0)  # Reiniciar timeout
               self.last_heartbeat = time.time()
               
               self.log_event(f"Inicia elección para término {self.current_term}")
           
           # Solicitar votos a todos los demás nodos
           for i in range(self.num_nodes):
               if i != self.node_id:
                   threading.Thread(target=self._request_vote, args=(i,)).start()
       
       def _request_vote(self, target_id):
           """Solicita un voto a otro nodo."""
           if not nodes[target_id].is_active:
               return
           
           with self.lock:
               term = self.current_term
               last_log_index = len(self.log) - 1
               last_log_term = self.log[last_log_index].term if last_log_index >= 0 else 0
           
           # Simular latencia de red
           time.sleep(random.uniform(0.1, 0.3))
           
           # Solicitar voto
           vote_granted = nodes[target_id].handle_vote_request(
               self.node_id, term, last_log_index, last_log_term)
           
           if vote_granted:
               with self.lock:
                   if self.state == NodeState.CANDIDATE and self.current_term == term:
                       self.votes_received += 1
                       self.log_event(f"Recibió voto de Nodo {target_id}, total: {self.votes_received}")
                       
                       # Verificar si ha ganado la elección
                       if self.votes_received > self.num_nodes // 2:
                           self._become_leader()
       
       def handle_vote_request(self, candidate_id, term, last_log_index, last_log_term):
           """Maneja una solicitud de voto."""
           with self.lock:
               if not self.is_active:
                   return False
               
               # Actualizar término si es necesario
               if term > self.current_term:
                   self.current_term = term
                   self.state = NodeState.FOLLOWER
                   self.voted_for = None
               
               # Verificar si puede votar por el candidato
               if (term == self.current_term and
                   (self.voted_for is None or self.voted_for == candidate_id)):
                   
                   # Verificar que el log del candidato está al menos tan actualizado como el nuestro
                   my_last_log_index = len(self.log) - 1
                   my_last_log_term = self.log[my_last_log_index].term if my_last_log_index >= 0 else 0
                   
                   if (last_log_term > my_last_log_term or
                       (last_log_term == my_last_log_term and last_log_index >= my_last_log_index)):
                       
                       self.voted_for = candidate_id
                       self.last_heartbeat = time.time()  # Reiniciar timeout
                       self.log_event(f"Vota por Nodo {candidate_id} en término {term}")
                       return True
           
           return False
       
       def _become_leader(self):
           """Convierte este nodo en líder."""
           with self.lock:
               if self.state != NodeState.CANDIDATE:
                   return
               
               self.state = NodeState.LEADER
               self.log_event(f"Se convierte en LÍDER para término {self.current_term}")
               
               # Inicializar índices para cada seguidor
               for i in range(self.num_nodes):
                   if i != self.node_id:
                       self.next_index[i] = len(self.log)
                       self.match_index[i] = -1
           
           # Iniciar envío de heartbeats
           self._send_heartbeats()
       
       def _send_heartbeats(self):
           """Envía heartbeats a todos los seguidores."""
           while self.is_active and self.state == NodeState.LEADER:
               # Enviar AppendEntries a todos los seguidores
               for i in range(self.num_nodes):
                   if i != self.node_id:
                       threading.Thread(target=self._append_entries, args=(i,)).start()
               
               # Esperar antes del siguiente heartbeat
               time.sleep(0.5)
       
       def _append_entries(self, target_id):
           """Envía una solicitud AppendEntries a un seguidor."""
           if not nodes[target_id].is_active:
               return
           
           with self.lock:
               if self.state != NodeState.LEADER:
                   return
               
               prev_log_index = self.next_index[target_id] - 1
               prev_log_term = self.log[prev_log_index].term if prev_log_index >= 0 else 0
               
               # Determinar entradas a enviar
               entries = self.log[self.next_index[target_id]:] if self.next_index[target_id] < len(self.log) else []
               
               # Enviar AppendEntries
               term = self.current_term
               leader_commit = self.commit_index
           
           # Simular latencia de red
           time.sleep(random.uniform(0.1, 0.3))
           
           # Enviar solicitud
           success = nodes[target_id].handle_append_entries(
               self.node_id, term, prev_log_index, prev_log_term, entries, leader_commit)
           
           if success:
               with self.lock:
                   if self.state == NodeState.LEADER and self.current_term == term:
                       # Actualizar índices para este seguidor
                       if entries:
                           self.next_index[target_id] = prev_log_index + 1 + len(entries)
                           self.match_index[target_id] = self.next_index[target_id] - 1
                           self.log_event(f"Replicó {len(entries)} entradas en Nodo {target_id}")
                       
                       # Actualizar commit_index si es posible
                       self._update_commit_index()
           else:
               with self.lock:
                   if self.state == NodeState.LEADER and self.current_term == term:
                       # Decrementar next_index y reintentar
                       self.next_index[target_id] = max(0, self.next_index[target_id] - 1)
       
       def handle_append_entries(self, leader_id, term, prev_log_index, prev_log_term, entries, leader_commit):
           """Maneja una solicitud AppendEntries."""
           with self.lock:
               if not self.is_active:
                   return False
               
               # Rechazar si el término es antiguo
               if term < self.current_term:
                   return False
               
               # Actualizar término si es necesario
               if term > self.current_term:
                   self.current_term = term
                   self.voted_for = None
               
               # Reconocer al líder
               self.state = NodeState.FOLLOWER
               self.last_heartbeat = time.time()
               
               # Verificar consistencia del log
               if prev_log_index >= 0:
                   if prev_log_index >= len(self.log) or self.log[prev_log_index].term != prev_log_term:
                       return False
               
               # Procesar entradas
               if entries:
                   # Eliminar entradas conflictivas y añadir nuevas
                   self.log = self.log[:prev_log_index + 1]
                   self.log.extend(entries)
                   self.log_event(f"Añade {len(entries)} entradas al log")
               else:
                   # Es un heartbeat
                   pass
               
               # Actualizar commit_index
               if leader_commit > self.commit_index:
                   self.commit_index = min(leader_commit, len(self.log) - 1)
                   self._apply_log_entries()
               
               return True
       
       def _update_commit_index(self):
           """Actualiza el índice de commit basado en la replicación."""
           with self.lock:
               for n in range(self.commit_index + 1, len(self.log)):
                   if self.log[n].term == self.current_term:
                       # Contar cuántos nodos tienen esta entrada
                       count = 1  # Este nodo
                       for i in range(self.num_nodes):
                           if i != self.node_id and self.match_index.get(i, -1) >= n:
                               count += 1
                       
                       if count > self.num_nodes // 2:
                           self.commit_index = n
                           self._apply_log_entries()
       
       def _apply_log_entries(self):
           """Aplica las entradas de log comprometidas."""
           with self.lock:
               while self.last_applied < self.commit_index:
                   self.last_applied += 1
                   entry = self.log[self.last_applied]
                   self.log_event(f"Aplica comando: {entry.command}")
       
       def append_command(self, command):
           """Añade un comando al log (solo para líderes)."""
           with self.lock:
               if self.state != NodeState.LEADER:
                   self.log_event(f"Rechaza comando: No es líder")
                   return False
               
               # Añadir entrada al log
               entry = LogEntry(self.current_term, command)
               self.log.append(entry)
               self.log_event(f"Añade comando al log: {command}")
               
               # Actualizar índices
               self.match_index[self.node_id] = len(self.log) - 1
               
               return True
       
       def fail(self):
           """Simula un fallo en este nodo."""
           with self.lock:
               self.is_active = False
               was_leader = self.state == NodeState.LEADER
               self.log_event("FALLA" + (" (era LÍDER)" if was_leader else ""))
           return was_leader
       
       def recover(self):
           """Recupera este nodo después de un fallo."""
           with self.lock:
               self.is_active = True
               self.state = NodeState.FOLLOWER
               self.last_heartbeat = time.time()
               self.log_event("RECUPERADO")
   
   def simulate_client_requests(nodes, num_requests=10):
       """Simula solicitudes de clientes al cluster."""
       for i in range(num_requests):
           time.sleep(random.uniform(0.5, 2.0))
           
           # Encontrar el líder actual
           leader = None
           for node in nodes:
               if node.is_active and node.state == NodeState.LEADER:
                   leader = node
                   break
           
           if leader:
               command = f"cmd-{i+1}"
               print(f"\n[CLIENTE] Envía comando '{command}' al líder (Nodo {leader.node_id})")
               leader.append_command(command)
           else:
               print(f"\n[CLIENTE] No hay líder disponible, comando descartado")
   
   def simulate_node_failures(nodes):
       """Simula fallos aleatorios en los nodos."""
       time.sleep(3)  # Esperar a que se establezca un líder inicial
       
       for _ in range(2):
           time.sleep(random.uniform(2, 4))
           
           # Seleccionar un nodo aleatorio para fallar
           active_nodes = [i for i, node in enumerate(nodes) if node.is_active]
           if active_nodes:
               fail_id = random.choice(active_nodes)
               was_leader = nodes[fail_id].fail()
               
               # Si el líder falló, verificar que se elige uno nuevo
               if was_leader:
                   print(f"\n[SISTEMA] El líder (Nodo {fail_id}) ha fallado")
           
           # Recuperar un nodo inactivo aleatorio
           time.sleep(random.uniform(2, 4))
           inactive_nodes = [i for i, node in enumerate(nodes) if not node.is_active]
           if inactive_nodes:
               recover_id = random.choice(inactive_nodes)
               nodes[recover_id].recover()
   
   def print_final_state(nodes):
       """Imprime el estado final de todos los nodos."""
       print("\n" + "="*50)
       print("ESTADO FINAL DEL SISTEMA")
       print("="*50)
       
       for node in nodes:
           state_str = "LÍDER" if node.state == NodeState.LEADER else "SEGUIDOR" if node.state == NodeState.FOLLOWER else "CANDIDATO"
           status = "Activo" if node.is_active else "Inactivo"
           print(f"Nodo {node.node_id}: {status}, {state_str}, Término {node.current_term}")
           print(f"  Log: {len(node.log)} entradas, Commit: {node.commit_index}, Aplicado: {node.last_applied}")
           
           # Mostrar comandos aplicados
           if node.last_applied >= 0:
               applied_commands = [node.log[i].command for i in range(node.last_applied + 1)]
               print(f"  Comandos aplicados: {applied_commands}")
   
   # Variable global para almacenar los nodos
   nodes = []
   
   def main():
       global nodes
       
       # Crear nodos
       num_nodes = 5
       nodes = [RaftNode(i, num_nodes) for i in range(num_nodes)]
       
       # Iniciar todos los nodos
       print("Iniciando simulación del algoritmo Raft simplificado...")
       for node in nodes:
           node.start()
       
       # Esperar a que se elija un líder
       time.sleep(3)
       
       # Iniciar hilos para simular solicitudes de clientes y fallos de nodos
       client_thread = threading.Thread(target=simulate_client_requests, args=(nodes,))
       failure_thread = threading.Thread(target=simulate_node_failures, args=(nodes,))
       
       client_thread.start()
       failure_thread.start()
       
       # Esperar a que terminen los hilos
       client_thread.join()
       failure_thread.join()
       
       # Continuar la simulación un poco más
       time.sleep(5)
       
       # Imprimir estado final
       print_final_state(nodes)
   
   if __name__ == "__main__":
       main()
   EOF
   ```

2. Crea un Dockerfile para ejecutar la simulación de Raft:
   ```bash
   cat > Dockerfile << 'EOF'
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY raft_simplified.py .
   
   CMD ["python", "raft_simplified.py"]
   EOF
   ```

3. Construye y ejecuta el contenedor:
   ```bash
   docker build -t raft-simulation .
   docker run raft-simulation
   ```

## Parte 6: Demostración de Datos y Particionamiento

### Paso 14: Crear un Directorio para Particionamiento

1. Crea un directorio para los ejemplos de particionamiento:
   ```bash
   cd ..
   mkdir -p particionamiento
   cd particionamiento
   ```

### Paso 15: Implementar Hashing Consistente

1. Crea un script Python para simular hashing consistente:
   ```bash
   cat > consistent_hashing.py << 'EOF'
   import hashlib
   import bisect
   import random
   import time
   import threading
   import os
   
   class ConsistentHash:
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
           
           print(f"Nodo {node} añadido al anillo")
       
       def remove_node(self, node):
           """Elimina un nodo del anillo."""
           for i in range(self.replicas):
               key = self._hash(f"{node}:{i}")
               if key in self.ring:
                   del self.ring[key]
                   self.sorted_keys.remove(key)
           
           print(f"Nodo {node} eliminado del anillo")
       
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
       
       def get_distribution(self):
           """Retorna la distribución de claves virtuales por nodo."""
           distribution = {}
           for node in set(self.ring.values()):
               distribution[node] = sum(1 for n in self.ring.values() if n == node)
           return distribution
   
   def simulate_key_distribution(ch, num_keys=1000):
       """Simula la distribución de claves entre nodos."""
       distribution = {}
       for node in set(ch.ring.values()):
           distribution[node] = 0
       
       for i in range(num_keys):
           key = f"key-{i}"
           node = ch.get_node(key)
           distribution[node] += 1
       
       print("\nDistribución de claves:")
       for node, count in distribution.items():
           print(f"  Nodo {node}: {count} claves ({count/num_keys*100:.1f}%)")
   
   def simulate_node_changes(ch, num_keys=1000):
       """Simula la redistribución de claves cuando se añaden o eliminan nodos."""
       # Mapeo inicial de claves a nodos
       initial_mapping = {}
       for i in range(num_keys):
           key = f"key-{i}"
           node = ch.get_node(key)
           initial_mapping[key] = node
       
       # Añadir un nuevo nodo
       new_node = "node-new"
       print(f"\nAñadiendo nuevo nodo: {new_node}")
       ch.add_node(new_node)
       
       # Verificar cuántas claves se mueven
       moved_keys = 0
       for key, old_node in initial_mapping.items():
           new_node = ch.get_node(key)
           if old_node != new_node:
               moved_keys += 1
       
       print(f"Claves redistribuidas: {moved_keys} ({moved_keys/num_keys*100:.1f}%)")
       
       # Eliminar un nodo existente
       remove_node = random.choice(list(set(ch.ring.values())))
       print(f"\nEliminando nodo: {remove_node}")
       
       # Mapeo antes de eliminar
       before_removal = {}
       for i in range(num_keys):
           key = f"key-{i}"
           node = ch.get_node(key)
           before_removal[key] = node
       
       ch.remove_node(remove_node)
       
       # Verificar cuántas claves se mueven
       moved_keys = 0
       for key, old_node in before_removal.items():
           if old_node == remove_node:  # Esta clave necesita moverse
               moved_keys += 1
       
       print(f"Claves redistribuidas: {moved_keys} ({moved_keys/num_keys*100:.1f}%)")
   
   def simulate_replication(ch, num_keys=10, replicas=3):
       """Simula la replicación de claves en múltiples nodos."""
       print("\nSimulación de replicación:")
       for i in range(num_keys):
           key = f"key-{i}"
           nodes = ch.get_nodes(key, replicas)
           print(f"  Clave {key} replicada en: {nodes}")
   
   def main():
       # Crear un hash consistente con algunos nodos iniciales
       nodes = ["node-1", "node-2", "node-3", "node-4"]
       ch = ConsistentHash(nodes)
       
       # Mostrar distribución inicial de nodos virtuales
       print("\nDistribución inicial de nodos virtuales:")
       for node, count in ch.get_distribution().items():
           print(f"  {node}: {count} nodos virtuales")
       
       # Simular distribución de claves
       simulate_key_distribution(ch)
       
       # Simular cambios en los nodos
       simulate_node_changes(ch)
       
       # Simular replicación
       simulate_replication(ch)
   
   if __name__ == "__main__":
       main()
   EOF
   ```

2. Crea un Dockerfile para ejecutar la simulación de hashing consistente:
   ```bash
   cat > Dockerfile << 'EOF'
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY consistent_hashing.py .
   
   CMD ["python", "consistent_hashing.py"]
   EOF
   ```

3. Construye y ejecuta el contenedor:
   ```bash
   docker build -t consistent-hashing .
   docker run consistent-hashing
   ```

### Paso 16: Implementar Sharding

1. Crea un script Python para simular sharding:
   ```bash
   cat > sharding.py << 'EOF'
   import time
   import random
   import threading
   import os
   import hashlib
   
   class ShardManager:
       def __init__(self, num_shards=10):
           """
           Inicializa el gestor de shards.
           
           Args:
               num_shards: Número de shards
           """
           self.num_shards = num_shards
           self.shard_to_node = {}  # shard_id -> node_id
           self.node_to_shards = {}  # node_id -> [shard_id]
           
           # Inicializar asignación de shards
           for shard_id in range(num_shards):
               self.shard_to_node[shard_id] = None
       
       def add_node(self, node_id):
           """Añade un nodo al sistema."""
           if node_id not in self.node_to_shards:
               self.node_to_shards[node_id] = []
               print(f"Nodo {node_id} añadido al sistema")
       
       def remove_node(self, node_id):
           """Elimina un nodo del sistema."""
           if node_id in self.node_to_shards:
               # Liberar todos los shards asignados a este nodo
               shards = self.node_to_shards[node_id].copy()
               for shard_id in shards:
                   self.shard_to_node[shard_id] = None
               
               del self.node_to_shards[node_id]
               print(f"Nodo {node_id} eliminado del sistema, liberados {len(shards)} shards")
               return shards
           return []
       
       def assign_shard(self, shard_id, node_id):
           """Asigna un shard a un nodo."""
           if node_id not in self.node_to_shards:
               self.add_node(node_id)
           
           # Si el shard ya estaba asignado a otro nodo, liberarlo
           current_node = self.shard_to_node.get(shard_id)
           if current_node is not None and current_node != node_id:
               self.node_to_shards[current_node].remove(shard_id)
           
           # Asignar el shard al nuevo nodo
           self.shard_to_node[shard_id] = node_id
           if shard_id not in self.node_to_shards[node_id]:
               self.node_to_shards[node_id].append(shard_id)
           
           print(f"Shard {shard_id} asignado al nodo {node_id}")
       
       def get_shard_for_key(self, key):
           """Determina el shard para una clave."""
           # Usar un hash simple para distribuir las claves
           hash_val = int(hashlib.md5(str(key).encode()).hexdigest(), 16) % self.num_shards
           return hash_val
       
       def get_node_for_key(self, key):
           """Obtiene el nodo responsable de una clave."""
           shard_id = self.get_shard_for_key(key)
           return self.shard_to_node.get(shard_id)
       
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
                   self.node_to_shards[under_node].append(shard_to_move)
                   self.shard_to_node[shard_to_move] = under_node
                   
                   # Registrar el movimiento
                   moves.append((shard_to_move, over_node, under_node))
                   print(f"Shard {shard_to_move} movido de nodo {over_node} a nodo {under_node}")
                   
                   # Actualizar estado de carga
                   if len(self.node_to_shards[under_node]) >= ideal_shards_per_node:
                       underloaded.pop(0)
           
           return moves
       
       def print_status(self):
           """Imprime el estado actual del sistema."""
           print("\nEstado del sistema de sharding:")
           print(f"  Número total de shards: {self.num_shards}")
           print(f"  Número de nodos: {len(self.node_to_shards)}")
           
           print("\nAsignación de shards:")
           for shard_id in range(self.num_shards):
               node = self.shard_to_node.get(shard_id)
               status = f"Asignado a nodo {node}" if node is not None else "No asignado"
               print(f"  Shard {shard_id}: {status}")
           
           print("\nCarga de nodos:")
           for node, shards in self.node_to_shards.items():
               print(f"  Nodo {node}: {len(shards)} shards {shards}")
   
   class DataStore:
       def __init__(self, shard_manager):
           self.shard_manager = shard_manager
           self.data = {}  # node_id -> {shard_id -> {key -> value}}
           self.lock = threading.Lock()
       
       def add_node(self, node_id):
           """Añade un nodo al almacén de datos."""
           with self.lock:
               if node_id not in self.data:
                   self.data[node_id] = {}
                   self.shard_manager.add_node(node_id)
       
       def remove_node(self, node_id):
           """Elimina un nodo del almacén de datos."""
           with self.lock:
               if node_id in self.data:
                   # Guardar datos antes de eliminar el nodo
                   node_data = self.data[node_id]
                   del self.data[node_id]
                   
                   # Eliminar nodo del gestor de shards
                   self.shard_manager.remove_node(node_id)
                   
                   return node_data
               return {}
       
       def put(self, key, value):
           """Almacena un valor para una clave."""
           shard_id = self.shard_manager.get_shard_for_key(key)
           node_id = self.shard_manager.get_node_for_key(key)
           
           if node_id is None:
               print(f"Error: No hay nodo asignado para el shard {shard_id}")
               return False
           
           with self.lock:
               if node_id not in self.data:
                   self.data[node_id] = {}
               
               if shard_id not in self.data[node_id]:
                   self.data[node_id][shard_id] = {}
               
               self.data[node_id][shard_id][key] = value
               print(f"Almacenado {key}={value} en shard {shard_id} (nodo {node_id})")
               return True
       
       def get(self, key):
           """Obtiene el valor para una clave."""
           shard_id = self.shard_manager.get_shard_for_key(key)
           node_id = self.shard_manager.get_node_for_key(key)
           
           if node_id is None:
               print(f"Error: No hay nodo asignado para el shard {shard_id}")
               return None
           
           with self.lock:
               if node_id not in self.data:
                   return None
               
               if shard_id not in self.data[node_id]:
                   return None
               
               value = self.data[node_id][shard_id].get(key)
               print(f"Recuperado {key}={value} de shard {shard_id} (nodo {node_id})")
               return value
       
       def rebalance(self):
           """Rebalancea los datos según la asignación de shards."""
           moves = self.shard_manager.balance_shards()
           
           with self.lock:
               for shard_id, from_node, to_node in moves:
                   # Mover datos del shard
                   if from_node in self.data and shard_id in self.data[from_node]:
                       # Asegurarse de que el nodo destino está inicializado
                       if to_node not in self.data:
                           self.data[to_node] = {}
                       
                       # Mover los datos
                       self.data[to_node][shard_id] = self.data[from_node][shard_id]
                       del self.data[from_node][shard_id]
                       
                       print(f"Datos del shard {shard_id} movidos de nodo {from_node} a nodo {to_node}")
   
   def simulate_operations(data_store, num_operations=100):
       """Simula operaciones de lectura y escritura."""
       keys = [f"key-{i}" for i in range(20)]
       
       for i in range(num_operations):
           # Decidir aleatoriamente entre lectura y escritura
           if random.random() < 0.7:  # 70% probabilidad de lectura
               key = random.choice(keys)
               data_store.get(key)
           else:
               key = random.choice(keys)
               value = f"value-{random.randint(1, 1000)}"
               data_store.put(key, value)
           
           time.sleep(0.05)
   
   def simulate_node_changes(data_store, shard_manager):
       """Simula adiciones y eliminaciones de nodos."""
       # Esperar un poco antes de empezar
       time.sleep(2)
       
       # Añadir un nuevo nodo
       new_node = f"node-{len(data_store.data) + 1}"
       print(f"\nAñadiendo nuevo nodo: {new_node}")
       data_store.add_node(new_node)
       
       # Asignar algunos shards al nuevo nodo
       for _ in range(2):
           # Encontrar un shard no asignado
           unassigned_shards = [s for s in range(shard_manager.num_shards) if shard_manager.shard_to_node.get(s) is None]
           if unassigned_shards:
               shard_id = random.choice(unassigned_shards)
               shard_manager.assign_shard(shard_id, new_node)
       
       # Rebalancear
       print("\nRebalanceando shards...")
       data_store.rebalance()
       
       # Esperar un poco
       time.sleep(2)
       
       # Eliminar un nodo existente
       if len(data_store.data) > 1:
           remove_node = random.choice(list(data_store.data.keys()))
           print(f"\nEliminando nodo: {remove_node}")
           data_store.remove_node(remove_node)
           
           # Reasignar los shards liberados
           available_nodes = list(data_store.data.keys())
           for shard_id in range(shard_manager.num_shards):
               if shard_manager.shard_to_node.get(shard_id) is None and available_nodes:
                   node_id = random.choice(available_nodes)
                   shard_manager.assign_shard(shard_id, node_id)
           
           # Rebalancear de nuevo
           print("\nRebalanceando shards después de eliminar nodo...")
           data_store.rebalance()
   
   def main():
       # Crear gestor de shards y almacén de datos
       num_shards = 10
       shard_manager = ShardManager(num_shards)
       data_store = DataStore(shard_manager)
       
       # Añadir nodos iniciales
       for i in range(3):
           node_id = f"node-{i}"
           data_store.add_node(node_id)
       
       # Asignar shards a nodos
       for shard_id in range(num_shards):
           node_id = f"node-{random.randint(0, 2)}"
           shard_manager.assign_shard(shard_id, node_id)
       
       # Imprimir estado inicial
       shard_manager.print_status()
       
       # Iniciar hilos para simular operaciones y cambios de nodos
       ops_thread = threading.Thread(target=simulate_operations, args=(data_store,))
       node_thread = threading.Thread(target=simulate_node_changes, args=(data_store, shard_manager))
       
       ops_thread.start()
       node_thread.start()
       
       # Esperar a que terminen los hilos
       ops_thread.join()
       node_thread.join()
       
       # Imprimir estado final
       print("\n" + "="*50)
       print("ESTADO FINAL DEL SISTEMA")
       print("="*50)
       shard_manager.print_status()
   
   if __name__ == "__main__":
       main()
   EOF
   ```

2. Actualiza el Dockerfile para ejecutar la simulación de sharding:
   ```bash
   cat > Dockerfile << 'EOF'
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY sharding.py .
   
   CMD ["python", "sharding.py"]
   EOF
   ```

3. Construye y ejecuta el contenedor:
   ```bash
   docker build -t sharding-simulation .
   docker run sharding-simulation
   ```

## Parte 7: Integración de Conceptos

### Paso 17: Crear un Script que Integre Múltiples Conceptos

1. Crea un script Python que integre varios conceptos de sistemas distribuidos:
   ```bash
   cat > integrated_system.py << 'EOF'
   import time
   import random
   import threading
   import hashlib
   import os
   from enum import Enum
   from collections import defaultdict
   
   class NodeState(Enum):
       FOLLOWER = 1
       CANDIDATE = 2
       LEADER = 3
   
   class VectorClock:
       def __init__(self, node_id, num_nodes):
           self.node_id = node_id
           self.clock = [0] * num_nodes
       
       def increment(self):
           self.clock[self.node_id] += 1
           return self.clock.copy()
       
       def update(self, other_clock):
           for i in range(len(self.clock)):
               self.clock[i] = max(self.clock[i], other_clock[i])
           self.clock[self.node_id] += 1
           return self.clock.copy()
       
       def __str__(self):
           return str(self.clock)
   
   class ConsistentHash:
       def __init__(self, replicas=100):
           self.replicas = replicas
           self.ring = {}
           self.sorted_keys = []
       
       def add_node(self, node_id):
           for i in range(self.replicas):
               key = self._hash(f"{node_id}:{i}")
               self.ring[key] = node_id
               bisect.insort(self.sorted_keys, key)
       
       def remove_node(self, node_id):
           for i in range(self.replicas):
               key = self._hash(f"{node_id}:{i}")
               if key in self.ring:
                   del self.ring[key]
                   self.sorted_keys.remove(key)
       
       def get_node(self, key):
           if not self.ring:
               return None
           
           hash_key = self._hash(key)
           idx = bisect.bisort_left(self.sorted_keys, hash_key) % len(self.sorted_keys)
           return self.ring[self.sorted_keys[idx]]
       
       def _hash(self, key):
           return int(hashlib.md5(str(key).encode()).hexdigest(), 16)
   
   class DistributedNode:
       def __init__(self, node_id, num_nodes):
           self.node_id = node_id
           self.num_nodes = num_nodes
           self.vector_clock = VectorClock(node_id, num_nodes)
           self.state = NodeState.FOLLOWER
           self.current_term = 0
           self.voted_for = None
           self.is_active = True
           self.data = {}
           self.log = []
           self.lock = threading.Lock()
       
       def log_event(self, event):
           timestamp = time.time()
           self.log.append((timestamp, event))
           print(f"[{time.strftime('%H:%M:%S')}] Nodo {self.node_id} ({self.state.name}): {event}")
       
       def put(self, key, value):
           with self.lock:
               if not self.is_active:
                   return False
               
               # Solo el líder puede escribir
               if self.state != NodeState.LEADER:
                   self.log_event(f"Rechaza escritura {key}={value} (no es líder)")
                   return False
               
               # Actualizar reloj vectorial
               clock = self.vector_clock.increment()
               
               # Almacenar valor con timestamp vectorial
               self.data[key] = (value, clock)
               self.log_event(f"Almacena {key}={value} con vector {clock}")
               return True
       
       def get(self, key):
           with self.lock:
               if not self.is_active:
                   return None
               
               if key in self.data:
                   value, clock = self.data[key]
                   self.log_event(f"Lee {key}={value}")
                   return value
               else:
                   self.log_event(f"Lee {key}=None (no existe)")
                   return None
       
       def start_election(self):
           with self.lock:
               if not self.is_active:
                   return
               
               self.state = NodeState.CANDIDATE
               self.current_term += 1
               self.voted_for = self.node_id
               self.log_event(f"Inicia elección para término {self.current_term}")
       
       def become_leader(self):
           with self.lock:
               if self.state != NodeState.CANDIDATE or not self.is_active:
                   return
               
               self.state = NodeState.LEADER
               self.log_event(f"Se convierte en LÍDER para término {self.current_term}")
       
       def fail(self):
           with self.lock:
               self.is_active = False
               was_leader = self.state == NodeState.LEADER
               self.log_event("FALLA" + (" (era LÍDER)" if was_leader else ""))
           return was_leader
       
       def recover(self):
           with self.lock:
               self.is_active = True
               self.state = NodeState.FOLLOWER
               self.log_event("RECUPERADO")
   
   def simulate_distributed_system():
       # Crear nodos
       num_nodes = 5
       nodes = [DistributedNode(i, num_nodes) for i in range(num_nodes)]
       
       # Elegir un líder inicial
       leader_id = random.randint(0, num_nodes - 1)
       nodes[leader_id].start_election()
       nodes[leader_id].become_leader()
       
       # Simular operaciones
       for _ in range(10):
           # Seleccionar un nodo aleatorio
           node_id = random.randint(0, num_nodes - 1)
           node = nodes[node_id]
           
           # Decidir aleatoriamente entre lectura y escritura
           if random.random() < 0.7:  # 70% probabilidad de lectura
               key = f"key-{random.randint(1, 5)}"
               node.get(key)
           else:
               key = f"key-{random.randint(1, 5)}"
               value = f"value-{random.randint(1, 100)}"
               node.put(key, value)
           
           time.sleep(0.5)
       
       # Simular fallo del líder
       nodes[leader_id].fail()
       
       # Elegir un nuevo líder
       active_nodes = [i for i, node in enumerate(nodes) if node.is_active]
       if active_nodes:
           new_leader_id = random.choice(active_nodes)
           nodes[new_leader_id].start_election()
           nodes[new_leader_id].become_leader()
       
       # Continuar con más operaciones
       for _ in range(5):
           node_id = random.randint(0, num_nodes - 1)
           node = nodes[node_id]
           
           if random.random() < 0.7:
               key = f"key-{random.randint(1, 5)}"
               node.get(key)
           else:
               key = f"key-{random.randint(1, 5)}"
               value = f"value-{random.randint(1, 100)}"
               node.put(key, value)
           
           time.sleep(0.5)
       
       # Recuperar el líder original
       nodes[leader_id].recover()
       
       # Imprimir estado final
       print("\n" + "="*50)
       print("ESTADO FINAL DEL SISTEMA")
       print("="*50)
       
       for node in nodes:
           state_str = "LÍDER" if node.state == NodeState.LEADER else "SEGUIDOR" if node.state == NodeState.FOLLOWER else "CANDIDATO"
           status = "Activo" if node.is_active else "Inactivo"
           print(f"Nodo {node.node_id}: {status}, {state_str}, Término {node.current_term}")
           print(f"  Datos: {len(node.data)} entradas")
           for key, (value, clock) in node.data.items():
               print(f"    {key} = {value} (vector {clock})")
   
   if __name__ == "__main__":
       print("Iniciando simulación de sistema distribuido integrado...")
       simulate_distributed_system()
   EOF
   ```

2. Actualiza el Dockerfile para ejecutar la simulación integrada:
   ```bash
   cat > Dockerfile << 'EOF'
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY integrated_system.py .
   
   CMD ["python", "integrated_system.py"]
   EOF
   ```

3. Construye y ejecuta el contenedor:
   ```bash
   docker build -t integrated-system .
   docker run integrated-system
   ```

## Conceptos de Sistemas Distribuidos Demostrados

1. **Tiempo y Orden**:
   - Relojes lógicos de Lamport
   - Relojes vectoriales
   - Detección de concurrencia

2. **Coordinación Distribuida**:
   - Algoritmo de elección de líder (Bully)
   - Exclusión mutua distribuida (Ricart-Agrawala)

3. **Consistencia**:
   - Sistema de quórum
   - CRDTs (Conflict-free Replicated Data Types)

4. **Tolerancia a Fallos y Consenso**:
   - Algoritmo de consenso Raft simplificado
   - Detección de fallos

5. **Datos y Particionamiento**:
   - Hashing consistente
   - Sharding

## Recursos Adicionales

- [Documentación oficial de Docker](https://docs.docker.com/)
- [Documentación de Python](https://docs.python.org/3/)
- [Libro: Designing Data-Intensive Applications](https://dataintensive.net/) de Martin Kleppmann
- [Artículo: Time, Clocks, and the Ordering of Events in a Distributed System](https://lamport.azurewebsites.net/pubs/time-clocks.pdf) de Leslie Lamport
- [Artículo: In Search of an Understandable Consensus Algorithm](https://raft.github.io/raft.pdf) de Diego Ongaro y John Ousterhout
