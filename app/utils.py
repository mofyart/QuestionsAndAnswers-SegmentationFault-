import jwt
import time
from SegmentationFault.settings import CENTRIFUGO_HMAC_SECRET_KEY # Или откуда вы берете настройки

def get_centrifugo_token(user_id):
    atributes = {
        "sub": str(user_id),
        "exp": int(time.time()) + 24 * 3600,
    }

    token = jwt.encode(atributes, CENTRIFUGO_HMAC_SECRET_KEY, algorithm="HS256")

    if isinstance(token, bytes):
        return token.decode('utf-8')

    print(token)
    return token
