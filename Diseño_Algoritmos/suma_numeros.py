#Suma de los dígitos de un número entero positivo usando recursividad
def suma_digitos_recursiva(n):
    if n == 0:
        return 0
    else:
        ultimo_digito = n % 10
        numero_restante = n // 10
        return ultimo_digito + suma_digitos_recursiva(numero_restante)

#Ejemplo de uso
numero1 = int(input("Introduce un número entero positivo: "))
if numero1 < 0:
    print("Por favor, introduce un número entero positivo.")
else:
    resultado1 = suma_digitos_recursiva(numero1)
    print(f"La suma de los dígitos de {numero1} es: {resultado1}")
