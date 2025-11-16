"""
Knowledge Fusion Layer Demo
Demonstrates the complete RAG workflow with Phase 5C implementation.
"""

import os
from pathlib import Path


def demo_knowledge_fusion():
    """Demonstrate knowledge fusion capabilities."""
    print("\n" + "="*70)
    print("KNOWLEDGE FUSION LAYER DEMO (Phase 5C)")
    print("="*70)
    
    # Import modules
    from knowledge_fusion import (
        ingest_document,
        search_knowledge,
        list_documents,
        get_knowledge_stats,
        _ensure_knowledge_dir
    )
    from orchestrator import execute_command
    
    # Step 1: Create sample documents
    print("\n📄 Step 1: Creating sample business documents...")
    _ensure_knowledge_dir()
    
    # Business strategy document
    strategy_doc = "./knowledge/demo_strategy.txt"
    with open(strategy_doc, 'w', encoding='utf-8') as f:
        f.write("""
        2025 Business Strategy
        
        Vision: Become the leading AI-powered business intelligence platform
        
        Strategic Pillars:
        1. Innovation - Develop cutting-edge AI features
        2. Customer Success - Achieve 98% satisfaction rate
        3. Market Expansion - Enter 5 new markets
        4. Operational Excellence - Reduce costs by 20%
        
        Financial Targets:
        - Revenue: $75M (50% growth)
        - Profit Margin: 30%
        - R&D Investment: $15M
        
        Key Initiatives:
        - Launch AI-powered analytics suite
        - Expand sales team by 40%
        - Open 3 new regional offices
        - Implement customer success program
        """)
    
    # Product roadmap
    roadmap_doc = "./knowledge/demo_roadmap.md"
    with open(roadmap_doc, 'w', encoding='utf-8') as f:
        f.write("""
# Product Roadmap 2025

## Q1 2025
- Launch Knowledge Fusion Layer
- Implement RAG capabilities
- Release offline document search

## Q2 2025
- Advanced analytics dashboard
- Multi-language support
- Mobile app beta

## Q3 2025
- Knowledge graph visualization
- Automated insights generation
- API marketplace launch

## Q4 2025
- Enterprise features
- Advanced security controls
- Global deployment
        """)
    
    print("   ✓ Created 2 sample documents")
    
    # Step 2: Ingest documents
    print("\n📥 Step 2: Ingesting documents into knowledge base...")
    
    result1 = ingest_document(
        strategy_doc,
        metadata={"type": "strategy", "year": "2025"}
    )
    print(f"   ✓ Strategy document: {result1.get('chunks')} chunks")
    
    result2 = ingest_document(
        roadmap_doc,
        metadata={"type": "roadmap", "year": "2025"}
    )
    print(f"   ✓ Roadmap document: {result2.get('chunks')} chunks")
    
    # Step 3: View knowledge base stats
    print("\n📊 Step 3: Knowledge base statistics...")
    stats = get_knowledge_stats()
    print(f"   Total documents: {stats['document_count']}")
    print(f"   Total chunks: {stats['chunk_count']}")
    print(f"   Status: {'✓ Operational' if stats['available'] else '✗ Unavailable'}")
    
    # Step 4: Semantic search
    print("\n🔍 Step 4: Semantic search demonstrations...")
    
    queries = [
        "What are our financial targets?",
        "Tell me about Q2 2025 plans",
        "What are the strategic pillars?"
    ]
    
    for query in queries:
        print(f"\n   Query: '{query}'")
        results = search_knowledge(query, top_k=2)
        
        if results:
            for i, result in enumerate(results, 1):
                text_preview = result['text'][:80].replace('\n', ' ').strip()
                relevance = (1.0 - result['distance']) * 100 if result['distance'] else 100
                print(f"      {i}. [{relevance:.1f}%] {text_preview}...")
                print(f"         Source: {result['metadata'].get('filename', 'unknown')}")
    
    # Step 5: Orchestrator integration
    print("\n🎯 Step 5: Orchestrator integration...")
    
    commands = [
        "query document: revenue targets",
        "search knowledge: product roadmap Q3"
    ]
    
    for command in commands:
        print(f"\n   Command: '{command}'")
        result = execute_command(command)
        print(f"   Status: {result['status']}")
        print(f"   Found: {result['outputs'].get('count', 0)} results")
        
        if result['outputs'].get('results'):
            first_result = result['outputs']['results'][0]
            print(f"   Top result: {first_result['text'][:60]}...")
    
    # Step 6: RAG workflow
    print("\n🤖 Step 6: Complete RAG workflow...")
    
    user_question = "What are our key initiatives for 2025?"
    print(f"\n   User Question: '{user_question}'")
    
    # Retrieve context
    print("   → Retrieving relevant context...")
    context_docs = search_knowledge(user_question, top_k=3)
    print(f"   ✓ Retrieved {len(context_docs)} relevant chunks")
    
    # Build context
    context = "\n\n".join([doc['text'] for doc in context_docs])
    print(f"   ✓ Built context ({len(context)} characters)")
    
    # Simulate augmented prompt
    augmented_prompt = f"""
Context from knowledge base:
{context[:300]}...

Question: {user_question}

Answer based on the context above:
"""
    
    print("   ✓ Augmented prompt ready for LLM")
    print("\n   Context Preview:")
    for i, doc in enumerate(context_docs[:2], 1):
        preview = doc['text'][:100].replace('\n', ' ').strip()
        print(f"      {i}. {preview}...")
    
    # Step 7: List all documents
    print("\n📚 Step 7: Document inventory...")
    docs = list_documents()
    print(f"   Total documents in knowledge base: {len(docs)}")
    
    demo_docs = [d for d in docs if 'demo_' in d['filename']]
    if demo_docs:
        print("\n   Demo documents:")
        for doc in demo_docs:
            print(f"      • {doc['filename']} ({doc['chunk_count']} chunks)")
    
    # Summary
    print("\n" + "="*70)
    print("DEMO COMPLETE")
    print("="*70)
    print("\n✅ Knowledge Fusion Layer Capabilities Demonstrated:")
    print("   • Document ingestion (multiple formats)")
    print("   • Semantic search (vector similarity)")
    print("   • Orchestrator integration (natural language)")
    print("   • RAG workflow (retrieval-augmented generation)")
    print("   • Knowledge base management")
    print("\n💡 Next Steps:")
    print("   • Upload your own documents via dashboard")
    print("   • Try: python -m flask run (start web interface)")
    print("   • Query: execute_command('query document: <your query>')")
    print("   • Read: KNOWLEDGE_FUSION_GUIDE.md")
    print("="*70)


if __name__ == "__main__":
    try:
        demo_knowledge_fusion()
    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("  • Install dependencies: pip install chromadb sentence-transformers")
        print("  • Run tests: python test_knowledge_fusion.py")
        print("  • Check guide: KNOWLEDGE_FUSION_GUIDE.md")
