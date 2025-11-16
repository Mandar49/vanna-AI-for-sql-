# Knowledge Fusion Layer Guide (Phase 5C)

## Overview

The Knowledge Fusion Layer provides **local document RAG (Retrieval-Augmented Generation)** capabilities for the Executive Intelligence System. It enables offline document ingestion, vectorization, and semantic search without external API calls.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│           KNOWLEDGE FUSION LAYER (Phase 5C)             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │   Document   │───▶│ Vectorization│───▶│ ChromaDB │  │
│  │   Ingestion  │    │   (MiniLM)   │    │  Storage │  │
│  └──────────────┘    └──────────────┘    └──────────┘  │
│         │                                       │        │
│         │                                       │        │
│         ▼                                       ▼        │
│  ┌──────────────┐                      ┌──────────────┐ │
│  │   Chunking   │                      │   Semantic   │ │
│  │   Strategy   │                      │    Search    │ │
│  └──────────────┘                      └──────────────┘ │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Key Features

### 1. **Offline Operation**
- No external API calls required
- Local vector storage with ChromaDB
- Sentence-transformers for embeddings (MiniLM)

### 2. **Multi-Format Support**
- Plain text (.txt, .md, .py, .js, .json, .csv)
- PDF documents (with PyPDF2)
- Word documents (with python-docx)

### 3. **Intelligent Chunking**
- Configurable chunk size (default: 500 characters)
- Overlapping chunks for context preservation (default: 50 characters)
- Maintains document metadata

### 4. **Semantic Search**
- Vector similarity search
- Configurable result count (top_k)
- Metadata filtering support
- Distance-based relevance scoring

## Installation

```bash
# Install required dependencies
pip install chromadb>=0.4.0
pip install sentence-transformers>=2.2.0

# Optional: For additional document formats
pip install PyPDF2>=3.0.0
pip install python-docx>=0.8.11
```

## Core Functions

### 1. Document Ingestion

```python
from knowledge_fusion import ingest_document

# Ingest a document
result = ingest_document(
    "./docs/business_plan.pdf",
    metadata={
        "category": "strategy",
        "author": "CEO",
        "year": "2025"
    }
)

print(f"Status: {result['success']}")
print(f"Chunks: {result['chunks']}")
print(f"Document ID: {result['document_id']}")
```

**Output:**
```
Status: True
Chunks: 15
Document ID: 4c5b1949a92cfed3b4975554da16f0bc
```

### 2. Knowledge Search

```python
from knowledge_fusion import search_knowledge

# Search for relevant information
results = search_knowledge(
    "What are our strategic objectives?",
    top_k=5
)

for result in results:
    print(f"Source: {result['metadata']['filename']}")
    print(f"Text: {result['text'][:100]}...")
    print(f"Relevance: {1.0 - result['distance']:.2%}")
    print()
```

**Output:**
```
Source: business_plan.pdf
Text: Strategic Objectives:
1. Expand market presence by 40%
2. Launch 5 new products...
Relevance: 95.3%
```

### 3. List Documents

```python
from knowledge_fusion import list_documents

# Get all documents in knowledge base
docs = list_documents()

for doc in docs:
    print(f"{doc['filename']}: {doc['chunk_count']} chunks")
    print(f"  Ingested: {doc['ingested_at']}")
```

### 4. Knowledge Statistics

```python
from knowledge_fusion import get_knowledge_stats

# Get knowledge base statistics
stats = get_knowledge_stats()

print(f"Documents: {stats['document_count']}")
print(f"Chunks: {stats['chunk_count']}")
print(f"Available: {stats['available']}")
```

### 5. Delete Document

```python
from knowledge_fusion import delete_document

# Remove a document from knowledge base
success = delete_document("./docs/old_plan.pdf")

if success:
    print("Document deleted successfully")
```

## Orchestrator Integration

The Knowledge Fusion Layer integrates seamlessly with the Orchestrator:

```python
from orchestrator import execute_command

# Query documents via natural language
result = execute_command("query document: strategic objectives")

print(f"Status: {result['status']}")
print(f"Found: {result['outputs']['count']} results")

for doc in result['outputs']['results']:
    print(f"- {doc['source']}: {doc['text'][:80]}...")
```

**Supported Commands:**
- `"query document: <search query>"`
- `"search knowledge: <search query>"`
- `"find document: <search query>"`

## Dashboard Integration

### Upload Documents

The dashboard provides a web interface for document management:

1. **Upload Button**: Click to select and upload documents
2. **Document List**: View all ingested documents
3. **Search Interface**: Query the knowledge base

### API Endpoints

#### POST /dashboard/upload_knowledge
Upload a document to the knowledge base.

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/dashboard/upload_knowledge', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log(`Uploaded: ${data.chunks} chunks`);
});
```

#### GET /dashboard/list_knowledge
List all documents in the knowledge base.

```javascript
fetch('/dashboard/list_knowledge')
.then(response => response.json())
.then(data => {
    console.log(`Documents: ${data.documents.length}`);
    console.log(`Total chunks: ${data.stats.chunk_count}`);
});
```

#### GET /dashboard/search_knowledge?query=<query>
Search the knowledge base.

```javascript
fetch('/dashboard/search_knowledge?query=strategic+objectives')
.then(response => response.json())
.then(data => {
    data.results.forEach(result => {
        console.log(`${result.source}: ${result.text}`);
    });
});
```

## RAG Workflow

Complete Retrieval-Augmented Generation workflow:

```python
from knowledge_fusion import search_knowledge

# Step 1: User asks a question
user_question = "What are our financial targets for 2025?"

# Step 2: Retrieve relevant context
context_docs = search_knowledge(user_question, top_k=3)

# Step 3: Build context for LLM
context = "\n\n".join([doc['text'] for doc in context_docs])

# Step 4: Augment prompt with context
augmented_prompt = f"""
Context from knowledge base:
{context}

Question: {user_question}

Answer based on the context above:
"""

# Step 5: Send to LLM (Ollama, etc.)
# response = llm.generate(augmented_prompt)
```

## Storage Structure

```
./knowledge/
├── chroma.sqlite3          # ChromaDB database
├── uploads/                # Uploaded documents
│   ├── business_plan.pdf
│   ├── strategy_doc.docx
│   └── market_analysis.txt
└── sample_doc.txt          # Test documents
```

## Configuration

### Chunk Size
Adjust chunk size for different document types:

```python
from knowledge_fusion import _chunk_text

# Smaller chunks for code
chunks = _chunk_text(code_text, chunk_size=300, overlap=30)

# Larger chunks for narrative documents
chunks = _chunk_text(doc_text, chunk_size=800, overlap=100)
```

### Search Parameters

```python
# More results
results = search_knowledge(query, top_k=10)

# Filter by metadata
results = search_knowledge(
    query,
    top_k=5,
    filter_metadata={"category": "strategy"}
)
```

## Performance Considerations

### Indexing Speed
- **Small documents** (<10 pages): ~1-2 seconds
- **Medium documents** (10-50 pages): ~5-10 seconds
- **Large documents** (>50 pages): ~15-30 seconds

### Search Speed
- **Typical query**: <100ms
- **Large knowledge base** (1000+ chunks): <500ms

### Storage Requirements
- **Text chunks**: ~1KB per chunk
- **Embeddings**: ~1.5KB per chunk (384-dim MiniLM)
- **Total**: ~2.5KB per chunk

**Example:** 100 documents × 20 chunks = 2000 chunks = ~5MB storage

## Best Practices

### 1. Document Organization
```python
# Use consistent metadata
ingest_document(
    "./docs/q1_report.pdf",
    metadata={
        "type": "report",
        "quarter": "Q1",
        "year": "2025",
        "department": "Finance"
    }
)
```

### 2. Chunk Size Selection
- **Technical docs**: 300-500 characters
- **Business docs**: 500-800 characters
- **Code files**: 200-400 characters

### 3. Search Optimization
```python
# Use specific queries
results = search_knowledge("Q1 2025 revenue targets")  # Good
results = search_knowledge("revenue")  # Too broad

# Adjust top_k based on use case
results = search_knowledge(query, top_k=3)  # Quick answers
results = search_knowledge(query, top_k=10)  # Comprehensive research
```

### 4. Metadata Filtering
```python
# Filter by category
results = search_knowledge(
    "strategic goals",
    filter_metadata={"category": "strategy"}
)

# Filter by date
results = search_knowledge(
    "quarterly results",
    filter_metadata={"year": "2025", "quarter": "Q1"}
)
```

## Testing

Run the comprehensive test suite:

```bash
python test_knowledge_fusion.py
```

**Test Coverage:**
- ✓ Initialization
- ✓ Document Ingestion
- ✓ Knowledge Search
- ✓ Document Listing
- ✓ Knowledge Stats
- ✓ Orchestrator Integration
- ✓ Multiple Document Types
- ✓ RAG Workflow

## Troubleshooting

### ChromaDB Not Available
```
✗ ChromaDB not installed. Install with: pip install chromadb
```
**Solution:** `pip install chromadb sentence-transformers`

### No Results Found
```python
results = search_knowledge("query")
# Returns: []
```
**Possible causes:**
1. No documents ingested
2. Query too specific
3. Wrong metadata filter

**Solution:**
```python
# Check knowledge base
stats = get_knowledge_stats()
print(f"Documents: {stats['document_count']}")

# Try broader query
results = search_knowledge("broader query", top_k=10)
```

### Slow Ingestion
**Causes:**
- Large documents
- Many chunks
- First-time model download

**Solution:**
- Use smaller chunk sizes
- Ingest documents in batches
- Pre-download sentence-transformers model

## Integration Examples

### Example 1: Executive Dashboard
```python
# Upload business plan
result = ingest_document(
    "./docs/business_plan_2025.pdf",
    metadata={"type": "strategy", "year": "2025"}
)

# Query via dashboard
results = search_knowledge("What are our growth targets?")

# Display in dashboard
for result in results:
    print(f"📄 {result['metadata']['filename']}")
    print(f"   {result['text'][:150]}...")
```

### Example 2: Automated Reports
```python
# Search for relevant data
context = search_knowledge("Q1 financial performance", top_k=5)

# Build report with context
from report_generator import build_executive_report

report = build_executive_report(
    title="Q1 Performance Summary",
    question="What was our Q1 performance?",
    sql="--",
    df=None,
    insights="\n\n".join([doc['text'] for doc in context]),
    charts=None
)
```

### Example 3: Voice Interface
```python
# Voice query
from voice_interface import listen_for_command

command = listen_for_command()  # "What are our strategic goals?"

# Search knowledge
results = search_knowledge(command, top_k=3)

# Speak results
from voice_interface import speak_text

for result in results:
    speak_text(result['text'])
```

## Future Enhancements

### Planned Features
- [ ] Multi-language support
- [ ] Image/diagram extraction from PDFs
- [ ] Automatic document summarization
- [ ] Knowledge graph visualization
- [ ] Incremental updates (re-indexing)
- [ ] Export/import knowledge base

### Advanced RAG Techniques
- [ ] Hybrid search (keyword + semantic)
- [ ] Re-ranking with cross-encoders
- [ ] Query expansion
- [ ] Context compression

## Summary

The Knowledge Fusion Layer provides:

✅ **Offline document RAG** - No external APIs required  
✅ **Multi-format support** - Text, PDF, Word, code files  
✅ **Semantic search** - Vector-based retrieval  
✅ **Dashboard integration** - Web UI for document management  
✅ **Orchestrator integration** - Natural language queries  
✅ **Comprehensive testing** - Full test suite included  

**Storage:** `./knowledge/` directory  
**Dependencies:** ChromaDB, sentence-transformers  
**Performance:** <100ms search, ~2.5KB per chunk  

---

**Phase 5C Complete** ✅  
Next: Advanced analytics and knowledge graph features
