# RAG (Retrieval-Augmented Generation) System for CI&T Flow GenAI Chatbot

This directory contains the implementation of our Retrieval-Augmented Generation (RAG) system, which enhances Large Language Model (LLM) responses with relevant information from our document collection.

## Architecture Overview

Our RAG system consists of five main components:

1. **Document Loading**: Ingests documents from various file formats
2. **Document Processing**: Splits documents into manageable chunks
3. **Embedding Generation**: Creates vector representations of text
4. **Vector Store**: Persists embeddings and enables efficient retrieval
5. **RAG Manager**: Orchestrates the workflow and enhances LLM responses

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │     │                 │
│  Document       │────▶│  Document       │────▶│  Embedding      │────▶│  Vector         │────▶│  RAG            │
│  Loader         │     │  Processor      │     │  Manager        │     │  Store          │     │  Manager        │
│                 │     │                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
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

### VectorStore (`vector_store.py`)

Stores and retrieves document embeddings using Chroma.

- **Features**:
  - Persistent storage of embeddings on disk
  - Efficient similarity search
  - Metadata filtering
  - Resource management with proper cleanup

```python
# Example usage
vector_store = VectorStore(persist_directory="./data/vector_db")
vector_store.add_documents(documents)
results = vector_store.similarity_search("What is the company policy on remote work?", k=3)
```

### RAGManager (`rag_manager.py`)

Orchestrates the entire RAG workflow and provides high-level APIs.

- **Features**:
  - Document statistics collection
  - Document loading and processing
  - Embedding initialization
  - Vector store management
  - Semantic search for relevant documents
  - Integration with LLM generation
  - Conversation history support

```python
# Example usage
rag_manager = RAGManager()
stats = rag_manager.get_document_stats()
documents = rag_manager.load_and_process_documents(index_to_vector_store=True)
relevant_docs = rag_manager.retrieve_relevant_documents("What is the company policy on remote work?")
```

## Workflow

### 1. Document Ingestion

When the system starts (if auto-indexing is enabled) or when triggered via the `/api/rag/process` or `/api/rag/reindex` endpoints:

1. The `RAGManager` uses `DocumentLoader` to scan the configured directory
2. Documents are loaded based on their file type
3. The `DocumentProcessor` splits documents into chunks
4. The `VectorStore` creates embeddings and stores them persistently
5. Chunks and their embeddings are available for retrieval

### 2. Query Processing

When a user query is received via the `/api/generate` endpoint:

1. The query is embedded using the same embedding model
2. The `VectorStore` performs similarity search to find relevant documents
3. The most relevant document chunks are retrieved
4. These chunks are used to enhance the prompt or system message sent to the LLM
5. The LLM generates a response based on both the query and the retrieved context

### 3. Conversation Support

For multi-turn conversations:

1. The last user message is used as the query for document retrieval
2. Retrieved context is injected into the system message
3. The full conversation history is preserved
4. The LLM responds with awareness of both the conversation history and the document context

## Vector Store Implementation

Our system uses Chroma for persistent vector storage:

- **Persistence**: Embeddings are stored on disk and persist between application restarts
- **Efficient Retrieval**: Fast similarity search using approximate nearest neighbors
- **Metadata Support**: Store and filter by document metadata
- **Resource Management**: Proper cleanup of resources during shutdown

## API Endpoints

The RAG system exposes several endpoints:

- `GET /api/rag/stats`: Get statistics about the documents in the RAG folder
- `GET /api/rag/process`: Load and process documents from the RAG folder
- `GET /api/rag/initialize-embeddings`: Initialize the embedding model
- `GET /api/rag/vector-store`: Get statistics about the vector store
- `POST /api/rag/query`: Query the vector store for relevant documents
- `POST /api/rag/reindex`: Reindex all documents in the RAG folder
- `DELETE /api/rag/vector-store`: Clear all documents from the vector store
- `POST /api/generate`: Generate text with RAG enhancement

## Configuration

The RAG system can be configured through environment variables in your `.env` file:

| Environment Variable | Description | Default | Impact of Changes |
|---------------------|-------------|---------|------------------|
| `APP_RAG_DOCUMENTS_PATH` | Directory where your documents are stored | `"./data/rag_documents"` | Changing this will point the system to a different document collection |
| `APP_RAG_CHUNK_SIZE` | Size of document chunks in characters | `1000` | Smaller chunks increase retrieval granularity but may lose context; larger chunks preserve more context but may reduce retrieval precision |
| `APP_RAG_CHUNK_OVERLAP` | Overlap between consecutive chunks | `200` | More overlap helps maintain context across chunk boundaries but increases storage requirements |
| `APP_RAG_EMBEDDING_MODEL` | Hugging Face model for embeddings | `"sentence-transformers/all-MiniLM-L6-v2"` | Different models offer trade-offs between speed, accuracy, and vector dimensions |
| `APP_VECTOR_STORE_DIRECTORY` | Directory for storing vector embeddings | `"./data/vector_db"` | Changing this will create a new vector store in the specified location |
| `APP_AUTO_INDEX_ON_STARTUP` | Whether to automatically index documents on startup | `false` | Set to `true` to automatically index documents when the application starts |

### After Changing Settings

After modifying settings in your `.env` file:

1. Restart the application for the changes to take effect
2. Re-process your documents if you changed `APP_RAG_CHUNK_SIZE` or `APP_RAG_CHUNK_OVERLAP`
3. Re-initialize embeddings if you changed `APP_RAG_EMBEDDING_MODEL`

You can do this through the API endpoints:
- `POST /api/rag/reindex?force=true` to re-process and re-index all documents
- `GET /api/rag/initialize-embeddings` to re-initialize the embedding model

## Future Enhancements

Potential improvements to the RAG system:

1. **Alternative Vector Stores**: Support for FAISS, Pinecone, or other vector databases
2. **Hybrid Search**: Combine semantic search with keyword-based search
3. **Advanced Metadata Filtering**: More sophisticated filtering by document source, date, or other metadata
4. **Feedback Loop**: Incorporate user feedback to improve retrieval quality
5. **Streaming Responses**: Support streaming for more responsive user experience
6. **Document Refresh**: Automatic detection and processing of new or updated documents

## References

- [LangChain Documentation](https://python.langchain.com/docs/modules/data_connection/retrievers/)
- [Hugging Face Sentence Transformers](https://www.sbert.net/)
- [Chroma Vector Database](https://www.trychroma.com/)
- [RAG Paper: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)