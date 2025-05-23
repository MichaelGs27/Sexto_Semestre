import mysql.connector
import threading
from mysql.connector import Error
import time

def actualizar_tipoid(id_tipo, nueva_desc, espera=2):
    try:
    # Establecer conexión con el servidor
        connection = mysql.connector.connect(
            host="localhost",
            port="3306",
            user="root",
            password="",
            database = "universidad"
        )
        cursor = connection.cursor()
        print(f"[{threading.current_thread().name}] Iniciando transacción.")

        #Iniciar transacción
        cursor.execute("START TRANSACTION")
        
        #Bloquear la fila para evitar 
        cursor.execute("SELECT cDescripcionTipoId FROM tiposid WHERE cTipoId = %s FOR UPDATE", (id_tipo,))

        #Lectura de datos actualizados 
        desc_actual = cursor.fetchone()
        print(f"[{threading.current_thread().name}] Descripción actual: {desc_actual[0]}")

        #Simulan edicion
        time.sleep(espera)

        #Actualizar descripcion
        cursor.execute("UPDATE tiposid SET cDescripcionTipoId = %s WHERE cTipoId = %s", (nueva_desc,id_tipo))
        connection.commit()
        print(f"[{threading.current_thread().name}] Descripcion actualizada a:{nueva_desc} ")

    except Error as e:
        print(f"[{threading.current_thread().name}] Error: {e}")
        connection.rollback()

    finally:
        connection.close()

#Crear hilos que simulan usuarios concurrentes 
hilo1 = threading.Thread(target=actualizar_tipoid, args=("CC","Cedula - Actualización A", 4), name="Usuario A")
hilo2 = threading.Thread(target=actualizar_tipoid, args=("CC","Tarjeta de Identidad - Actualización B", 4), name="Usuario B")
hilo3 = threading.Thread(target=actualizar_tipoid, args=("CC","Cedula ya - Actualización C", 4), name="Usuario C")
hilo4 = threading.Thread(target=actualizar_tipoid, args=("CC","Tarjeta de  - Actualización D", 4), name="Usuario D")
hilo5 = threading.Thread(target=actualizar_tipoid, args=("CC","Tarjeta de Identidad - Actualización E", 4), name="Usuario E")
hilo6 = threading.Thread(target=actualizar_tipoid, args=("CC","Tarjeta de PEA - Actualización F", 4), name="Usuario F")
hilo7 = threading.Thread(target=actualizar_tipoid, args=("CC","Tarjeta de Identidad - Actualización G", 4), name="Usuario G")

hilo1.start()
hilo2.start()
hilo3.start()
hilo4.start()
hilo5.start()
hilo6.start()
hilo7.start()

hilo1.join()
hilo2.join()
hilo3.join()
hilo4.join()
hilo5.join()
hilo6.join()
hilo7.join()