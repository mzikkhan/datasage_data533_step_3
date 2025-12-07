import unittest
from test_pdf_loader import TestPDFLoader
from test_txt_loader import TestTXTLoader
from test_csv_loader import TestCSVLoader
from test_text_chunker import TestTextChunker

def load():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TestPDFLoader))
    s.addTest(unittest.makeSuite(TestTXTLoader))
    s.addTest(unittest.makeSuite(TestCSVLoader))
    s.addTest(unittest.makeSuite(TestTextChunker))
    return s

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(load())