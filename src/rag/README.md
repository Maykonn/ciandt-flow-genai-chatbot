# RAG (Retrieval-Augmented Generation) System

This directory contains the implementation of our Retrieval-Augmented Generation (RAG) system, which enhances Large Language Model (LLM) responses with relevant information from our document collection.

## Architecture Overview

Our RAG system consists of four main components:

1. **Document Loading**: Ingests documents from various file formats
2. **Document Processing**: Splits documents into manageable chunks
3. **Embedding Generation**: Creates vector representations of text
4. **Retrieval & Generation**: Finds relevant documents and enhances LLM responses

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Document       │────▶│  Document       │────▶│  Embedding      │────▶│  RAG            │
│  Loader         │     │  Processor      │     │  Manager        │     │  Manager        │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Components in Detail

### DocumentLoader (`document_loader.py`)

Responsible for loading documents from the file system.

- **Supported File Types**: PDF, TXT (extensible to other formats)
- **Features**:
  - Automatic file type detection
  - Directory traversal
  - Error handling for unsupported file types

```python
# Example usage
loader = DocumentLoader(docs_path="./data/rag_documents")
documents = loader.load_documents()
```

### DocumentProcessor (`document_processor.py`)

Splits documents into smaller, manageable chunks for better retrieval.

- **Configuration**:
  - `chunk_size`: Size of each document chunk (default: 1000 characters)
  - `chunk_overlap`: Overlap between consecutive chunks (default: 200 characters)
- **Features**:
  - Recursive text splitting that respects semantic boundaries
  - Metadata preservation across chunks
  - Chunk ID assignment for tracking

```python
# Example usage
processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
chunks = processor.split_documents(documents)
```

### EmbeddingManager (`embedding_manager.py`)

Generates vector embeddings for text using pre-trained models.

- **Models**:
  - Default: `sentence-transformers/all-MiniLM-L6-v2`
  - Configurable through settings
- **Features**:
  - Lazy initialization of embedding models
  - Batch processing of documents
  - Error handling for embedding generation

```python
# Example usage
embedding_manager = EmbeddingManager(model_name="sentence-transformers/all-MiniLM-L6-v2")
embeddings = embedding_manager.get_embeddings(["This is a sample text"])
```

### RAGManager (`rag_manager.py`)

Orchestrates the entire RAG workflow and provides high-level APIs.

- **Features**:
  - Document statistics collection
  - Document loading and processing
  - Embedding initialization
  - Semantic search for relevant documents
  - Integration with LLM generation

```python
# Example usage
rag_manager = RAGManager()
stats = rag_manager.get_document_stats()
documents = rag_manager.load_and_process_documents()
relevant_docs = rag_manager.retrieve_relevant_documents("What is the company policy on remote work?")
```

## Workflow

### 1. Document Ingestion

When the system starts or when triggered via the `/api/rag/process` endpoint:

1. The `RAGManager` uses `DocumentLoader` to scan the configured directory
2. Documents are loaded based on their file type
3. The `DocumentProcessor` splits documents into chunks
4. Chunks are stored with their metadata for later retrieval

### 2. Embedding Generation

When initialized or when triggered via the `/api/rag/initialize-embeddings` endpoint:

1. The `EmbeddingManager` loads the configured embedding model
2. Document chunks can be embedded on-demand or pre-embedded

### 3. Query Processing

When a user query is received via the `/api/generate` endpoint:

1. The query is embedded using the same embedding model
2. Cosine similarity is calculated between the query embedding and all document embeddings
3. The most relevant document chunks are retrieved
4. These chunks are used to enhance the prompt sent to the LLM
5. The LLM generates a response based on both the query and the retrieved context

## Semantic Search Implementation

Our system uses cosine similarity to find relevant documents:

```python
def _cosine_similarity(self, vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    import numpy as np
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)
```

Documents are ranked by their similarity to the query, and the top-k most relevant documents are used to enhance the LLM prompt.

## API Endpoints

The RAG system exposes several endpoints:

- `GET /api/rag/stats`: Get statistics about the documents in the RAG folder
- `GET /api/rag/process`: Load and process documents from the RAG folder
- `GET /api/rag/initialize-embeddings`: Initialize the embedding model
- `POST /api/generate`: Generate text with RAG enhancement

## Configuration

The RAG system can be configured through environment variables in your `.env` file:

| Environment Variable | Description | Default | Impact of Changes |
|---------------------|-------------|---------|------------------|
| `APP_RAG_DOCUMENTS_PATH` | Directory where your documents are stored | `"./data/rag_documents"` | Changing this will point the system to a different document collection |
| `APP_RAG_CHUNK_SIZE` | Size of document chunks in characters | `1000` | Smaller chunks increase retrieval granularity but may lose context; larger chunks preserve more context but may reduce retrieval precision |
| `APP_RAG_CHUNK_OVERLAP` | Overlap between consecutive chunks | `200` | More overlap helps maintain context across chunk boundaries but increases storage requirements |
| `APP_RAG_EMBEDDING_MODEL` | Hugging Face model for embeddings | `"sentence-transformers/all-MiniLM-L6-v2"` | Different models offer trade-offs between speed, accuracy, and vector dimensions |

### After Changing Settings

After modifying settings in your `.env` file:

1. Restart the application for the changes to take effect
2. Re-process your documents if you changed `APP_RAG_CHUNK_SIZE` or `APP_RAG_CHUNK_OVERLAP`
3. Re-initialize embeddings if you changed `APP_RAG_EMBEDDING_MODEL`

You can do this through the API endpoints:
- `GET /api/rag/process` to re-process documents
- `GET /api/rag/initialize-embeddings` to re-initialize the embedding model

## Future Enhancements

Potential improvements to the RAG system:

1. **Persistent Vector Store**: Implement a database like FAISS, Chroma, or Pinecone
2. **Hybrid Search**: Combine semantic search with keyword-based search
3. **Metadata Filtering**: Allow filtering by document source, date, or other metadata
4. **Feedback Loop**: Incorporate user feedback to improve retrieval quality
5. **Streaming Responses**: Support streaming for more responsive user experience

## References

- [LangChain Documentation](https://python.langchain.com/docs/modules/data_connection/retrievers/)
- [Hugging Face Sentence Transformers](https://www.sbert.net/)
- [RAG Paper: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
