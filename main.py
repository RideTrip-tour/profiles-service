import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.middlerware.request_context import user_context_middleware
from app.routes.admin_routes import router as admin_router
from app.routes.profiles_routes import router as user_router
from app.utils.logging import LOGGING_CONFIG
from config import settings

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Service is starting up...")
    yield
    logger.info("Service is shutting down...")


def create_app() -> FastAPI:
    app = FastAPI(
        docs_url=f"/api/{settings.app_name.split('-')[0]}/docs",
        redoc_url=f"/api/{settings.app_name.split('-')[0]}/redoc",
        openapi_url=f"/api/{settings.app_name.split('-')[0]}/openapi.json",
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.middleware("http")(user_context_middleware)

    @app.get(f"/{settings.app_name.split('-')[0]}/health")
    async def health_check():
        return {"status": "ok"}

    # Подключаем пользовательские роутеры
    app.include_router(user_router)

    # Подключаем администратоские роутеры
    app.include_router(admin_router)

    return app


app = create_app()
