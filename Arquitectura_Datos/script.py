import requests
import json
import time
import random
import string

# --- CONFIGURACIÓN (reemplazar esto) ---
# Revisa la documentación de Tinybird, pero el formato recomendado es:
TINYBIRD_URL = "https://api.us-east.tinybird.co/v0/events?name=hello_tinybird"
TINYBIRD_TOKEN = "p.eyJ1IjogIjEyMzJjN2EyLTQ5ZjEtNDBlNy05OTVhLTZhMTEwZTI4ZThkZiIsICJpZCI6ICI1ZTY0YTA2OS0zMjM2LTQ4YzAtYjhiNy0xNzI5ZDc0OTg3MjciLCAiaG9zdCI6ICJ1c19lYXN0In0.s1-ts8dOvUVjdxXMKRoLpTXpA571sHjSTEXVNskUFnA" 
# ---------------------------------------------------------

def generar_evento_sensor( ):
    """Genera una lectura de sensor simulada."""
    caracter = random.choice(string.ascii_letters + string.digits)
    return {
        "user_id": random.randrange(3001, 9000),
        "command": caracter,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }

def enviar_evento(evento):
    """Envía el evento al endpoint de Tinybird."""
    headers = {'Authorization': f'Bearer {TINYBIRD_TOKEN}'}
    try:
        r = requests.post(TINYBIRD_URL, data=json.dumps(evento), headers=headers)
        r.raise_for_status() # Lanza un error si la petición falla (ej. 4xx o 5xx)
        print(f"Evento enviado: {evento} -> Status: {r.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar el evento: {e}")

if __name__ == "__main__":
    print("Iniciando simulación de sensores... Presiona CTRL+C para detener.")
    while True:
        evento_nuevo = generar_evento_sensor()
        enviar_evento(evento_nuevo)
        time.sleep(5) # Espera 5 segundos antes de enviar el siguiente evento

