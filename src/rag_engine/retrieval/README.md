# Retrieval Subpackage - Function Details

## Authored by: Zaed Khan

## Overview

The `retrieval` subpackage provides the core functionality for retrieving relevant documents and generating answers using language models. It implements custom solutions using Python's standard library to interact with Ollama, replacing external dependencies on LangChain and LlamaIndex.

## Modules

### `generator.py`
Contains classes for generating answers using the Ollama LLM API.

### `retriever.py`
Contains classes for embedding text and retrieving relevant documents from a vector store.

### `data_models.py`
Defines shared data models used across the retrieval subpackage.

---

## Detailed Function Reference

## `data_models.py`

### `Document`

A lightweight data structure for storing document content and associated metadata.

#### `__init__(page_content: str, metadata: Dict[str, Any] = None)`

**Purpose:** Initializes a new Document instance.

**Parameters:**
- `page_content` (str): The main text content of the document
- `metadata` (Dict[str, Any], optional): Dictionary containing additional information about the document (e.g., source, page number, author). Defaults to empty dict if not provided.

**How it works:**
1. Stores the provided `page_content` as an instance attribute
2. If `metadata` is None, initializes it as an empty dictionary
3. Otherwise, stores the provided metadata dictionary

**Example:**
```python
doc = Document(
    page_content="Python is a programming language.",
    metadata={"source": "intro.pdf", "page": 1}
)
```

#### `__repr__() -> str`

**Purpose:** Returns a string representation of the Document for debugging and logging.

**How it works:**
1. Truncates `page_content` to first 50 characters for readability
2. Includes the full metadata dictionary
3. Formats as: `Document(page_content='<first 50 chars>...', metadata=<metadata>)`

**Returns:** String representation of the document

---

## `generator.py`

### `Ollama`

A low-level HTTP client for communicating with the Ollama API to generate text completions.

#### `__init__(model: str, base_url: str = "http://localhost:11434")`

**Purpose:** Initializes the Ollama client with model configuration.

**Parameters:**
- `model` (str): Name of the Ollama model to use (e.g., "llama3.1", "mistral")
- `base_url` (str, optional): Base URL of the Ollama server. Defaults to local instance.

**How it works:**
1. Stores the model name for use in API requests
2. Stores the base URL for constructing API endpoints

**Example:**
```python
ollama = Ollama(model="llama3.1", base_url="http://localhost:11434")
```

#### `complete(prompt: str) -> str`

**Purpose:** Sends a prompt to Ollama and retrieves the generated text response.

**Parameters:**
- `prompt` (str): The text prompt to send to the language model

**Returns:** Generated text response from the model

**How it works:**
1. Constructs the API endpoint URL: `{base_url}/api/generate`
2. Creates a JSON payload with:
   - `model`: The model name
   - `prompt`: The input text
   - `stream`: Set to False for synchronous response
3. Encodes the payload as UTF-8 JSON
4. Creates an HTTP POST request with:
   - URL: The API endpoint
   - Data: Encoded JSON payload
   - Headers: `Content-Type: application/json`
5. Sends the request using `urllib.request.urlopen()`
6. Checks response status (raises exception if not 200)
7. Parses the JSON response and extracts the `"response"` field
8. Returns the generated text

**Error Handling:**
- Raises exception if HTTP status is not 200
- Catches `URLError` and re-raises with descriptive message if Ollama is unreachable

**Example:**
```python
response = ollama.complete("What is Python?")
# Returns: "Python is a high-level programming language..."
```

---

### `LLMGenerator`

High-level interface for generating context-aware answers using retrieved documents.

#### `__init__(model: str = "llama3.1")`

**Purpose:** Initializes the LLM generator with an Ollama client.

**Parameters:**
- `model` (str, optional): Name of the Ollama model to use. Defaults to "llama3.1"

**How it works:**
1. Creates an internal `Ollama` instance with the specified model
2. Stores it as `self.llm` for use in answer generation

**Example:**
```python
generator = LLMGenerator(model="llama3.1")
```

#### `generate_answer(question: str, context_docs: List[Document]) -> str`

**Purpose:** Generates an answer to a question using provided context documents.

**Parameters:**
- `question` (str): The question to answer
- `context_docs` (List[Document]): List of relevant documents to use as context

**Returns:** Generated answer as a string

**How it works:**
1. **Context Formatting:**
   - Iterates through each document in `context_docs`
   - For each document, formats as: `Source: {metadata}\nContent: {page_content}`
   - Joins all formatted documents with double newlines
2. **Prompt Construction:**
   - Creates a structured prompt:
     ```
     Use the following context to answer the question:
     
     {context_str}
     
     Question: {question}
     Answer:
     ```
3. **Generation:**
   - Sends the complete prompt to `self.llm.complete()`
   - Receives and returns the generated answer

**Example:**
```python
docs = [
    Document(page_content="Python was created in 1991.", metadata={"source": "wiki"}),
    Document(page_content="Python is interpreted.", metadata={"source": "docs"})
]
answer = generator.generate_answer("When was Python created?", docs)
# Returns: "Python was created in 1991."
```

#### `summarize_docs(docs: List[Document]) -> str`

**Purpose:** Generates a bullet-point summary from a list of documents.

**Parameters:**
- `docs` (List[Document]): List of documents to summarize

**Returns:** Generated summary as a string

**How it works:**
1. **Context Extraction:**
   - Iterates through each document in `docs`
   - Extracts only the `page_content` from each document
   - Joins all content with double newlines
2. **Prompt Construction:**
   - Creates a summarization prompt:
     ```
     Summarize the following text in concise bullet points:
     
     {context_str}
     
     Summary:
     ```
3. **Generation:**
   - Sends the prompt to `self.llm.complete()`
   - Returns the generated summary

**Example:**
```python
docs = [
    Document(page_content="Python is versatile.", metadata={}),
    Document(page_content="Python has extensive libraries.", metadata={})
]
summary = generator.summarize_docs(docs)
# Returns: "- Python is a versatile language\n- It has extensive libraries"
```

#### `evaluate_relevance(question: str, answer: str) -> str`

**Purpose:** Asks the LLM to rate the relevance of an answer to a question.

**Parameters:**
- `question` (str): The original question
- `answer` (str): The answer to evaluate

**Returns:** Evaluation and rating as a string

**How it works:**
1. **Prompt Construction:**
   - Creates an evaluation prompt:
     ```
     Question: {question}
     Answer: {answer}
     
     Rate the relevance of the answer to the question on a scale of 1 to 10.
     Provide a brief explanation for your rating.
     ```
2. **Generation:**
   - Sends the prompt to `self.llm.complete()`
   - Returns the LLM's evaluation

**Example:**
```python
evaluation = generator.evaluate_relevance(
    question="What is Python?",
    answer="Python is a high-level programming language."
)
# Returns: "Rating: 10\nExplanation: The answer directly..."
```

---

## `retriever.py`

### `OllamaEmbedder`

Generates vector embeddings for text using Ollama's embedding models.

#### `__init__(model: str = "nomic-embed-text", base_url: str = "http://localhost:11434")`

**Purpose:** Initializes the embedder with model configuration.

**Parameters:**
- `model` (str, optional): Name of the embedding model. Defaults to "nomic-embed-text"
- `base_url` (str, optional): Base URL of the Ollama server. Defaults to local instance.

**How it works:**
1. Stores the embedding model name
2. Stores the base URL for API requests

**Example:**
```python
embedder = OllamaEmbedder(model="nomic-embed-text")
```

#### `_get_embedding(text: str) -> List[float]`

**Purpose:** Internal method to generate a single embedding vector for text.

**Parameters:**
- `text` (str): The text to embed

**Returns:** List of float values representing the embedding vector

**How it works:**
1. Constructs API endpoint: `{base_url}/api/embeddings`
2. Creates JSON payload:
   - `model`: The embedding model name
   - `prompt`: The input text to embed
3. Encodes payload as UTF-8 JSON
4. Creates HTTP POST request with appropriate headers
5. Sends request using `urllib.request.urlopen()`
6. Checks response status (raises exception if not 200)
7. Parses JSON response and extracts the `"embedding"` field
8. Returns the embedding vector as a list of floats

**Error Handling:**
- Raises exception if HTTP status is not 200
- Catches `URLError` and re-raises with descriptive message

**Note:** This is a private method (prefixed with `_`) used internally by public methods.

#### `embed_query(text: str) -> List[float]`

**Purpose:** Embeds a single query string for semantic search.

**Parameters:**
- `text` (str): The query text to embed

**Returns:** Embedding vector as a list of floats

**How it works:**
1. Calls `_get_embedding(text)` internally
2. Returns the resulting embedding vector

**Example:**
```python
query_vector = embedder.embed_query("What is machine learning?")
# Returns: [0.123, -0.456, 0.789, ...]  (typically 384 or 768 dimensions)
```

#### `embed_documents(texts: List[str]) -> List[List[float]]`

**Purpose:** Embeds multiple documents for indexing or batch processing.

**Parameters:**
- `texts` (List[str]): List of document texts to embed

**Returns:** List of embedding vectors, one for each input text

**How it works:**
1. Iterates through each text in the input list
2. Calls `_get_embedding(text)` for each one
3. Collects all embeddings in a list
4. Returns the list of embedding vectors

**Note:** This method makes sequential API calls. For large batches, this may be slow.

**Example:**
```python
docs = ["Document 1 text", "Document 2 text", "Document 3 text"]
doc_vectors = embedder.embed_documents(docs)
# Returns: [[0.1, 0.2, ...], [0.3, 0.4, ...], [0.5, 0.6, ...]]
```

---

### `Retriever`

Retrieves semantically relevant documents from a vector store using embedding-based search.

#### `__init__(vector_store: VectorStore, embedder: OllamaEmbedder)`

**Purpose:** Initializes the retriever with necessary components.

**Parameters:**
- `vector_store` (VectorStore): The vector database containing indexed documents
- `embedder` (OllamaEmbedder): The embedder to use for query embedding

**How it works:**
1. Stores reference to the vector store as `self.vs`
2. Stores reference to the embedder as `self.embedder`
3. Both are used in the `retrieve()` method

**Example:**
```python
retriever = Retriever(vector_store=vs, embedder=embedder)
```

#### `retrieve(query: str, k: int = 5, filter: dict = None) -> List[Document]`

**Purpose:** Retrieves the top-k most semantically similar documents to a query.

**Parameters:**
- `query` (str): The search query text
- `k` (int, optional): Number of documents to retrieve. Defaults to 5
- `filter` (dict, optional): Optional metadata filters to apply during search

**Returns:** List of Document objects, ordered by relevance (most relevant first)

**How it works:**
1. **Embed Query:**
   - Calls `self.embedder.embed_query(query)` to convert the query text to a vector
   - Result is a list of floats representing the query embedding
2. **Search Vector Store:**
   - Accesses the underlying Chroma instance via `self.vs.store`
   - Calls `similarity_search_by_vector(embedding, k=k, filter=filter)`
   - This performs cosine similarity search in the vector database
3. **Convert Results:**
   - The vector store returns LangChain Document objects
   - Iterates through results and converts each to our custom Document class
   - Extracts `page_content` and `metadata` from each result
   - Creates new Document instances with this data
4. **Return:**
   - Returns list of custom Document objects

**Why the conversion?**
The conversion from LangChain Documents to custom Documents ensures independence from external libraries and provides a consistent interface.

**Example:**
```python
results = retriever.retrieve("What is Python?", k=3)
# Returns: [Document(...), Document(...), Document(...)]
# Ordered by relevance to the query
```

#### `retrieve_with_scores(query: str, k: int = 5) -> List[Tuple[Document, float]]`

**Purpose:** Retrieves the top-k most semantically similar documents along with their similarity scores.

**Parameters:**
- `query` (str): The search query text
- `k` (int, optional): Number of documents to retrieve. Defaults to 5

**Returns:** List of tuples, each containing a Document and its similarity score (float)

**How it works:**
1. **Search with Scores:**
   - Accesses the underlying Chroma instance via `self.vs.store`
   - Calls `similarity_search_with_score(query, k=k)`
   - This performs similarity search and returns both documents and scores
2. **Convert Results:**
   - Iterates through the (document, score) tuples
   - Converts each LangChain Document to a custom Document
   - Preserves the score for each document
3. **Return:**
   - Returns list of (Document, float) tuples
   - Lower scores indicate higher similarity in Chroma

**Example:**
```python
results = retriever.retrieve_with_scores("What is Python?", k=3)
for doc, score in results:
    print(f"Score: {score:.4f} | {doc.page_content[:50]}...")
# Output:
# Score: 0.3215 | Python is a high-level programming language...
# Score: 0.4102 | Python was created by Guido van Rossum...
# Score: 0.4523 | Python emphasizes code readability...
```

#### `retrieve_by_source(query: str, source: str, k: int = 5) -> List[Document]`

**Purpose:** Retrieves documents filtered by a specific source file.

**Parameters:**
- `query` (str): The search query text
- `source` (str): Source identifier to filter by (e.g., file path)
- `k` (int, optional): Number of documents to retrieve. Defaults to 5

**Returns:** List of Document objects from the specified source, ordered by relevance

**How it works:**
1. **Filter Construction:**
   - Creates a metadata filter dictionary: `{"source": source}`
2. **Filtered Retrieval:**
   - Calls the standard `retrieve()` method with the filter
   - This limits search to documents with matching source metadata
3. **Return:**
   - Returns list of filtered documents

**Example:**
```python
# Retrieve only from a specific file
results = retriever.retrieve_by_source(
    query="machine learning",
    source="/path/to/ml_guide.pdf",
    k=5
)
# Returns only documents from ml_guide.pdf that match the query
```

---

## See Also

- **[documentation.md](./documentation.md)** - Comprehensive usage guide with examples and architecture
- **[test.py](./test.py)** - Runnable test demonstrations
