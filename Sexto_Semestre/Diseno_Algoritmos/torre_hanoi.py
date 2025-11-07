#Función recursiva para resolver el problema de la Torre de Hanoi
def torre_hanoi(n, origen, destino, auxiliar):
    if n == 1:
        print(f"Mover disco 1 de {origen} a {destino}")
        return 1
    else:
        combinaciones = 0
        combinaciones += torre_hanoi(n - 1, origen, auxiliar, destino)
        print(f"Mover disco {n} de {origen} a {destino}")
        combinaciones += 1
        combinaciones += torre_hanoi(n - 1, auxiliar, destino, origen)
        return combinaciones

# Ejemplo de uso
n = int(input("Ingrese el número de discos: "))
total_combinaciones = torre_hanoi(n, 'A', 'C', 'B')
print(f"Total de movimientos: {total_combinaciones}")