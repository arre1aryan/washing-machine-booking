from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    machine_service_url: str = "http://localhost:8001"
    auth_service_url: str = "http://localhost:8003"

    class Config:
        env_file = ".env"


settings = Settings()