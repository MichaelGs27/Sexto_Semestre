#factorial
def factorial(n, nivel=0):
    indent = "  " * nivel  # Indentación para visualizar la recursión
    print(f"{indent}Calculando factorial({n})")
    
    if n <= 1:
        print(f"{indent}factorial({n}) = 1")
        return 1
    else:
        result = n * factorial(n-1, nivel + 1)
        print(f"{indent}factorial({n}) = {n} * factorial({n-1}) = {result}")
        return result

# Ejemplo de uso
n = 4
print(f"\nCalculando el factorial de {n}:")
resultado = factorial(n)
print(f"\nResultado final: {n}! = {resultado}")
