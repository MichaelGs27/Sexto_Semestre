# Importamos la librería `requests` para hacer solicitudes HTTP a la API.
import requests

# Creamos una lista vacía que contendrá los nombres de los países.
paises = []
paises_con_urls = {}
# URL de la API de restcountries para obtener todos los países de la región de Europa.
url = "https://restcountries.com/v3.1/region/europe"

# Hacemos una solicitud GET a la URL de la API para obtener los datos.
respuesta = requests.get(url)
# Convertimos la respuesta JSON de la API en un objeto de Python (una lista de diccionarios).
datos = respuesta.json()
# Iteramos a través de cada diccionario de país en la lista `datos`.
for name in datos:
    nombre_pais = name['name']['common'].lower()
    mapa_url = name['maps']['googleMaps']
    paises.append(nombre_pais)
    paises_con_urls[nombre_pais] = mapa_url 

paises.sort()
print(f"Lista ordenada:\n{paises}")

def busqueda_binaria(lista, objetivo):
    # Inicializamos los índices para el inicio y el final de la lista.
    izquierda = 0
    derecha = len(lista) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        valor_medio = lista[medio]
        if valor_medio == objetivo:
            return medio
        elif valor_medio < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return -1

    # Recorremos cada elemento de la lista desde el principio hasta el final.
def busqueda_lineal(lista, objetivo):
    for i in range(len(lista)):
        if lista[i] == objetivo:
            return i
    return -1

# Solicitamos al usuario que ingrese el nombre del país que desea buscar.
try:
    pais_objetivo = input("Escribe un pais: ")
    Desicion = int(input("Elige el tipo de busqueda (1- Lineal, 2- Binaria): "))
except:
    print("Error: Entrada inválida.")
else:
    # Condición que evalúa la elección del usuario.
    if Desicion == 1:
        indice = busqueda_lineal(paises, pais_objetivo)
        if indice != -1:
            print(f"El país '{pais_objetivo}' y su url de google maps es: {paises_con_urls[pais_objetivo]}")
        else:
            print("País no encontrado.")
    else:
        indice = busqueda_binaria(paises, pais_objetivo)
        if indice != -1:
            print(f"El país '{pais_objetivo}' y su url de google maps es: {paises_con_urls[pais_objetivo]}")
        else:
            print("País no encontrado.")