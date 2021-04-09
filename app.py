"""
Most top-level instanciator and runner. Main point of entry for the server code.
"""
import logging.config
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi_route_logger_middleware import RouteLoggerMiddleware
from config.db import close_connection_to_mongo, _is_testing
from config.main import app
from routes.users import router as users_router
from routes.events import router as events_router
from routes.feedback import router as feedback_router
from routes.admin import router as admin_router
from routes.images import router as images_router
from routes.auth import router as auth_router


@app.get("/")
def index():
    return {"Hello": "World"}


origins = [
    "https://localhost",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:8081",
    "https://sparkdevteams.github.io",
    "https://sparkdevteams.github.io/underline-frontend",
    "https://github.io",
    "https://sparkdev-underline.herokuapp.com",
]

ALLOWED_HOSTS = [
    "https://sparkdev-underline.herokuapp.com",
    "https://sparkdevteams.github.io",
    "https://sparkdevteams.github.io/underline-frontend",
    "https://github.io",
    "http://localhost:80800",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost",
    "http://localhost",
    "localhost",
    "http://localtest.me:80800",
    "http://localtest.me",
    "http://localtest.me",
    "localtest.me",
]

ALLOWED_HEADERS = ["*", "x-requested-with"]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=ALLOWED_HEADERS)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS if not _is_testing() else ["*"],
)

logging.config.fileConfig("./logging.conf")
app.add_middleware(RouteLoggerMiddleware)


def custom_schema():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Underline x Sparkdev API",
        version="v.1.0",
        description="Backend API for 2021 Spring FUTxSparkdev project",
        routes=app.routes)
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.include_router(users_router)
app.include_router(events_router)
app.include_router(feedback_router)
app.include_router(admin_router)
app.include_router(images_router)
app.include_router(auth_router)

app.add_event_handler("shutdown", close_connection_to_mongo)

app.openapi = custom_schema
