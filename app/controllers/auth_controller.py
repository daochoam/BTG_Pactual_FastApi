from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from app.config import Config, cognito_client
from app.documents.auth_models import LoginUserModel, RegisterUserModel
from app.utils.secret_hash import get_secret_hash

import app.schemas.users as users


def register_user(data: RegisterUserModel):

    if users.users_db.scan(
        FilterExpression="nit = :n OR email = :e",
        ExpressionAttributeValues={":n": data.nit, ":e": data.email}
    ).get("Items"):
        raise HTTPException(status_code=400, detail="NIT or Email already registered")

    try:
        response = cognito_client.sign_up(
            ClientId=Config.AWS_COGNITO_CLIENT_ID,
            Username=data.email,
            Password=data.password,
            SecretHash=get_secret_hash(data.email),
            UserAttributes=[
                {"Name": "name", "Value": data.name},
                {"Name": "family_name", "Value": data.last_name},
                {"Name": "email", "Value": data.email},
                {"Name": "phone_number", "Value": data.phone},
                {"Name": "custom:role", "Value": data.role or users.UserSchema.RoleEnum.USER},
            ]
        )
    except cognito_client.exceptions.UsernameExistsException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    user = users.UserSchema(
        nit=data.nit,
        name=data.name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        role=data.role or users.UserSchema.RoleEnum.USER,
        id=response["UserSub"]
    )
    users.users_db.put_item(Item=user.to_dict())

    return {
        "detail": "User registered successfully",
        "items": {"user_id": response["UserSub"]},
        "status": status.HTTP_201_CREATED
    }

def login_user(data: LoginUserModel):
    user_items = users.users_db.scan(FilterExpression="email = :e",ExpressionAttributeValues={":e": data.email}).get("Items")
    if not user_items:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not registered")

    user = user_items[0]
    if not user.get("verified", True):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not verified")

    try:
        response = cognito_client.initiate_auth(
            ClientId=Config.AWS_COGNITO_CLIENT_ID,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={
                "USERNAME": data.email,
                "PASSWORD": data.password,
                "SECRET_HASH": get_secret_hash(data.email)
            },
        )

        access_token = response["AuthenticationResult"]["AccessToken"]
        refresh_token = response["AuthenticationResult"]["RefreshToken"]

        user_info = cognito_client.get_user(AccessToken=access_token)
        attributes = {attr["Name"]: attr["Value"] for attr in user_info["UserAttributes"]}

        body = {
            "detail": "Login successful",
            "data": {
                "id": attributes.get("sub"),
                "role": attributes.get("custom:role"),
            }
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Refresh-Token": refresh_token
        }
        return JSONResponse(content=body, headers=headers, status_code=status.HTTP_200_OK)

    except cognito_client.exceptions.NotAuthorizedException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    except cognito_client.exceptions.UserNotConfirmedException:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not verified")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def logout_user(authorization: str, refresh_token: str):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing access token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    access_token = authorization.split(" ")[1]

    try:
        cognito_client.revoke_token(
            Token=refresh_token,
            ClientId=Config.AWS_COGNITO_CLIENT_ID,
            ClientSecret=Config.AWS_COGNITO_CLIENT_SECRET
        )
        
        body = {
            "detail": "Logout successful",
            "data": {},
        }
        
        return JSONResponse(content=body, status_code=status.HTTP_200_OK)
    except Exception as e:
        try:
            cognito_client.global_sign_out(AccessToken=access_token)
        except Exception:
            pass
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
