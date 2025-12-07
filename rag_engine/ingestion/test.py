<<<<<<< Updated upstream
print("hi")
=======
from .loaders import PDFLoader, TXTLoader, CSVLoader
from .chunker import TextChunker
from langchain_core.documents import Document

#test ingestion(by Yihang Wang)
def test_csv():
    #load csv file
    loader = CSVLoader()
    docs = loader.load(["../../fruits_processed.csv"])
    print("csv rows loaded:", len(docs))
    if docs:
        print("first row text:", docs[0].page_content)
    print(loader.summary())

def test_txt():
    #load txt file
    loader = TXTLoader()
    try:
        docs = loader.load(["testsample.txt"])
        print("txt docs loaded:", len(docs))
        if docs:
            print("sample text:", docs[0].page_content[:60])
        print(loader.summary())
    except Exception as e:
        print("txt test skipped:", e)

def test_pdf():
    #load pdf file
    loader = PDFLoader()
    try:
        docs = loader.load(["../../project_description.pdf"])
        print("pdf docs loaded:", len(docs))
        print(loader.summary())
    except Exception as e:
        print("pdf test skipped:", e)

def test_chunker():
    #fake doc for testing chunking
    fake_text = "x"*1500
    doc = Document(page_content=fake_text, metadata={})

    #make chunker
    c = TextChunker(chunk_size=500, overlap=100)

    #split one doc
    pieces = c.chunk_one(doc)
    print("chunks:", len(pieces))

    #print each chunk size
    for i, p in enumerate(pieces):
        print("chunk", i, "length:", len(p.page_content))

if __name__ == "__main__":
    print("running ingestion tests...\n")
    test_csv()
    test_txt()
    test_pdf()
    test_chunker()
    print("\nfinished ingestion tests.")
>>>>>>> Stashed changes
