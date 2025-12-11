# Indexing Module Documentation

## Overview

The indexing module transforms documents into searchable vector representations. It consists of three components that work together to enable semantic search: **Embedder**, **VectorStore**, and **IndexingEngine**.

---

## Architecture

```
Document → IndexingEngine → [Validation] → [Loading] → [Chunking] → [Embedding] → VectorStore
                                                                          ↓
User Query → Embedder → Vector → VectorStore.search() → Ranked Results
```

---

## Components

### 1. Embedder (`embedder.py`)

Converts text into numerical vectors that capture semantic meaning.

#### `__init__(model_name: str = "all-MiniLM-L6-v2")`

Initializes the embedder with a HuggingFace model.

**Parameters:**

- `model_name`: HuggingFace model identifier

**Example:**

```python
embedder = Embedder(model_name="all-MiniLM-L6-v2")
```

---

#### `embed_query(text: str) -> List[float]`

Embeds a single text query into a vector.

**How it works:**

1. Preprocesses text (removes extra whitespace, strips edges)
2. Sends to HuggingFace model
3. Returns 384-dimensional vector

**Parameters:**

- `text`: Text to embed

**Returns:**

- List of 384 floating-point numbers

**Example:**

```python
embedding = embedder.embed_query("What is machine learning?")
# Returns: [-0.0165, 0.0456, ..., 0.0234]  (384 numbers)
```

**Custom Logic:**

- `_preprocess_text()`: Normalizes whitespace for consistent embeddings

---

#### `embed_documents(texts: List[str], show_progress: bool = False) -> List[List[float]]`

Embeds multiple texts in batch.

**How it works:**

1. Loops through each text
2. Calls `embed_query()` for each
3. Shows progress every 10 documents (if enabled)
4. Returns list of all embeddings

**Parameters:**

- `texts`: List of texts to embed
- `show_progress`: Display progress updates

**Returns:**

- List of embedding vectors

**Example:**

```python
texts = ["Doc 1", "Doc 2", "Doc 3"]
embeddings = embedder.embed_documents(texts, show_progress=True)
# Output: "Embedding progress: 3/3 documents"
#         "Batch complete: 3 documents embedded"
```

---

#### `get_embedding_dimension() -> int`

Returns the dimensionality of embeddings.

**Returns:**

- Integer (384 for all-MiniLM-L6-v2)

**Example:**

```python
dim = embedder.get_embedding_dimension()
print(dim)  # 384
```

---

### 2. VectorStore (`vector_store.py`)

Manages storage and retrieval of document embeddings using ChromaDB.

#### `__init__(embedding_model, persist_dir: str = None)`

Initializes the vector store.

**Parameters:**

- `embedding_model`: The embedding function from Embedder
- `persist_dir`: Directory for persistent storage (optional)

**Example:**

```python
vs = VectorStore(
    embedding_model=embedder.model,
    persist_dir="./my_db"
)
```

**Custom Tracking:**

- `_doc_count`: Total documents indexed
- `_metadata_index`: Maps doc_id → metadata (source, timestamp, length)
- `_source_index`: Maps source → list of doc_ids
- `_search_stats`: Tracks searches and popular sources

---

#### `add_documents(docs: List[Document]) -> List[str]`

Adds documents with automatic ID assignment and metadata tracking.

**How it works:**

1. Assigns unique ID (format: `doc_000001`, `doc_000002`, ...)
2. Extracts source from metadata (`path` or `source` field)
3. Records: source, timestamp, content length
4. Indexes documents by source
5. Adds custom metadata: `doc_id`, `indexed_at`
6. Stores in ChromaDB
7. Returns list of assigned IDs

**Parameters:**

- `docs`: List of Document objects

**Returns:**

- List of document IDs

**Example:**

```python
from langchain_core.documents import Document

docs = [
    Document(
        page_content="Python is a programming language",
        metadata={"path": "intro.txt", "type": "txt"}
    )
]

doc_ids = vs.add_documents(docs)
# Output: "Added 1 documents (IDs: doc_000000 to doc_000000)"
print(doc_ids)  # ['doc_000000']
```

**Custom Logic:**

- Sequential ID generation ensures uniqueness
- Timestamp tracking for provenance
- Source indexing enables fast filtering

---

#### `search(query: str, k: int = 5, filter: dict = None) -> List[Document]`

Searches for similar documents with analytics.

**How it works:**

1. Records query for analytics
2. Performs vector similarity search in ChromaDB
3. Adds ranking metadata to results:
   - `search_rank`: Position (1, 2, 3, ...)
   - `relevance_score`: Inverse rank (1.0, 0.5, 0.33, ...)
4. Updates source popularity statistics
5. Returns ranked documents

**Parameters:**

- `query`: Search query text
- `k`: Number of results
- `filter`: Optional metadata filter

**Returns:**

- List of Document objects with ranking metadata

**Example:**

```python
results = vs.search("machine learning", k=3)

for doc in results:
    rank = doc.metadata['search_rank']
    score = doc.metadata['relevance_score']
    print(f"Rank {rank} (score: {score}): {doc.page_content[:50]}")
```

**Custom Logic:**

- Tracks all queries for analytics
- Adds relevance scores to results
- Monitors which sources are frequently retrieved

---

#### `search_by_source(query: str, source: str, k: int = 5) -> List[Document]`

Searches within documents from a specific source.

**How it works:**

- Creates metadata filter for the source
- Calls `search()` with filter
- Returns only documents from that source

**Parameters:**

- `query`: Search query
- `source`: Source path to filter by
- `k`: Number of results

**Example:**

```python
results = vs.search_by_source("findings", source="report.pdf", k=3)
```

---

#### `get_sources() -> List[str]`

Returns all unique source paths in the vector store.

**Example:**

```python
sources = vs.get_sources()
print(sources)  # ['intro.txt', 'report.pdf', 'data.csv']
```

---

#### `get_document_count_by_source(source: str) -> int`

Returns number of documents from a source.

**Example:**

```python
count = vs.get_document_count_by_source("report.pdf")
print(f"{count} documents from report.pdf")
```

---

#### `get_statistics() -> Dict`

Returns comprehensive analytics about the vector store.

**Returns:**
Dictionary with:

- `total_documents`: Total indexed
- `unique_sources`: Number of unique sources
- `source_distribution`: Documents per source
- `total_searches`: Total queries performed
- `unique_queries`: Number of unique queries
- `avg_results_per_search`: Average results returned
- `top_searched_sources`: Most frequently retrieved sources
- `avg_document_length`: Average characters per document
- `persist_directory`: Storage location

**Example:**

```python
stats = vs.get_statistics()
print(f"Total documents: {stats['total_documents']}")
print(f"Total searches: {stats['total_searches']}")
```

---

#### `get_document_info(doc_id: str) -> Optional[Dict]`

Retrieves metadata for a specific document.

**Example:**

```python
info = vs.get_document_info("doc_000001")
print(f"Source: {info['source']}")
print(f"Indexed at: {info['timestamp']}")
```

---

#### `list_documents_by_source(source: str) -> List[str]`

Lists all document IDs from a source.

**Example:**

```python
doc_ids = vs.list_documents_by_source("report.pdf")
print(f"IDs: {doc_ids}")
```

---

### 3. IndexingEngine (`index_engine.py`)

Orchestrates the complete indexing pipeline with validation and tracking.

#### `__init__(persist_dir, embedding_model, chunk_size, overlap)`

Initializes the indexing engine.

**Parameters:**

- `persist_dir`: Vector database directory (default: "./datasage_store")
- `embedding_model`: HuggingFace model name (default: "all-MiniLM-L6-v2")
- `chunk_size`: Max characters per chunk (default: 1000)
- `overlap`: Overlapping characters (default: 200)

**Example:**

```python
indexer = IndexingEngine(
    persist_dir="./my_index",
    chunk_size=500,
    overlap=50
)
```

**Custom Tracking:**

- `_indexed_files`: Set of successfully indexed file paths
- `_failed_files`: Maps failed files to error messages
- `_indexing_history`: List of all operations with timestamps
- `_supported_extensions`: {'.pdf', '.csv', '.txt'}

---

#### `index(file_path, metadata=None, force_reindex=False, verbose=True) -> List[Document]`

Indexes a single file through the complete pipeline.

**How it works:**

1. **Validation**: Checks file existence, readability, type, size
2. **Duplicate Check**: Verifies if already indexed
3. **Loading**: Selects loader (PDFLoader/CSVLoader/TXTLoader) and loads
4. **Metadata**: Applies custom metadata to documents
5. **Chunking**: Splits into smaller chunks using TextChunker
6. **Embedding & Storage**: Embeds and stores in VectorStore
7. **Tracking**: Records operation with timestamp and duration

**Parameters:**

- `file_path`: Path to file
- `metadata`: Additional metadata to attach
- `force_reindex`: Re-index even if already processed
- `verbose`: Print progress messages

**Returns:**

- List of created document chunks

**Example:**

```python
chunks = indexer.index(
    "report.pdf",
    metadata={"department": "research"},
    verbose=True
)
# Output shows validation, loading, chunking, and storage steps
```

**Custom Logic:**

- Pre-flight validation prevents processing invalid files
- Duplicate detection saves time
- Complete history for auditing
- Detailed progress tracking

---

#### `batch_index(file_paths, metadata=None, continue_on_error=True, verbose=True) -> Dict`

Indexes multiple files with error recovery.

**How it works:**

1. Iterates through each file
2. Attempts to index each one
3. On error: logs failure and continues (if `continue_on_error=True`)
4. Returns dictionary mapping paths to chunks
5. Prints summary statistics

**Parameters:**

- `file_paths`: List of file paths
- `metadata`: Metadata for all files
- `continue_on_error`: Continue if a file fails
- `verbose`: Print progress

**Returns:**

- Dict mapping file paths to created chunks

**Example:**

```python
files = ["doc1.pdf", "doc2.csv", "doc3.txt"]
results = indexer.batch_index(files)

for file, chunks in results.items():
    print(f"{file}: {len(chunks)} chunks")
```

---

#### `search(query: str, k: int = 5, filter: dict = None) -> List[Document]`

Convenience method to search indexed documents.

**Example:**

```python
results = indexer.search("machine learning", k=3)
```

---

#### `get_indexed_files() -> List[str]`

Returns list of successfully indexed files.

**Example:**

```python
files = indexer.get_indexed_files()
print(f"Indexed: {files}")
```

---

#### `get_failed_files() -> Dict[str, str]`

Returns dictionary of failed files and their errors.

**Example:**

```python
failed = indexer.get_failed_files()
for file, error in failed.items():
    print(f"{file}: {error}")
```

---

#### `get_indexing_history() -> List[Dict]`

Returns complete history of indexing operations.

**Each entry contains:**

- `file_path`: File that was indexed
- `timestamp`: When operation started
- `status`: "success" or "failed"
- `duration_seconds`: How long it took
- `documents_loaded`: Number of documents loaded
- `chunks_created`: Number of chunks created
- `error`: Error message (if failed)

**Example:**

```python
history = indexer.get_indexing_history()
for entry in history:
    print(f"{entry['file_path']}: {entry['status']}")
```

---

#### `get_system_statistics() -> Dict`

Returns comprehensive system-wide statistics.

**Returns:**
Dictionary with:

- `indexing`: Files indexed, failed, total chunks, timing
- `configuration`: Chunk size, overlap, model info, dimension
- `vector_store`: All vector store statistics

**Example:**

```python
stats = indexer.get_system_statistics()
print(f"Files indexed: {stats['indexing']['files_indexed']}")
print(f"Total chunks: {stats['indexing']['total_chunks_created']}")
print(f"Model: {stats['configuration']['embedding_model']}")
```

---

#### `reset_history()`

Clears indexing history (keeps indexed files tracked).

**Example:**

```python
indexer.reset_history()
```

---

## Complete Usage Example

```python
from rag_engine.indexing.embedder import Embedder
from rag_engine.indexing.vector_store import VectorStore
from rag_engine.indexing.index_engine import IndexingEngine

# 1. Initialize
indexer = IndexingEngine(
    persist_dir="./my_database",
    chunk_size=500,
    overlap=50
)

# 2. Index documents
chunks = indexer.index("research_paper.pdf", verbose=True)
print(f"Indexed: {len(chunks)} chunks")

# 3. Search
results = indexer.search("neural networks", k=5)
for i, doc in enumerate(results, 1):
    rank = doc.metadata['search_rank']
    print(f"{i}. Rank {rank}: {doc.page_content[:80]}...")

# 4. Get statistics
stats = indexer.get_system_statistics()
print(f"Total documents: {stats['vector_store']['total_documents']}")
print(f"Total searches: {stats['vector_store']['total_searches']}")
```

---

## Integration with Ingestion Module

The indexing module works with the ingestion module's components:

**Loaders Used:**

- `PDFLoader`: Loads PDF files, combines all pages into one document
- `CSVLoader`: Loads CSV rows as individual documents
- `TXTLoader`: Loads text files as single documents

**Chunker Used:**

- `TextChunker.chunk_docs()`: Splits documents into smaller chunks with overlap

**Metadata Format:**
Documents from ingestion have:

- `path`: File path
- `name`: File name
- `type`: File type ("pdf", "csv", "txt")
- `row`: Row number (CSV only)

---

## Custom Logic Summary

### What Makes This OOP (Not Just Library Wrappers)

**Embedder:**

- Custom text preprocessing pipeline
- Batch progress tracking
- Dimension introspection

**VectorStore:**

- Automatic unique ID generation (doc_000001, doc_000002, ...)
- Metadata indexing by source for fast lookups
- Search analytics: tracks queries, popular sources
- Relevance scoring: adds rank and score to results
- Timestamp tracking: when each document was added

**IndexingEngine:**

- File validation: type, existence, size, permissions
- Duplicate detection: prevents re-indexing same file
- Automatic loader selection: chooses PDFLoader/CSVLoader/TXTLoader
- Complete operation history: timestamp, duration, status
- Batch processing: error recovery for multiple files
- Progress tracking: verbose output with step-by-step updates
- System-wide statistics: aggregates all component metrics

These features add significant value beyond the underlying libraries (LangChain, ChromaDB, HuggingFace), demonstrating real OOP design with:

- **State management**: Tracking indexed files, history, statistics
- **Business logic**: Validation, duplicate detection, error handling
- **Orchestration**: Coordinating multiple components
- **Analytics**: Monitoring usage patterns and performance

Update on Tests for Step 3:
- To run the tests, simply run run_coverage.py
- To run the coverage report for the tests, run the following code (requires Coverage.py) from the rag_engine/indexing folder:
```
coverage run --include="embedder.py,vector_store.py,index_engine.py" -m unittest discover -s . -p "test_*.py" -v
```
