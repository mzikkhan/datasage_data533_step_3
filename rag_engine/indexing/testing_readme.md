# Testing Documentation for Indexing Module

## Overview

This directory contains comprehensive unit tests for the indexing module, including tests for `embedder.py`, `vector_store.py`, and `index_engine.py`.

---

## Test Structure

### Test Files

```
rag_engine/indexing/tests/
├── test_embedder.py          # Tests for Embedder (5 test classes, 10+ test cases)
├── test_vector_store.py      # Tests for VectorStore (4 test classes, 8+ test cases)
├── test_index_engine.py      # Tests for IndexingEngine (4 test classes, 8+ test cases)
└── test_suite.py             # Test suite combining all tests
```

### Test Classes

Each test file contains multiple test classes focusing on different aspects:

**test_embedder.py:**

- `TestEmbedderInitialization` - Initialization and configuration
- `TestEmbedderTextPreprocessing` - Text preprocessing functionality
- `TestEmbedderQueryEmbedding` - Single query embedding
- `TestEmbedderBatchProcessing` - Batch document embedding
- `TestEmbedderUtilityMethods` - Utility functions

**test_vector_store.py:**

- `TestVectorStoreInitialization` - Initialization
- `TestVectorStoreAddDocuments` - Adding documents
- `TestVectorStoreSearch` - Search functionality
- `TestVectorStoreUtilities` - Utility methods

**test_index_engine.py:**

- `TestIndexingEngineInitialization` - Initialization
- `TestIndexingEngineValidation` - File validation
- `TestIndexingEngineIndexing` - Document indexing
- `TestIndexingEngineBatchProcessing` - Batch operations

---

### Test Case Requirements Met

**Four test classes per module** (embedder, vector_store, index_engine)
**Two+ test cases per class** (most have 4+ test cases)
**Four+ assertions per test case** (comprehensive validation)
**setUp() and tearDown() methods** (resource management)
**setUpClass() and tearDownClass() methods** (class-level setup)

### Test Coverage

- **Initialization tests** - Verify components initialize correctly
- **Functionality tests** - Test core features work as expected
- **Error handling tests** - Verify graceful error handling
- **Edge case tests** - Test boundary conditions and unusual inputs
- **Integration tests** - Verify components work together

---

## Error Handling Tested

### Embedder Error Handling

- Empty string inputs
- Special characters
- Very long text
- Empty lists for batch processing

### VectorStore Error Handling

- Empty document lists
- Empty search queries
- Non-existent document IDs
- Invalid source names

### IndexingEngine Error Handling

- Non-existent files
- Empty files
- Unsupported file types
- Duplicate file indexing
- Batch processing with errors

---