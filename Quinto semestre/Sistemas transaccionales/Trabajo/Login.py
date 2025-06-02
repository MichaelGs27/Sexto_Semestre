import tkinter as tk
from tkinter import messagebox
from InterfazParqueadero import interfazParqueadero
import mysql.connector

# Función para conectar a la BD
def conectar():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="",
        database="parqueadero"
    )
#Variable para los intentos de iniciar sesión 
intentos = 0

#Funcion para verificar que exista el usuario

def verificar_login():
    global intentos
    usuario = entry_usuario.get()
    contrasena = entry_contrasena.get()

#Si el usuario y la contraseña estan vacion envia un mensaje 
    if not usuario or not contrasena:
        messagebox.showwarning("Campos vacíos", "Ingrese usuario y contraseña")
        return

    try:
        conn = conectar()
        cursor = conn.cursor()

#Hace una consulta para verficar que exista el usuario

        query = "SELECT cContraseña FROM usuario WHERE cNomUsuario = %s"
        cursor.execute(query, (usuario,))
        resultado = cursor.fetchone()

        if resultado is None:
            messagebox.showerror("Error", "Usuario no encontrado")
            intentos += 1
        else:
            contrasenaBd = resultado[0]
            if contrasena == contrasenaBd:  
                messagebox.showinfo("Éxito", "¡Bienvenido al sistema de parqueadero!")
                ventana.destroy()
                interfazParqueadero()
                return
            else:
                messagebox.showerror("Error", "Contraseña incorrecta")
                intentos += 1
#Va disminuyendo los intentos si el usuario o contraseña son incorrectos 
        if intentos >= 3:
            messagebox.showerror("Acceso bloqueado", "Has superado el número de intentos. Cerrando aplicación.")
            ventana.destroy()
        else:
            restantes = 3 - intentos
            messagebox.showwarning("Intentos restantes", f"Te quedan {restantes} intento(s)")

    except mysql.connector.Error as err:
        messagebox.showerror("Error BD", f"No se pudo conectar o consultar la base de datos: {err}")
    finally:
        if 'conn' in locals():
            conn.close()


# Interfaz de login 
ventana = tk.Tk()
ventana.title("ParkU - Login")
ventana.geometry("300x200")
ventana.configure(bg="#34495e")

tk.Label(ventana, text="Usuario", bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)
entry_usuario = tk.Entry(ventana, font=("Arial", 12))
entry_usuario.pack()

tk.Label(ventana, text="Contraseña", bg="#34495e", fg="white", font=("Arial", 12)).pack(pady=5)
entry_contrasena = tk.Entry(ventana, show="*", font=("Arial", 12))
entry_contrasena.pack()

tk.Button(ventana, text="Iniciar Sesión", command=verificar_login,
          bg="#27ae60", fg="white", font=("Arial", 12)).pack(pady=15)

ventana.mainloop()
