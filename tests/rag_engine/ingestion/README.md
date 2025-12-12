Ingestion Subpackage
Author: Yihang Wang

This folder has the code I wrote for reading files and splitting them into chunks. The other subpackages depend on this, because they expect the data to already be in Document format.

Two main modules:
1. loaders.py  
This has the file loading classes:
- DocumentLoader(base)
- PDFLoader
- TXTLoader
- CSVLoader

Each loader class:
- loads one type of file
- returns Document objects
- keeps track of how many docs or rows were loaded
- has summary() and reset()

2. chunker.py  
This has the TextChunker class. It splits text from the Document objects using the chunk_size and overlap we choose.

Main methods:
- chunk_docs(docs)
- chunk_one(doc)
- set_size(size)

example:
from ingestion.loaders import TXTLoader
from ingestion.chunker import TextChunker
loader = TXTLoader()  
docs = loader.load(["example.txt"])
chunker = TextChunker(chunk_size=400, overlap=100) 
parts = chunker.chunk_docs(docs)

This is just loading a text file and splitting it into smaller parts
