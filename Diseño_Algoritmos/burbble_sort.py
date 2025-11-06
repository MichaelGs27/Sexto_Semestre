def bubble_sort(lista):
    n = len(lista)
    # Recorre toda la lista
    for i in range(n):
        print(i)
        print(n)
        # El bucle interno se detiene antes del último elemento ya ordenado
        print(n-i-1)
        for j in range(0, n-i-1):
            print("el valor interno=",j)
            print("el valor de la lista=",lista[j])
            print("el valor de la lista siguiente=",lista[j+1])
            # Compara elementos adyacentes
            if lista[j] > lista[j+1]:
                # Intercambia los elementos si están en el orden incorrecto
                lista[j], lista[j+1] = lista[j+1], lista[j]
                print(lista)
    return lista

# Ejemplo de uso
mi_lista = [64, 34, 25, 12, 22, 11, 90]
print(f"Lista original: {mi_lista}")
lista_ordenada = bubble_sort(mi_lista)
print(f"Lista ordenada con Bubble Sort: {lista_ordenada}")