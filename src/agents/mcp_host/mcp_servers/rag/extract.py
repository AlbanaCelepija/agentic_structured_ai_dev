import os
import io
import zipfile
import requests
from io import BytesIO
from langchain_community.document_loaders import (
    WebBaseLoader,
    DirectoryLoader,
    TextLoader,
)
from langchain_core.documents import Document
from rag.domain import Engineer
from tqdm import tqdm
from typing import Generator


def get_extraction_generator(
    engineers: list[Engineer],
) -> Generator[tuple[Engineer, list[Document]], None, None]:

    print(engineers)
    progress_bar = tqdm(
        engineers,
        desc="Extracting docs",
        unit="engineer",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}",
        ncols=100,
        position=0,
        leave=True,
    )
    for engineer in progress_bar:
        progress_bar.set_postfix_str(f"Engineer: {engineer.id}")
        engineer_docs = extract_codebase(engineer.urls, "downloads")
        #engineer_docs = extract_engineer_website(engineer, engineer.urls)

        yield (engineer.id, engineer_docs)


def extract_engineer_website(engineer: str, urls: list[str]) -> list[Document]:
    """Extract documents for a single toolkit documentation website.

    Args:
        engineer: Engineer object containing engineer information.
        urls: List of URLs to extract content from.

    Returns:
        list[Document]: List of documents extracted from the website for the engineer.
    """

    def extract_paragraphs_and_headers(soup) -> str:
        # Extract paragraphs and headers
        content = []
        for element in soup.find_all(["p", "h1", "h2", "h3", "h4", "h5", "h6"]):
            content.append(element.get_text())
        return "\n\n".join(content)

    if len(urls) == 0:
        return []

    loader = WebBaseLoader(show_progress=False)
    soups = loader.scrape_all(urls)

    documents = []
    for url, soup in zip(urls, soups):
        text = extract_paragraphs_and_headers(soup)
        metadata = {
            "source": url,
            "engineer": engineer,
        }

        documents.append(Document(page_content=text, metadata=metadata))

    return documents


def download_and_extract_repo(repo_url, target_dir, branch="main"):
    repo_name = repo_url.rstrip("/").split("/")[-1]
    zip_url = f"{repo_url}/archive/refs/heads/{branch}.zip"
    response = requests.get(zip_url)
    response.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(target_dir)
    print(f"Downloaded {repo_name} to {target_dir}")


def extract_codebase(repo_url_list: list[str], repo_folder: str) -> list[Document]:
    documents = []
    for url in repo_url_list:
        download_and_extract_repo(url, repo_folder)
        loader = DirectoryLoader(
            f"{repo_folder}/", glob="**/*.py", loader_cls=TextLoader
        )
        docs = loader.load()
        documents.extend(docs)
    return documents


if __name__ == "__main__":
    docs = extract_codebase(["https://github.com/evidentlyai/evidently"], "downloads")
    print(docs)
