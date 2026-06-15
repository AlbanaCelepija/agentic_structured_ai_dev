"""Download GitHub repos and load their source files as LangChain Documents."""

import zipfile
from io import BytesIO
from pathlib import Path

import requests
from langchain_core.documents import Document
from loguru import logger

from .config import settings


def _zip_url(repo_url: str) -> str:
    return repo_url.rstrip("/") + "/archive/refs/heads/main.zip"


def download_repo(toolkit_name: str, repo_url: str) -> Path:
    """Download and extract a GitHub repo ZIP under settings.DOWNLOADS_DIR.

    Re-uses an existing extraction directory so repeated runs skip the network call.
    Returns the path to the extracted root directory.
    """
    dest = settings.DOWNLOADS_DIR / toolkit_name
    if dest.exists():
        logger.info(f"[{toolkit_name}] Repo already extracted at {dest}, skipping download.")
        return dest

    dest.mkdir(parents=True, exist_ok=True)
    zip_url = _zip_url(repo_url)
    logger.info(f"[{toolkit_name}] Downloading {zip_url} …")

    response = requests.get(zip_url, timeout=120)
    response.raise_for_status()

    with zipfile.ZipFile(BytesIO(response.content)) as z:
        z.extractall(dest)

    logger.info(f"[{toolkit_name}] Extracted to {dest}")
    return dest


def _top_level_module(file_path: Path, repo_root: Path) -> str:
    """Return the top-level package name relative to the repo root."""
    try:
        rel = file_path.relative_to(repo_root)
        return rel.parts[0] if rel.parts else ""
    except ValueError:
        return ""


def load_repo_documents(toolkit_name: str, repo_root: Path) -> list[Document]:
    """Walk *repo_root* and return one Document per indexed file.

    Metadata attached to each document:
      - toolkit   : "fairlearn" | "holisticai"
      - file_path : POSIX path relative to repo root
      - file_type : ".py" | ".md" | ".rst"
      - module    : top-level directory / package name
    """
    docs: list[Document] = []
    extensions = set(settings.INDEXED_EXTENSIONS)

    for file_path in sorted(repo_root.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix not in extensions:
            continue
        # Skip hidden dirs, __pycache__, and test fixtures that are just data
        rel = file_path.relative_to(repo_root)
        if any(part.startswith(".") or part == "__pycache__" for part in rel.parts):
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            logger.warning(f"[{toolkit_name}] Could not read {file_path}, skipping.")
            continue

        if not content.strip():
            continue

        docs.append(
            Document(
                page_content=content,
                metadata={
                    "toolkit": toolkit_name,
                    "file_path": rel.as_posix(),
                    "file_type": file_path.suffix,
                    "module": _top_level_module(file_path, repo_root),
                },
            )
        )

    logger.info(f"[{toolkit_name}] Loaded {len(docs)} files from {repo_root}")
    return docs
