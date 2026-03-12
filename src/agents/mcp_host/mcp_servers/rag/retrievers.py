from langchain_community.vectorstores import FAISS
from rag.embeddings import get_embedding_model, get_embeddings_mini

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_mongodb.retrievers import (
    MongoDBAtlasHybridSearchRetriever,
)

Retriever = MongoDBAtlasHybridSearchRetriever

from rag.config import settings


def get_retriever(
    embedding_model_id: str,
    k: int = 3,
    device: str = "cpu",
) -> Retriever:
    """Creates and returns a hybrid search retriever with the specified embedding model.

    Args:
        embedding_model_id (str): The identifier for the embedding model to use.
        k (int, optional): Number of documents to retrieve. Defaults to 3.
        device (str, optional): Device to run the embedding model on. Defaults to "cpu".

    Returns:
        Retriever: A configured hybrid search retriever.
    """

    embedding_model = get_embedding_model()

    return get_hybrid_search_retriever(embedding_model, k)


def get_hybrid_search_retriever(
    embedding_model: HuggingFaceEmbeddings, k: int
) -> MongoDBAtlasHybridSearchRetriever:
    """Creates a MongoDB Atlas hybrid search retriever with the given embedding model.

    Args:
        embedding_model (HuggingFaceEmbeddings): The embedding model to use for vector search.
        k (int): Number of documents to retrieve.

    Returns:
        MongoDBAtlasHybridSearchRetriever: A configured hybrid search retriever using both
            vector and text search capabilities.
    """
    vectorstore = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string=settings.MONGO_URI,
        embedding=embedding_model,
        namespace=f"{settings.MONGO_DB_NAME}.{settings.MONGO_LONG_TERM_MEMORY_COLLECTION}",
        text_key="chunk",
        embedding_key="embedding",
        relevance_score_fn="dotProduct",
    )

    retriever = MongoDBAtlasHybridSearchRetriever(
        vectorstore=vectorstore,
        search_index_name="hybrid_search_index",
        top_k=k,
        vector_penalty=50,
        fulltext_penalty=50,
    )

    return retriever


def get_mongo_retriever():
    client = MongoClient("mongodb://localhost:27017")
    db = client["long_term_memory"]
    collection = db["memory_vectors"]
    embeddings = get_embedding_model()

    # Vector store
    vectorstore = MongoDBVectorSearch(
        collection=collection, embedding=embeddings, index_name="vector_index"
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    return retriever


def load_faiss_retriever(engineer: str):
    embeddings = get_embedding_model()
    vectorstore = FAISS.load_local(
        f"vectorstore_{engineer}.db", embeddings, allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 4})
    return retriever
