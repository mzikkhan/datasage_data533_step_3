import unittest
import sys
import os

# Add the project root to the path so we can import rag_engine and tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from rag_engine.retrieval.tests.test_data_models import TestDataModels
from rag_engine.retrieval.tests.test_generator import TestGenerator
from rag_engine.retrieval.tests.test_retriever import TestRetriever

def suite():
    test_suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    
    test_suite.addTests(loader.loadTestsFromTestCase(TestDataModels))
    test_suite.addTests(loader.loadTestsFromTestCase(TestGenerator))
    test_suite.addTests(loader.loadTestsFromTestCase(TestRetriever))
    
    return test_suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite())
    if not result.wasSuccessful():
        sys.exit(1)
