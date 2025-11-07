# ... (en coordinator.py)
from worker_b import count_words

# ¡MAL! La clave también está hardcodeada aquí
result_b = count_words("un texto de ejemplo", api_key="12345-super-secreto")
print(f"Resultado de Worker B: {result_b} palabras")
