def insertion_sort(lista):
    n = len(lista)
    # Recorre la lista desde el segundo elemento
    for i in range(1, n):
        key = lista[i]
        j = i - 1
        print(f"Clave actual: {key}, Índice: {i}")
        print(j)
        # Mueve los elementos de la lista ordenada que son mayores que la 'key'
        # a una posición adelante de su posición actual
        while j >= 0 and key < lista[j]:
            print(lista)
            lista[j + 1] = lista[j]
            print(lista)

            j -= 1
        lista[j + 1] = key
        print(lista)
        print(f"Lista actual: {lista}")
    return lista

# Ejemplo de uso
mi_lista = [64, 34, 25, 12, 22, 11, 90]
print(f"Lista original: {mi_lista}")
lista_ordenada = insertion_sort(mi_lista)
print(f"Lista ordenada con Insertion Sort: {lista_ordenada}")