from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IndexingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding="utf-8")

    # PostgreSQL / pgvector
    POSTGRES_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/fairness_toolkit_codebase",
        description="SQLAlchemy async-compatible connection string for pgvector.",
    )
    PGVECTOR_COLLECTION: str = "fairness_toolkit_codebase"

    # Embedding model
    EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384
    EMBEDDING_DEVICE: str = "cpu"

    # Chunking
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 76  # ~15 %

    # Download destination
    DOWNLOADS_DIR: Path = Path(__file__).parent / "downloads"

    # Fairness toolkits to index: name -> GitHub repo URL
    FAIRNESS_TOOLKITS: dict[str, str] = {
        "fairlearn": "https://github.com/fairlearn/fairlearn",
        "holisticai": "https://github.com/holistic-ai/holisticai",
    }

    # File extensions to index
    INDEXED_EXTENSIONS: tuple[str, ...] = (".py", ".md", ".rst")


settings = IndexingSettings()
