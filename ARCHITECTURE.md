# CI&T Flow GenAI Chatbot Architecture

This document provides an overview of the architecture for the CI&T Flow GenAI Chatbot, detailing its components, interactions, and data flow.

## Overview

The CI&T Flow GenAI Chatbot is designed to integrate with CI&T Flow APIs to provide advanced text generation capabilities using OpenAI's models. It leverages Retrieval-Augmented Generation (RAG) to enhance responses with relevant information from a document collection.

## High-Level Architecture

```
┌──────────────────────────┐
│      Client (Postman)    │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      FastAPI Backend     │
│  (ciandt-flow-genai-chatbot) │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│      CI&T Flow API       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│  Retrieval-Augmented Gen │
│        (RAG System)      │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     Chroma Vector Store  │
└──────────────────────────┘
```

## Components

### 1. FastAPI Backend

- **Purpose**: Serves as the main entry point for API requests, handling authentication, routing, and response generation.
- **Key Features**:
  - Authentication with CI&T Flow APIs
  - Token management and caching
  - Error handling and logging
  - Lifespan event handlers for resource management

### 2. CI&T Flow API

- **Purpose**: Provides access to GenAI Large Language Model capabilities.
- **Interactions**:
  - The backend authenticates and communicates with the Flow API to generate text.
  - Handles token-based authentication and request retries.

### 3. Retrieval-Augmented Generation (RAG) System

- **Purpose**: Enhances LLM responses with relevant information from a document collection.
- **Components**:
  - **DocumentLoader**: Loads documents from the file system.
  - **DocumentProcessor**: Splits documents into manageable chunks.
  - **EmbeddingManager**: Generates vector embeddings for text.
  - **VectorStore**: Stores and retrieves document embeddings using Chroma.
  - **RAGManager**: Orchestrates the RAG workflow and integrates with the LLM.

### 4. Chroma Vector Store

- **Purpose**: Provides persistent storage for document embeddings, enabling efficient retrieval.
- **Features**:
  - Persistent storage on disk
  - Efficient similarity search
  - Metadata filtering
  - Resource management with proper cleanup

## Data Flow

1. **Request Handling**:
   - The client sends a request to the FastAPI backend.
   - The backend authenticates the request and forwards it to the appropriate endpoint.

2. **Text Generation**:
   - For text generation requests, the backend communicates with the CI&T Flow API.
   - If RAG is enabled, the backend retrieves relevant documents from the vector store to enhance the prompt.

3. **RAG Workflow**:
   - Documents are loaded and processed into chunks.
   - Chunks are embedded and stored in the vector store.
   - During query processing, relevant chunks are retrieved and used to enhance LLM responses.

4. **Response Generation**:
   - The backend receives the response from the CI&T Flow API.
   - The response is formatted and returned to the client.

## Configuration

The application is configured using environment variables or a `.env` file. Key settings include:

- **CI&T Flow API Settings**: Token, base URL, client ID, etc.
- **RAG Settings**: Document path, chunk size, embedding model, etc.
- **Vector Store Settings**: Directory for storing embeddings, auto-indexing, etc.

## Deployment

The application can be deployed using Docker, Kubernetes, or any cloud platform that supports Python applications. Key considerations include:

- **Scalability**: Ensure the application can handle increased load by scaling horizontally.
- **Security**: Protect API endpoints with authentication and rate limiting.
- **Monitoring**: Implement logging and monitoring to track application performance and errors.

## Performance Characteristics

Based on comprehensive testing (September 2025), the system demonstrates the following performance characteristics:

### Response Times

| Component | Operation | Average Response Time (ms) |
|-----------|-----------|----------------------------|
| Basic Endpoints | Health Check | 3,365 |
| RAG System | Document Processing | 3,127 |
| RAG System | Embedding Initialization | 4,680 |
| Vector Store | Query | 2,295 |
| Vector Store | Reindex | 3,367 |
| Text Generation | Basic Generation | 4,306 |
| Text Generation | RAG-Enhanced Generation | 5,948 |
| Text Generation | Message-Based Generation | 6,978 |
| Text Generation | RAG + Messages Generation | 6,404 |

### Token Usage Analysis

The architecture's design impacts token usage in LLM requests:

| Generation Method | Total Tokens | Relative Cost |
|-------------------|--------------|---------------|
| Basic Generation | 299 | Baseline |
| RAG Generation | 355 | +19% |
| Messages Generation | 596 | +99% |
| RAG + Messages Generation | 1,129 | +277% |

This demonstrates the trade-off between response quality and computational cost. The RAG + Messages approach provides the most contextually relevant responses but at a higher token usage.

## Testing Architecture

The system includes a comprehensive testing architecture to validate all components:

```
┌──────────────────────────┐
│    Postman Collection    │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│    Automated Test Suite  │
│    (60 Tests Across      │
│     15 Endpoints)        │
└────────────┬─────────────┘
             │
             ▼
┌─────────────┬─────────────┐
│             │             │
▼             ▼             ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│  Basic   │  │   RAG    │  │  Text    │
│ Endpoint │  │  System  │  │Generation│
│  Tests   │  │  Tests   │  │  Tests   │
└──────────┘  └──────────┘  └──────────┘
```

### Test Coverage

- **Basic Endpoints**: 9 tests validating core functionality and health checks
- **RAG System**: 20 tests covering document processing, embedding, and vector operations
- **Vector Store**: 14 tests for storage, retrieval, and management operations
- **Text Generation**: 20 tests comparing different generation methods and configurations

All tests are automated and can be run using the provided Postman collection. See the [postman/README.md](postman/README.md) file for detailed test results and instructions.

## Scalability Considerations

Based on performance testing, the following scalability considerations should be addressed:

1. **Embedding Generation**: The most resource-intensive operation (4,680ms average). Consider:
   - Pre-computing embeddings for documents
   - Implementing a queue system for large document collections
   - Distributing embedding generation across multiple workers

2. **Text Generation with RAG**: Requires significant processing time (5,948ms average). Consider:
   - Implementing caching for common queries
   - Optimizing the number of retrieved documents based on query complexity
   - Using streaming responses for better user experience

3. **Vector Store Performance**: Scales with document count (currently tested with 632 documents). Consider:
   - Implementing sharding for very large document collections
   - Using more efficient vector search algorithms for larger collections
   - Periodic optimization of the vector store

## Conclusion

The CI&T Flow GenAI Chatbot architecture is designed to provide robust and scalable text generation capabilities, leveraging the power of RAG to enhance responses with document knowledge. This document provides a comprehensive overview of the system's components, interactions, and data flow, serving as a guide for developers and stakeholders.