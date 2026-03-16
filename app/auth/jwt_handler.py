import jwt
from datetime import datetime, timedelta
import random

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

CURRENT_USER_ID = random.randint(1, 1000) 


def create_token():
    payload = {
        "user_id": CURRENT_USER_ID,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):

    try:
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(decoded)
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_user_id(decoded: dict): 
    return decoded.get("user_id")



_token = create_token()
_decoded = verify_token(_token)
DECODED_USER_ID = get_user_id(_decoded)
