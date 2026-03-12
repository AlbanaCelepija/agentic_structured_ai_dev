import os, pymongo, pprint
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv, find_dotenv

_ = load_dotenv(find_dotenv())

from rag.embeddings import get_embedding_model

MONGODB_URI = "mongodb://localhost:27017/?directConnection=true"
vector_store = None

def split_docs():    
    """
    Splits a PDF document into smaller documents.

    The documents are then returned.

    Returns:
        A list of documents.
    """
    # Load the PDF
    loader = PyPDFLoader("https://investors.mongodb.com/node/13176/pdf")
    data = loader.load()
    # Split PDF into documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=20)
    docs = text_splitter.split_documents(data)
    # Print the first document
    print(docs[0])
    return docs

def instantiate_vector_store(embedding, docs):
    # Instantiate the vector store using your MongoDB connection string
    vector_store = MongoDBAtlasVectorSearch.from_connection_string(
        connection_string = MONGODB_URI,
        namespace = "langchain_db.test",
        embedding = embedding,
        index_name = "vector_index"
    )
    # Add documents to the vector store
    vector_store.add_documents(documents=docs)
    # Use helper method to create the vector search index
    vector_store.create_vector_search_index(
    dimensions = 1024, # The number of vector dimensions to  index
    filters = [ "page_label" ]
    )
    return vector_store

def search(query):
    results = vector_store.similarity_search_with_score(
        query = query, k = 3
    )
    return results

def get_retriever():
    # Instantiate MongoDB Vector Search as a retriever
    retriever = vector_store.as_retriever(
        search_type = "similarity",
        search_kwargs = { "k": 10 }
    )
    return retriever

def run_chain(retriever):
    # Define a prompt template
    template = """
        Use the following pieces of context to answer the question at the end.
        {context}
        Question: {question}
    """
    prompt = PromptTemplate.from_template(template)
    model = ChatOpenAI(model="gpt-4o")
    # Construct a chain to answer questions on your data
    chain = (
    { "context": retriever, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
    )
    # Prompt the chain
    question = "What was MongoDB's latest acquisition?"
    answer = chain.invoke(question)
    print("Question: " + question)
    print("Answer: " + answer)
    

if __name__ == "__main__":
    embedding = get_embedding_model()
    docs = split_docs()
    vector_store = instantiate_vector_store(embedding, docs)
    retriever = get_retriever()
    run_chain(retriever)