#  Interfaz Gráfica de Usuario para la Calculadora de Rutas Múltiples
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List
import requests 
import logicaAPI as logicaAPI 

#  Lista Ampliada de Ciudades 
CIUDADES_DISPONIBLES = [
    "Bogota, Colombia",
    "Medellin, Colombia",
    "Cali, Colombia",
    "Barranquilla, Colombia",
    "Cartagena, Colombia",
    "Bucaramanga, Colombia",
    "Pereira, Colombia",
    "Manizales, Colombia",
    "Cucuta, Colombia",
    "Ibague, Colombia",
    "Villavicencio, Colombia",
    "Santa Marta, Colombia",
    "Neiva, Colombia",
    "Pasto, Colombia",
    "Monteria, Colombia",
    "Armenia, Colombia",
    "Valledupar, Colombia",
    "Sincelejo, Colombia",
    "Popayan, Colombia",
    "Tunja, Colombia"
]

MAX_DESTINOS = 5

class InterfazRutaApp:
    def __init__(self, master: tk.Tk):
        self.master = master
        master.title("🛣️ Calculadora de Rutas Múltiples")
        master.resizable(False, False)

        # Variables para los Combobox
        self.inicio_seleccionado = tk.StringVar()
        self.destino_seleccionado = tk.StringVar()
        
        # Variables para mostrar los resultados
        self.distancia_resultado = tk.StringVar(value="--")
        self.tiempo_resultado = tk.StringVar(value="--")
        self.recorrido_resultado = tk.StringVar(value="Ruta no calculada") 
        
        self.puntos_ruta: List[str] = []
        
        self._aplicar_estilos()
        self._crear_widgets()
    #  Métodos de Configuración de la UI 
    def _aplicar_estilos(self):
        style = ttk.Style()
        style.theme_use('clam') 
        style.configure('Accent.TButton', 
                        font=('Helvetica', 12, 'bold'), 
                        foreground='white', 
                        background='#4CAF50', 
                        padding=10, 
                        relief='flat')
        style.map('Accent.TButton', 
                 background=[('active', '#388E3C')])
        style.configure('TLabelFrame', 
                        font=('Helvetica', 10, 'bold'), 
                        relief='groove', 
                        padding=(10, 10))
        style.configure('Result.TLabel', font=('Helvetica', 10), foreground='#333333')
        style.configure('ResultBold.TLabel', font=('Helvetica', 10, 'bold'), foreground='#000000')
    #Función para crear los widgets
    def _crear_widgets(self):
        #Frame principal
        main_frame = ttk.Frame(self.master, padding="15", style='TFrame')
        main_frame.grid(row=0, column=0, sticky="nsew")
        #LabelFrame para la entrada de datos
        input_frame = ttk.LabelFrame(main_frame, text="📍 Definición de la Ruta", padding="10")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        # Punto de Inicio (P0)
        ttk.Label(input_frame, text="Inicio (P0):", style='ResultBold.TLabel').grid(row=0, column=0, pady=(5, 5), sticky="w")
        self.combobox_inicio = ttk.Combobox(input_frame, textvariable=self.inicio_seleccionado, values=CIUDADES_DISPONIBLES, state="readonly", width=37)
        self.combobox_inicio.grid(row=1, column=0, columnspan=2, pady=(0, 15), sticky="ew")
    
        if "Ibague, Colombia" in CIUDADES_DISPONIBLES:
            self.combobox_inicio.set("Ibague, Colombia")
        elif CIUDADES_DISPONIBLES:
            self.combobox_inicio.set(CIUDADES_DISPONIBLES[0])

        # Selección de Destino Intermedio
        ttk.Label(input_frame, text="Próxima Parada:", style='ResultBold.TLabel').grid(row=2, column=0, pady=(0, 5), sticky="w")
        self.combobox_destinos = ttk.Combobox(input_frame, textvariable=self.destino_seleccionado, values=CIUDADES_DISPONIBLES, state="readonly", width=37)
        self.combobox_destinos.grid(row=3, column=0, columnspan=2, sticky="ew")
        
        if len(CIUDADES_DISPONIBLES) > 1:
            self.combobox_destinos.set(CIUDADES_DISPONIBLES[1]) 

        # Botones de Añadir/Eliminar Destino
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
        
        self.btn_añadir = ttk.Button(btn_frame, text="➕ Añadir", command=self._añadir_destino)
        self.btn_añadir.pack(side=tk.LEFT, padx=(0, 5), expand=True, fill='x')
        
        self.btn_eliminar = ttk.Button(btn_frame, text="➖ Eliminar", command=self._eliminar_destino)
        self.btn_eliminar.pack(side=tk.LEFT, padx=(5, 0), expand=True, fill='x')
        
        # Lista de Destinos (Listbox) 
        ttk.Label(input_frame, text=f"Destinos intermedios (Máx. {MAX_DESTINOS}):", style='ResultBold.TLabel').grid(row=5, column=0, columnspan=2, pady=(10, 5), sticky="w")
        
        listbox_frame = ttk.Frame(input_frame)
        listbox_frame.grid(row=6, column=0, columnspan=2, sticky="ew")
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        self.listbox_ruta = tk.Listbox(listbox_frame, width=45, height=5, yscrollcommand=scrollbar.set, bd=1, relief="sunken")
        self.listbox_ruta.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.listbox_ruta.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón de Iniciar Cálculo
        self.btn_calcular = ttk.Button(main_frame, text="🚀 CALCULAR RUTA COMPLETA", command=self._iniciar_calculo, style='Accent.TButton')
        self.btn_calcular.grid(row=1, column=0, sticky="ew", pady=(5, 15))
        #Frame para mostrar los resultados
        results_frame = ttk.LabelFrame(main_frame, text="✅ Resultados del Viaje", padding="10")
        results_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))

        # Recorrido Completo
        ttk.Label(results_frame, text="Recorrido:", style='ResultBold.TLabel').grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        self.label_recorrido = ttk.Label(results_frame, textvariable=self.recorrido_resultado, wraplength=350, justify=tk.LEFT, style='Result.TLabel', anchor="w")
        self.label_recorrido.grid(row=0, column=1, sticky="w", padx=5, pady=5, columnspan=2)

        # Separador visual
        ttk.Separator(results_frame, orient=tk.HORIZONTAL).grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)

        # Distancia
        ttk.Label(results_frame, text="Distancia Total:", style='ResultBold.TLabel').grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(results_frame, textvariable=self.distancia_resultado, style='Result.TLabel').grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # Tiempo
        ttk.Label(results_frame, text="Tiempo Estimado:", style='ResultBold.TLabel').grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Label(results_frame, textvariable=self.tiempo_resultado, style='Result.TLabel').grid(row=3, column=1, sticky="w", padx=5, pady=2)


    #  Métodos de Lógica de la UI (Sin Cambios Funcionales) 
    def _añadir_destino(self):
        destino = self.destino_seleccionado.get().strip()
        inicio = self.inicio_seleccionado.get().strip() 
        
        if not destino:
            messagebox.showwarning("Error", "Selecciona un destino válido.")
            return
        if len(self.puntos_ruta) >= MAX_DESTINOS:
            messagebox.showwarning("Límite Alcanzado", f"Solo puedes agregar hasta {MAX_DESTINOS} destinos intermedios.")
            return
        if destino in self.puntos_ruta or destino == inicio:
            messagebox.showinfo("Duplicado", "Este punto ya es el inicio o ya está en la ruta.")
            return
            
        self.puntos_ruta.append(destino)
        self._actualizar_listbox()
        self._limpiar_resultados() 
    # Método para eliminar un destino seleccionado
    def _eliminar_destino(self):
        try:
            indice_seleccionado = self.listbox_ruta.curselection()[0]
            del self.puntos_ruta[indice_seleccionado]
            self._actualizar_listbox()
            self._limpiar_resultados() 
        except IndexError:
            messagebox.showwarning("Selección", "Por favor, selecciona un destino de la lista para eliminar.")
    # Actualizar el Listbox con los destinos actuales
    def _actualizar_listbox(self):
        self.listbox_ruta.delete(0, tk.END)
        for i, punto in enumerate(self.puntos_ruta):
            self.listbox_ruta.insert(tk.END, f"{i+1}. {punto}") 
    # Limpiar los resultados mostrados
    def _limpiar_resultados(self):
        self.distancia_resultado.set("--")
        self.tiempo_resultado.set("--")
        self.recorrido_resultado.set("Ruta no calculada")
    # Iniciar el cálculo de la ruta completa
    def _iniciar_calculo(self):
        inicio = self.inicio_seleccionado.get().strip() 
        if not inicio:
            messagebox.showerror("Error de Entrada", "Debes seleccionar un Punto de Inicio.")
            return
        if not self.puntos_ruta:
            messagebox.showerror("Error de Ruta", "Debes añadir al menos un Destino intermedio.")
            return
        ruta_completa = [inicio] + self.puntos_ruta
        
        # Mostrar mensaje de cálculo
        self.distancia_resultado.set("...calculando...")
        self.tiempo_resultado.set("...calculando...")
        self.recorrido_resultado.set("Procesando: " + " → ".join(ruta_completa))
        self.master.update_idletasks() 
        # Llamar a la capa de lógica de negocio
        try:
            resultado = logicaAPI.calcular_ruta_completa(ruta_completa)
            if "error" in resultado:
                self._limpiar_resultados()
                messagebox.showerror("Error de Cálculo", f"No se pudo completar el cálculo.\nDetalles: {resultado['error']}")
            else:
                self._mostrar_resultado_final(resultado)
        except Exception as e:
            self._limpiar_resultados()
            messagebox.showerror("Error Crítico", f"Ocurrió un error inesperado. Detalles: {e}")
    # Mostrar resultados finales en la UI
    def _mostrar_resultado_final(self, resultado: dict):
        self.recorrido_resultado.set(resultado['puntos'].replace(" -> ", " → "))
        self.distancia_resultado.set(f"{resultado['distancia_total_km']} km")
        self.tiempo_resultado.set(resultado['tiempo_total_formato'])
#  Ejecución de la Aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazRutaApp(root)
    root.mainloop()