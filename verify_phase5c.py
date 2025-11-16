"""
Phase 5C Verification Script
Verifies Knowledge Fusion Layer integration with all subsystems.
"""

import os
import sys

def verify_knowledge_fusion():
    """Verify knowledge fusion module."""
    print("\n" + "="*70)
    print("PHASE 5C VERIFICATION - Knowledge Fusion Layer")
    print("="*70)
    
    results = []
    
    # Test 1: Module imports
    print("\n1. Verifying module imports...")
    try:
        from knowledge_fusion import (
            ingest_document,
            search_knowledge,
            list_documents,
            get_knowledge_stats,
            delete_document
        )
        print("   ✓ All knowledge_fusion functions imported")
        results.append(("Module Imports", True))
    except Exception as e:
        print(f"   ✗ Import failed: {e}")
        results.append(("Module Imports", False))
        return results
    
    # Test 2: ChromaDB availability
    print("\n2. Checking ChromaDB availability...")
    try:
        from knowledge_fusion import _get_chroma_client
        client = _get_chroma_client()
        if client:
            print("   ✓ ChromaDB initialized successfully")
            results.append(("ChromaDB", True))
        else:
            print("   ⚠ ChromaDB not available (install: pip install chromadb)")
            results.append(("ChromaDB", False))
    except Exception as e:
        print(f"   ✗ ChromaDB check failed: {e}")
        results.append(("ChromaDB", False))
    
    # Test 3: Document ingestion
    print("\n3. Testing document ingestion...")
    try:
        from knowledge_fusion import ingest_document, _ensure_knowledge_dir
        
        _ensure_knowledge_dir()
        test_file = "./knowledge/verify_test.txt"
        
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("This is a test document for Phase 5C verification.")
        
        result = ingest_document(test_file, metadata={"test": "phase5c"})
        
        if result["success"]:
            print(f"   ✓ Document ingested ({result.get('chunks')} chunks)")
            results.append(("Document Ingestion", True))
        else:
            print(f"   ✗ Ingestion failed: {result['message']}")
            results.append(("Document Ingestion", False))
    except Exception as e:
        print(f"   ✗ Ingestion test failed: {e}")
        results.append(("Document Ingestion", False))
    
    # Test 4: Knowledge search
    print("\n4. Testing knowledge search...")
    try:
        from knowledge_fusion import search_knowledge
        
        search_results = search_knowledge("test document", top_k=3)
        
        if search_results:
            print(f"   ✓ Search returned {len(search_results)} results")
            results.append(("Knowledge Search", True))
        else:
            print("   ⚠ No search results (knowledge base may be empty)")
            results.append(("Knowledge Search", False))
    except Exception as e:
        print(f"   ✗ Search test failed: {e}")
        results.append(("Knowledge Search", False))
    
    # Test 5: Orchestrator integration
    print("\n5. Testing orchestrator integration...")
    try:
        from orchestrator import execute_command
        
        result = execute_command("query document: test")
        
        if result["status"] == "success":
            print(f"   ✓ Orchestrator query successful")
            print(f"     Found: {result['outputs'].get('count', 0)} results")
            results.append(("Orchestrator Integration", True))
        else:
            print(f"   ✗ Orchestrator query failed: {result['message']}")
            results.append(("Orchestrator Integration", False))
    except Exception as e:
        print(f"   ✗ Orchestrator test failed: {e}")
        results.append(("Orchestrator Integration", False))
    
    # Test 6: Dashboard endpoints
    print("\n6. Verifying dashboard endpoints...")
    try:
        from dashboard_gateway import (
            upload_knowledge,
            list_knowledge,
            search_knowledge_endpoint
        )
        print("   ✓ All dashboard endpoints available")
        results.append(("Dashboard Endpoints", True))
    except Exception as e:
        print(f"   ✗ Dashboard verification failed: {e}")
        results.append(("Dashboard Endpoints", False))
    
    # Test 7: Knowledge statistics
    print("\n7. Checking knowledge base statistics...")
    try:
        from knowledge_fusion import get_knowledge_stats
        
        stats = get_knowledge_stats()
        
        print(f"   Documents: {stats.get('document_count', 0)}")
        print(f"   Chunks: {stats.get('chunk_count', 0)}")
        print(f"   Available: {stats.get('available', False)}")
        
        if stats.get('available'):
            print("   ✓ Knowledge base operational")
            results.append(("Knowledge Stats", True))
        else:
            print("   ⚠ Knowledge base not available")
            results.append(("Knowledge Stats", False))
    except Exception as e:
        print(f"   ✗ Stats check failed: {e}")
        results.append(("Knowledge Stats", False))
    
    # Test 8: File format support
    print("\n8. Testing file format support...")
    try:
        from knowledge_fusion import _extract_text_from_file, _ensure_knowledge_dir
        
        _ensure_knowledge_dir()
        formats_tested = []
        
        # Test .txt
        txt_file = "./knowledge/test.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("Test text file")
        text = _extract_text_from_file(txt_file)
        if text:
            formats_tested.append("txt")
        
        # Test .md
        md_file = "./knowledge/test.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write("# Test markdown")
        text = _extract_text_from_file(md_file)
        if text:
            formats_tested.append("md")
        
        # Test .py
        py_file = "./knowledge/test.py"
        with open(py_file, 'w', encoding='utf-8') as f:
            f.write("# Test python\nprint('hello')")
        text = _extract_text_from_file(py_file)
        if text:
            formats_tested.append("py")
        
        print(f"   ✓ Supported formats: {', '.join(formats_tested)}")
        results.append(("File Format Support", len(formats_tested) >= 3))
    except Exception as e:
        print(f"   ✗ Format test failed: {e}")
        results.append(("File Format Support", False))
    
    return results


def print_summary(results):
    """Print verification summary."""
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, status in results if status)
    total = len(results)
    
    for test_name, status in results:
        symbol = "✓" if status else "✗"
        print(f"{symbol} {test_name}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 Phase 5C - Knowledge Fusion Layer: FULLY OPERATIONAL")
        print("\nCapabilities:")
        print("  • Local document RAG (retrieval-augmented reasoning)")
        print("  • Offline vectorization with MiniLM")
        print("  • ChromaDB vector storage")
        print("  • Multi-format document support")
        print("  • Orchestrator integration")
        print("  • Dashboard web interface")
        print("  • Semantic search")
    else:
        print(f"\n⚠ {total - passed} check(s) failed")
        print("\nRecommendations:")
        if not any(status for name, status in results if "ChromaDB" in name):
            print("  • Install ChromaDB: pip install chromadb sentence-transformers")
        print("  • Run: python test_knowledge_fusion.py")
        print("  • Check: KNOWLEDGE_FUSION_GUIDE.md")
    
    print("="*70)


if __name__ == "__main__":
    results = verify_knowledge_fusion()
    print_summary(results)
    
    # Exit with appropriate code
    all_passed = all(status for _, status in results)
    sys.exit(0 if all_passed else 1)
