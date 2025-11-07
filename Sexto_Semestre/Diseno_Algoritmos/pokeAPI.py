#Importamos la librería requests para consumir la API
import requests

#Construir el grafo de pokemones
def construir_grafo_pokemones(nodo_actual, grafo):
    nombre_pokemon = nodo_actual['species']['name']
    grafo[nombre_pokemon] = []

    if 'evolves_to' in nodo_actual and nodo_actual['evolves_to']:
        for evolucion in nodo_actual['evolves_to']:
            nombre_siguiente_pokemon = evolucion['species']['name']
            grafo[nombre_pokemon].append(nombre_siguiente_pokemon)
            construir_grafo_pokemones(evolucion, grafo)

#Funcion para obtener la cadena de evoluciones
def obtener_cadena_evolucion(chainid):
    url = f'https://pokeapi.co/api/v2/evolution-chain/{chainid}/'
    print(f"Obteniendo datos de la URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Verifica si la solicitud fue exitosa
        data = response.json()
        nodo_inicial = data['chain']
        grafo_evolucion = {}
        construir_grafo_pokemones(nodo_inicial, grafo_evolucion)
        return grafo_evolucion
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos de la API: {e}")
        return None

#Busqueda funcion para encontrar un objetivo a traves de una busqueda binaria
def busqueda_binaria(lista_ordenada, objetivo):
    izquierda, derecha = 0, len(lista_ordenada) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        valor_medio = lista_ordenada[medio]
        if valor_medio== objetivo:
            return medio
        elif valor_medio < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return False

if __name__ == "__main__":
    print("---FASE 1: Obtener cadena de evoluciones---")
    grafo_bulsabur = obtener_cadena_evolucion(1)
    if grafo_bulsabur:
        print("\n Grafo (Bulsabur):")
        print(grafo_bulsabur)
        print("-"*40)
        print("---FASE 2: Búsqueda Binaria---")
        nodos_pokemon = sorted(grafo_bulsabur.keys())
        print(f"Nodos ordenados para la busqueda: {nodos_pokemon}")
        # Caso 1: Buscar un Pokémon que SÍ está en el grafo
        pokemon_a_buscar_1 = 'ivysaur'
        resultado_1 = busqueda_binaria(nodos_pokemon, pokemon_a_buscar_1)
        print(f"¿Está '{pokemon_a_buscar_1}' en la cadena de evolución?")
        print(f"Resultado: {resultado_1}")
        
        # Caso 2: Buscar un Pokémon que NO está en el grafo
        pokemon_a_buscar_2 = 'charmander'
        resultado_2 = busqueda_binaria(nodos_pokemon, pokemon_a_buscar_2)
        print(f"¿Está '{pokemon_a_buscar_2}' en la cadena de evolución?")
        print(f"Resultado: {resultado_2}")
#Hacer clase constructura en un archivo diferente y hacerlo recursivo
