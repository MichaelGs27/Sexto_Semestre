# logica.py
import math
import random
from typing import List, Tuple

# Clase Nodo
class Nodo:
    def __init__(self, id: int, x: float, y: float, volumen: int = 1,
                 hora_inicio: int = 480, hora_fin: int = 1080):
        self.id = id
        self.x = x
        self.y = y
        self.volumen = volumen
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin

    def __repr__(self):
        return f"N{self.id}"

# Calcular distancia entre dos nodos
def distancia(a: Nodo, b: Nodo) -> float:
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

# Calcular costo total de una ruta
def costo_ruta(ruta: List[Nodo]) -> float:
    return sum(distancia(ruta[i], ruta[i+1]) for i in range(len(ruta)-1))

# Mejorar ruta
def cruzar_mejora(ruta: List[Nodo], i: int, j: int) -> bool:
    if j - i < 2: return False
    A, B, C, D = ruta[i-1], ruta[i], ruta[j-1], ruta[j]
    return (distancia(A, B) + distancia(C, D)) > (distancia(A, C) + distancia(B, D))

# Asignar clientes a furgonetas
def asignar_clientes_greedy(nodos: List[Nodo], almacen: Nodo, capacidad_max: int, num_furgonetas: int = 5):
    clientes = [n for n in nodos if n.id != 0]
    clientes.sort(key=lambda c: distancia(almacen, c))

    furgonetas = [[] for _ in range(num_furgonetas)]
    carga_actual = [0] * num_furgonetas

    for cliente in clientes:
        mejor_idx = -1
        menor_carga = float('inf')
        for i in range(num_furgonetas):
            if carga_actual[i] + cliente.volumen <= capacidad_max and carga_actual[i] < menor_carga:
                menor_carga = carga_actual[i]
                mejor_idx = i
        if mejor_idx != -1:
            furgonetas[mejor_idx].append(cliente)
            carga_actual[mejor_idx] += cliente.volumen
    return furgonetas

# Optimizar ruta de una furgoneta
def optimizar_ruta_furgoneta(clientes: List[Nodo], almacen: Nodo) -> List[Nodo]:
    if not clientes:
        return [almacen]
    clientes.sort(key=lambda c: math.atan2(c.y - almacen.y, c.x - almacen.x))
    ruta = [almacen] + clientes + [almacen]

    mejorada = True
    iteracion = 0
    while mejorada and iteracion < 50: 
        mejorada = False
        for i in range(1, len(ruta) - 2):
            for j in range(i + 2, len(ruta)):
                if cruzar_mejora(ruta, i, j):
                    ruta[i:j] = ruta[j-1:i-1:-1]
                    mejorada = True
        iteracion += 1
    return ruta

def generar_datos_prueba(num_clientes=200, radio=15.0, capacidad_max=40):
    random.seed(42)
    almacen = Nodo(0, 0.0, 0.0, 0, 0, 1440)
    nodos = [almacen]
    for i in range(1, num_clientes + 1):
        r = random.gauss(radio * 0.6, radio * 0.4)
        ang = random.uniform(0, 2 * math.pi)
        x = r * math.cos(ang)
        y = r * math.sin(ang)
        volumen = random.randint(1, 3)
        hora_inicio = random.randint(480, 900)
        hora_fin = hora_inicio + random.randint(60, 180)
        nodos.append(Nodo(i, x, y, volumen, hora_inicio, hora_fin))
    return almacen, nodos, capacidad_max

# Ejecutar optimización completa
def ejecutar_optimizacion(num_clientes=200, capacidad_max=40, num_furgonetas=5):
    almacen, nodos, cap = generar_datos_prueba(num_clientes, 15.0, capacidad_max)
    asignadas = asignar_clientes_greedy(nodos, almacen, cap, num_furgonetas)
    rutas = [optimizar_ruta_furgoneta(clientes, almacen) for clientes in asignadas]
    resultados = []
    total_km = 0
    for i, ruta in enumerate(rutas):
        entregas = len(ruta) - 2
        km = costo_ruta(ruta)
        total_km += km
        resultados.append({
            'furgoneta': i+1,
            'entregas': entregas,
            'distancia': round(km, 1),
            'ruta': ruta
        })
    return resultados, total_km