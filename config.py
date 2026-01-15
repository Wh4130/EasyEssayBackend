from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra = "ignore")

Config = Settings()

broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL

