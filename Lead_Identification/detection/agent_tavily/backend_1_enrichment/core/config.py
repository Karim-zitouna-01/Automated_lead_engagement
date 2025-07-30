from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Manages application settings using Pydantic.
    Loads variables from a .env file.
    """
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8', 
        extra='ignore'
    )

    GEMINI_API_KEY: str
    TAVILY_API_KEY: str
    PORT: int = 8002

# Create a single, reusable instance of the settings
settings = Settings()
