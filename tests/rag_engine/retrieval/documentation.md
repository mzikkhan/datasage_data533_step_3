# Retrieval Subpackage Documentation

## Overview

The `retrieval` subpackage is a core component of the RAG (Retrieval Augmented Generation) engine that handles document retrieval and answer generation using Large Language Models. It provides custom implementations built with Python's standard library to interact with Ollama, eliminating dependencies on LangChain and LlamaIndex.

## Architecture

The retrieval subpackage consists of three main modules:

```
rag_engine/retrieval/
├── data_models.py      # Shared data structures
├── generator.py        # LLM answer generation
├── retriever.py        # Document embedding and retrieval
└── README.md          # Module reference
```

## Components

### 1. Data Models (`data_models.py`)

#### `Document`
A lightweight data structure for storing document content and metadata.

**Attributes:**
- `page_content` (str): The main text content of the document
- `metadata` (dict): Additional information about the document (source, ID, etc.)

**Example:**
```python
from rag_engine.retrieval.data_models import Document

doc = Document(
    page_content="Python is a high-level programming language.",
    metadata={"source": "intro.pdf", "page": 1}
)
```

### 2. Generator (`generator.py`)

#### `Ollama` Class
Low-level client for communicating with the Ollama API.

**Methods:**
- `complete(prompt: str) -> str`: Sends a prompt and returns the generated response

**Example:**
```python
from rag_engine.retrieval.generator import Ollama

ollama = Ollama(model="llama3.1")
response = ollama.complete("What is Python?")
```

#### `LLMGenerator` Class
High-level interface for generating answers using retrieved context.

**Methods:**
- `generate_answer(question: str, context_docs: List[Document]) -> str`: Generates an answer based on the question and provided context documents

**Example:**
```python
from rag_engine.retrieval.generator import LLMGenerator
from rag_engine.retrieval.data_models import Document

generator = LLMGenerator(model="llama3.1")
docs = [
    Document(page_content="Python was created by Guido van Rossum.", metadata={}),
    Document(page_content="Python is known for its simplicity.", metadata={})
]
answer = generator.generate_answer("Who created Python?", docs)
```

**Additional Methods:**
- `summarize_docs(docs: List[Document]) -> str`: Generates a concise bullet-point summary from documents
- `evaluate_relevance(question: str, answer: str) -> str`: Evaluates and rates how well an answer addresses a question

**Example:**
```python
# Summarize documents
summary = generator.summarize_docs(docs)
print(summary)  # Returns bullet-point summary

# Evaluate answer quality
evaluation = generator.evaluate_relevance(
    question="Who created Python?",
    answer="Python was created by Guido van Rossum."
)
print(evaluation)  # Returns rating and explanation
```

### 3. Retriever (`retriever.py`)

#### `OllamaEmbedder` Class
Generates vector embeddings for text using Ollama's embedding API.

**Methods:**
- `embed_query(text: str) -> List[float]`: Embeds a single query string
- `embed_documents(texts: List[str]) -> List[List[float]]`: Embeds multiple documents

**Example:**
```python
from rag_engine.retrieval.retriever import OllamaEmbedder

embedder = OllamaEmbedder(model="nomic-embed-text")
query_embedding = embedder.embed_query("What is machine learning?")
doc_embeddings = embedder.embed_documents([
    "ML is a subset of AI",
    "Neural networks are used in ML"
])
```

#### `Retriever` Class
Retrieves relevant documents from a vector store based on semantic similarity.

**Methods:**
- `retrieve(query: str, k: int = 5, filter: dict = None) -> List[Document]`: Retrieves the top-k most relevant documents
- `retrieve_with_scores(query: str, k: int = 5) -> List[Tuple[Document, float]]`: Retrieves documents with their similarity scores
- `retrieve_by_source(query: str, source: str, k: int = 5) -> List[Document]`: Retrieves documents filtered by a specific source file

**Example:**
```python
from rag_engine.retrieval.retriever import Retriever, OllamaEmbedder
from rag_engine.indexing.vector_store import VectorStore
from rag_engine.indexing.embedder import Embedder

# Initialize components
embedder = Embedder(model_name="BAAI/bge-small-en-v1.5")
vs = VectorStore(embedding_model=embedder.model, persist_dir="./vector_db")

# Create retriever
retriever = Retriever(vector_store=vs, embedder=OllamaEmbedder())

# Retrieve documents
docs = retriever.retrieve("What is Python?", k=5)

# Retrieve with similarity scores
results = retriever.retrieve_with_scores("machine learning", k=3)
for doc, score in results:
    print(f"Score: {score:.4f} | {doc.page_content[:50]}...")

# Retrieve from specific source
source_docs = retriever.retrieve_by_source(
    query="neural networks",
    source="/path/to/ml_book.pdf",
    k=5
)
```

## Complete Workflow Example

```python
from rag_engine.retrieval.retriever import Retriever, OllamaEmbedder
from rag_engine.retrieval.generator import LLMGenerator
from rag_engine.indexing.vector_store import VectorStore
from rag_engine.indexing.embedder import Embedder

# 1. Setup vector store (assumes documents are already indexed)
embedder = Embedder(model_name="BAAI/bge-small-en-v1.5")
vs = VectorStore(embedding_model=embedder.model, persist_dir="./vector_db")

# 2. Initialize retriever and generator
retriever = Retriever(vector_store=vs, embedder=OllamaEmbedder())
generator = LLMGenerator(model="llama3.1")

# 3. RAG workflow
question = "What are the benefits of Python?"
context_docs = retriever.retrieve(question, k=5)
answer = generator.generate_answer(question, context_docs)

print(f"Q: {question}")
print(f"A: {answer}")
```
