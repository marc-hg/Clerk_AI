import asyncio
import os
from app.services.rag_service import CVRagSystem


async def create_rag():
    # Get the project root directory (parent of app directory)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cv_directory = os.path.join(project_root, "data", "cv_storage")

    print(f"Processing CVs from: {cv_directory}")

    # Initialize the RAG system
    rag_system = CVRagSystem()

    try:
        # Process all CVs in the directory
        result = await rag_system.process_cv_directory(cv_directory)
        print(f"Directory processing complete: {result}")

        # Perform a query test
        queries = [
            "Someone who has experience with Vue",
            "Someone with experience in DDD",
            "Someone who has worked in Vaughan Systems",
            "The person with the most machine learning skill",
            "Someone with storybook experience",
            "Has worked in Venezuela",
            "Has worked in Poland"
        ]
        for query in queries:
            print(f"\nExecuting query: {query}")
            # summary_results = await rag_system.query_cv_database(query, top_k=3)
            summary_results = await rag_system.smart_query_cv_database(query, top_k=3)

            if not summary_results or not summary_results.source_nodes:
                print("No relevant summaries found.")
            else:
                # Only show the first result, even if we retrieved more
                node = summary_results.source_nodes[0]
                print("\nTop Result:")
                metadata = node.metadata
                print(f"Name: {metadata.get('name', 'N/A')}")
                print(f"Email: {metadata.get('email', 'N/A')}")
                print(f"Country: {metadata.get('country', 'N/A')}")
                print(f"Skills: {metadata.get('skills_text', 'N/A')}")
                print(f"Summary: {metadata.get('summary', 'No summary available.')}")
                print(f"Relevance Score: {node.score if hasattr(node, 'score') else 'N/A'}")
                print("-" * 50)

        return result

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    # Optional: Clear existing database before creating new one
    import shutil
    db_path = "./data/chroma_db"
    if os.path.exists(db_path):
        print(f"Removing existing database at {db_path}")
        shutil.rmtree(db_path)
    
    asyncio.run(create_rag())
