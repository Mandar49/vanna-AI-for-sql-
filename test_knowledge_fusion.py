"""
Test suite for Knowledge Fusion Layer (Phase 5C)
Tests document ingestion, retrieval, and RAG capabilities.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_knowledge_fusion_initialization():
    """Test 1: Knowledge fusion initialization."""
    print("\n" + "="*70)
    print("TEST 1: Knowledge Fusion Initialization")
    print("="*70)
    
    try:
        from knowledge_fusion import _get_chroma_client, get_knowledge_stats
        
        # Initialize client
        client = _get_chroma_client()
        
        if client:
            print("✓ ChromaDB client initialized")
            
            # Get stats
            stats = get_knowledge_stats()
            print(f"✓ Knowledge base stats: {stats}")
            
            return True
        else:
            print("⚠ ChromaDB not available (install with: pip install chromadb)")
            return False
            
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False


def test_document_ingestion():
    """Test 2: Document ingestion."""
    print("\n" + "="*70)
    print("TEST 2: Document Ingestion")
    print("="*70)
    
    try:
        from knowledge_fusion import ingest_document, _ensure_knowledge_dir
        
        # Create test document
        _ensure_knowledge_dir()
        test_doc_path = "./knowledge/test_business_plan.txt"
        
        with open(test_doc_path, 'w', encoding='utf-8') as f:
            f.write("""
            Executive Business Plan 2025
            
            Mission Statement:
            To deliver innovative solutions that transform business operations
            and drive sustainable growth for our clients.
            
            Strategic Objectives:
            1. Expand market presence in North America by 40%
            2. Launch 5 new AI-powered products
            3. Achieve 95% customer satisfaction rating
            4. Increase revenue by 50% year-over-year
            
            Key Initiatives:
            - Digital transformation program
            - Customer success platform
            - Innovation lab establishment
            - Strategic partnerships
            
            Financial Targets:
            - Revenue: $50M
            - Profit Margin: 25%
            - R&D Investment: 15% of revenue
            
            Market Analysis:
            The AI business intelligence market is growing at 30% CAGR.
            Our competitive advantage lies in offline-first architecture
            and executive-focused features.
            """)
        
        print(f"✓ Test document created: {test_doc_path}")
        
        # Ingest document
        result = ingest_document(
            test_doc_path,
            metadata={
                "category": "strategy",
                "year": "2025",
                "department": "Executive"
            }
        )
        
        if result["success"]:
            print(f"✓ Document ingested successfully")
            print(f"  - Document ID: {result.get('document_id')}")
            print(f"  - Chunks created: {result.get('chunks')}")
            return True
        else:
            print(f"✗ Ingestion failed: {result['message']}")
            return False
            
    except Exception as e:
        print(f"✗ Document ingestion test failed: {e}")
        return False


def test_knowledge_search():
    """Test 3: Knowledge search and retrieval."""
    print("\n" + "="*70)
    print("TEST 3: Knowledge Search")
    print("="*70)
    
    try:
        from knowledge_fusion import search_knowledge
        
        # Test queries
        test_queries = [
            "What are our strategic objectives?",
            "What is our revenue target?",
            "Tell me about market analysis",
            "What are the key initiatives?"
        ]
        
        all_passed = True
        
        for query in test_queries:
            print(f"\nQuery: '{query}'")
            results = search_knowledge(query, top_k=3)
            
            if results:
                print(f"✓ Found {len(results)} results")
                for i, result in enumerate(results, 1):
                    text_preview = result['text'][:100].replace('\n', ' ')
                    print(f"  {i}. {text_preview}...")
                    print(f"     Source: {result['metadata'].get('filename', 'unknown')}")
            else:
                print(f"⚠ No results found")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Knowledge search test failed: {e}")
        return False


def test_document_listing():
    """Test 4: List documents in knowledge base."""
    print("\n" + "="*70)
    print("TEST 4: Document Listing")
    print("="*70)
    
    try:
        from knowledge_fusion import list_documents
        
        documents = list_documents()
        
        if documents:
            print(f"✓ Found {len(documents)} documents in knowledge base:")
            for doc in documents:
                print(f"  • {doc['filename']}")
                print(f"    - Source: {doc['source']}")
                print(f"    - Chunks: {doc['chunk_count']}")
                print(f"    - Ingested: {doc['ingested_at']}")
            return True
        else:
            print("⚠ No documents found in knowledge base")
            return False
            
    except Exception as e:
        print(f"✗ Document listing test failed: {e}")
        return False


def test_knowledge_stats():
    """Test 5: Knowledge base statistics."""
    print("\n" + "="*70)
    print("TEST 5: Knowledge Base Statistics")
    print("="*70)
    
    try:
        from knowledge_fusion import get_knowledge_stats
        
        stats = get_knowledge_stats()
        
        print(f"Knowledge Base Statistics:")
        print(f"  • Available: {stats.get('available', False)}")
        print(f"  • Documents: {stats.get('document_count', 0)}")
        print(f"  • Chunks: {stats.get('chunk_count', 0)}")
        print(f"  • Collection: {stats.get('collection_name', 'N/A')}")
        
        if stats.get('available'):
            print("✓ Knowledge base is operational")
            return True
        else:
            print("⚠ Knowledge base not available")
            return False
            
    except Exception as e:
        print(f"✗ Statistics test failed: {e}")
        return False


def test_orchestrator_integration():
    """Test 6: Orchestrator integration with knowledge fusion."""
    print("\n" + "="*70)
    print("TEST 6: Orchestrator Integration")
    print("="*70)
    
    try:
        from orchestrator import execute_command
        
        # Test document query command
        test_commands = [
            "query document: strategic objectives",
            "search knowledge: revenue target",
            "find document: market analysis"
        ]
        
        all_passed = True
        
        for command in test_commands:
            print(f"\nCommand: '{command}'")
            result = execute_command(command)
            
            print(f"  Status: {result['status']}")
            print(f"  Message: {result['message']}")
            
            if result['status'] == 'success':
                outputs = result.get('outputs', {})
                results = outputs.get('results', [])
                print(f"  Results: {len(results)} documents found")
                
                for i, doc_result in enumerate(results[:2], 1):
                    print(f"    {i}. {doc_result['source']}: {doc_result['text'][:80]}...")
            else:
                print(f"  ⚠ Command failed")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Orchestrator integration test failed: {e}")
        return False


def test_multiple_document_types():
    """Test 7: Ingestion of multiple document types."""
    print("\n" + "="*70)
    print("TEST 7: Multiple Document Types")
    print("="*70)
    
    try:
        from knowledge_fusion import ingest_document, _ensure_knowledge_dir
        
        _ensure_knowledge_dir()
        
        # Test different file types
        test_files = []
        
        # 1. Markdown file
        md_path = "./knowledge/test_readme.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write("""
# Product Documentation

## Overview
Our AI-powered business intelligence platform provides real-time insights.

## Features
- Offline operation
- Voice interface
- Automated reporting
- Profile management

## Installation
```bash
pip install -r requirements.txt
```
            """)
        test_files.append(("Markdown", md_path))
        
        # 2. Python file
        py_path = "./knowledge/test_code.py"
        with open(py_path, 'w', encoding='utf-8') as f:
            f.write("""
def calculate_revenue(sales, costs):
    '''Calculate net revenue.'''
    return sales - costs

def growth_rate(current, previous):
    '''Calculate growth rate percentage.'''
    return ((current - previous) / previous) * 100
            """)
        test_files.append(("Python", py_path))
        
        # 3. JSON file
        json_path = "./knowledge/test_config.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write("""
{
  "company": "AI Solutions Inc",
  "departments": ["Sales", "Marketing", "Finance", "HR"],
  "fiscal_year": 2025,
  "targets": {
    "revenue": 50000000,
    "growth": 0.5,
    "customers": 1000
  }
}
            """)
        test_files.append(("JSON", json_path))
        
        # Ingest all files
        all_passed = True
        
        for file_type, file_path in test_files:
            print(f"\nIngesting {file_type} file: {os.path.basename(file_path)}")
            result = ingest_document(file_path, metadata={"type": file_type})
            
            if result["success"]:
                print(f"  ✓ Ingested successfully ({result.get('chunks')} chunks)")
            else:
                print(f"  ✗ Ingestion failed: {result['message']}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Multiple document types test failed: {e}")
        return False


def test_rag_workflow():
    """Test 8: Complete RAG workflow (Retrieval-Augmented Generation)."""
    print("\n" + "="*70)
    print("TEST 8: RAG Workflow")
    print("="*70)
    
    try:
        from knowledge_fusion import search_knowledge
        
        # Simulate RAG workflow
        user_question = "What are our financial targets for 2025?"
        
        print(f"User Question: '{user_question}'")
        print("\nStep 1: Retrieve relevant context...")
        
        # Retrieve relevant documents
        context_docs = search_knowledge(user_question, top_k=3)
        
        if not context_docs:
            print("⚠ No context retrieved")
            return False
        
        print(f"✓ Retrieved {len(context_docs)} relevant chunks")
        
        # Build context
        print("\nStep 2: Build context from retrieved documents...")
        context = "\n\n".join([doc['text'] for doc in context_docs])
        print(f"✓ Context built ({len(context)} characters)")
        
        # Simulate augmented response (in real scenario, this would go to LLM)
        print("\nStep 3: Generate augmented response...")
        print("✓ Context ready for LLM augmentation")
        print("\nRetrieved Context Preview:")
        for i, doc in enumerate(context_docs, 1):
            print(f"\n  Chunk {i} (from {doc['metadata'].get('filename', 'unknown')}):")
            print(f"  {doc['text'][:150]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ RAG workflow test failed: {e}")
        return False


def run_all_tests():
    """Run all knowledge fusion tests."""
    print("\n" + "="*70)
    print("KNOWLEDGE FUSION TEST SUITE (Phase 5C)")
    print("="*70)
    
    tests = [
        ("Initialization", test_knowledge_fusion_initialization),
        ("Document Ingestion", test_document_ingestion),
        ("Knowledge Search", test_knowledge_search),
        ("Document Listing", test_document_listing),
        ("Knowledge Stats", test_knowledge_stats),
        ("Orchestrator Integration", test_orchestrator_integration),
        ("Multiple Document Types", test_multiple_document_types),
        ("RAG Workflow", test_rag_workflow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠ {total_count - passed_count} test(s) failed")
    
    print("="*70)
    
    return passed_count == total_count


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
