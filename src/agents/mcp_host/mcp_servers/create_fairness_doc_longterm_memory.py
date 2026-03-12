from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from rag.extract import get_extraction_generator
from rag.domain import Engineer, EngineerExtract
from rag.embeddings import get_embedding_model
from rag.retrievers import Retriever, get_retriever
from rag.splitters import Splitter, get_splitter, get_splitter_simple
from rag.mongo.client import MongoClientWrapper
from rag.mongo.indexes import MongoIndex
from rag.config import settings

   
class LongTermMemoryCreator:
    def __init__(self, retriever: Retriever, splitter: Splitter) -> None:
        self.retriever = retriever
        self.splitter = splitter

    @classmethod
    def build_from_settings(cls) -> "LongTermMemoryCreator":
        retriever = get_retriever(
            embedding_model_id=settings.RAG_TEXT_EMBEDDING_MODEL_ID,
            k=settings.RAG_TOP_K,
            device=settings.RAG_DEVICE,
        )
        splitter = get_splitter(chunk_size=settings.RAG_CHUNK_SIZE)

        return cls(retriever, splitter)

    def __call__(self, engineers) -> None:
        if len(engineers) == 0:
            logger.warning("No engineers to extract. Exiting.")

            return

        # First clear the long term memory collection to avoid duplicates.
        with MongoClientWrapper(
            model=Document, collection_name=settings.MONGO_LONG_TERM_MEMORY_COLLECTION
        ) as client:
            client.clear_collection()

        extraction_generator = get_extraction_generator(engineers)
        for _, docs in extraction_generator:
            chunked_docs = self.splitter.split_documents(docs)
            print(chunked_docs)
            self.retriever.vectorstore.add_documents(chunked_docs)

        self.__create_index()

    def __create_index(self) -> None:
        with MongoClientWrapper(
            model=Document, collection_name=settings.MONGO_LONG_TERM_MEMORY_COLLECTION
        ) as client:
            self.index = MongoIndex(
                retriever=self.retriever,
                mongodb_client=client,
            )
            self.index.create(
                is_hybrid=True, embedding_dim=settings.RAG_TEXT_EMBEDDING_MODEL_DIM
            )

def create_longterm_memory_mongo():
    engineers = EngineerExtract.from_json(settings.EXTRACTION_METADATA_FILE_PATH)
    long_term_memory_creator = LongTermMemoryCreator.build_from_settings()
    long_term_memory_creator(engineers)
    
def create_longterm_memory_simple():
    engineers = EngineerExtract.from_json(settings.EXTRACTION_METADATA_FILE_PATH)
    splitter = get_splitter_simple(chunk_size=settings.RAG_CHUNK_SIZE)
    embeddings = get_embedding_model()
    extraction_generator = get_extraction_generator(engineers)
    for engineer, docs in extraction_generator:
        chunked_docs = splitter.split_documents(docs)
        print(engineer)
        vectordb = FAISS.from_documents(chunked_docs, embeddings)
        vectordb.save_local(f"vectorstore_{engineer}.db")
    
if __name__ == "__main__":    
    create_longterm_memory_simple() 
