from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://diligence:diligence@localhost:5432/diligence"
    temporal_address: str = "localhost:7233"
    temporal_task_queue: str = "diligence-task-queue"
    upload_dir: str = "uploads"
    use_temporal: bool = False
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None


settings = Settings()