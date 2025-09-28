import mysql.connector
from mysql.connector import Error

try:
    # Establish connection to the MySQL server
    connection = mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password=""
    )

    if connection.is_connected():
        cursor = connection.cursor()
        # Create the database (if it doesn't exist)
        cursor.execute("CREATE DATABASE IF NOT EXISTS polarizados")
        print("Base de datos creada exitosamente o ya existe.")

        # Select the database
        cursor.execute("USE polarizados")

        # --- Table creation block with corrected order ---
        # 1. Base tables (without foreign keys)
        create_table_tiposdoc = """
        CREATE TABLE IF NOT EXISTS TiposDoc(
            idTipoDoc VARCHAR(20) NOT NULL,
            descripcion VARCHAR(100) NOT NULL,
            PRIMARY KEY (idTipoDoc)
        )
        """
        cursor.execute(create_table_tiposdoc)
        print("Tabla TiposDoc creada exitosamente o ya existe.")

        create_table_tiposvehiculos = """
        CREATE TABLE IF NOT EXISTS TiposVehiculos(
            idTipoVehiculo INT AUTO_INCREMENT,
            tipoVehiculo VARCHAR(100) NOT NULL,
            PRIMARY KEY (idTipoVehiculo)
        )
        """
        cursor.execute(create_table_tiposvehiculos)
        print("Tabla TiposVehiculos creada exitosamente o ya existe.")
        
        create_table_servicios = """
        CREATE TABLE IF NOT EXISTS servicios(
            idServicio INT AUTO_INCREMENT,
            nombreServicio VARCHAR(100) NOT NULL,
            precio DECIMAL(10,2) NOT NULL,
            PRIMARY KEY (idServicio)
        )
        """
        cursor.execute(create_table_servicios)
        print("Tabla servicios creada exitosamente o ya existe.")

        # 2. Tables that depend on the first ones
        create_table_usuarios = """
        CREATE TABLE IF NOT EXISTS usuarios(
            idUsuario INT AUTO_INCREMENT,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            correo VARCHAR(100) NOT NULL,
            telefono VARCHAR(15),
            direccion VARCHAR(200),
            idTipoDoc VARCHAR(20),  -- Corrected line: Data type changed to VARCHAR(20)
            numeroDoc VARCHAR(20),
            PRIMARY KEY (idUsuario),
            FOREIGN KEY (idTipoDoc) REFERENCES TiposDoc(idTipoDoc)
        )
        """
        cursor.execute(create_table_usuarios)
        print("Tabla usuarios creada exitosamente o ya existe.")
        
        create_table_vehiculos = """
        CREATE TABLE IF NOT EXISTS vehiculos(
            idVehiculo INT AUTO_INCREMENT,
            marca VARCHAR(100) NOT NULL,
            modelo VARCHAR(100) NOT NULL,
            año INT,
            color VARCHAR(50),
            idTipoVehiculo INT,
            idUsuario INT,
            PRIMARY KEY (idVehiculo),
            FOREIGN KEY (idTipoVehiculo) REFERENCES TiposVehiculos(idTipoVehiculo),
            FOREIGN KEY (idUsuario) REFERENCES usuarios(idUsuario)
        )
        """
        cursor.execute(create_table_vehiculos)
        print("Tabla vehiculos creada exitosamente o ya existe.")

        create_table_tiposservicios = """
        CREATE TABLE IF NOT EXISTS TiposServicios(
            idTipoServicio INT AUTO_INCREMENT,
            idServicio INT NOT NULL,
            nombreTiposervicio VARCHAR(100) NOT NULL,
            precio DECIMAL(10,2) NOT NULL,
            PRIMARY KEY (idTipoServicio),
            FOREIGN KEY (idServicio) REFERENCES servicios(idServicio)
        )
        """
        cursor.execute(create_table_tiposservicios)
        print("Tabla TiposServicios creada exitosamente o ya existe.")
        
        create_table_faq = """
        CREATE TABLE IF NOT EXISTS FAQ(
            idFAQ INT AUTO_INCREMENT,
            pregunta VARCHAR(255) NOT NULL,
            respuesta VARCHAR(255) NOT NULL,
            idServicio INT,
            PRIMARY KEY (idFAQ),
            FOREIGN KEY (idServicio) REFERENCES servicios(idServicio)
        )
        """
        cursor.execute(create_table_faq)
        print("Tabla FAQ creada exitosamente o ya existe.")

        create_table_testimonios = """
        CREATE TABLE IF NOT EXISTS testimonios(
            idTestimonio INT AUTO_INCREMENT,
            idUsuario INT,
            comentario VARCHAR(500) NOT NULL,
            fecha DATE,
            idServicio INT,
            PRIMARY KEY (idTestimonio),
            FOREIGN KEY (idUsuario) REFERENCES usuarios(idUsuario),
            FOREIGN KEY (idServicio) REFERENCES servicios(idServicio)
        )
        """
        cursor.execute(create_table_testimonios)
        print("Tabla testimonios creada exitosamente o ya existe.")

        # 3. Tables that depend on the previous ones
        create_table_promociones = """
        CREATE TABLE IF NOT EXISTS promociones(
            idPromocion INT AUTO_INCREMENT,
            idTipoServicio INT,
            nombrePromocion VARCHAR(100) NOT NULL,
            precioPromocion DECIMAL(10,2) NOT NULL,
            fechaInicio DATE,
            fechaFin DATE,
            estado VARCHAR(50),
            descuento DECIMAL(5,2),
            idServicio INT,
            PRIMARY KEY (idPromocion),
            FOREIGN KEY (idTipoServicio) REFERENCES TiposServicios(idTipoServicio),
            FOREIGN KEY (idServicio) REFERENCES servicios(idServicio)
        )
        """
        cursor.execute(create_table_promociones)
        print("Tabla promociones creada exitosamente o ya existe.")
        
        create_table_portafolio = """
        CREATE TABLE IF NOT EXISTS portafolio(
            idPortafolio INT AUTO_INCREMENT,
            idServicio INT,
            idTipoServicio INT,
            nombrePromocion VARCHAR(225) NOT NULL,
            descripcion VARCHAR(500) NOT NULL,
            PRIMARY KEY (idPortafolio),
            FOREIGN KEY (idServicio) REFERENCES servicios(idServicio),
            FOREIGN KEY (idTipoServicio) REFERENCES TiposServicios(idTipoServicio)
        )
        """
        cursor.execute(create_table_portafolio)
        print("Tabla portafolio creada exitosamente o ya existe.")

        create_table_citas = """
        CREATE TABLE IF NOT EXISTS citas(
            idCita INT AUTO_INCREMENT,
            idTipoServicio INT,
            n_Fecha DATE,
            estado VARCHAR(50),
            descripcionTipoD VARCHAR(100),
            idUsuario INT,
            idServicio INT,
            observaciones VARCHAR(255),
            idTipoVehiculo INT,
            idVehiculo INT,
            PRIMARY KEY (idCita),
            FOREIGN KEY (idTipoServicio) REFERENCES TiposServicios(idTipoServicio),
            FOREIGN KEY (idUsuario) REFERENCES usuarios(idUsuario),
            FOREIGN KEY (idServicio) REFERENCES servicios(idServicio),
            FOREIGN KEY (idTipoVehiculo) REFERENCES TiposVehiculos(idTipoVehiculo),
            FOREIGN KEY (idVehiculo) REFERENCES vehiculos(idVehiculo)
        )
        """
        cursor.execute(create_table_citas)
        print("Tabla citas creada exitosamente o ya existe.")
        
        # Commit the changes
        connection.commit()

except Error as e:
    print("Error al conectarse al MySQL:", e)

finally:
    if 'connection' in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexión cerrada en la base de datos.")