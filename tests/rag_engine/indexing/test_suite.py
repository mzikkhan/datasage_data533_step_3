"""
Test Suite for Indexing Module
Combines all test classes into a single test suite for comprehensive testing.
"""

import unittest
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)

from test_embedder import (
    TestEmbedderInitialization,
    TestEmbedderTextPreprocessing,
    TestEmbedderQueryEmbedding,
    TestEmbedderBatchProcessing,
    TestEmbedderUtilityMethods
)

from test_vector_store import (
    TestVectorStoreInitialization,
    TestVectorStoreAddDocuments,
    TestVectorStoreSearch,
    TestVectorStoreUtilities
)

from test_index_engine import (
    TestIndexingEngineInitialization,
    TestIndexingEngineValidation,
    TestIndexingEngineIndexing,
    TestIndexingEngineBatchProcessing
)

def create_test_suite():
    """
    Creates a test suite containing all test classes.
    Returns:
        unittest.TestSuite: Complete test suite
    """
    suite = unittest.TestSuite()
    
    loader = unittest.TestLoader()
    
    print("=" * 70)
    print("BUILDING TEST SUITE FOR INDEXING MODULE")
    print("=" * 70)
    
    # Adding tests
    print("\nAdding Embedder Tests...")
    suite.addTests(loader.loadTestsFromTestCase(TestEmbedderInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestEmbedderTextPreprocessing))
    suite.addTests(loader.loadTestsFromTestCase(TestEmbedderQueryEmbedding))
    suite.addTests(loader.loadTestsFromTestCase(TestEmbedderBatchProcessing))
    suite.addTests(loader.loadTestsFromTestCase(TestEmbedderUtilityMethods))
    print(f"  Added 5 test classes for Embedder")
    
    print("\nAdding VectorStore Tests...")
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStoreInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStoreAddDocuments))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStoreSearch))
    suite.addTests(loader.loadTestsFromTestCase(TestVectorStoreUtilities))
    print(f"  Added 4 test classes for VectorStore")
    
    print("\nAdding IndexingEngine Tests...")
    suite.addTests(loader.loadTestsFromTestCase(TestIndexingEngineInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestIndexingEngineValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestIndexingEngineIndexing))
    suite.addTests(loader.loadTestsFromTestCase(TestIndexingEngineBatchProcessing))
    print(f"  Added 4 test classes for IndexingEngine")
    
    print("\n" + "=" * 70)
    print(f"TOTAL TEST CLASSES: 13")
    print(f"TOTAL TEST CASES: {suite.countTestCases()}")
    print("=" * 70)
    return suite


def run_test_suite():
    """
    Runs the complete test suite with detailed reporting.
    """
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    print("\n" + "=" * 70)
    print("RUNNING ALL TESTS")
    print("=" * 70 + "\n")
    
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    exit_code = run_test_suite()
    sys.exit(exit_code)