P = True
Q = False
R = not P or Q
P = input("Escribe algo: ").lower()
Q = input("Escribe algo mas: ").lower()
Y = not P and Q
print(f"si P es {P}, Q es {Q}, entonces R = not P or Q es {R}")
print(f"si P es {P}, Q es {Q}, entonces Y = not P and Q es {Y}")
