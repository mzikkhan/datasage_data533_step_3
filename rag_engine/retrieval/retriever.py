from typing import List, Tuple
import json
import urllib.request
import urllib.error
from .data_models import Document
from ..indexing.vector_store import VectorStore

class OllamaEmbedder:
    """
    A simple Ollama embedder to embed documents and queries.
    """
    def __init__(self, model: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def _get_embedding(self, text: str) -> List[float]:
        url = f"{self.base_url}/api/embeddings"
        payload = {
            "model": self.model,
            "prompt": text
        }
        data = json.dumps(payload).encode("utf-8")
        
        req = urllib.request.Request(
            url, 
            data=data, 
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                if response.status != 200:
                    raise Exception(f"Ollama API returned status {response.status}")
                result = json.loads(response.read().decode("utf-8"))
                return result.get("embedding", [])
        except urllib.error.URLError as e:
            raise Exception(f"Failed to connect to Ollama at {self.base_url}: {e}")

    def embed_query(self, text: str) -> List[float]:
        return self._get_embedding(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._get_embedding(text) for text in texts]

class Retriever:
    """
    A simple retriever to retrieve documents from a vector store.
    """
    def __init__(self, vector_store: VectorStore, embedder: OllamaEmbedder):
        self.vs = vector_store
        self.embedder = embedder

    def retrieve(self, query: str, k: int = 5, filter: dict = None) -> List[Document]:
        """
        Retrieve documents based on a query.
        """
        embedding = self.embedder.embed_query(query)
        results = self.vs.store.similarity_search_by_vector(embedding, k=k, filter=filter)
        return [Document(page_content=d.page_content, metadata=d.metadata) for d in results]

    def retrieve_with_scores(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """
        Retrieve documents along with their similarity scores.
        """
        # Chroma returns (doc, score) tuples when using similarity_search_with_score
        results = self.vs.store.similarity_search_with_score(query, k=k)
        
        output = []
        for doc, score in results:
            new_doc = Document(page_content=doc.page_content, metadata=doc.metadata)
            output.append((new_doc, score))
        return output

    def retrieve_by_source(self, query: str, source: str, k: int = 5) -> List[Document]:
        """
        Retrieve documents filtered by a specific source file.
        """
        return self.retrieve(query, k=k, filter={"source": source})
