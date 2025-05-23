import Pyro5.api
import mysql.connector
import signal   
import sys

@Pyro5.api.expose     #Esta anotacion permite que la clase sea respuesta a
class ServicioTiposId:
    def __init__(self):
        #Establecela conexion con la base de datos MYSQL al iniciar el servicio
        self.conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="oscar2004",
        )
    
    def consultar_descripcion(self, codigo):
        try:
            cursor = self.conn.cursor()
            #Señecciona la base de datos para trabajar con ella
            cursor.execute("USE empresa")
            consulta = "SELECT Descripcion FROM tipoid WHERE IdTipoId = %s"
            cursor.execute(consulta, (codigo,))
            resultado = cursor.fetchone()
            cursor.close()

            if resultado:
                return resultado[0]
            else:
                return "Codigo no encontrado"
        except mysql.connector.Error as err:
            #Captura cualquier error de MYSQL y lo convierte en un mensaje simple
            return f"Error de base de datos: {err}"
        except Exception as e:
            #Captura cualquier otro error y lo convierte en un mensaje simple
            return f"Error desconocido: {str(e)}"
    
    def __del__(self):
        #Este metodo especial se ejecuta al destruir l objeto y cierra la conexion a la base de datos
        self.conn.close()

def finalizar_servidor(sig,frame):
    print("\n[INFO] servidor finalizado correctamente")
    sys.exit(0) 

# Capturar Ctrl+C (señal SIGINT) para un cierre limpio
signal.signal(signal.SIGINT,finalizar_servidor)

#Configura el servidor RMI
daemon = Pyro5.api.Daemon()                             #Crea un demonio de Pyro5 para esperar conexiones remotas
uri = daemon.register(ServicioTiposId)                  #Registra el objeto ServicioTiposId para ser accedido remotamente
print("Servidor TiposId corriendo. URI:", uri)          #Imprime el URI que el cliente necesita para conectarse
daemon.requestLoop()                                    #Inicia el bucle de escucha de solicitudes remotas