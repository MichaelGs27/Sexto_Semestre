import time
import random
import threading
import os
from collections import defaultdict

class GCounter:
    """
    Contador creciente (G-Counter) - Un CRDT que solo permite incrementos.
    Cada nodo mantiene un contador local para s� mismo y el valor global
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
        """Fusiona con otro contador tomando el m�ximo para cada posici�n."""
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
    Conjunto creciente (G-Set) - Un CRDT que solo permite a�adir elementos.
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
        """A�ade un elemento al conjunto."""
        self.elements.add(element)
        self.log_event(f"A�ade elemento '{element}', tama�o: {len(self.elements)}")
    
    def contains(self, element):
        """Comprueba si un elemento est� en el conjunto."""
        return element in self.elements
    
    def value(self):
        """Obtiene todos los elementos del conjunto."""
        return self.elements.copy()
    
    def merge(self, other_set):
        """Fusiona con otro conjunto tomando la uni�n."""
        self.elements = self.elements.union(other_set.elements)
        self.log_event(f"Fusiona conjuntos, nuevo tama�o: {len(self.elements)}")

class TwoPhaseSet:
    """
    Conjunto de dos fases (2P-Set) - Un CRDT que permite a�adir y eliminar elementos.
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
        """A�ade un elemento al conjunto."""
        self.additions.add(element)
        self.log_event(f"A�ade elemento '{element}'")
    
    def remove(self, element):
        """Elimina un elemento del conjunto."""
        if self.contains(element):
            self.removals.add(element)
            self.log_event(f"Elimina elemento '{element}'")
    
    def contains(self, element):
        """Comprueba si un elemento est� en el conjunto."""
        return self.additions.contains(element) and not self.removals.contains(element)
    
    def value(self):
        """Obtiene todos los elementos actuales del conjunto."""
        return {e for e in self.additions.value() if e not in self.removals.value()}
    
    def merge(self, other_set):
        """Fusiona con otro conjunto."""
        self.additions.merge(other_set.additions)
        self.removals.merge(other_set.removals)
        self.log_event(f"Fusiona conjuntos, nuevo tama�o: {len(self.value())}")

def simulate_network_partition(nodes, partition_duration=3):
    """Simula una partici�n de red entre los nodos."""
    # Dividir los nodos en dos grupos
    middle = len(nodes) // 2
    group1 = nodes[:middle]
    group2 = nodes[middle:]
    
    print(f"\n[SISTEMA] Iniciando partici�n de red por {partition_duration} segundos")
    print(f"[SISTEMA] Grupo 1: Nodos {[node.node_id for node in group1]}")
    print(f"[SISTEMA] Grupo 2: Nodos {[node.node_id for node in group2]}")
    
    # Simular operaciones en ambos grupos durante la partici�n
    def operate_on_group(group, name):
        for _ in range(3):
            time.sleep(random.uniform(0.5, 1.0))
            node = random.choice(group)
            
            # Realizar operaci�n aleatoria
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
    
    # Esperar el tiempo de la partici�n
    time.sleep(partition_duration - 3)  # Restar el tiempo de operaciones
    
    print(f"\n[SISTEMA] Finalizando partici�n de red")
    
    # Sincronizar los nodos despu�s de la partici�n
    print(f"\n[SISTEMA] Sincronizando nodos despu�s de la partici�n")
    
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
    print("Iniciando simulaci�n de PN-Counters...")
    for _ in range(5):
        node = random.choice(pn_counters)
        if random.random() < 0.7:
            node.increment()
        else:
            node.decrement()
    
    # Simular partici�n de red
    simulate_network_partition(pn_counters)
    
    # Imprimir estado final
    print_final_state(pn_counters)
    
    print("\n" + "="*50)
    
    # Crear conjuntos 2P
    two_phase_sets = [TwoPhaseSet(i) for i in range(num_nodes)]
    
    # Realizar algunas operaciones iniciales
    print("\nIniciando simulaci�n de 2P-Sets...")
    for _ in range(5):
        node = random.choice(two_phase_sets)
        element = f"item-{random.randint(1, 10)}"
        node.add(element)
    
    # Simular partici�n de red
    simulate_network_partition(two_phase_sets)
    
    # Imprimir estado final
    print_final_state(two_phase_sets)

if __name__ == "__main__":
    main()
