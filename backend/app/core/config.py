from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Tecport Lead Intelligence"
    app_env: str = "development"
    secret_key: str = "change-me-in-.env"

    frontend_url: str = "http://localhost:5173"
    backend_url: str = "http://localhost:8000"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    database_url: str = "sqlite:///./dev.db"

    playwright_headless: bool = True
    max_results_per_search: int = 20
    max_pages_per_search: int = 50
    max_concurrent_requests: int = 3
    request_timeout_seconds: int = 30

    access_token_expire_minutes: int = 1440
    export_directory: str = "./exports"


settings = Settings()
