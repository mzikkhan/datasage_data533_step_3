"""
Unit tests for the IndexingEngine module.
Tests file indexing, validation, and orchestration with error handling.
"""

import unittest
import sys
import os
import shutil

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)

from rag_engine.indexing.index_engine import IndexingEngine


class TestIndexingEngineInitialization(unittest.TestCase):
    """Test cases for IndexingEngine initialization."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestIndexingEngineInitialization ===")
        cls.test_dir = "./test_ie_init"
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestIndexingEngineInitialization ===")
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    def setUp(self):
        """Set up test fixtures."""
        self.indexer = None
    
    def tearDown(self):
        """Clean up after each test."""
        if self.indexer:
            del self.indexer
    
    def test_default_initialization(self):
        """Test initialization with default parameters."""
        self.indexer = IndexingEngine()
        self.assertIsNotNone(self.indexer, "IndexingEngine should be created")
        self.assertIsNotNone(self.indexer.embedder, "Embedder should be initialized")
        self.assertIsNotNone(self.indexer.vector_store, "VectorStore should be initialized")
        self.assertIsNotNone(self.indexer.chunker, "Chunker should be initialized")
    
    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        self.indexer = IndexingEngine(
            persist_dir=self.test_dir,
            chunk_size=500,
            overlap=50
        )
        self.assertEqual(self.indexer.persist_dir, self.test_dir,
                        "Persist dir should match")
        self.assertEqual(self.indexer.chunk_size, 500, "Chunk size should match")
        self.assertEqual(self.indexer.overlap, 50, "Overlap should match")
        self.assertEqual(len(self.indexer._indexed_files), 0,
                        "Should start with no indexed files")


class TestIndexingEngineValidation(unittest.TestCase):
    """Test cases for file validation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestIndexingEngineValidation ===")
        cls.test_dir = "./test_ie_validation"
        cls.indexer = IndexingEngine(persist_dir=cls.test_dir)
        
        cls.valid_txt = "valid_test.txt"
        with open(cls.valid_txt, 'w') as f:
            f.write("Test content")
        
        cls.empty_txt = "empty_test.txt"
        with open(cls.empty_txt, 'w') as f:
            pass
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestIndexingEngineValidation ===")
        del cls.indexer
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        if os.path.exists(cls.valid_txt):
            os.remove(cls.valid_txt)
        if os.path.exists(cls.empty_txt):
            os.remove(cls.empty_txt)
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def test_validate_existing_file(self):
        """Test validation of existing file."""
        file_path = self.valid_txt
        try:
            self.indexer._validate_file(file_path)
            self.assertTrue(True, "Validation should pass for valid file")
        except Exception as e:
            self.fail(f"Should not raise exception for valid file: {e}")
    
    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file (error handling)."""
        file_path = "nonexistent_file.txt"

        with self.assertRaises(FileNotFoundError) as context:
            self.indexer._validate_file(file_path)
        
        self.assertIn("File not found", str(context.exception),
                     "Error message should mention file not found")
        self.assertIsInstance(context.exception, FileNotFoundError,
                             "Should raise FileNotFoundError")
    
    def test_validate_empty_file(self):
        """Test validation of empty file (error handling)."""
        file_path = self.empty_txt
        with self.assertRaises(ValueError) as context:
            self.indexer._validate_file(file_path)
        
        self.assertIn("empty", str(context.exception).lower(),
                     "Error message should mention empty")
        self.assertIsInstance(context.exception, ValueError,
                             "Should raise ValueError")
    
    def test_validate_unsupported_extension(self):
        """Test validation of unsupported file type (error handling)."""
        file_path = "test.xyz"
        with open(file_path, 'w') as f:
            f.write("content")
        
        try:
            with self.assertRaises(ValueError) as context:
                self.indexer._validate_file(file_path)
            
            self.assertIn("Unsupported", str(context.exception),
                         "Error message should mention unsupported")
            self.assertIsInstance(context.exception, ValueError,
                                 "Should raise ValueError")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)


class TestIndexingEngineIndexing(unittest.TestCase):
    """Test cases for document indexing."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestIndexingEngineIndexing ===")
        cls.test_dir = "./test_ie_indexing"
        cls.indexer = IndexingEngine(persist_dir=cls.test_dir, chunk_size=100, overlap=20)
        
        cls.test_txt = "test_doc.txt"
        with open(cls.test_txt, 'w') as f:
            f.write("This is a test document for indexing. " * 10)
        
        cls.test_csv = "test_data.csv"
        with open(cls.test_csv, 'w') as f:
            f.write("name,value\n")
            f.write("item1,100\n")
            f.write("item2,200\n")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestIndexingEngineIndexing ===")
        del cls.indexer
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        if os.path.exists(cls.test_txt):
            os.remove(cls.test_txt)
        if os.path.exists(cls.test_csv):
            os.remove(cls.test_csv)
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def test_index_single_file(self):
        """Test indexing a single file."""
        file_path = self.test_txt
        chunks = self.indexer.index(file_path, verbose=False)
        self.assertIsNotNone(chunks, "Chunks should not be None")
        self.assertGreater(len(chunks), 0, "Should create at least one chunk")
        self.assertIn(os.path.abspath(file_path), self.indexer._indexed_files,
                     "File should be tracked as indexed")
        self.assertEqual(len(self.indexer._indexing_history), 1,
                        "Should have one history entry")
    
    def test_index_duplicate_file(self):
        """Test indexing same file twice (duplicate detection)."""
        file_path = self.test_txt
        self.indexer.index(file_path, verbose=False)  # First index
        chunks = self.indexer.index(file_path, verbose=False)  # Second index
        self.assertEqual(len(chunks), 0, "Should return empty list for duplicate")
        self.assertIn(os.path.abspath(file_path), self.indexer._indexed_files,
                     "File should still be tracked")
        self.assertGreater(len(self.indexer._indexing_history), 1,
                          "Should have history entries")
    
    def test_index_with_custom_metadata(self):
        """Test indexing with custom metadata."""
        file_path = self.test_csv
        custom_metadata = {"category": "test", "priority": "high"}
        chunks = self.indexer.index(file_path, metadata=custom_metadata, verbose=False)
        
        self.assertGreater(len(chunks), 0, "Should create chunks")
        has_custom_meta = any("category" in chunk.metadata for chunk in chunks)
        self.assertTrue(has_custom_meta, "Should have custom metadata")
        self.assertIsNotNone(chunks[0].metadata, "Should have metadata")
    
    def test_index_nonexistent_file(self):
        """Test indexing non-existent file (error handling)."""
        file_path = "nonexistent.txt"
        with self.assertRaises(FileNotFoundError):
            self.indexer.index(file_path, verbose=False)
        
        self.assertIn(file_path, self.indexer._failed_files,
                     "Failed file should be tracked")
        self.assertNotIn(os.path.abspath(file_path), self.indexer._indexed_files,
                        "Should not be in indexed files")


class TestIndexingEngineBatchProcessing(unittest.TestCase):
    """Test cases for batch indexing."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestIndexingEngineBatchProcessing ===")
        cls.test_dir = "./test_ie_batch"
        cls.indexer = IndexingEngine(persist_dir=cls.test_dir)
        cls.test_files = []
        for i in range(3):
            filename = f"batch_test_{i}.txt"
            with open(filename, 'w') as f:
                f.write(f"Content for file {i}")
            cls.test_files.append(filename)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestIndexingEngineBatchProcessing ===")
        del cls.indexer
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        for filename in cls.test_files:
            if os.path.exists(filename):
                os.remove(filename)
    
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def tearDown(self):
        """Clean up after each test."""
        pass
    
    def test_batch_index_multiple_files(self):
        """Test batch indexing multiple files."""
        file_paths = self.test_files
        
        results = self.indexer.batch_index(file_paths, verbose=False)
        
        self.assertIsNotNone(results, "Results should not be None")
        self.assertEqual(len(results), len(file_paths),
                        "Should have result for each file")
        self.assertTrue(all(len(chunks) > 0 for chunks in results.values()),
                       "All files should be indexed")
        self.assertEqual(len(self.indexer._indexed_files), len(file_paths),
                        "All files should be tracked")
    
    def test_batch_index_with_errors(self):
        """Test batch indexing with some invalid files (error recovery)."""
        file_paths = self.test_files + ["nonexistent.txt"]
        
        results = self.indexer.batch_index(
            file_paths,
            continue_on_error=True,
            verbose=False
        )
        
        self.assertEqual(len(results), len(file_paths),
                        "Should have result for each file")
        successful = sum(1 for chunks in results.values() if len(chunks) > 0)
        self.assertEqual(successful, len(self.test_files),
                        "Valid files should be indexed")
        self.assertIn("nonexistent.txt", self.indexer._failed_files,
                     "Failed file should be tracked")
    
    def test_batch_index_empty_list(self):
        """Test batch indexing with empty list (error handling)."""
        file_paths = []
        results = self.indexer.batch_index(file_paths, verbose=False)
        self.assertIsNotNone(results, "Results should not be None")
        self.assertEqual(len(results), 0, "Should return empty dict")
        self.assertIsInstance(results, dict, "Should return dictionary")
        self.assertEqual(results, {}, "Should be empty dictionary")
    
    def test_batch_index_stop_on_error(self):
        """Test batch indexing stops on first error."""
        file_paths = ["nonexistent.txt"] + self.test_files
        with self.assertRaises(FileNotFoundError):
            self.indexer.batch_index(
                file_paths,
                continue_on_error=False,  # Stop on error
                verbose=False
            )

if __name__ == '__main__':
    unittest.main(verbosity=2)