# auth_server.py
import jwt
import time

JWT_SECRET = "mi-clave-super-secreta-para-firmar-tokens" 

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': time.time() + 300 # Expira en 5 minutos
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token
