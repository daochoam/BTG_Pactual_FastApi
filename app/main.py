# app/__init__.py
from fastapi import FastAPI
from app.routes.routes import main_routes
from app.config import Config
from app.dynamo_db import dynamo_db

def create_app() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI
    """
    app = FastAPI(
        title="BTG API",
        description="Documentación de la API de BTG Pactual",
        version="2.0.0",
        contact={
            "name": "Daniel Ochoa",
            "email": "dfom89@gmail.com",
        },
        license_info={
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT",
        },
        docs_url="/swagger",  # cambia la ruta de swagger (por defecto /docs)
        redoc_url="/redocs",  # cambia la ruta de redoc (por defecto /redoc)
    )



    # Guardar configuración global en app.state
    app.state.config = Config

    # Evento de startup para inicializar DynamoDB
    if Config.ENVIRONMENT_MODE == "development":
        @app.on_event("startup")
        async def startup_event():
            dynamo_db()  # Aquí inicializas tus tablas o conexiones

    @app.get("/")
    def read_root():
        return {"message": "Hola desde FastAPI BTG_Pactual"}

    # Registrar routers automáticamente
    for router in main_routes:
        app.include_router(router, prefix="/api")

    return app


# Crear instancia de la app para uvicorn
app = create_app()

