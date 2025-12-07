import os
from rag_engine import RagEngine

def main():

    # Global Path to your CSV file
    csv_path = "/Users/zaedkhan/Desktop/data533_project_experiments/datasage/fruits_processed.csv"
    
    # Optional metadata for the document
    metadata = {
        "dataset_name": "Processed Fruits Dataset",
        "description": "Contains fruit categories, quantities, prices, and other attributes."
    }

    # Initialize the RAG Engine
    print("\n🔧 Initializing RAG Engine...")
    engine = RagEngine(csv_path, metadata=metadata, model_name="tinyllama:1.1b")

    # Define your analysis question
    query = "Provide a detailed summary of the key insights from this dataset."

    print("\n🤖 Asking the model for insights...")
    
    # Function 1
    response = engine.query(query)
    print("\n📊 Query Insights:\n")
    print(response)

    # Function 2
    summary = engine.summary()
    print("\n📊 Summary Insights:\n")
    print(summary)

    # Function 3
    search_results = engine.search_documents("price", top_k=2)
    for i, res in enumerate(search_results, 1):
        print(f"Result {i}: {res['content'][:50]}... (Source: {res['source'].get('source', 'Unknown')})")

    # Function 4
    stats = engine.get_knowledge_stats()
    print(f"Total Documents: {stats.get('total_documents')}")
    print(f"Unique Sources: {stats.get('unique_sources')}")

    # Function 5
    # Create a dummy file to add
    # with open("extra_info.txt", "w") as f:
    #     f.write("Bananas are rich in potassium and great for energy.")
    
    # try:
    #     msg = engine.add_knowledge(["extra_info.txt"])
    #     print(msg)
    # finally:
    #     if os.path.exists("extra_info.txt"):
    #         os.remove("extra_info.txt")

if __name__ == "__main__":
    main()