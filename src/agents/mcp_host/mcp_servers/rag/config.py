from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", extra="ignore", env_file_encoding="utf-8"
    )
    # --- MongoDB Configuration ---
    MONGO_URI: str = Field(
        default="mongodb://localhost:27017/?directConnection=true",
        description="Connection URI for the local MongoDB Atlas instance.",
    )
    MONGO_DB_NAME: str = "engineer_agents"
    MONGO_STATE_CHECKPOINT_COLLECTION: str = "engineer_state_checkpoints"
    MONGO_STATE_WRITES_COLLECTION: str = "engineer_state_writes"
    MONGO_LONG_TERM_MEMORY_COLLECTION: str = "engineer_long_term_memory"

    # --- Agents Configuration ---
    TOTAL_MESSAGES_SUMMARY_TRIGGER: int = 30
    TOTAL_MESSAGES_AFTER_SUMMARY: int = 5

    # --- RAG Configuration ---
    RAG_TEXT_EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    RAG_TEXT_EMBEDDING_MODEL_DIM: int = 384
    RAG_TOP_K: int = 3
    RAG_DEVICE: str = "cpu"
    RAG_CHUNK_SIZE: int = 256

    # --- Paths Configuration ---
    EVALUATION_DATASET_FILE_PATH: Path = Path("data/evaluation_dataset.json")
    EXTRACTION_METADATA_FILE_PATH: Path = Path("rag/resource_repo.json")


settings = Settings()
