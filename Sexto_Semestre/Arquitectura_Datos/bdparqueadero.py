import mysql.connector
from mysql.connector import Error

connection = None 

try:
    # Establecer conexión con el servidor
    connection = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="Michael.10"
    )

    if connection and connection.is_connected():
        cursor = connection.cursor()

        # Crear la base de datos (si no existe)
        cursor.execute("CREATE DATABASE IF NOT EXISTS Parqueadero")
        print("Base de datos 'Parqueadero' creada exitosamente o ya existe.")

        # Seleccionar la base de datos
        cursor.execute("USE Parqueadero")

        #Crear tabla roles
        create_table_roles = """
        CREATE TABLE IF NOT EXISTS roles (
            idrol INT AUTO_INCREMENT,
            nombre VARCHAR(20) UNIQUE,
            PRIMARY KEY (idrol) 
        )
        """
        cursor.execute(create_table_roles)
        print("Tabla roles creada exitosamente o ya existe.") 

        # Crear tabla tipo_vehiculos 
        create_table_tipo_vehiculo="""
        CREATE TABLE IF NOT EXISTS tipo_vehiculos (
            id_tipo INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) NOT NULL UNIQUE
        )
        """
        cursor.execute(create_table_tipo_vehiculo)
        print("Tabla tipo_vehiculos creada exitosamente o ya existe.")

        # Crear tabla tarifas 
        create_table_tarifas = """
        CREATE TABLE IF NOT EXISTS tarifas (
            id_tarifa INT AUTO_INCREMENT,
            valor_tarifa DECIMAL(10, 2) NOT NULL, -- DECIMAL para valores monetarios
            tipo_id INT NOT NULL, -- Debe coincidir con el tipo de dato de tipo_vehiculos.id_tipo
            FOREIGN KEY (tipo_id) REFERENCES tipo_vehiculos(id_tipo),
            PRIMARY KEY (id_tarifa)
        )
        """
        cursor.execute(create_table_tarifas)
        print("Tabla tarifas creada exitosamente o ya existe.")

        # Crear tabla usuarios
        create_table_usuarios = """
        CREATE TABLE IF NOT EXISTS usuarios (
            idusuario INT AUTO_INCREMENT,
            nombre_usuario VARCHAR(50) UNIQUE,
            contrasena VARCHAR(100) NOT NULL,
            activo BOOLEAN DEFAULT TRUE,
            ultimo_acceso DATETIME,
            idrol INT,
            FOREIGN KEY (idrol) REFERENCES roles(idrol),
            PRIMARY KEY (idusuario)
        )
        """
        cursor.execute(create_table_usuarios)
        print("Tabla usuarios creada exitosamente o ya existe.")

        # Crear tabla vehiculos
        create_table_vehiculo = """ 
        CREATE TABLE IF NOT EXISTS vehiculos (
            placa VARCHAR(10) PRIMARY KEY,
            id_tarifa INT,
            FOREIGN KEY (id_tarifa) REFERENCES tarifas(id_tarifa)
        )
        """
        cursor.execute(create_table_vehiculo)
        print("Tabla vehiculos creada exitosamente o ya existe.")

        #Crear tabla registros
        create_table_registro_parqueo = """
        CREATE TABLE IF NOT EXISTS registros (
            id_registro INT AUTO_INCREMENT,
            placa VARCHAR(10), -- Nombre de columna del diagrama
            id_usuario INT,
            fecha_entrada DATETIME,
            fecha_salida DATETIME,
            pagado BOOLEAN DEFAULT FALSE, -- Nombre de columna del diagrama
            FOREIGN KEY (placa) REFERENCES vehiculos(placa),
            FOREIGN KEY (id_usuario) REFERENCES usuarios(idusuario),
            PRIMARY KEY (id_registro)
        )
        """
        cursor.execute(create_table_registro_parqueo)
        print("Tabla registros creada exitosamente o ya existe.")

        # Confirmar los cambios
        connection.commit()

except Error as e:
    print("Error al conectarse a MySQL:", e)

finally:
    if connection is not None and connection.is_connected(): 
        if 'cursor' in locals() and cursor is not None:
             cursor.close()
        connection.close()
        print("Conexión cerrada en la base de datos.")