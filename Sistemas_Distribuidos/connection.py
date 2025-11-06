import mysql.connector
from mysql.connector import Error

try:
    # Establecer conexión con el servidor
    connection = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password=""
    )

    if connection.is_connected():
        cursor = connection.cursor()
        # Crear la base de datos (si no existe)
        cursor.execute("CREATE DATABASE IF NOT EXISTS Empresa")
        print("Base de datos creada exitosamente o ya existe.")
        
        # Seleccionar la base de datos correcta
        cursor.execute("USE Empresa")

        # Crear tabla TiposId
        create_table_TiposId = """ 
        CREATE TABLE IF NOT EXISTS TiposId(
            cIdTipoId VARCHAR(10) NOT NULL,
            cDescripcion VARCHAR(45) NOT NULL,
            PRIMARY KEY (cIdTipoId)
        )
        """
        cursor.execute(create_table_TiposId)
        print("Tabla TiposId creada exitosamente o ya existe.")

        # Crear tabla Genero
        create_table_genero = """ 
        CREATE TABLE IF NOT EXISTS Genero(
            cIdGenero INT AUTO_INCREMENT,
            cDescripcion VARCHAR(45) NOT NULL,
            PRIMARY KEY (cIdGenero)
        )
        """
        cursor.execute(create_table_genero)
        print("Tabla Genero creada exitosamente o ya existe.")

        cursor.execute("USE Empresa")
        # Crear tabla Personas
        create_table_personas = """ 
        CREATE TABLE IF NOT EXISTS Personas(
            cIdPersona INT AUTO_INCREMENT,
            cNombre VARCHAR(45) NOT NULL,
            cApellido VARCHAR(45) NOT NULL,
<<<<<<< HEAD
            cidTipoId varchar(10) NOT NULL,
=======
            cidTipoId INT,
>>>>>>> f7a7aa03e8736b0ad22c542b4d86314797b98d95
            cIdGenero INT,
            PRIMARY KEY (cIdPersona),
            FOREIGN KEY (cidTipoId) REFERENCES TiposId(cIdTipoId),
            FOREIGN KEY (cIdGenero) REFERENCES Genero(cIdGenero)
        )
        """
        cursor.execute(create_table_personas)
        print("Tabla Personas creada exitosamente o ya existe.")

        # Confirmar los cambios
        connection.commit()

except Error as e:
    print("Error al conectarse al MySQL:", e)

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexión cerrada en la base de datos.")