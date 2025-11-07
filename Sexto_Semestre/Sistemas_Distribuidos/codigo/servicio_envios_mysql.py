# servicio_envios_mysql.py
import json
import mysql.connector
from google.cloud import pubsub_v1

# --- Configuración GCP ---
project_id = "ecommerce-476614"
subscription_id = "suscripcion-envios"
# -------------------------

# --- Configuración de la Base de Datos ---
DB_CONFIG = {
    'user': 'root',
    'password': 'Michael.10',
    'host': '127.0.0.1',
    'database': 'ecommerce_db',
    'port': 3306
}
# -----------------------------------------

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    print("\n---")
    print("[Servicio de Envíos] ¡Nuevo evento recibido!")
    
    conn = None
    try:
        data = json.loads(message.data.decode('utf-8'))
        id_pedido = data['id_pedido']
        print(f"Procesando pedido: {id_pedido}")

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO envios (id_pedido, estado) VALUES (%s, %s)", (id_pedido, 'PREPARADO'))
        conn.commit()
        
        print(f"Envío preparado para el pedido {id_pedido}.")
        message.ack()
        
    except Exception as e:
        print(f"Error procesando el mensaje: {e}")
        if conn: conn.rollback()
        message.nack()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
    print("---")

print("[Servicio de Envíos] Escuchando nuevos pedidos en MySQL...")
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)

try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()
    print("Servicio detenido.")
