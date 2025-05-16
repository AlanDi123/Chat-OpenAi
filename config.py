from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    # DB
    SQLITE_URL: str = "sqlite:///./data/conversations.db"
    # OpenAI
    OPENAI_API_KEY: str
    MODEL: str = "gpt-4o-mini"
    TEMPERATURE: float = 0.7
    MAX_HISTORY: int = 20
    # Imágenes
    IMAGE_COUNT: int = 1
    IMAGE_SIZE: str = "1024x1024"
    # Uploads
    UPLOAD_FOLDER: str = "./uploads"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
