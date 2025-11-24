import requests
import os
import zipfile
from io import BytesIO

def download_and_extract_repo(repo_url, extract_dir):
    """Download and extract the GitHub repository ZIP file."""
    if repo_url.endswith('/'):
        repo_url = repo_url[:-1]
    zip_url = f"{repo_url}/archive/refs/heads/main.zip"

    response = requests.get(zip_url)
    response.raise_for_status()

    with zipfile.ZipFile(BytesIO(response.content)) as z:
        z.extractall(extract_dir)

def get_py_files(repo_dir):
    """Get a list of Python files in the repository."""
    py_files = []
    for root, _, files in os.walk(repo_dir):
        for file in files:
            file_path = os.path.join(root, file)
            _, file_extension = os.path.splitext(file_path)
            if file_extension == '.py':
                py_files.append(file_path)
    return py_files

def write_files_to_text(py_files, output_file):
    """Write the paths and contents of non-binary files to a text file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        for file_path in py_files:
            print(f"Writing {file_path}")
            f.write(f"Path: {file_path}\n")
            f.write("Content:\n")
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                f.write(file.read())
            f.write("\n\n")
            
            
def query_vectorsote(vectorstore):
    query = """What were the trends in median household income across
            different states in the United States between 2021 and 2022."""  
    relevant_documents = vectorstore.similarity_search(query)
    print(f'There are {len(relevant_documents)} documents retrieved which are relevant to the query. Display the first one:\n')
    print(relevant_documents[0].page_content)