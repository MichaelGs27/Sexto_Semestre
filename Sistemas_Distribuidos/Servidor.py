#Servidor de sockets simples en python
import socket

HOST = '10.78.203.91'  # Direccion IP del Local
PORT = 3000         # Puerto que escucha

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))  # Vincula la direccion y el puerto
    s.listen()            # Escucha conexiones entrantes
    print(f"Servidor escuchando en {HOST}:{PORT}")
    conn, addr = s.accept()  # Acepta una conexion entrante
    with conn:
        print('Conectado por', addr)
        while True:
            data = conn.recv(1024)  # Recibe datos del cliente
            if not data:
                break
            print(f"Recibido: {data.decode()}")
            respuesta = f"servidor recibio: {data.decode()}"
            conn.sendall(data)  # Envía los datos de vuelta al cliente (eco)