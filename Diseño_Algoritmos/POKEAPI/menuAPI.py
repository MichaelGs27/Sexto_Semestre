# Importamos la lógica necesaria desde el archivo 'pokemon_logic'
from logicaAPI import PokemonEvolution, busqueda_binaria

def main():
    print("Evolución de Pokémon y Búsqueda Binaria")
    
    # --- FASE 1: Obtener cadena de evoluciones (Bulbasaur, ID 1) ---
    print("\n--- FASE 1: Obtener cadena de evoluciones (Bulbasaur) ---") 
    # Se crea una instancia de la clase, lo que dispara la llamada a la API
    cadena_bulbasaur = PokemonEvolution(chain_id=1)
    grafo_bulbasaur = cadena_bulbasaur.get_grafo()

    if grafo_bulbasaur:
        print("\nGrafo de Evolución (Bulbasaur):")
        # Mostrar el grafo resultante
        print(grafo_bulbasaur)
        print("-" * 40)
        
        # --- FASE 2: Búsqueda Binaria sobre los Nodos ---
        print("--- FASE 2: Búsqueda Binaria sobre los Nodos ---")
        
        # 1. Preparar datos: Obtener los nodos ordenados para la búsqueda
        nodos_pokemon = cadena_bulbasaur.get_nodos_ordenados()
        print(f"Nodos ordenados para la busqueda: {nodos_pokemon}")

        # 2. Caso de prueba 1: Buscar un Pokémon que SÍ está en el grafo
        pokemon_a_buscar_1 = 'ivysaur'
        resultado_1 = busqueda_binaria(nodos_pokemon, pokemon_a_buscar_1)
        
        print(f"\n ¿Está '{pokemon_a_buscar_1}' en la cadena de evolución?")
        if resultado_1 is not False:
            print(f"Resultado: Sí, se encuentra en el índice {resultado_1}.")
        else:
            print(f"Resultado: No se encontró.")
        
        # 3. Caso de prueba 2: Buscar un Pokémon que NO está en el grafo
        pokemon_a_buscar_2 = 'charmander'
        resultado_2 = busqueda_binaria(nodos_pokemon, pokemon_a_buscar_2)
        
        print(f"\n❔ ¿Está '{pokemon_a_buscar_2}' en la cadena de evolución?")
        if resultado_2 is not False:
            print(f"Resultado: Sí, se encuentra en el índice {resultado_2}.")
        else:
            print(f"Resultado: No se encontró.)")

if __name__ == "__main__":
    main()