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

4. **Configuración de AWS Lambda para actualizar el estado `verified`:**

Para automatizar la actualización del estado `verified` de los usuarios, puedes crear una función Lambda en AWS que se active mediante eventos (por ejemplo, desde Cognito, DynamoDB Streams o una API Gateway).

**Pasos básicos:**

- Crea una función Lambda en AWS Console.
- Asigna permisos necesarios para acceder a DynamoDB y Cognito.
- Implementa la lógica para actualizar el campo `verified` en la tabla DynamoDB del usuario correspondiente.
- Configura el trigger (por ejemplo, evento de confirmación de usuario en Cognito).
- Actualiza el código de Lambda para manejar el evento y modificar el estado en la base de datos `Users`.

**Código Lambda (Python):**
```python
import os
import boto3
from datetime import datetime
from zoneinfo import ZoneInfo

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ.get("DB_TABLE"))

def lambda_handler(event, context):
    email = event["request"]["userAttributes"].get("email")

    # Buscar item por email
    response = table.scan(
        FilterExpression="email = :e",
        ExpressionAttributeValues={":e": email}
    )
    
    if response["Items"]:
        user = response["Items"][0]
        user_id = user["id"]

        # Actualizar DynamoDB
        table.update_item(
            Key={"id": user_id},
            UpdateExpression="SET verified = :v, updated_at = :u",
            ExpressionAttributeValues={
                ":v": True,
                ":u": datetime.now(ZoneInfo(os.environ.get("TIME_ZONE", "UTC"))).isoformat()
            }
        )

    return event

```
5. **Inicia el servidor FastAPI:**
  ```bash
  uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
  ```

## Notas

- configura los servicios de AWS necesarios (DynamoDB, Cognito, SES, SMTP).
- No compartas tus credenciales en repositorios públicos.
- Modifica las variables según tu entorno y necesidades.

# Esquemas de Datos
### - Esquema de Usuario (`UserSchema`)

El esquema `UserSchema` define los atributos principales de un usuario en la base de datos DynamoDB. Incluye campos para la identificación, información personal, rol, fondos, moneda, estado de verificación y fechas relevantes.

| Atributo     | Descripción                                      |
|--------------|--------------------------------------------------|
| `id`         | Identificador único del usuario (cognito_id)           |
| `nit`        | Número de identificación tributaria              |
| `name`       | Nombre del usuario                               |
| `last_name`  | Apellido del usuario                             |
| `email`      | Correo electrónico                               |
| `phone`      | Teléfono de contacto                             |
| `role`       | Rol del usuario (`USER` o `ADMIN`)               |
| `amount`     | Monto de fondos asignados                        |
| `currency`   | Moneda de transacción asociada al usuario        |
| `verified`   | Estado de verificación de cuenta del usuario               |
| `created_at` | Fecha de creación del registro                   |
| `updated_at` | Fecha de última actualización                    |

### - Esquema de Categorías (`CategorySchema`)

El esquema `CategorySchema` representa una categoría almacenada en DynamoDB. Incluye campos para la identificación, nombre, descripción, usuarios relacionados y fechas de creación/actualización.

| Atributo        | Descripción                                      |
|-----------------|--------------------------------------------------|
| `id`            | Identificador único de la categoría (UUID)        |
| `name`          | Nombre de la categoría                            |
| `description`   | Descripción de la categoría                       |
| `user_created`  | Usuario que creó la categoría                     |
| `user_updated`  | Usuario que actualizó la categoría                |
| `created_at`    | Fecha de creación de la categoría                 |
| `updated_at`    | Fecha de última actualización                     |

### - Esquema de Fondos Bancarios (`BankFundsSchema`)

El esquema `BankFundsSchema` define los atributos principales de un fondo bancario almacenado en DynamoDB. Incluye campos para la identificación, nombre, categoría, monto mínimo, moneda, usuarios relacionados y fechas de creación/actualización.

| Atributo      | Descripción                                         |
|---------------|-----------------------------------------------------|
| `id`          | Identificador único del fondo bancario (UUID)       |
| `name`        | Nombre del fondo bancario                           |
| `category_id` | ID de la categoría asociada                         |
| `min_amount`  | Monto mínimo requerido para el fondo                |
| `currency`    | Moneda del fondo (`USD`, `EUR`, `GBP`, `JPY`, `COP`, `BRL`) |
| `user_created`| Usuario que creó el fondo bancario                  |
| `user_updated`| Usuario que actualizó el fondo bancario             |
| `created_at`  | Fecha de creación del fondo bancario                |
| `updated_at`  | Fecha de última actualización                       |

### - Esquema de Fondos Bancarios de Usuario (`UserBankFundsSchema`)

El esquema `UserBankFundsSchema` representa la relación entre un usuario y un fondo bancario en DynamoDB. Incluye campos para la identificación, usuario, fondo bancario, monto, moneda, estado, y fechas de creación/actualización.

| Atributo      | Descripción                                         |
|---------------|-----------------------------------------------------|
| `id`          | Identificador único de la relación (UUID)           |
| `user_id`     | ID del usuario asociado                             |
| `bank_funds_id` | ID del fondo bancario asociado                    |
| `amount`      | Monto asignado al usuario en el fondo               |
| `currency`    | Moneda del fondo (`USD`, `EUR`, `GBP`, `JPY`, `COP`, `BRL`) |
| `status`      | Estado de la relación (`OPEN`, `CLOSED`)            |
| `created_at`  | Fecha de creación de la relación                    |
| `updated_at`  | Fecha de última actualización                       |

### - Esquema de Auditoría de Fondos Bancarios de Usuario (`UserBankFundsAuditSchema`)

El esquema `UserBankFundsAuditSchema` extiende el esquema de fondos bancarios de usuario para registrar auditorías de cambios. Incluye campos para la identificación única de la auditoría, referencia al registro original, estado, monto, y fechas relevantes.

| Atributo    | Descripción                                         |
|-------------|-----------------------------------------------------|
| `id`        | Identificador único del registro de auditoría (UUID)|
| `parent_id` | ID de la relación original de fondo bancario de usuario |
| `user_id`   | ID del usuario asociado                             |
| `bank_funds_id` | ID del fondo bancario asociado                  |
| `amount`    | Monto asignado al usuario en el fondo               |
| `currency`  | Moneda del fondo (`USD`, `EUR`, `GBP`, `JPY`, `COP`, `BRL`) |
| `status`    | Estado de la relación (`OPEN`, `CLOSED`)            |
| `created_at`| Fecha de creación del registro de auditoría         |


# Rutas del proyecto

- Todos los endpoints requieren autenticación de usuario.
- El endpoint de creación (`/category` y `/bank-funds`) requieren autenticación de administrador.
- Los registros de auditoría permiten consultar el historial de acciones sobre fondos bancarios asociados a usuarios.

### Rutas de Autenticación

| Método | Endpoint           | Descripción                | Body/Headers                       |
|--------|--------------------|----------------------------|------------------------------------|
| POST   | `/auth/register`   | Registro de usuario        | Body: `RegisterUserModel`          |
| POST   | `/auth/login`      | Inicio de sesión           | Body: `LoginUserModel`             |
| POST   | `/auth/logout`     | Cierre de sesión           | Headers: `Authorization`, `X-Refresh-Token` |

**Modelos:**
- `RegisterUserModel`: Datos requeridos para registrar un usuario.
- `LoginUserModel`: Credenciales para iniciar sesión.

**Notas:**
- El endpoint `/auth/logout` requiere los headers `Authorization` y `X-Refresh-Token`.
- Todos los endpoints responden en formato JSON.

### Rutas de Categorías

| Método | Endpoint             | Descripción                        | Body/Headers                       |
|--------|----------------------|------------------------------------|------------------------------------|
| POST   | `/category/`         | Crear una categoría                | Body: `CreateCategoryModel`, Headers: `Authorization` (admin) |
| GET    | `/category/`         | Obtener todas las categorías       | Ninguno                            |
| GET    | `/category/{id}`     | Obtener una categoría por ID       | Path: `id`                         |

**Modelos:**
- `CreateCategoryModel`: Datos requeridos para crear una categoría.
- `UpdateCategoryModel`: Datos para actualizar una categoría.


### Rutas de Fondos Bancarios

| Método | Endpoint                    | Descripción                        | Body/Headers                       |
|--------|-----------------------------|------------------------------------|------------------------------------|
| POST   | `/bank-funds/`              | Crear un fondo bancario            | Body: `CreateBankFundsModel`, Headers: `Authorization` (admin) |
| GET    | `/bank-funds/`              | Obtener todos los fondos bancarios | Ninguno                            |
| GET    | `/bank-funds/{bank_funds_id}` | Obtener fondo bancario por ID      | Path: `bank_funds_id`              |
| PUT    | `/bank-funds/{bank_funds_id}` | Actualizar fondo bancario          | Path: `bank_funds_id`, Body: `UpdateBankFundsModel`, Headers: `Authorization` (admin) |

**Modelos:**
- `CreateBankFundsModel`: Datos requeridos para crear un fondo bancario.
- `UpdateBankFundsModel`: Datos para actualizar un fondo bancario.


### Rutas de Fondos Bancarios de Usuario

| Método | Endpoint                               | Descripción                                         | Body/Headers                       |
|--------|----------------------------------------|-----------------------------------------------------|------------------------------------|
| POST   | `/user-bank-funds/{bank_funds_id}`     | Asociar un fondo bancario a un usuario              | Path: `bank_funds_id`, Headers: `Authorization` |
| GET    | `/user-bank-funds/`                    | Obtener todos los fondos bancarios de un usuario     | Headers: `Authorization`           |
| GET    | `/user-bank-funds/{id}`                | Obtener un fondo bancario de usuario por ID          | Path: `id`, Headers: `Authorization` |
| DELETE | `/user-bank-funds/{user_bank_funds_id}`| Eliminar un fondo bancario asociado a un usuario     | Path: `user_bank_funds_id`, Headers: `Authorization` |

### Rutas de Auditoría de Fondos Bancarios de Usuario

| Método | Endpoint                                         | Descripción                                              | Body/Headers             |
|--------|--------------------------------------------------|----------------------------------------------------------|--------------------------|
| GET    | `/user-bank-funds-audit/`                        | Obtener todos los registros de auditoría de fondos bancarios por usuario | Headers: `Authorization` |
| GET    | `/user-bank-funds-audit/{user_bank_funds_audit_id}` | Obtener un registro de auditoría por ID                  | Path: `user_bank_funds_audit_id`, Headers: `Authorization` |

### Rutas de Usuarios

| Método | Endpoint         | Descripción                                                                 | Body/Headers                       |
|--------|------------------|-----------------------------------------------------------------------------|------------------------------------|
| GET    | `/users/`        | Obtener todos los usuarios (solo ADMIN) o solo el usuario autenticado        | Headers: `Authorization`           |

**Notas:**
- El endpoint `/users` devuelve todos los usuarios si el rol es ADMIN, de lo contrario solo la información del usuario autenticado.
- Requiere autenticación mediante el header `Authorization`.

