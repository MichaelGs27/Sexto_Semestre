# interfaz.py
import tkinter as tk
from tkinter import ttk, messagebox
import time
from logica import ejecutar_optimizacion

class AppRutas:
    def __init__(self, root):
        self.root = root
        self.root.title("Optimizador de Rutas - 5 Furgonetas")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")

        self.crear_interfaz()

    #Crear interfaz gráfica
    def crear_interfaz(self):
        frame_izq = tk.Frame(self.root, bg="#2c3e50", width=250)
        frame_izq.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        frame_izq.pack_propagate(False)

        tk.Label(frame_izq, text="Optimizador de Rutas", font=("Arial", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=15)

        # Parámetros
        tk.Label(frame_izq, text="Clientes:", bg="#2c3e50", fg="white").pack(anchor="w", padx=20)
        self.entry_clientes = tk.Entry(frame_izq, width=10)
        self.entry_clientes.insert(0, "200")
        self.entry_clientes.pack(padx=20, pady=2)

        tk.Label(frame_izq, text="Capacidad por furgoneta:", bg="#2c3e50", fg="white").pack(anchor="w", padx=20)
        self.entry_capacidad = tk.Entry(frame_izq, width=10)
        self.entry_capacidad.insert(0, "40")
        self.entry_capacidad.pack(padx=20, pady=2)

        btn_optimizar = tk.Button(
            frame_izq, text="INICIAR OPTIMIZACIÓN", bg="#27ae60", fg="white",
            font=("Arial", 12, "bold"), command=self.iniciar_optimizacion
        )
        btn_optimizar.pack(pady=20, padx=20, fill=tk.X)

        frame_der = tk.Frame(self.root, bg="#ecf0f1")
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tabla de resultados
        self.tree = ttk.Treeview(frame_der, columns=("Furgoneta", "Entregas", "Distancia"), show="headings", height=12)
        self.tree.heading("Furgoneta", text="Furgoneta")
        self.tree.heading("Entregas", text="Entregas")
        self.tree.heading("Distancia", text="Distancia (km)")
        self.tree.column("Furgoneta", width=80, anchor="center")
        self.tree.column("Entregas", width=80, anchor="center")
        self.tree.column("Distancia", width=100, anchor="center")
        self.tree.pack(pady=10, fill=tk.X)

        # Resumen
        self.label_resumen = tk.Label(
            frame_der, text="Presiona 'INICIAR' para optimizar rutas.",
            font=("Arial", 11), bg="#ecf0f1", fg="#2c3e50", justify="left"
        )
        self.label_resumen.pack(pady=10, anchor="w", padx=20)

    # Iniciar optimización al presionar el botón
    def iniciar_optimizacion(self):
        try:
            num_clientes = int(self.entry_clientes.get())
            capacidad = int(self.entry_capacidad.get())
            if num_clientes <= 0 or capacidad <= 0:
                raise ValueError
        except:
            messagebox.showerror("Error", "Ingresa números válidos.")
            return

        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.label_resumen.config(text="Optimizando rutas...")
        self.root.update()

        inicio = time.time()
        resultados, total_km = ejecutar_optimizacion(num_clientes, capacidad, 5)
        duracion = time.time() - inicio

        # Llenar tabla
        for res in resultados:
            self.tree.insert("", "end", values=(
                res['furgoneta'],
                res['entregas'],
                f"{res['distancia']} km"
            ))

        # Actualizar resumen
        self.label_resumen.config(
            text=f"Total: {total_km:.1f} km\n"
                 f"Promedio por furgoneta: {total_km/5:.1f} km\n"
                 f"Tiempo de cálculo: {duracion:.2f} segundos"
        )

#Inicio de la App
if __name__ == "__main__":
    root = tk.Tk()
    app = AppRutas(root)
    root.mainloop()