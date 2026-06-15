"""CLI entrypoint: python -m indexing.run [--toolkit fairlearn|holisticai]

Run from the mcp_servers/ directory:
    python -m indexing.run                    # index both toolkits
    python -m indexing.run --toolkit fairlearn # index only fairlearn
"""

import argparse

from loguru import logger

from .config import settings
from .indexer import get_embedding_model, get_vectorstore, index_toolkit


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Index fairness toolkit codebases into pgvector.")
    parser.add_argument(
        "--toolkit",
        choices=list(settings.FAIRNESS_TOOLKITS.keys()),
        default=None,
        help="Index a single toolkit. Omit to index all configured toolkits.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        help="Number of document chunks per Postgres upsert batch (default: 64).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    embeddings = get_embedding_model()
    vectorstore = get_vectorstore(embeddings)

    toolkits = (
        {args.toolkit: settings.FAIRNESS_TOOLKITS[args.toolkit]}
        if args.toolkit
        else settings.FAIRNESS_TOOLKITS
    )

    for name, url in toolkits.items():
        index_toolkit(name, url, vectorstore, batch_size=args.batch_size)

    logger.info("Done.")


if __name__ == "__main__":
    main()
