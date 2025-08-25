from app.routes.auth_routes import auth_routes
from app.routes.bank_funds_routes import bank_funds_routes
from app.routes.category_routes import category_routes
from app.routes.user_bank_funds_routes import user_bank_funds_routes
from app.routes.user_bank_funds_audit_routes import user_bank_funds_audit_routes
from app.routes.user_routes import users_routes

# Lista de routers para incluir en FastAPI
main_routes = [
    auth_routes,
    bank_funds_routes,
    category_routes,
    user_bank_funds_routes,
    user_bank_funds_audit_routes,
    users_routes
]
