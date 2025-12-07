from typing import List
from pathlib import Path
from langchain_core.documents import Document
import csv

class DocumentLoader:
    #base class for all loaders
    def __init__(self):
        #how many docs loaded
        self.count =0  

    def load(self, paths: List[str]) -> List[Document]:
        #subclass must override
        raise NotImplementedError

    def _ext_ok(self, p: str, ext: str) -> bool:
        #check ext
        return p.lower().endswith(ext)

    def _add(self, n: int):
        #update count
        self.count += n


class PDFLoader(DocumentLoader):
    #load pdf files
    def load(self, paths: List[str]) -> List[Document]:
        out = []

        try:
            from pypdf import PdfReader
        except:
            raise ImportError("need pypdf")

        for p in paths:
            if not self._ext_ok(p, ".pdf"):
                continue

            reader = PdfReader(p)
            buf = []

            #read pages
            for pg in reader.pages:
                txt = pg.extract_text() or ""
                buf.append(txt)

            all_txt = "\n".join(buf).strip()

            if all_txt:
                d = Document(
                    page_content=all_txt,
                    metadata={
                        "name": Path(p).name,
                        "path": p,
                        "type": "pdf"
                    }
                )
                out.append(d)

        self._add(len(out))
        return out

    def summary(self):
        #just show count
        return f"pdf: {self.count}"

    def reset(self):
        #reset counter
        self.count = 0


class TXTLoader(DocumentLoader):
    #load txt files
    def load(self, paths: List[str]) -> List[Document]:
        out = []

        for p in paths:
            if not self._ext_ok(p, ".txt"):
                continue

            with open(p, encoding="utf-8") as f:
                txt = f.read().strip()

            d = Document(
                page_content=txt,
                metadata={
                    "name": Path(p).name,
                    "path": p,
                    "type": "txt"
                }
            )
            out.append(d)

        self._add(len(out))
        return out

    def summary(self):
        return f"txt: {self.count}"

    def reset(self):
        self.count = 0


class CSVLoader(DocumentLoader):
    #load csv rows
    def load(self, paths: List[str]) -> List[Document]:
        out = []

        for p in paths:
            if not self._ext_ok(p, ".csv"):
                continue

            with open(p, encoding="utf-8", newline="") as f:
                r = csv.DictReader(f)
                for i, row in enumerate(r):
                    line = ", ".join(f"{k}={v}" for k, v in row.items())
                    d = Document(
                        page_content=line,
                        metadata={
                            "name": Path(p).name,
                            "path": p,
                            "row": i,
                            "type": "csv"
                        }
                    )
                    out.append(d)

        self._add(len(out))
        return out

    def summary(self):
        return f"csv rows: {self.count}"

    def reset(self):
        self.count = 0