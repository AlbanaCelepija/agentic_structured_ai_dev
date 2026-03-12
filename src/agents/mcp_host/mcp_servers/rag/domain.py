import json
from pathlib import Path
from typing import List
from pydantic import BaseModel, Field


class Engineer(BaseModel):
    name: str = Field(description="Name of the toolkit")
    requirement: str = Field(
        description="Requirement dimension to be met by the toolkit"
    )

    def __str__(self) -> str:
        return f"Engineer(name={self.name}, requirement={self.requirement})"


class EngineerExtract(BaseModel):
    id: str = Field(description="Unique identifier for the engineer")
    urls: List[str] = Field(
        description="List of URLs with information about the engineer"
    )

    @classmethod
    def from_json(cls, metadata_file: Path) -> list["EngineerExtract"]:
        with open(metadata_file, "r") as f:
            engineers_data = json.load(f)

        return [cls(**engineer) for engineer in engineers_data]
