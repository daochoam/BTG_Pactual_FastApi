# BTG Pactual FastAPI Project

Este proyecto utiliza **FastAPI** para construir una API robusta con integración a servicios AWS y autenticación mediante Cognito.

## Ejecución del Proyecto

1. **Clona el repositorio:**
  ```bash
  git clone https://github.com/tu_usuario/BTG_Pactual_FastApi.git
  cd BTG_Pactual_FastApi
  ```

2. **Instala las dependencias:**
  ```bash
  pip install -r requirements.txt
  ```

3. **Configura las variables de entorno:**

  Crea un archivo `.env` en la raíz del proyecto y agrega las siguientes variables:

  ```env
  AWS_ACCESS_KEY_ID=           # ID de clave de acceso para AWS
  AWS_SECRET_ACCESS_KEY=       # Clave secreta de acceso para AWS
  AWS_REGION=                  # Región de AWS (ejemplo: us-east-1)
  DYNAMO_TABLE=                # Nombre de la tabla DynamoDB

  AWS_COGNITO_CLIENT_ID=       # ID de cliente de la aplicación Cognito
  AWS_COGNITO_CLIENT_SECRET=   # Secreto de cliente de Cognito
  AWS_COGNITO_REDIRECT_URI=    # URI de redirección para autenticación Cognito
  AWS_COGNITO_DOMAIN=          # Dominio de Cognito (ejemplo: tu-dominio.auth.us-east-1.amazoncognito.com)
  AWS_COGNITO_USER_POOL_ID=    # ID del grupo de usuarios Cognito

  SES_VERIFIED_EMAIL=          # Email verificado en AWS SES para envío
  AWS_SMTP_HOST=               # Host SMTP de AWS
  AWS_SMTP_PORT=               # Puerto SMTP de AWS
  AWS_SMTP_USER=               # Usuario SMTP de AWS
  AWS_SMTP_PASS=               # Contraseña SMTP de AWS

  JWT_SECRET_KEY=              # Clave secreta para firmar JWT
  JWT_EXPIRE_MINUTES=          # Minutos de expiración del JWT
  JWT_ALGORITHM=               # Algoritmo de cifrado JWT (ejemplo: HS256)

  TIME_ZONE=                   # Zona horaria del proyecto (ejemplo: America/Mexico_City)
  ```

4. **Inicia el servidor FastAPI:**
  ```bash
  uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
  ```

## Notas

- Asegúrate de tener configurados los servicios de AWS (DynamoDB, Cognito, SES, SMTP).
- No compartas tus credenciales en repositorios públicos.
- Modifica las variables según tu entorno y necesidades.
