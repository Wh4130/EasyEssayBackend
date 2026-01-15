from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

Config = Settings()

broker_url = Config.model_config.REDIS_URL
result_backend = Config.model_config.REDIS_URL

