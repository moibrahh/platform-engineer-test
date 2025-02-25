import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from my_service.config.config import settings
from my_service.models.models import HealthCheckResponse
from my_service.utils.logger import setup_logger
from my_service.api.v1.api import router

logger = setup_logger()
logger.debug(f"Running with config: {settings}")

def get_application():
    _app = FastAPI(title=settings.FASTAPI_PROJECT_NAME)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    # Include the router
    _app.include_router(router)
    
    return _app

app = get_application()

@app.get("/healthcheck")
async def healthcheck() -> HealthCheckResponse:
    logger.debug("healthcheck hit")
    return HealthCheckResponse(
        status_code=status.HTTP_200_OK,
        message="Server is running!"
    )

if __name__ == "__main__":
    uvicorn.run(
        "my_service.main:app",
        host="0.0.0.0",
        port=9000,
        reload=True
    )
