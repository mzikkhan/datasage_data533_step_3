Ingestion Subpackage Documentation  
Author: Yihang Wang

This is the part I worked on. The ingestion subpackage is basically for reading files and getting the text ready for the other parts of the project. We used txt, pdf, and csv because these are commonly used.
There are two modules: loaders.py and chunker.py.

loaders.py
This file has a parent class called DocumentLoader. The other three classes (PDFLoader, TXTLoader, CSVLoader) inherit from it. The parent class keeps a counter and has small helper functions, and the child classes focus on actually loading the files.
PDFLoader reads all pages of a pdf using pypdf and joins the text together. It creates one Document for each file and stores simple info like name and type. It also has summary() and reset().
TXTLoader just reads the entire txt file at once. It returns one Document per txt. Also has summary() and reset().
CSVLoader reads CSV rows one by one. Each row becomes a Document. The metadata includes the row number. Also has summary() and reset().

chunker.py 
This is where we split the text. The TextChunker class has chunk_docs() to loop through multiple documents and chunk_one() to split one document. There is also set_size() in case we need to update the chunk size.
The splitting uses chunk_size and overlap so the chunks aren’t totally disconnected.
That’s the main idea of the ingestion part.
