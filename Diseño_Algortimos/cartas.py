lista = ["9T", "2P", "11C", "5D", "1P", "8C", "3D", "12T", "6P", "10T", 
        "4C", "7D", "13C", "2T", "9P", "12D", "1C", "5T", "11P", "8D", 
        "4P", "6D", "13T", "10P", "3C", "7T", "1D", "11D", "2C", "9D", 
        "13P", "8T", "4T", "12P", "6C", "5P", "10C", "3P", "7P", "12C", 
        "2D", "1T", "11T", "10D", "4D", "8P", "9C", "13D", "5C", "6T", "3T", "7C"]

def ordenar_cartas(lista):

    n = len(lista)
    for i in range(n):
        for j in range(0, n - i - 1):
            # Extrae el número y la letra de cada elemento.
            num_actual = int(lista[j][:-1])
            letra_actual = lista[j][-1]
            num_siguiente = int(lista[j+1][:-1])
            letra_siguiente = lista[j+1][-1]
            # Compara primero por el número
            if num_actual > num_siguiente:
                lista[j], lista[j+1] = lista[j+1], lista[j]
            # Si los números son iguales, compara por la letra
            elif num_actual == num_siguiente and letra_actual > letra_siguiente:
                lista[j], lista[j+1] = lista[j+1], lista[j]
    return lista

print(f"""Lista desordenada:
{lista}""")
lista_ordenada = ordenar_cartas(lista)
print(f"""Lista ordenada: 
{lista_ordenada}""")

