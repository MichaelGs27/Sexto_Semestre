# servicio_pedidos_mysql.py
import uuid
import json
import mysql.connector
from google.cloud import pubsub_v1

# --- Configuración GCP ---
project_id = "ecommerce-476614" 
topic_id = "nuevos-pedidos"
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

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def crear_y_publicar_pedido():
    """Simula la creación de un pedido, lo guarda en MySQL y lo publica."""
    
    id_pedido = str(uuid.uuid4())
    pedido_data = {"id_pedido": id_pedido, "id_cliente": 456, "total": 150.75}
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        insert_query = "INSERT INTO pedidos (id_pedido, id_cliente, total, estado) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, (pedido_data['id_pedido'], pedido_data['id_cliente'], pedido_data['total'], 'RECIBIDO'))
        conn.commit()
        
        print(f"Pedido {id_pedido} guardado en MySQL con estado 'RECIBIDO'.")
        
    except mysql.connector.Error as err:
        print(f"Error al guardar en MySQL: {err}")
        return
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    try:
        mensaje_bytes = json.dumps(pedido_data).encode('utf-8')
        future = publisher.publish(topic_path, mensaje_bytes)
        message_id = future.result()
        print(f"Evento de nuevo pedido publicado en Pub/Sub. ID del mensaje: {message_id}")
    except Exception as e:
        print(f"Error al publicar en Pub/Sub: {e}")

if __name__ == "__main__":
    crear_y_publicar_pedido()
