import json
import os
from typing import List, Dict, Any, Set

from llama_index.core import Settings, VectorStoreIndex, Response
from llama_index.core.schema import Document
from llama_index.core.storage import StorageContext
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.core.storage.index_store import SimpleIndexStore

from app.utils.pdf_conversion import file_to_text, file_path_to_text
from app.services.file_info_extraction import extract_fields_user_v1, get_gpt_response
from app.services.db_service import DatabaseService

from nltk.corpus import stopwords
import nltk


async def process_single_cv(file_path: str) -> Dict[str, Any]:
    """Process a single CV file and extract its information."""
    try:
        filename = os.path.basename(file_path)
        cv_text = file_path_to_text(file_path)
        if not cv_text:
            return {"status": "error", "message": f"Failed to extract text from {filename}"}

        cv_json = await extract_fields_user_v1(cv_text)

        # Store in database
        db_service = DatabaseService()
        cv_id = await db_service.store_cv_data(cv_json)
        
        # Add cv_id to metadata
        metadata = {
            "source_file": filename,
            "name": cv_json.get("name", ""),
            "email": cv_json.get("email", ""),
            "country": cv_json.get("country", ""),
            # Store only skills above 70%
            "key_skills": json.dumps({k: v for k, v in cv_json.get("skills", {}).items() if v >= 50}),
            # Store only company names
            "companies": json.dumps(
                list(cv_json.get("companies", {}).keys()) if isinstance(cv_json.get("companies"),
                                                                        dict) else cv_json.get("companies", []))
        }

        # Add cv_id to metadata
        metadata["cv_id"] = cv_id

        # Create detailed content for the document text
        skills_details = []
        for skill, level in cv_json.get("skills", {}).items():
            if level >= 90:
                skill_str = f"Expert level proficiency in {skill.lower()}"
            elif level >= 70:
                skill_str = f"Advanced proficiency in {skill.lower()}"
            elif level >= 50:
                skill_str = f"Intermediate level knowledge of {skill.lower()}"
            else:
                skill_str = f"Basic knowledge of {skill.lower()}"
            skills_details.append(skill_str)

        # Format companies information
        companies_data = cv_json.get('companies', {})
        if isinstance(companies_data, dict):
            companies_list = list(companies_data.keys())
        elif isinstance(companies_data, list):
            companies_list = companies_data
        else:
            companies_list = []

        # Create document text with sections
        document_text = f"""
    Profile Summary:
    {cv_json.get('name', '')} is a professional based in {cv_json.get('country', '')}.

    Work History:
    Previously worked at: {', '.join(companies_list)}

    Technical Expertise:
    {'. '.join(skills_details)}

    Professional Summary:
    {cv_json.get('comment', '')}

    Original CV Content:
    {cv_text}
    """

        # Create Document with text and minimal metadata
        document = Document(
            text=document_text,
            metadata=metadata
        )

        return {
            "status": "success",
            "document": document
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


class CVRagSystem:
    def __init__(self):
        """Initialize the CV RAG system with in-memory storage."""
        # Initialize OpenAI embeddings with configuration
        self.embed_model = OpenAIEmbedding(
            model="text-embedding-3-large",
            dimensions=1536,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # Configure global settings
        Settings.embed_model = self.embed_model
        Settings.chunk_size = 512
        Settings.chunk_overlap = 20
        Settings.store_embeddings = True

        # Initialize storage components
        vector_store = SimpleVectorStore()
        docstore = SimpleDocumentStore()
        index_store = SimpleIndexStore()

        # Create storage context
        self.storage_context = StorageContext.from_defaults(
            vector_store=vector_store,
            docstore=docstore,
            index_store=index_store
        )

        # Initialize index as None
        self.index = None

        # Download NLTK data if needed
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

        # Get both English and Spanish stopwords
        self.stop_words = set(stopwords.words('english') + stopwords.words('spanish'))

        # Add some CV-specific stop words
        self.stop_words.update({
            'find', 'show', 'get', 'someone', 'person', 'people',
            'buscar', 'mostrar', 'obtener', 'alguien', 'persona', 'gente'
        })

    async def process_cv_directory(self, directory_path: str) -> Dict[str, Any]:
        """Process all CVs in the directory and add them to the RAG system."""
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        processed_docs = []
        errors = []

        for filename in os.listdir(directory_path):
            if filename.endswith('.pdf'):
                print(f"Processing: {filename}")
                file_path = os.path.join(directory_path, filename)
                result = await process_single_cv(file_path)

                if result["status"] == "success":
                    doc = result["document"]
                    processed_docs.append(doc)
                    print(f"Successfully processed: {filename}")
                else:
                    errors.append({"file": filename, "error": result["message"]})
                    print(f"Error processing {filename}: {result['message']}")

        if processed_docs:
            try:
                print("\nCreating index from documents...")
                # Configure chunk size in Settings
                Settings.chunk_size = 2048  # Increased chunk size
                Settings.chunk_overlap = 20

                # Create index
                self.index = VectorStoreIndex.from_documents(
                    documents=processed_docs,
                    storage_context=self.storage_context,
                    show_progress=True
                )

                # Verify index creation
                if self.index is not None:
                    print(f"\n✓ Index created successfully with {len(processed_docs)} documents")

                    # Verify vector store
                    vector_store = self.storage_context.vector_store
                    print("\nVerifying vector store:")

                else:
                    raise ValueError("Failed to create index - index is None")

            except Exception as e:
                print(f"Error creating index: {str(e)}")
                return {"status": "error", "message": f"Failed to create index: {str(e)}"}

        return {
            "status": "success",
            "processed_documents": len(processed_docs),
            "errors": errors if errors else None
        }

    async def smart_query_cv_database(self, query: str, top_k: int = 10):
        """Vector search with structured metadata matching."""
        if self.index is None:
            raise ValueError("Index has not been created yet. Please process documents first.")

        print(f"\n=== Starting smart query processing ===")
        print(f"Original query: {query}")

        # Create enhanced query
        enhanced_query = f"""
        Looking for candidates with experience in {query}.
        This includes relevant work history, projects, and technical expertise.
        """

        print("\nCreating query engine...")
        query_engine = self.index.as_query_engine(
            similarity_top_k=top_k * 2,  # Get more results initially for reranking
            response_mode="no_text",  # We just want the nodes, not a generated response
        )

        print("\nExecuting query...")
        try:
            results = query_engine.query(enhanced_query)
            if not hasattr(results, 'source_nodes') or not results.source_nodes:
                print("No results found")
                return results

            print(f"\nFound {len(results.source_nodes)} initial matches")

            # Rescore results
            rescored_nodes = []
            for node in results.source_nodes:
                try:
                    base_score = getattr(node, 'score', 0.0)
                    boost = 0.0
                    metadata = node.metadata

                    # Check metadata for matches
                    try:
                        companies = json.loads(metadata.get('companies', '[]'))
                        key_skills = json.loads(metadata.get('key_skills', '{}'))
                        country = metadata.get('country', '')  # Get country as string

                        # Company matches
                        if any(company.lower() in query.lower() for company in companies):
                            boost += 0.3  # 30% boost for company match

                        # Skill matches
                        for skill in key_skills:
                            if skill.lower() in query.lower():
                                boost += 0.3  # 30% boost per matching skill

                        # Country matching - fixed the syntax error
                        if country and country.lower() in query.lower():
                            boost += 0.3  # 30% boost for country match

                    except json.JSONDecodeError:
                        print(f"Warning: Could not parse metadata for {metadata.get('name', 'unknown')}")

                    # Calculate final score
                    final_score = base_score * (1 + boost)
                    node.score = final_score
                    rescored_nodes.append(node)

                    print(f"\nCandidate: {metadata.get('name', 'N/A')}")
                    print(f"Base score: {base_score:.3f}")
                    print(f"Boost: {boost:.3f}")
                    print(f"Final score: {final_score:.3f}")

                except Exception as e:
                    print(f"Error processing node: {str(e)}")
                    continue

            # Sort and select top results
            rescored_nodes.sort(key=lambda x: x.score, reverse=True)
            results.source_nodes = rescored_nodes[:top_k]

            print("\n=== Final Rankings ===")
            for i, node in enumerate(results.source_nodes, 1):
                print(f"{i}. {node.metadata.get('name', 'N/A')} - Score: {node.score:.3f}")

            return results

        except Exception as e:
            print(f"Error during query execution: {str(e)}")
            raise

    async def query_cv_database(self, query: str, top_k: int = 10):
        """Execute a standard query without special processing."""
        if self.index is None:
            raise ValueError("Index has not been created yet. Please process documents first.")

        vector_query_engine = self.index.as_query_engine(
            similarity_top_k=top_k,
            response_mode="no_text"
        )

        return vector_query_engine.query(query)
