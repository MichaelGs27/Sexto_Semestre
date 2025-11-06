import requests
import json

API_KEY = "AIzaSyDGF5U-4OqhctSFx8iKKaCon_Dcpsneuvk"
BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"

def obtener_distancia_y_tiempo(origen: str, destino: str) -> tuple[int, int]:
    params = {
        "origins": origen,
        "destinations": destino,
        "mode": "driving",
        "units": "metric",
        "key": API_KEY
    }
    # Llamada a la API
    try:
        respuesta = requests.get(BASE_URL, params=params, timeout=10)
        respuesta.raise_for_status() 
        datos = respuesta.json()
        # Validación de la respuesta de la API a nivel superior
        if datos["status"] != "OK":
            print(f"Error de la API global: {datos.get('error_message', datos['status'])}")
            return 0, 0
        elemento = datos["rows"][0]["elements"][0]
        # Validación del elemento (si la ruta no se puede encontrar)
        if elemento["status"] != "OK":
            print(f"Advertencia de segmento ({origen} -> {destino}): {elemento['status']}. Se asumirá 0 km/0 tiempo.")
            return 0, 0
        distancia_m = elemento["distance"]["value"]
        tiempo_s = elemento["duration"]["value"]
        return distancia_m, tiempo_s
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión con la API: {e}")
        return 0, 0
    except (json.JSONDecodeError, IndexError, KeyError) as e:
        print(f"Error al procesar datos JSON de la API: {e}")
        return 0, 0
def calcular_ruta_completa(puntos: list[str]) -> dict:
    if len(puntos) < 2:
        return {"error": "Se requieren al menos dos puntos (origen y destino)."}
    total_distancia_m = 0
    total_tiempo_s = 0
    # Iterar sobre los segmentos: (P0->P1), (P1->P2), ...
    for i in range(len(puntos) - 1):
        origen = puntos[i]
        destino = puntos[i+1]
        # Llama a la capa de Infraestructura
        distancia_m, tiempo_s = obtener_distancia_y_tiempo(origen, destino)
        # Si la API devolvió 0, asumimos un fallo y terminamos o continuamos (aquí se acumula lo que se pudo)
        if distancia_m == 0 and tiempo_s == 0:
            print(f"No se pudo calcular el segmento {origen} -> {destino}. La ruta total será parcial.")
        # Acumular los resultados (incluso si es 0 en caso de fallo)
        total_distancia_m += distancia_m
        total_tiempo_s += tiempo_s
    # Si la suma es cero, probablemente hubo un fallo en toda la ruta.
    if total_distancia_m == 0 and total_tiempo_s == 0:
        return {"error": "No se pudo obtener información de la ruta completa. Verifique los nombres de los puntos y su clave API."}
    # Preparar el resultado final
    return {
        "distancia_total_km": round(total_distancia_m / 1000, 2),
        "tiempo_total_formato": _formatear_tiempo(total_tiempo_s),
        "puntos": " -> ".join(puntos)
    }
# Función auxiliar para formatear el tiempo en una cadena legible
def _formatear_tiempo(segundos: int) -> str:
    if segundos <= 60:
        return "Menos de un minuto"
        
    SEGUNDOS_POR_MINUTO = 60
    SEGUNDOS_POR_HORA = 3600
    SEGUNDOS_POR_DIA = 86400

    dias = segundos // SEGUNDOS_POR_DIA
    segundos_restantes = segundos % SEGUNDOS_POR_DIA
    horas = segundos_restantes // SEGUNDOS_POR_HORA
    segundos_restantes = segundos_restantes % SEGUNDOS_POR_HORA
    minutos = segundos_restantes // SEGUNDOS_POR_MINUTO

    partes = []

    if dias > 0:
        texto_dias = "día" if dias == 1 else "días"
        partes.append(f"{dias} {texto_dias}")
    
    # Siempre mostramos horas y minutos si el tiempo es significativo o si es el único componente
    if horas > 0 or (dias == 0 and minutos > 0):
        partes.append(f"{horas}h")

    if minutos > 0 or (dias == 0 and horas == 0 and minutos > 0):
        partes.append(f"{minutos}m")
        
    # Caso especial: si es menos de 1 hora, asegura que se vean los minutos
    if dias == 0 and horas == 0 and minutos > 0:
        return f"{minutos}m"
    # Caso especial: si es menos de 1 minuto, asegura que se vea "Menos de un minuto"
    return " ".join(partes)