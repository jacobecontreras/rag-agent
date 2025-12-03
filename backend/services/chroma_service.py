import os
import chromadb
import logging
from typing import List, Dict, Any, Optional
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

COLLECTION_NAME = "artifact_chunks"
BATCH_SIZE = 100
DEFAULT_MODEL = "all-MiniLM-L6-v2"

logger = logging.getLogger(__name__)


class ChromaService:
    def __init__(self, persist_directory: str = None):
        """Initialize ChromaDB service with persistent storage"""
        if persist_directory is None:
            # Default to same directory as SQLite database
            persist_directory = os.path.join(os.path.dirname(__file__), "..", "database", "chroma")

        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Initialize embedding function with MPS GPU support 
        self.embedding_function = SentenceTransformerEmbeddingFunction(
            model_name=DEFAULT_MODEL,
            device='mps'
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=self.embedding_function,
            metadata={"description": "LEAPP forensic report artifact chunks"}
        )

    def embed_and_store_chunks(self, job_name: str, chunks_data: List[Dict[str, Any]]) -> bool:
        """Embed and store chunks in ChromaDB"""
        try:
            if not chunks_data:
                return True

            # Prepare documents and metadata
            documents = []
            metadatas = []
            ids = []

            for chunk in chunks_data:
                # Use the JSON data as document
                document = chunk['data_json']
                documents.append(document)

                # Prepare metadata
                metadata = {
                    'job_name': chunk['job_name'],
                    'artifact_type_id': chunk['artifact_type_id'],
                    'row_index': chunk['row_index'],
                    'file_name': chunk.get('file_name', 'unknown')
                }
                metadatas.append(metadata)

                # Create unique ID
                chunk_id = f"{job_name}_{chunk['artifact_type_id']}_{chunk['row_index']}"
                ids.append(chunk_id)

            # Add to collection in batches to avoid memory issues
            for i in range(0, len(documents), BATCH_SIZE):
                batch_end = min(i + BATCH_SIZE, len(documents))
                self.collection.add(
                    documents=documents[i:batch_end],
                    metadatas=metadatas[i:batch_end],
                    ids=ids[i:batch_end]
                )

            return True

        except Exception as e:
            return False

    def reset_collection(self) -> bool:
        """Reset the ChromaDB collection"""
        try:
            self.client.delete_collection(COLLECTION_NAME)
            self.collection = self.client.get_or_create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"description": "LEAPP forensic report artifact chunks"}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False

    def query_chunks(self, query_text: str, job_name: Optional[str] = None, n_results: int = 10) -> List[Dict[str, Any]]:
        """Query chunks from ChromaDB"""
        try:
            # Prepare where clause if job_name is specified
            where_clause = {"job_name": job_name} if job_name else None

            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results,
                where=where_clause
            )

            # Format results safely
            if not results['documents'] or not results['documents'][0]:
                return []

            docs = results['documents'][0]
            metadatas = results['metadatas'][0] if results['metadatas'] else [{}] * len(docs)
            distances = results['distances'][0] if results['distances'] else [0] * len(docs)
            ids = results['ids'][0] if results['ids'] else [''] * len(docs)

            return [
                {
                    'document': doc,
                    'metadata': metadatas[i] if i < len(metadatas) else {},
                    'distance': distances[i] if i < len(distances) else 0,
                    'id': ids[i] if i < len(ids) else ''
                }
                for i, doc in enumerate(docs)
            ]

        except Exception as e:
            logger.error(f"Error querying chunks: {str(e)}")
            return []

# Global instance
chroma_service = ChromaService()