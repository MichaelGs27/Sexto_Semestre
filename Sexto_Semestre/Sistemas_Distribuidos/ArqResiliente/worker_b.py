# worker_b.py
API_KEY_SECRETA = "12345-super-secreto" # ¡MAL! Hardcodeado en el código

def count_words(text, api_key):
    if api_key != API_KEY_SECRETA:
        raise PermissionError("API Key inválida!")
    print("WORKER B: Clave válida. Contando palabras.")
    return len(text.split())
