import hmac
import hashlib
import base64

from app.config import Config

def get_secret_hash(username: str):
    message = username + Config.AWS_COGNITO_CLIENT_ID
    dig = hmac.new(
        str.encode(Config.AWS_COGNITO_CLIENT_SECRET),
        msg=str.encode(message),
        digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(dig).decode()