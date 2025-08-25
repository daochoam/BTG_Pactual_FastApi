import os
import boto3
from datetime import timedelta, timezone
from dotenv import load_dotenv
from zoneinfo import ZoneInfo

# Cargar variables del .env
load_dotenv()

class Config:
    ENVIRONMENT_MODE = os.getenv("ENVIRONMENT_MODE", "development")
    # Configuración de Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "devkey")
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

    # Configuración de AWS
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
    AWS_REGION = os.getenv("AWS_REGION", "us-east-2")
    # Nombre de tabla por defecto (opcional)
    DYNAMO_TABLE = os.getenv("DYNAMO_TABLE", "BTG_PACTUAL")

    AWS_COGNITO_CLIENT_ID = os.getenv("AWS_COGNITO_CLIENT_ID", "<tu-client-id>")
    AWS_COGNITO_CLIENT_SECRET = os.getenv("AWS_COGNITO_CLIENT_SECRET", "<tu-client-secret>")
    AWS_COGNITO_DOMAIN = os.getenv("AWS_COGNITO_DOMAIN", "<tu-dominio-cognito>")
    AWS_COGNITO_USER_POOL_ID = os.getenv("AWS_COGNITO_USER_POOL_ID", "<tu-user-pool-id>")

    SES_VERIFIED_EMAIL = os.getenv("SES_VERIFIED_EMAIL", "noreply@btgpactual.com")
    AWS_SMTP_USER = os.getenv("AWS_SMTP_USER", "TU_SMTP_USER")
    AWS_SMTP_PASS = os.getenv("AWS_SMTP_PASS", "TU_SMTP_PASS")
    AWS_SMTP_HOST = os.getenv("AWS_SMTP_HOST", "email-smtp.us-east-1.amazonaws.com")
    AWS_SMTP_PORT = os.getenv("AWS_SMTP_PORT", 587)

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_jwt_secret_key")
    JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 30))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

    # Usando zoneinfo
    TIME_ZONE = ZoneInfo(os.getenv("TIME_ZONE", "UTC"))

boto3_kwargs = {"region_name": Config.AWS_REGION}
if Config.ENVIRONMENT_MODE == "development":
    boto3_kwargs.update({
        "aws_access_key_id": Config.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": Config.AWS_SECRET_ACCESS_KEY
    })


# Recurso para operaciones de datos (put_item, get_item, etc.)
dynamodb = boto3.resource("dynamodb", **boto3_kwargs)
# Cliente para administración de tablas (create_table, list_tables, etc.)
dynamodb_client = boto3.client("dynamodb", **boto3_kwargs)

cognito_client = boto3.client("cognito-idp", region_name=Config.AWS_REGION)

__all__ = ["dynamodb", "dynamodb_client", "cognito_client"]
