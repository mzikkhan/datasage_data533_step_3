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

from rag_engine.indexing.index_engine import (
    IndexingEngine,
    IndexingException,
    FileValidationError,
    LoaderError,
    ChunkingError,
    StorageError
)


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
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
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
    
    def test_invalid_chunk_size(self):
        """Test initialization with invalid chunk size."""
        with self.assertRaises(IndexingException) as context:
            self.indexer = IndexingEngine(chunk_size=0)
        self.assertIn("chunk_size must be", str(context.exception))
    
    def test_negative_overlap(self):
        """Test initialization with negative overlap."""
        with self.assertRaises(IndexingException) as context:
            self.indexer = IndexingEngine(overlap=-10)
        self.assertIn("overlap must be", str(context.exception))
    
    def test_overlap_greater_than_chunk_size(self):
        """Test initialization with overlap >= chunk_size."""
        with self.assertRaises(IndexingException) as context:
            self.indexer = IndexingEngine(chunk_size=100, overlap=100)
        self.assertIn("overlap must be smaller than chunk_size", str(context.exception))


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
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        if os.path.exists(cls.valid_txt):
            os.remove(cls.valid_txt)
        if os.path.exists(cls.empty_txt):
            os.remove(cls.empty_txt)
    
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
        with self.assertRaises(FileValidationError) as context:
            self.indexer._validate_file(file_path)
        
        self.assertIn("File not found", str(context.exception),
                     "Error message should mention file not found")
    
    def test_validate_empty_file(self):
        """Test validation of empty file (error handling)."""
        file_path = self.empty_txt
        with self.assertRaises(FileValidationError) as context:
            self.indexer._validate_file(file_path)
        
        self.assertIn("empty", str(context.exception).lower(),
                     "Error message should mention empty")
    
    def test_validate_unsupported_extension(self):
        """Test validation of unsupported file type (error handling)."""
        file_path = "test.xyz"
        with open(file_path, 'w') as f:
            f.write("content")
        
        try:
            with self.assertRaises(FileValidationError) as context:
                self.indexer._validate_file(file_path)
            
            self.assertIn("Unsupported", str(context.exception),
                         "Error message should mention unsupported")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def test_validate_empty_path(self):
        """Test validation with empty file path."""
        with self.assertRaises(FileValidationError) as context:
            self.indexer._validate_file("")
        self.assertIn("File not found", str(context.exception))
    
    def test_validate_directory_not_file(self):
        """Test validation when path is a directory."""
        test_dir = "./test_temp_dir"
        os.makedirs(test_dir, exist_ok=True)
        try:
            with self.assertRaises(FileValidationError) as context:
                self.indexer._validate_file(test_dir)
            self.assertIn("Path is not a file", str(context.exception))
        finally:
            if os.path.exists(test_dir):
                shutil.rmtree(test_dir)


class TestIndexingEngineLoading(unittest.TestCase):
    """Test cases for loader selection and error handling."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestIndexingEngineLoading ===")
        cls.test_dir = "./test_ie_loading"
        cls.indexer = IndexingEngine(persist_dir=cls.test_dir)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestIndexingEngineLoading ===")
        del cls.indexer
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
    
    def test_get_loader_for_txt(self):
        """Test getting loader for .txt file."""
        from rag_engine.ingestion.loaders import TXTLoader
        loader = self.indexer._get_loader("test.txt")
        self.assertIsInstance(loader, TXTLoader)
    
    def test_get_loader_for_csv(self):
        """Test getting loader for .csv file."""
        from rag_engine.ingestion.loaders import CSVLoader
        loader = self.indexer._get_loader("test.csv")
        self.assertIsInstance(loader, CSVLoader)
    
    def test_get_loader_for_pdf(self):
        """Test getting loader for .pdf file."""
        from rag_engine.ingestion.loaders import PDFLoader
        loader = self.indexer._get_loader("test.pdf")
        self.assertIsInstance(loader, PDFLoader)
    
    def test_get_loader_unsupported_type(self):
        """Test getting loader for unsupported file type."""
        with self.assertRaises(LoaderError) as context:
            self.indexer._get_loader("test.xyz")
        self.assertIn("No loader available", str(context.exception))


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
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        if os.path.exists(cls.test_txt):
            os.remove(cls.test_txt)
        if os.path.exists(cls.test_csv):
            os.remove(cls.test_csv)
    
    def test_index_single_file(self):
        """Test indexing a single file."""
        file_path = self.test_txt
        chunks = self.indexer.index(file_path, verbose=False)
        print(f"DEBUG: File path: {file_path}, exists: {os.path.exists(file_path)}")
        print(f"DEBUG: Chunks returned: {len(chunks) if chunks else 0}")
        print(f"DEBUG: File path: {file_path}, exists: {os.path.exists(file_path)}")
        print(f"DEBUG: Chunks returned: {len(chunks) if chunks else 0}")
        self.assertIsNotNone(chunks, "Chunks should not be None")
        self.assertGreater(len(chunks), 0, "Should create at least one chunk")
        self.assertIn(os.path.abspath(file_path), self.indexer._indexed_files,
                     "File should be tracked as indexed")
    
    def test_index_duplicate_file(self):
        """Test indexing same file twice (duplicate detection)."""
        file_path = self.test_txt
        self.indexer.index(file_path, verbose=False)  # First index
        chunks = self.indexer.index(file_path, verbose=False)  # Second index
        self.assertEqual(len(chunks), 0, "Should return empty list for duplicate")
    
    def test_index_with_custom_metadata(self):
        """Test indexing with custom metadata."""
        file_path = self.test_csv
        custom_metadata = {"category": "test", "priority": "high"}
        chunks = self.indexer.index(file_path, metadata=custom_metadata, verbose=False)
        
        self.assertGreater(len(chunks), 0, "Should create chunks")
        has_custom_meta = any("category" in chunk.metadata for chunk in chunks)
        self.assertTrue(has_custom_meta, "Should have custom metadata")
    
    def test_index_nonexistent_file(self):
        """Test indexing non-existent file (error handling)."""
        file_path = "nonexistent.txt"
        with self.assertRaises(FileValidationError):
            self.indexer.index(file_path, verbose=False)
        
        self.assertIn(file_path, self.indexer._failed_files,
                     "Failed file should be tracked")
    
    def test_index_with_force_reindex(self):
        """Test re-indexing with force_reindex flag."""
        file_path = self.test_txt
        # First index
        chunks1 = self.indexer.index(file_path, verbose=False)
        # Force re-index
        chunks2 = self.indexer.index(file_path, force_reindex=True, verbose=False)
        self.assertGreater(len(chunks2), 0, "Should re-index with force_reindex=True")


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
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        for filename in cls.test_files:
            if os.path.exists(filename):
                os.remove(filename)
    
    def test_batch_index_multiple_files(self):
        """Test batch indexing multiple files."""
        results = self.indexer.batch_index(self.test_files, verbose=False)
        
        self.assertIsNotNone(results, "Results should not be None")
        self.assertEqual(len(results), len(self.test_files),
                        "Should have result for each file")
        self.assertTrue(all(len(chunks) > 0 for chunks in results.values()),
                       "All files should be indexed")
    
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
        self.assertIn("nonexistent.txt", self.indexer._failed_files,
                     "Failed file should be tracked")
    
    def test_batch_index_empty_list(self):
        """Test batch indexing with empty list (error handling)."""
        results = self.indexer.batch_index([], verbose=False)
        self.assertIsNotNone(results, "Results should not be None")
        self.assertEqual(len(results), 0, "Should return empty dict")
    
    def test_batch_index_stop_on_error(self):
        """Test batch indexing stops on first error."""
        file_paths = ["nonexistent.txt"] + self.test_files
        with self.assertRaises(FileValidationError):
            self.indexer.batch_index(
                file_paths,
                continue_on_error=False,
                verbose=False
            )
    
    def test_batch_index_none_input(self):
        """Test batch indexing with None input."""
        with self.assertRaises(ValueError) as context:
            self.indexer.batch_index(None, verbose=False)
        self.assertIn("NoneType", str(context.exception))


class TestIndexingEngineSearch(unittest.TestCase):
    """Test cases for search functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestIndexingEngineSearch ===")
        cls.test_dir = "./test_ie_search"
        cls.indexer = IndexingEngine(persist_dir=cls.test_dir)
        
        cls.test_file = "search_test.txt"
        with open(cls.test_file, 'w') as f:
            f.write("Machine learning and artificial intelligence are related fields.")
        
        cls.indexer.index(cls.test_file, verbose=False)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestIndexingEngineSearch ===")
        del cls.indexer
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        if os.path.exists(cls.test_file):
            os.remove(cls.test_file)
    
    def test_search_basic(self):
        """Test basic search functionality."""
        results = self.indexer.search("machine learning", k=2)
        self.assertIsNotNone(results)
        self.assertIsInstance(results, list)
    
    def test_search_empty_query(self):
        """Test search with empty query."""
        # Empty queries are allowed and return results
        results = self.indexer.search("")
        self.assertIsInstance(results, list)
    
    def test_search_invalid_k(self):
        """Test search with invalid k value."""
        with self.assertRaises(TypeError) as context:
            self.indexer.search("test", k=0)
        self.assertIn("Number of requested results", str(context.exception))
    
    def test_search_with_filter(self):
        """Test search with metadata filter."""
        results = self.indexer.search("machine", k=2, filter={"type": "txt"})
        self.assertIsNotNone(results)


class TestIndexingEngineUtilities(unittest.TestCase):
    """Test cases for utility methods."""
    
    @classmethod
    def setUpClass(cls):
        """Set up class-level resources."""
        print("\n=== Starting TestIndexingEngineUtilities ===")
        cls.test_dir = "./test_ie_utils"
        cls.indexer = IndexingEngine(persist_dir=cls.test_dir)
        
        cls.test_file = "utils_test.txt"
        with open(cls.test_file, 'w') as f:
            f.write("Test content for utilities")
        
        cls.indexer.index(cls.test_file, verbose=False)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources."""
        print("=== Finished TestIndexingEngineUtilities ===")
        del cls.indexer
        import time
        time.sleep(0.1)  # Brief delay for file handles
        import time
        time.sleep(0.1)  # Brief delay for file handles
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)
        if os.path.exists(cls.test_file):
            os.remove(cls.test_file)
    
    def test_get_indexed_files(self):
        """Test getting list of indexed files."""
        files = self.indexer.get_indexed_files()
        self.assertIsNotNone(files)
        self.assertIsInstance(files, list)
        self.assertGreater(len(files), 0)
    
    def test_get_failed_files(self):
        """Test getting failed files dictionary."""
        failed = self.indexer.get_failed_files()
        self.assertIsNotNone(failed)
        self.assertIsInstance(failed, dict)
    
    def test_get_indexing_history(self):
        """Test getting indexing history."""
        history = self.indexer.get_indexing_history()
        self.assertIsNotNone(history)
        self.assertIsInstance(history, list)
        self.assertGreater(len(history), 0)
    
    def test_get_system_statistics(self):
        """Test getting system statistics."""
        stats = self.indexer.get_system_statistics()
        self.assertIsNotNone(stats)
        self.assertIsInstance(stats, dict)
        self.assertIn("indexing", stats)
        self.assertIn("configuration", stats)
        self.assertIn("vector_store", stats)
    
    def test_reset_history(self):
        """Test resetting history."""
        self.indexer.reset_history()
        history = self.indexer.get_indexing_history()
        self.assertEqual(len(history), 0, "History should be empty after reset")
        failed = self.indexer.get_failed_files()
        self.assertEqual(len(failed), 0, "Failed files should be empty after reset")
    
    def test_check_duplicate(self):
        """Test duplicate checking."""
        is_dup = self.indexer._check_duplicate(self.test_file)
        self.assertTrue(is_dup, "File should be detected as duplicate")
        
        is_not_dup = self.indexer._check_duplicate("nonexistent.txt")
        self.assertFalse(is_not_dup, "Non-indexed file should not be duplicate")


if __name__ == '__main__':
    unittest.main(verbosity=2)