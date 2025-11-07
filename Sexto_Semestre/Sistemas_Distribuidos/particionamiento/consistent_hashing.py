import hashlib
import bisect

class ConsistentHashRing:
    """Implementa un anillo simple de Hashing Consistente."""
    def __init__(self, replicas=100):
        self.replicas = replicas # Numero de replicas virtuales por nodo
        self.ring = {}           # Almacena el hash del nodo y el nombre del nodo
        self.sorted_keys = []    # Claves de hash ordenadas para busqueda binaria

    def _gen_hash(self, key):
        """Genera un hash numerico (de 0 a 2^32 - 1) para una clave."""
        return int(hashlib.sha1(key.encode()).hexdigest(), 16) & 0xFFFFFFFF

    def add_node(self, node):
        """Anade un nodo (fisico) al anillo con sus replicas virtuales."""
        for i in range(self.replicas):
            key = self._gen_hash(f"{node}:{i}")
            self.ring[key] = node
            self.sorted_keys.append(key)
        self.sorted_keys.sort()
        print(f"Anadido nodo: {node} (Total de claves en el anillo: {len(self.sorted_keys)})")

    def remove_node(self, node):
        """Elimina un nodo (fisico) y sus replicas virtuales del anillo."""
        for i in range(self.replicas):
            key = self._gen_hash(f"{node}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)
        print(f"Eliminado nodo: {node} (Total de claves en el anillo: {len(self.sorted_keys)})")

    def get_node(self, key):
        """Encuentra el nodo responsable de una clave de dato."""
        if not self.ring:
            return None
            
        data_hash = self._gen_hash(key)
        
        # Encontrar la posicion de insercion de data_hash en sorted_keys
        # Esto encuentra el nodo cuya clave de hash es igual o inmediatamente superior al hash del dato.
        idx = bisect.bisect(self.sorted_keys, data_hash)
        
        # Si llegamos al final, volvemos al principio del anillo (idx=0)
        if idx == len(self.sorted_keys):
            idx = 0
            
        node_key = self.sorted_keys[idx]
        return self.ring[node_key]

def main():
    ring = ConsistentHashRing(replicas=100)
    
    # 1. Anadir nodos iniciales
    nodes = ["Servidor_A", "Servidor_B", "Servidor_C"]
    for node in nodes:
        ring.add_node(node)
        
    # 2. Asignar datos a los nodos
    data_items = ["usuario_1", "usuario_2", "producto_a", "orden_55", "cache_key_x", "video_id_7"]
    initial_mapping = {}
    
    print("\n--- Mapeo Inicial de Datos ---")
    for item in data_items:
        node = ring.get_node(item)
        initial_mapping[item] = node
        print(f"Dato '{item}' -> {node}")
        
    # 3. Simular adicion de un nodo
    new_node = "Servidor_D"
    print(f"\n--- Anadiendo nodo {new_node} ---")
    ring.add_node(new_node)
    
    # 4. Verificar reubicacion de datos
    relocated_count = 0
    print("\n--- Mapeo Despues de Anadir Servidor_D ---")
    for item in data_items:
        new_node = ring.get_node(item)
        print(f"Dato '{item}' -> {new_node}", end="")
        if new_node != initial_mapping[item]:
            relocated_count += 1
            print(" <--- REUBICADO")
        else:
            print()

    print(f"\nResumen: {relocated_count} de {len(data_items)} datos reubicados.")

if __name__ == "__main__":
    main()
