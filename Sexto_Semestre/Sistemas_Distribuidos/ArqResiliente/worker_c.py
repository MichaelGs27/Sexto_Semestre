# worker_b.py
import jwt
JWT_SECRET = "mi-clave-super-secreta-para-firmar-tokens"

def count_words_jwt(text, token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        print(f"WORKER C: Token válido para el usuario {payload['user_id']}. Contando palabras.")
        return len(text.split())
    except jwt.ExpiredSignatureError:
        raise PermissionError("¡El token ha expirado!")
    except jwt.InvalidTokenError:
        raise PermissionError("¡Token inválido!")
