from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str

    max_file_size: int = 1024*1024

    allowed_extensions: set[str] = {'.txt', '.json', ''}
settings = Settings()