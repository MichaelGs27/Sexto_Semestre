import time
import random

class Node:
    def __init__(self, node_id, total_nodes):
        self.id = node_id
        self.value = 0
        self.version = 0
        self.total_nodes = total_nodes

    def write(self, new_value):
        # Simula una escritura: incrementa la versión y actualiza el valor
        self.version += 1
        self.value = new_value
        print(f"  P{self.id} WRITE: Valor={self.value}, Versión={self.version}")
        return self.version, self.value

    def read(self):
        # Simula una lectura
        return self.version, self.value

def simulate_quorum_write(nodes, N, W, new_value):
    print(f"\n--- Simulación de Escritura (N={N}, W={W}) ---")
    
    # 1. Seleccionar un subconjunto de W nodos para la escritura
    target_nodes = random.sample(nodes, W)
    print(f"Seleccionando {W} nodos para escritura: {[n.id for n in target_nodes]}")

    # 2. Ejecutar la escritura
    latest_version = 0
    latest_value = None
    
    for node in target_nodes:
        version, value = node.write(new_value)
        if version > latest_version:
            latest_version = version
            latest_value = value

    # 3. Respuesta de escritura (confirmación)
    print(f"Escritura completada. Última versión escrita: {latest_version}")
    return latest_version

def simulate_quorum_read(nodes, N, R):
    print(f"\n--- Simulación de Lectura (N={N}, R={R}) ---")
    
    # 1. Seleccionar un subconjunto de R nodos para la lectura
    target_nodes = random.sample(nodes, R)
    print(f"Seleccionando {R} nodos para lectura: {[n.id for n in target_nodes]}")
    
    # 2. Ejecutar la lectura y encontrar la versión más reciente
    readings = []
    latest_version = -1
    latest_value = None
    
    for node in target_nodes:
        version, value = node.read()
        readings.append((node.id, version, value))
        if version > latest_version:
            latest_version = version
            latest_value = value

    # 3. Respuesta de lectura
    print("Lecturas obtenidas:")
    for id, version, value in readings:
        print(f"  P{id}: Valor={value}, Versión={version}")
        
    print(f"Resultado final (versión más reciente): Valor={latest_value}, Versión={latest_version}")
    return latest_version

def main():
    N = 5 # Número total de réplicas
    
    # Quorum Estricto (Consistencia Fuerte): R + W > N
    W_STRICT = 3 
    R_STRICT = 3 
    
    # Quorum Flexible (Consistencia Débil): R + W <= N
    W_FLEX = 2
    R_FLEX = 2

    nodes = [Node(i, N) for i in range(N)]

    print(f"Sistema de {N} nodos inicializado.")
    
    # --- SIMULACIÓN 1: CONSISTENCIA FUERTE (R=3, W=3) ---
    print("\n" + "="*50)
    print("SIMULACIÓN 1: CONSISTENCIA FUERTE (R=3, W=3)")
    print("="*50)
    
    simulate_quorum_write(nodes, N, W_STRICT, "Dato A")
    simulate_quorum_read(nodes, N, R_STRICT)

    # --- SIMULACIÓN 2: CONSISTENCIA DÉBIL (R=2, W=2) ---
    print("\n" + "="*50)
    print("SIMULACIÓN 2: CONSISTENCIA DÉBIL (R=2, W=2)")
    print("="*50)
    
    simulate_quorum_write(nodes, N, W_FLEX, "Dato B")
    simulate_quorum_read(nodes, N, R_FLEX)

if __name__ == "__main__":
    main()
