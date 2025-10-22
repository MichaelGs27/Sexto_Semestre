import requests
# 1. Función de búsqueda binaria
def busqueda_binaria(lista_ordenada: list, objetivo: str) -> bool | int:
    """
    Busca un objetivo en una lista ordenada utilizando el algoritmo de 
    búsqueda binaria.

    Retorna el índice del objetivo si se encuentra, o False si no está.
    """
    izquierda, derecha = 0, len(lista_ordenada) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2 
        valor_medio = lista_ordenada[medio]
        
        if valor_medio == objetivo:
            return medio 
        elif valor_medio < objetivo:
            izquierda = medio + 1 
        else:
            derecha = medio - 1 
    # Objetivo no encontrado    
    return False

# 2. Clase para la gestión de la evolución
class PokemonEvolution:

    BASE_URL = 'https://pokeapi.co/api/v2/evolution-chain/'
    # Constructor
    def __init__(self, chain_id):
        self.chain_id = chain_id
        self.grafo_evolucion = {}
        self._obtener_cadena_evolucion()
    #funcion recursiva para construir el grafo
    def _construir_grafo_pokemones_recursivo(self, nodo_actual):

        nombre_pokemon = nodo_actual['species']['name']
        # Inicializa la lista de adyacencia si el nodo es nuevo
        if nombre_pokemon not in self.grafo_evolucion:
            self.grafo_evolucion[nombre_pokemon] = []

        if 'evolves_to' in nodo_actual and nodo_actual['evolves_to']:
            for evolucion in nodo_actual['evolves_to']:
                nombre_siguiente_pokemon = evolucion['species']['name']
                # Añade la evolución al grafo
                self.grafo_evolucion[nombre_pokemon].append(nombre_siguiente_pokemon)
                # Llamada recursiva para la siguiente evolución
                self._construir_grafo_pokemones_recursivo(evolucion)

    # Función para obtener la cadena de evolución desde la API
    def _obtener_cadena_evolucion(self):
        url = f'{self.BASE_URL}{self.chain_id}/'
        print(f"Obteniendo datos de la URL: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()  # Lanza una excepción para errores 4xx/5xx
            data = response.json()
            nodo_inicial = data['chain']
            # Inicializa la construcción del grafo
            self._construir_grafo_pokemones_recursivo(nodo_inicial)
            print("Grafo de evolución construido exitosamente.")
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener datos de la API: {e}")
            self.grafo_evolucion = None # Establece el grafo a None en caso de error
    # Métodos para acceder a los datos
    def get_grafo(self):
        return self.grafo_evolucion
    #Metodo para obtener nodos ordenados
    def get_nodos_ordenados(self):
        if self.grafo_evolucion is not None:
            return sorted(self.grafo_evolucion.keys())
        return []