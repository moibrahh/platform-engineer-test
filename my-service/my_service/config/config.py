from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pydantic import AnyHttpUrl


class Settings(BaseSettings):
    BACKEND_ORIGINS: List[AnyHttpUrl] = []
    FASTAPI_PROJECT_NAME: str = "ArgoCD Service"
    LOG_LEVEL: str = "DEBUG"

    # ArgoCD Config defaults
    ARGOCD_SERVER: str = "localhost"
    ARGOCD_PORT: str = "8080"  # ArgoCD is running on 8080
    ARGOCD_URL: str = f"{ARGOCD_SERVER}:{ARGOCD_PORT}"
    ARGOCD_PASSWORD: str = "zvBFWXRxbRAKVsW7%"
    ARGOCD_USERNAME: str = "admin"
    TOKEN_CACHE_TTL: int = 600

    # ArgoCD settings
    ARGOCD_API_URL: str = "https://localhost:8080"
    ARGOCD_AUTH_TOKEN: str = "zvBFWXRxbRAKVsW7%"

    model_config = SettingsConfigDict(env_nested_delimiter='__')


settings = Settings(_env_file=".env")
