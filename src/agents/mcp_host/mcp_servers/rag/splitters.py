from langchain_text_splitters import RecursiveCharacterTextSplitter

Splitter = RecursiveCharacterTextSplitter


def get_splitter(chunk_size: int) -> Splitter:
    """Returns a token-based text splitter with overlap.

    Args:
        chunk_size: Number of tokens for each text chunk.

    Returns:
        Splitter: A configured text splitter instance that
            splits text into overlapping chunks based on token count.
    """

    chunk_overlap = int(0.15 * chunk_size)

    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )


def get_splitter_simple(chunk_size: int) -> Splitter:
    chunk_overlap = int(0.15 * chunk_size)
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
