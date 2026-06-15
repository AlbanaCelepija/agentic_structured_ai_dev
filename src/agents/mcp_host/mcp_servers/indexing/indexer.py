"""Index fairness toolkit codebases into a pgvector collection.

Pipeline per toolkit:
  1. Download + extract repo (loaders.download_repo)
  2. Load all indexed files as Documents (loaders.load_repo_documents)
  3. Split into chunks with a Python-aware splitter
  4. Embed with HuggingFace model and upsert into pgvector (PGVector)

The resulting PGVector store is later reused by the MCP retriever tool.
"""

from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from loguru import logger

from .config import settings
from .loaders import download_repo, load_repo_documents


# ---------------------------------------------------------------------------
# Splitters – language-aware for Python, generic for docs
# ---------------------------------------------------------------------------

def _get_python_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )


def _get_markdown_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter.from_language(
        language=Language.MARKDOWN,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )


def _get_generic_splitter() -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )


_SPLITTER_BY_EXT = {
    ".py": _get_python_splitter,
    ".md": _get_markdown_splitter,
}


def split_documents(docs: list[Document]) -> list[Document]:
    """Split each Document with the appropriate language-aware splitter."""
    py_docs = [d for d in docs if d.metadata.get("file_type") == ".py"]
    md_docs = [d for d in docs if d.metadata.get("file_type") == ".md"]
    other_docs = [d for d in docs if d.metadata.get("file_type") not in (".py", ".md")]

    chunks: list[Document] = []
    if py_docs:
        chunks.extend(_get_python_splitter().split_documents(py_docs))
    if md_docs:
        chunks.extend(_get_markdown_splitter().split_documents(md_docs))
    if other_docs:
        chunks.extend(_get_generic_splitter().split_documents(other_docs))

    return chunks


# ---------------------------------------------------------------------------
# Embedding model
# ---------------------------------------------------------------------------

def get_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL_ID,
        model_kwargs={"device": settings.EMBEDDING_DEVICE, "trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": True},
    )


# ---------------------------------------------------------------------------
# PGVector store factory
# ---------------------------------------------------------------------------

def get_vectorstore(embeddings: HuggingFaceEmbeddings) -> PGVector:
    """Return a PGVector store backed by the configured Postgres instance.

    PGVector creates the table and pgvector extension automatically on first use.
    All toolkits share one collection; toolkit is stored in metadata for filtering.
    """
    return PGVector(
        embeddings=embeddings,
        collection_name=settings.PGVECTOR_COLLECTION,
        connection=settings.POSTGRES_URL,
        use_jsonb=True,
    )


# ---------------------------------------------------------------------------
# Main indexing pipeline
# ---------------------------------------------------------------------------

def index_toolkit(
    toolkit_name: str,
    repo_url: str,
    vectorstore: PGVector,
    batch_size: int = 64,
) -> None:
    """Download, chunk, and embed one toolkit's codebase into *vectorstore*."""
    logger.info(f"=== Indexing [{toolkit_name}] from {repo_url} ===")

    repo_root = download_repo(toolkit_name, repo_url)

    # GitHub archives extract into a sub-directory like "fairlearn-main/"
    subdirs = [p for p in repo_root.iterdir() if p.is_dir()]
    effective_root = subdirs[0] if len(subdirs) == 1 else repo_root

    raw_docs = load_repo_documents(toolkit_name, effective_root)
    chunks = split_documents(raw_docs)

    logger.info(f"[{toolkit_name}] {len(raw_docs)} files → {len(chunks)} chunks")

    # Batch upsert to avoid hitting Postgres parameter limits
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        vectorstore.add_documents(batch)
        logger.info(f"[{toolkit_name}] Upserted batch {i // batch_size + 1} ({len(batch)} chunks)")

    logger.info(f"[{toolkit_name}] Indexing complete.")


def run_indexing() -> PGVector:
    """Index all configured fairness toolkits and return the shared vectorstore."""
    embeddings = get_embedding_model()
    vectorstore = get_vectorstore(embeddings)

    for toolkit_name, repo_url in settings.FAIRNESS_TOOLKITS.items():
        index_toolkit(toolkit_name, repo_url, vectorstore)

    logger.info("All toolkits indexed successfully.")
    return vectorstore
