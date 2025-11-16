"""
Executive Intelligence Layer - Knowledge Fusion (Phase 5C)
Local document RAG (retrieval-augmented reasoning) with offline vectorization.
Uses ChromaDB for vector storage and sentence-transformers for embeddings.
"""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import threading

# Storage
KNOWLEDGE_DIR = "./knowledge"
KNOWLEDGE_LOCK = threading.Lock()

# ChromaDB client (lazy loaded)
_chroma_client = None
_collection = None


def _ensure_knowledge_dir():
    """Ensure knowledge directory exists."""
    Path(KNOWLEDGE_DIR).mkdir(parents=True, exist_ok=True)


def _get_chroma_client():
    """Get or create ChromaDB client."""
    global _chroma_client, _collection
    
    if _chroma_client is None:
        try:
            import chromadb
            from chromadb.config import Settings
            
            _ensure_knowledge_dir()
            
            # Create persistent client
            _chroma_client = chromadb.PersistentClient(
                path=KNOWLEDGE_DIR,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            _collection = _chroma_client.get_or_create_collection(
                name="knowledge_base",
                metadata={"description": "Executive Intelligence Knowledge Base"}
            )
            
            print(f"✓ ChromaDB initialized at {KNOWLEDGE_DIR}")
            
        except ImportError:
            print("✗ ChromaDB not installed. Install with: pip install chromadb")
            return None
    
    return _chroma_client


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk in characters
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk.strip():
            chunks.append(chunk.strip())
        
        start = end - overlap
    
    return chunks


def _extract_text_from_file(file_path: str) -> str:
    """
    Extract text from various file formats.
    
    Args:
        file_path: Path to file
        
    Returns:
        Extracted text
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext in ['.txt', '.md', '.py', '.js', '.json', '.csv']:
            # Plain text files
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        elif ext == '.pdf':
            # PDF files
            try:
                import PyPDF2
                text = []
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        text.append(page.extract_text())
                return '\n'.join(text)
            except ImportError:
                print("⚠ PyPDF2 not installed. Install with: pip install PyPDF2")
                return ""
        
        elif ext in ['.docx']:
            # Word documents
            try:
                import docx
                doc = docx.Document(file_path)
                return '\n'.join([para.text for para in doc.paragraphs])
            except ImportError:
                print("⚠ python-docx not installed. Install with: pip install python-docx")
                return ""
        
        else:
            # Try as plain text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    
    except Exception as e:
        print(f"✗ Error extracting text from {file_path}: {e}")
        return ""


def ingest_document(file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Ingest a document into the knowledge base.
    
    Args:
        file_path: Path to document file
        metadata: Optional metadata (author, date, category, etc.)
        
    Returns:
        Result dictionary with ingestion status
        
    Example:
        result = ingest_document(
            "./docs/business_plan.pdf",
            metadata={"category": "strategy", "author": "CEO"}
        )
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "message": f"File not found: {file_path}"
        }
    
    # Get ChromaDB client
    client = _get_chroma_client()
    if not client:
        return {
            "success": False,
            "message": "ChromaDB not available"
        }
    
    try:
        with KNOWLEDGE_LOCK:
            # Extract text
            print(f"📄 Extracting text from {file_path}...")
            text = _extract_text_from_file(file_path)
            
            if not text:
                return {
                    "success": False,
                    "message": "No text extracted from file"
                }
            
            # Chunk text
            chunks = _chunk_text(text, chunk_size=500, overlap=50)
            print(f"   ✓ Created {len(chunks)} chunks")
            
            # Generate document ID
            doc_id = hashlib.md5(file_path.encode()).hexdigest()
            
            # Prepare metadata
            base_metadata = {
                "source": file_path,
                "filename": os.path.basename(file_path),
                "ingested_at": datetime.now().isoformat(),
                "chunk_count": len(chunks)
            }
            
            if metadata:
                base_metadata.update(metadata)
            
            # Add chunks to collection
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{**base_metadata, "chunk_index": i} for i in range(len(chunks))]
            
            _collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas
            )
            
            print(f"✓ Document ingested: {os.path.basename(file_path)} ({len(chunks)} chunks)")
            
            return {
                "success": True,
                "message": f"Document ingested successfully",
                "document_id": doc_id,
                "chunks": len(chunks)
            }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Ingestion failed: {str(e)}"
        }


def search_knowledge(query: str, top_k: int = 5, filter_metadata: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """
    Search knowledge base for relevant information.
    
    Args:
        query: Search query
        top_k: Number of results to return
        filter_metadata: Optional metadata filters
        
    Returns:
        List of relevant chunks with metadata
        
    Example:
        results = search_knowledge("What is our business strategy?", top_k=3)
        for result in results:
            print(result['text'])
            print(f"Source: {result['metadata']['source']}")
    """
    # Get ChromaDB client
    client = _get_chroma_client()
    if not client:
        print("✗ ChromaDB not available")
        return []
    
    try:
        with KNOWLEDGE_LOCK:
            # Search collection
            results = _collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            
            if results and results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted_results.append({
                        "text": doc,
                        "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                        "distance": results['distances'][0][i] if results['distances'] else None,
                        "id": results['ids'][0][i] if results['ids'] else None
                    })
            
            print(f"✓ Found {len(formatted_results)} relevant chunks")
            
            return formatted_results
    
    except Exception as e:
        print(f"✗ Search failed: {e}")
        return []


def list_documents() -> List[Dict[str, Any]]:
    """
    List all documents in the knowledge base.
    
    Returns:
        List of document metadata
        
    Example:
        docs = list_documents()
        for doc in docs:
            print(f"{doc['filename']}: {doc['chunk_count']} chunks")
    """
    client = _get_chroma_client()
    if not client:
        return []
    
    try:
        with KNOWLEDGE_LOCK:
            # Get all items
            all_items = _collection.get()
            
            # Group by document
            docs_dict = {}
            
            if all_items and all_items['metadatas']:
                for metadata in all_items['metadatas']:
                    source = metadata.get('source', 'unknown')
                    if source not in docs_dict:
                        docs_dict[source] = {
                            "source": source,
                            "filename": metadata.get('filename', 'unknown'),
                            "ingested_at": metadata.get('ingested_at', 'unknown'),
                            "chunk_count": 0
                        }
                    docs_dict[source]["chunk_count"] += 1
            
            return list(docs_dict.values())
    
    except Exception as e:
        print(f"✗ List documents failed: {e}")
        return []


def delete_document(file_path: str) -> bool:
    """
    Delete a document from the knowledge base.
    
    Args:
        file_path: Path to document (used as identifier)
        
    Returns:
        True if successful
        
    Example:
        if delete_document("./docs/old_plan.pdf"):
            print("Document deleted")
    """
    client = _get_chroma_client()
    if not client:
        return False
    
    try:
        with KNOWLEDGE_LOCK:
            # Generate document ID
            doc_id = hashlib.md5(file_path.encode()).hexdigest()
            
            # Get all IDs for this document
            all_items = _collection.get()
            
            if all_items and all_items['ids']:
                ids_to_delete = [
                    id for id in all_items['ids']
                    if id.startswith(doc_id)
                ]
                
                if ids_to_delete:
                    _collection.delete(ids=ids_to_delete)
                    print(f"✓ Deleted document: {os.path.basename(file_path)} ({len(ids_to_delete)} chunks)")
                    return True
            
            return False
    
    except Exception as e:
        print(f"✗ Delete failed: {e}")
        return False


def get_knowledge_stats() -> Dict[str, Any]:
    """
    Get knowledge base statistics.
    
    Returns:
        Dictionary with statistics
        
    Example:
        stats = get_knowledge_stats()
        print(f"Total documents: {stats['document_count']}")
        print(f"Total chunks: {stats['chunk_count']}")
    """
    client = _get_chroma_client()
    if not client:
        return {
            "available": False,
            "document_count": 0,
            "chunk_count": 0
        }
    
    try:
        with KNOWLEDGE_LOCK:
            all_items = _collection.get()
            
            # Count unique documents
            sources = set()
            if all_items and all_items['metadatas']:
                for metadata in all_items['metadatas']:
                    sources.add(metadata.get('source', 'unknown'))
            
            return {
                "available": True,
                "document_count": len(sources),
                "chunk_count": len(all_items['ids']) if all_items and all_items['ids'] else 0,
                "collection_name": _collection.name if _collection else None
            }
    
    except Exception as e:
        print(f"✗ Stats failed: {e}")
        return {
            "available": False,
            "document_count": 0,
            "chunk_count": 0,
            "error": str(e)
        }


if __name__ == "__main__":
    print("="*70)
    print("KNOWLEDGE FUSION TEST")
    print("="*70)
    print()
    
    # Test 1: Initialize
    print("1. Initializing knowledge base...")
    client = _get_chroma_client()
    if client:
        print("   ✓ ChromaDB initialized")
    else:
        print("   ✗ ChromaDB not available")
    print()
    
    # Test 2: Create sample document
    print("2. Creating sample document...")
    sample_doc = "./knowledge/sample_doc.txt"
    _ensure_knowledge_dir()
    with open(sample_doc, 'w', encoding='utf-8') as f:
        f.write("""
        Business Strategy Document
        
        Our company focuses on three key areas:
        1. Customer satisfaction through excellent service
        2. Innovation in product development
        3. Sustainable growth and profitability
        
        Key Metrics:
        - Customer retention: 95%
        - Revenue growth: 25% YoY
        - Market share: 15%
        
        Strategic Goals:
        - Expand into new markets
        - Launch 3 new products
        - Increase customer base by 30%
        """)
    print(f"   ✓ Sample document created: {sample_doc}")
    print()
    
    # Test 3: Ingest document
    if client:
        print("3. Ingesting document...")
        result = ingest_document(sample_doc, metadata={"category": "strategy"})
        print(f"   Status: {result.get('message')}")
        print()
        
        # Test 4: Search knowledge
        print("4. Searching knowledge base...")
        results = search_knowledge("What are our strategic goals?", top_k=3)
        if results:
            print(f"   Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['text'][:80]}...")
        print()
        
        # Test 5: List documents
        print("5. Listing documents...")
        docs = list_documents()
        print(f"   Total documents: {len(docs)}")
        for doc in docs:
            print(f"      • {doc['filename']}: {doc['chunk_count']} chunks")
        print()
        
        # Test 6: Get stats
        print("6. Knowledge base statistics...")
        stats = get_knowledge_stats()
        print(f"   Documents: {stats['document_count']}")
        print(f"   Chunks: {stats['chunk_count']}")
        print()
    
    print("="*70)
    print("✅ Knowledge Fusion ready")
    print("="*70)
