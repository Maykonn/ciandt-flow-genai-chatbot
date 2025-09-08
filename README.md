# ciandt-flow-genai-chatbot
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

## Project Structure
The project is organized as follows:
- src/: Main source code
  - api/: API routes and endpoints
  - config/: Configuration management
  - core/: Core functionality including Flow API client and token manager
  - rag/: Retrieval-Augmented Generation components
  - utils/: Utility functions and validators
- tests/: Unit and integration tests
- postman/: Postman collections for API testing

## Installation
### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup
1. Clone the repository:
```
git clone https://github.com/yourusername/ciandt-flow-genai-chatbot.git
cd ciandt-flow-genai-chatbot
```

2. Create a virtual environment:
```
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```
venv\Scripts\activate
```
- macOS/Linux:
```
source venv/bin/activate
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Create a `.env` file based on the example:
```
cp .env.example .env
```

6. Edit the `.env` file with your actual values:
```
APP_FLOW_API_TOKEN=your-client-secret-here
APP_FLOW_API_BASE_URL=https://flow.ciandt.com
APP_FLOW_API_ORCHESTRATION_PATH=/ai-orchestration-api/v1
APP_FLOW_API_AUTH_PATH=/auth-engine-api/v1
APP_FLOW_API_CLIENT_ID=your-client-id-here
APP_FLOW_API_TENANT=stretto
APP_FLOW_API_AGENT=default-agent
APP_FLOW_API_APP_TO_ACCESS=llm-api
APP_FLOW_API_TOKEN_MAX_RETRIES=3
APP_FLOW_API_TOKEN_BASE_TIMEOUT=10
APP_FLOW_API_TOKEN_TIMEOUT_MULTIPLIER=1.5
APP_FLOW_API_TOKEN_RETRY_DELAY=1.0
APP_FLOW_API_TOKEN_CACHE_PATH=.token_cache.json
APP_RAG_DOCUMENTS_PATH=./data/rag_documents
APP_RAG_CHUNK_SIZE=1000
APP_RAG_CHUNK_OVERLAP=200
APP_RAG_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Configuration
The application can be configured using environment variables or a `.env` file. The following settings are available:

### CI&T Flow API Settings
- `APP_FLOW_API_TOKEN`: Your CI&T Flow API token (client secret)
- `APP_FLOW_API_BASE_URL`: Base URL for the CI&T Flow API
- `APP_FLOW_API_ORCHESTRATION_PATH`: Path for the orchestration API
- `APP_FLOW_API_AUTH_PATH`: Path for the authentication API
- `APP_FLOW_API_CLIENT_ID`: Your CI&T Flow API client ID
- `APP_FLOW_API_TENANT`: CI&T Flow tenant name
- `APP_FLOW_API_AGENT`: CI&T Flow agent name
- `APP_FLOW_API_APP_TO_ACCESS`: CI&T Flow app to access

### Token Management Settings
- `APP_FLOW_API_TOKEN_MAX_RETRIES`: Maximum number of retry attempts for token retrieval
- `APP_FLOW_API_TOKEN_BASE_TIMEOUT`: Base timeout in seconds for token retrieval
- `APP_FLOW_API_TOKEN_TIMEOUT_MULTIPLIER`: Multiplier for timeout on each retry
- `APP_FLOW_API_TOKEN_RETRY_DELAY`: Delay in seconds between retry attempts
- `APP_FLOW_API_TOKEN_CACHE_PATH`: Path to token cache file

### RAG Settings
- `APP_RAG_DOCUMENTS_PATH`: Path to the RAG documents folder
- `APP_RAG_CHUNK_SIZE`: Size of document chunks in characters (default: 1000)
- `APP_RAG_CHUNK_OVERLAP`: Overlap between consecutive chunks (default: 200)
- `APP_RAG_EMBEDDING_MODEL`: Hugging Face model for embeddings (default: sentence-transformers/all-MiniLM-L6-v2)

## Running the Application
Run the application using:
```
python run.py
```

Or directly with uvicorn:
```
python -m uvicorn src.main:app --reload
```

The API will be available at http://localhost:8000

## API Endpoints
- `GET /`: Root endpoint, returns a welcome message
- `GET /api/health`: Health check endpoint, validates Flow API connection and RAG documents path
- `POST /api/generate`: Generate text using the Flow API's OpenAI Chat Completions endpoint
- `GET /api/rag/stats`: Get statistics about the documents in the RAG folder
- `GET /api/rag/process`: Load and process documents from the RAG folder
- `GET /api/rag/initialize-embeddings`: Initialize the embedding model

### Generate Text Endpoint
Request body:
```json
{
  "prompt": "What is artificial intelligence?",
  "max_tokens": 3000,
  "model": "gpt-4o",
  "stream": false,
  "use_rag": true
}
```

Response:
```json
{
  "text": "Artificial intelligence (AI) refers to the simulation of human intelligence in machines...",
  "full_response": {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": 1677652288,
    "model": "gpt-4o",
    "choices": [
      {
        "index": 0,
        "message": {
          "role": "assistant",
          "content": "Artificial intelligence (AI) refers to the simulation of human intelligence in machines..."
        },
        "finish_reason": "stop"
      }
    ]
  }
}
```

## RAG (Retrieval-Augmented Generation)

This application includes a RAG system that enhances LLM responses with information from your document collection.

### Quick Start: Using RAG

1. **Prepare your documents**:
   - Place your documents in the `./data/rag_documents` folder (or your configured path)
   - Supported formats: PDF, TXT

2. **Process your documents**:
   ```
   curl -X GET http://localhost:8000/api/rag/process
   ```

3. **Initialize embeddings**:
   ```
   curl -X GET http://localhost:8000/api/rag/initialize-embeddings
   ```

4. **Generate text with RAG**:
   ```
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
   ```
   curl -X GET http://localhost:8000/api/rag/stats
   ```

### Recommended Embedding Models

- `sentence-transformers/all-MiniLM-L6-v2`: Fast, lightweight (384 dimensions)
- `sentence-transformers/all-mpnet-base-v2`: More accurate but slower (768 dimensions)
- `sentence-transformers/multi-qa-mpnet-base-dot-v1`: Optimized for question-answering

## API Testing
This project includes Postman collections for API testing. You can find them in the `postman` folder:
- Import the collection and environment files into Postman
- Set your Flow API token in the environment variables
- Use the collection to test all API endpoints

See the postman/README.md file for detailed instructions.

## Testing
Run tests using pytest:
```
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
- `RAGManager`: Orchestrates the RAG workflow and retrieves relevant documents

### Settings Management
The `Settings` class manages application configuration:
- Loads settings from environment variables or `.env` file
- Provides type validation and default values
- Centralizes configuration management

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
