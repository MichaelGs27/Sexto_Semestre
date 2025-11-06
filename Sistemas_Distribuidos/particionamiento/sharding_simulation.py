import random

# Simulaci�n de las bases de datos (shards)
SHARDS = {
    0: {"name": "Shard_Europa", "data": {}},
    1: {"name": "Shard_America", "data": {}},
    2: {"name": "Shard_Asia", "data": {}},
    3: {"name": "Shard_Oceania", "data": {}},
}
NUM_SHARDS = len(SHARDS)

def get_shard_id(user_id):
    """Calcula el ID del shard usando la operacion modulo."""
    return user_id % NUM_SHARDS

def write_user_data(user_id, user_name):
    """Simula la escritura de datos del usuario en el shard correspondiente."""
    shard_id = get_shard_id(user_id)
    shard_name = SHARDS[shard_id]["name"]
    
    SHARDS[shard_id]["data"][user_id] = user_name
    print(f"ESCRITO: Usuario {user_id} ({user_name}) -> {shard_name} (Shard {shard_id})")
    
    return shard_id

def read_user_data(user_id):
    """Simula la lectura de datos del usuario, primero localizando el shard."""
    shard_id = get_shard_id(user_id)
    shard_name = SHARDS[shard_id]["name"]
    
    if user_id in SHARDS[shard_id]["data"]:
        user_name = SHARDS[shard_id]["data"][user_id]
        print(f"LEIDO: Usuario {user_id} ({user_name}) encontrado en {shard_name}")
        return user_name
    else:
        print(f"FALLO: Usuario {user_id} no encontrado en {shard_name} (Shard {shard_id})")
        return None

def display_shards_status():
    """Muestra el estado actual y el tamano de cada shard."""
    print("\n--- Estado Actual de los Shards ---")
    for id, shard in SHARDS.items():
        data_count = len(shard["data"])
        print(f"{shard['name']} (Shard {id}): {data_count} usuarios almacenados.")
    print("---------------------------------")


def main():
    print(f"Iniciando simulacion de Sharding con {NUM_SHARDS} shards (Particion por ID Modulo {NUM_SHARDS}).")
    
    users = {
        101: "Alice",   # 101 % 4 = 1
        202: "Bob",     # 202 % 4 = 2
        303: "Charlie", # 303 % 4 = 3
        400: "David",   # 400 % 4 = 0
        1005: "Eve",    # 1005 % 4 = 1
        1008: "Frank",  # 1008 % 4 = 0
    }
    
    # 1. Escritura de datos
    print("\n--- 1. Escribiendo Datos de Usuarios ---")
    for uid, name in users.items():
        write_user_data(uid, name)
        
    display_shards_status()
    
    # 2. Lectura de datos
    print("\n--- 2. Leyendo Datos Especificos ---")
    read_user_data(101)
    read_user_data(400)
    
    # 3. Lectura de un ID que no existe (y verificacion de la ruta)
    read_user_data(110) # 110 % 4 = 2. Buscar en Shard_Asia.

if __name__ == "__main__":
    main()
