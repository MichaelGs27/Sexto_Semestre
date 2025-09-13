#Cliente de sockets simples en python
import socket

HOST = '10.78.201.28'  # Direccion IP del Servidor
PORT = 3000         # Puerto del Servidor

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))  # Conecta al servidor
    while True:
        mensaje = input("Ingrese un mensaje (o 'salir' para terminar): ")
        if mensaje.lower() == 'salir':
            break
        s.sendall(mensaje.encode())  # Envía el mensaje al servidor
        data = s.recv(1024)          # Recibe la respuesta del servidor
        print(f"Respuesta del servidor: {data.decode()}")