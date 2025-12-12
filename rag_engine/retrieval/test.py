"""
Retrieval Subpackage Demo

This script demonstrates how to use the components of the `retrieval` subpackage.
"""

import sys
import os
from unittest.mock import MagicMock

# Add the project root to the python path so we can import rag_engine
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from rag_engine.retrieval.retriever import Retriever, OllamaEmbedder
from rag_engine.retrieval.generator import LLMGenerator
from rag_engine.retrieval.data_models import Document

def main():
    print("\nStarting Retrieval Subpackage Demo...\n")

    # 1. Setup Mock Vector Store
    # We mock the vector store to return sample documents without needing a real DB
    print("Initializing components (with mocked VectorStore)...")
    
    mock_vs = MagicMock()
    
    # Define some sample documents that our "database" contains
    sample_docs = [
        Document(
            page_content="Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the use of significant indentation.",
            metadata={"source": "python_wiki.txt", "topic": "programming"}
        ),
        Document(
            page_content="Python is dynamically typed and garbage-collected. It supports multiple programming paradigms, including structured, object-oriented and functional programming.",
            metadata={"source": "python_features.txt", "topic": "programming"}
        ),
        Document(
            page_content="Guido van Rossum began working on Python in the late 1980s as a successor to the ABC programming language and first released it in 1991 as Python 0.9.0.",
            metadata={"source": "history.txt", "topic": "history"}
        )
    ]
    
    # Mock the similarity search to return our sample docs
    # We need to return objects that have page_content and metadata attributes
    mock_vs.store.similarity_search_by_vector.return_value = sample_docs

    # 2. Initialize Components (with Mocks)
    # We mock the embedder to avoid needing a real Ollama instance for this demo
    embedder = MagicMock(spec=OllamaEmbedder)
    embedder.embed_query.return_value = [0.1, 0.2, 0.3] # Dummy embedding
    
    retriever = Retriever(vector_store=mock_vs, embedder=embedder)
    
    # We mock the generator to avoid needing a real Ollama instance
    generator = MagicMock(spec=LLMGenerator)
    generator.generate_answer.return_value = "Python is a high-level programming language created by Guido van Rossum."
    generator.summarize_docs.return_value = "- Python is high-level\n- Created by Guido van Rossum\n- Supports multiple paradigms"
    generator.evaluate_relevance.return_value = "Rating: 10/10\nExplanation: The answer accurately defines Python."

    # 3. Demonstrate Retrieval
    query = "What is Python?"
    print(f"\nRetrieving documents for query: '{query}'")
    
    # This will call embedder.embed_query 
    retrieved_docs = retriever.retrieve(query, k=2)
    
    print(f"Found {len(retrieved_docs)} documents:")
    for i, doc in enumerate(retrieved_docs, 1):
        print(f"{i}. {doc.page_content[:100]}... (Source: {doc.metadata['source']})")

    # 4. Demonstrate Generation (RAG)
    print(f"\nGenerating answer using retrieved context...")
    answer = generator.generate_answer(query, retrieved_docs)
    print(f"Answer: {answer}")

    # 5. Demonstrate Summarization
    print(f"\nSummarizing the retrieved documents...")
    summary = generator.summarize_docs(retrieved_docs)
    print(f"Summary:\n{summary}")

    # 6. Demonstrate Relevance Evaluation
    print(f"\nEvaluating answer relevance...")
    evaluation = generator.evaluate_relevance(query, answer)
    print(f"Evaluation:\n{evaluation}")

    print("\nDemo Complete!")

if __name__ == "__main__":
    main()
