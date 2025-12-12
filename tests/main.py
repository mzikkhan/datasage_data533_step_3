"""
DataSage Demo
This script demonstrates the core functionalities of the DataSage RAG engine.
"""

import os
from rag_engine import RagEngine

def main():
    data_path = "your_document.csv"  # Change this to your file path
    
    # Optional: Add metadata to help organize and track your documents
    metadata = {
        "dataset_name": "My Dataset",
        "description": "Description of your data",
        "version": "1.0"
    }
    
    # Initialize the RAG Engine
    engine = RagEngine(
        data_files=data_path,
        metadata=metadata,
        model_name="tinyllama:1.1b"  # You can change to other Ollama models
    )
    
    print("✅ Engine initialized successfully!\n")
    
    # FUNCTION 1: Ask a question about your data
    question = "What are the main insights from this data?"
    answer = engine.query(question)
    print(answer)

    # FUNCTION 2: Get summary insights from your data
    summary = engine.summary()
    print(summary)
    
    # FUNCTION 3: Search Documents and find relevant content
    search_term = "apples"
    results = engine.search_documents(search_term, top_k=3)

    for i, result in enumerate(results, 1):
        content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
        source = result['source'].get('name', 'Unknown')
        print(f"{i}. Source: {source}")
        print(f"   Content: {content_preview}")
        print()
    
    # FUNCTION 4: Inspect Your Knowledge Base
    stats = engine.get_knowledge_stats()
    
    print(f"\n📊 Knowledge Base Overview:")
    print(f"   • Total Documents: {stats.get('total_documents', 0)}")
    print(f"   • Unique Sources: {stats.get('unique_sources', 0)}")
    print(f"   • Total Searches: {stats.get('total_searches', 0)}")
    print(f"   • Unique Queries: {stats.get('unique_queries', 0)}")
    
    if stats.get('source_distribution'):
        print(f"\n   📁 Source Distribution:")
        for source, count in stats['source_distribution'].items():
            source_name = os.path.basename(source)
            print(f"      - {source_name}: {count} documents")


if __name__ == "__main__":
    main()
