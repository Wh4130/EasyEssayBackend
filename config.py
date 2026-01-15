from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    model_config = SettingsConfigDict(env_file=".env")

Config = Settings()

broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL

