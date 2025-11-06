import mysql.connector
from mysql.connector import Error

try:
    # Establecer conexión con el servidor
    connection = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="Michael.10"
    )

    if connection.is_connected():
        cursor = connection.cursor()
        # Crear la base de datos (si no existe)
        cursor.execute("CREATE DATABASE IF NOT EXISTS users")
        print("Base de datos creada exitosamente o ya existe.")
        
        # Seleccionar la base de datos
        cursor.execute("USE users")
        # Crear tabla Genero
        create_table_user = """ 
        CREATE TABLE IF NOT EXISTS User(
            id INT AUTO_INCREMENT,
            nombre VARCHAR(100) NOT NULL,
            correo VARCHAR(100) NOT NULL,
            PRIMARY KEY (id)
        )
        """
        cursor.execute(create_table_user)
        print("Tabla Genero creada exitosamente o ya existe.")

        # Confirmar los cambios
        connection.commit()


except Error as e:
    print("Error al conectarse al MySQL:", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexión cerrada en la base de datos.")
