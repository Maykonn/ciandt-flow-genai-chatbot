# CI&T Flow GenAI Chatbot

Backend service for integrating with CI&T Flow APIs to provide GenAI LLM capabilities.

## Overview

This project implements a backend service that connects to CI&T Flow APIs for accessing GenAI Large Language Model capabilities. It provides a robust API for generating text using OpenAI's Chat Completions endpoint with proper authentication, token management, and error handling.

## Features

- **Authentication**: Secure token-based authentication with CI&T Flow APIs
- **Token Management**: Automatic token retrieval, caching, and renewal
- **Configurable Retries**: Customizable retry logic for API requests
- **Error Handling**: Comprehensive error handling for API requests
- **Health Checks**: Endpoint to validate connections and configurations
- **Text Generation**: API endpoint for generating text using OpenAI models
- **RAG Support**: Retrieval-Augmented Generation for knowledge-grounded responses
- **Persistent Vector Store**: Chroma-based vector database for efficient retrieval
- **Conversation History Support**: Maintain context across multiple conversation turns

## Documentation

- [Architecture Overview](ARCHITECTURE.md): Detailed architecture of the application.
- [RAG System Details](src/rag/README.md): Information about the RAG components and workflow.
- [Postman Collection](postman/README.md): Instructions for using the Postman collection to test the API.

## Project Structure

The project is organized as follows:

- **src/**: Main source code
  - **api/**: API routes and endpoints
  - **config/**: Configuration management
  - **core/**: Core functionality including Flow API client and token manager
  - **rag/**: Retrieval-Augmented Generation components
  - **utils/**: Utility functions and validators
  - **scripts/**: Utility scripts for tasks like document indexing

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ciandt-flow-genai-chatbot
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     .\venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a `.env` file based on the example**:
   ```bash
   cp .env.example .env
   ```

6. **Edit the `.env` file with your actual values**:
   ```ini
   APP_FLOW_API_TOKEN=your-token
   APP_FLOW_API_BASE_URL=https://flow.ciandt.com
   APP_FLOW_API_ORCHESTRATION_PATH=/ai-orchestration-api/v1
   APP_FLOW_API_AUTH_PATH=/auth-engine-api/v1
   APP_FLOW_API_CLIENT_ID=your-client-id
   APP_FLOW_API_APP_TO_ACCESS=llm-api
   APP_RAG_DOCUMENTS_PATH=./data/rag_documents
   APP_RAG_CHUNK_SIZE=1000
   APP_RAG_CHUNK_OVERLAP=200
   APP_RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
   APP_AUTO_INDEX_ON_STARTUP=false
   APP_VECTOR_STORE_DIRECTORY=./data/vector_db
   ```

## Running the Application

Run the application using:

```bash
python run.py
```

Or directly with uvicorn:

```bash
python -m uvicorn src.main:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

The application provides the following API endpoints:

### Basic Endpoints

- **`GET /`**: Root endpoint, returns a welcome message
- **`GET /api/health`**: Health check endpoint, validates Flow API connection, RAG documents path, and vector store

### RAG Operations

- **`GET /api/rag/stats`**: Get statistics about the documents in the RAG folder
- **`GET /api/rag/process`**: Load and process documents from the RAG folder
- **`GET /api/rag/process?index_to_vector_store=true`**: Load, process, and index documents to the vector store
- **`GET /api/rag/initialize-embeddings`**: Initialize the embedding model

### Vector Store Operations

- **`GET /api/rag/vector-store`**: Get vector store statistics
- **`POST /api/rag/query`**: Query the vector store for relevant documents
- **`POST /api/rag/reindex?force=false`**: Reindex all documents in the RAG folder
- **`DELETE /api/rag/vector-store`**: Clear all documents from the vector store

### Text Generation

- **`POST /api/generate`**: Generate text using the Flow API's OpenAI Chat Completions endpoint with optional RAG and conversation history

## RAG (Retrieval-Augmented Generation)

This application includes a RAG system that enhances LLM responses with information from your document collection.

### Quick Start: Using RAG

1. **Prepare your documents**:
   - Place your documents in the `./data/rag_documents` folder (or your configured path)
   - Supported formats: PDF, TXT

2. **Process your documents**:
   ```bash
   curl -X GET http://localhost:8000/api/rag/process
   ```

3. **Initialize embeddings**:
   ```bash
   curl -X GET http://localhost:8000/api/rag/initialize-embeddings
   ```

4. **Generate text with RAG**:
   ```bash
   curl -X POST http://localhost:8000/api/generate \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "What information do we have about Project X?",
       "max_tokens": 3000,
       "model": "gpt-4o",
       "use_rag": true
     }'
   ```

5. **Check document statistics**:
   ```bash
   curl -X GET http://localhost:8000/api/rag/stats
   ```

### Recommended Embedding Models

- `sentence-transformers/all-MiniLM-L6-v2`: Fast, lightweight (384 dimensions)
- `sentence-transformers/all-mpnet-base-v2`: More accurate but slower (768 dimensions)
- `sentence-transformers/multi-qa-mpnet-base-dot-v1`: Optimized for question-answering

## API Testing

This project includes comprehensive Postman collections for API testing. You can find them in the `postman` folder:

- Import the collection and environment files into Postman
- Set your Flow API token in the environment variables
- Use the collection to test all API endpoints

The Postman collection includes:
- 60 automated tests covering all API endpoints
- Detailed performance metrics for each endpoint
- Token usage analysis for different generation methods
- Test visualization capabilities

Recent test runs show 100% pass rate with an average response time of 3.3 seconds across all endpoints. Text generation with RAG and conversation history shows the highest token usage (1,129 tokens) but provides the most contextually relevant responses.

See the [postman/README.md](postman/README.md) file for detailed instructions and complete test results.

## Testing

Run tests using pytest:

```bash
pytest
```

## Key Components

### Token Manager

The `TokenManager` class handles authentication with the CI&T Flow API:

- Retrieves access tokens using client credentials
- Caches tokens to minimize API calls
- Automatically refreshes expired tokens
- Implements configurable retry logic for token retrieval

### Flow API Client

The `FlowAPIClient` class provides a clean interface for interacting with the CI&T Flow API:

- Makes authenticated requests to the API
- Handles request formatting and response parsing
- Implements error handling and logging

### RAG System

The RAG system enhances LLM responses with information from your document collection:

- `DocumentLoader`: Loads documents from various file formats
- `DocumentProcessor`: Splits documents into manageable chunks
- `EmbeddingManager`: Creates vector representations of text
- `VectorStore`: Persistent storage for document embeddings using Chroma
- `RAGManager`: Orchestrates the RAG workflow and retrieves relevant documents

### Settings Management

The `Settings` class manages application configuration:

- Loads settings from environment variables or `.env` file
- Provides type validation and default values
- Centralizes configuration management

### Application Lifecycle Management

The application uses FastAPI's lifespan event handlers for proper resource management:

- **Startup**: Initialize connections, validate configurations, and optionally index documents
- **Shutdown**: Clean up resources and close connections

## Development

### Adding New Endpoints

To add new endpoints, create or modify files in the `src/api` directory. Make sure to register your routes with the FastAPI app in `main.py`.

### Extending the Flow API Client

To add more functionality for the Flow API, extend the `FlowAPIClient` class in `src/core/flow_client.py`.

### Customizing RAG

To customize the RAG system:

1. Update the RAG settings in your `.env` file
2. Add support for new document types in `DocumentLoader`
3. Modify the retrieval logic in `RAGManager.retrieve_relevant_documents()`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

[Specify your license here]

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [CI&T Flow API](https://flow.ciandt.com/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [httpx](https://www.python-httpx.org/)
- [LangChain](https://python.langchain.com/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
- [Chroma](https://www.trychroma.com/)