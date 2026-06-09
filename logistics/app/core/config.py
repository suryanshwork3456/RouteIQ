from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/logistics_db"
    SYNC_DATABASE_URL: str = "postgresql+psycopg2://user:password@localhost:5432/logistics_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    SECRET_KEY: str = "change-this-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # External APIs
    OSRM_BASE_URL: str = "http://router.project-osrm.org"
    GOOGLE_MAPS_API_KEY: str = ""

    # Assignment Engine
    ASSIGNMENT_INTERVAL_SECONDS: int = 30
    MAX_BATCH_SIZE: int = 4
    MAX_BATCH_RADIUS_KM: float = 1.5

    # Efficiency Score Weights (must sum to 1.0)
    WEIGHT_DISTANCE: float = 0.40
    WEIGHT_BATCH: float = 0.30
    WEIGHT_RATING: float = 0.20
    WEIGHT_BUSYNESS: float = 0.10

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
