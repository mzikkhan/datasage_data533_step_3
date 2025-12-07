from typing import List
from langchain_core.documents import Document

class TextChunker:
    #split long text into smaller chunks
    def __init__(self, chunk_size=1000, overlap=200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_docs(self, docs: List[Document]) -> List[Document]:
        #loop docs
        result = []
        for d in docs:
            parts = self.chunk_one(d)
            result.extend(parts)
        return result

    def chunk_one(self, doc: Document) -> List[Document]:
        #split one doc
        t = doc.page_content
        res = []
        start = 0

        while start < len(t):
            end = start + self.chunk_size
            piece = t[start:end]

            meta2 = dict(doc.metadata)
            meta2["chunk"] = len(res)

            new_doc = Document(
                page_content=piece,
                metadata=meta2
            )
            res.append(new_doc)

            start = end - self.overlap

        return res

    def set_size(self, s: int):
        #change chunk size
        self.chunk_size = s