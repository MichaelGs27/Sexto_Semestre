def selection_sort(lista):
    n = len(lista)
    # Recorre la lista de 0 a n-1
    for i in range(n):
        print(i)
        # Encuentra el índice del elemento mínimo en la parte no ordenada
        min_idx = i
        for j in range(i+1, n):
            print("el valor interno=", j)
            print("el valor de la lista=", lista[j])
            # Compara el elemento actual con el mínimo encontrado
            print("el valor del mínimo actual=", lista[min_idx])
            if lista[j] < lista[min_idx]:
                print("Nuevo mínimo encontrado en el índice", j)
                min_idx = j
        print("Índice del mínimo encontrado:", min_idx)
        print("Lista antes del intercambio:", lista)
        # Intercambia el elemento mínimo con el primer elemento de la parte no ordenada
        lista[i], lista[min_idx] = lista[min_idx], lista[i]
        print("Lista después del intercambio:", lista)
    return lista

# Ejemplo de uso
mi_lista = [64, 34, 25, 12, 22, 11, 90]
print(f"Lista original: {mi_lista}")
lista_ordenada = selection_sort(mi_lista)
print(f"Lista ordenada con Selection Sort: {lista_ordenada}")