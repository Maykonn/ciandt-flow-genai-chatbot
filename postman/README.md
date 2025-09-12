# Postman Collections for CI&T Flow GenAI Chatbot

This folder contains Postman collections and environments for testing the CI&T Flow GenAI Chatbot API.

## Files

- `ciandt-flow-genai-chatbot.postman_collection.json`: The main Postman collection with all API endpoints
- `ciandt-flow-genai-chatbot-local.postman_environment.json`: Environment variables for local development
- `ciandt-flow-genai-chatbot.postman_test_run`: Results from the latest test run, showing test outcomes and performance metrics

## How to Import

1. Open Postman.
2. Click on the "Import" button in the top left corner.
3. Select the "File" tab and browse to this folder.
4. Select the collection and environment files.
5. Click "Import".

## Setting Up the Environment

1. After importing, click on "Environments" in the sidebar.
2. Select "ciandt-flow-genai-chatbot-local".
3. Update the `baseUrl` value if necessary (default: `http://localhost:8000`).
4. Click "Save".

## Using the Collection

1. Make sure the "ciandt-flow-genai-chatbot-local" environment is selected.
2. Expand the "ciandt-flow-genai-chatbot" collection.
3. Start with the "Health Check" request to verify your setup.
4. All requests use the `{{baseUrl}}` variable, which is set in the environment.

## Available Endpoints

The collection is organized into logical folders:

### Basic Endpoints

- **Root Endpoint**: `GET /` - Basic check to ensure the service is running.
- **Health Check**: `GET /api/health` - Comprehensive health check that validates Flow API connection, RAG documents path, and vector store.

### RAG Operations

- **Get Document Stats**: `GET /api/rag/stats` - Get statistics about the documents in the RAG folder.
- **Process Documents**: `GET /api/rag/process` - Load and process documents from the RAG folder.
- **Process Documents with Indexing**: `GET /api/rag/process?index_to_vector_store=true` - Load, process, and index documents to the vector store.
- **Initialize Embeddings**: `GET /api/rag/initialize-embeddings` - Initialize the embedding model.

### Vector Store

- **Get Vector Store Stats**: `GET /api/rag/vector-store` - Get statistics about the vector store.
- **Query Vector Store**: `POST /api/rag/query` - Query the vector store for relevant documents.
- **Reindex Documents**: `POST /api/rag/reindex?force=false` - Reindex all documents in the RAG folder.
- **Clear Vector Store**: `DELETE /api/rag/vector-store` - Clear all documents from the vector store.

### Text Generation

- **Generate Text (Basic)**: `POST /api/generate` - Generate text using the Flow API's OpenAI Chat Completions endpoint without RAG.
- **Generate Text (RAG Enabled)**: `POST /api/generate` - Generate text using the Flow API with RAG enhancement.
- **Generate Text with Messages (Basic)**: `POST /api/generate` - Generate text using the Flow API with message-based input.
- **Generate Text with Messages (RAG Enabled)**: `POST /api/generate` - Generate text using the Flow API with message-based input and RAG.

## Testing Conversation History

To test conversation history with RAG, use the "Generate Text with Messages (RAG Enabled)" request. This demonstrates how to:

1. Use system messages to set the assistant's behavior.
2. Include previous messages in the conversation.
3. Leverage RAG to enhance responses with document knowledge.

Example request body:
```json
{
  "prompt": "Who is the debtor?",
  "max_tokens": 3000,
  "model": "gpt-4o",
  "stream": false,
  "use_rag": true,
  "messages": [
    {"role": "system", "content": "Provide deep technical information about the context."},
    {"role": "assistant", "content": "Jane Doe"},
    {"role": "user", "content": "What are the payment terms?"}
  ]
}
```

## Using the Collection Runner

The Collection Runner in Postman allows you to run all requests in a collection in sequence, which is useful for automated testing.

1. **Open the Collection Runner**:
   - Click on the "Runner" button in the bottom right corner of Postman.

2. **Configure the Run**:
   - Select the "ciandt-flow-genai-chatbot" collection.
   - Choose the "ciandt-flow-genai-chatbot-local" environment.
   - Set the number of iterations, delay between requests, and any other settings as needed.

3. **Run the Collection**:
   - Click the "Run" button to execute all requests in the collection.
   - The Collection Runner will execute each request in sequence and display the results.

4. **Review Results**:
   - After the run completes, review the results to see which tests passed or failed.
   - Click on individual requests in the runner to see detailed results and logs.
   - You can export the test run results as a JSON file for documentation or analysis.

## Test Results Visualization

The collection includes a special "Check Environment Variables" request that provides a visualization of all test results. This request:

1. Collects all response data from previous requests stored in the environment variable
2. Displays a summary table of all stored responses
3. Shows key statistics about the API's performance

## Current Test Results

The most recent test run (September 12, 2025) shows:

- **Total Tests**: 60
- **Passed Tests**: 60
- **Failed Tests**: 0
- **Total Run Time**: 49.8 seconds

### Detailed Test Results

| Endpoint | Response Time (ms) | Tests Passed | Key Tests |
|----------|-------------------|--------------|-----------|
| Root Endpoint | 4 | 4/4 | Status code, Welcome message, Response time, Content-type |
| Health Check | 3,365 | 5/5 | Status code, Health status, Flow API connection, RAG documents, Vector store |
| Clear Vector Store | 2,014 | 2/2 | Status code, Vector store clearance |
| Get Document Stats | 2,024 | 4/4 | Status code, Document stats, Stats consistency, Document availability |
| Process Documents | 3,111 | 5/5 | Status code, Processed documents, Document count, Required properties, Consistency |
| Process Documents with Indexing | 3,127 | 4/4 | Status code, Indexed documents, Document count, Count matching |
| Initialize Embeddings | 4,680 | 3/3 | Status code, Embedding model, Model matching |
| Get Vector Store Stats | 2,198 | 4/4 | Status code, Vector store stats, Embedding model, Document presence |
| Query Vector Store | 2,295 | 4/4 | Status code, Relevant documents, Required properties, Result count |
| Reindex Documents | 3,367 | 4/4 | Status code, Reindexing confirmation, Document count, Count consistency |
| Generate Text (Basic) | 4,306 | 5/5 | Status code, Generated text, OpenAI data, Relevance, Token usage |
| Generate Text (RAG Enabled) | 5,948 | 5/5 | Status code, RAG text, OpenAI data, RAG relevance, Token usage |
| Generate Text with Messages (Basic) | 6,978 | 5/5 | Status code, Message text, OpenAI data, Message relevance, Token usage |
| Generate Text with Messages (RAG Enabled) | 6,404 | 5/5 | Status code, RAG message text, OpenAI data, Context relevance, Token usage |
| Check Environment Variables | 4 | 1/1 | Environment variable validation |

### Key Statistics

- **Total Documents**: 1
- **Vector Store Documents**: 632
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2
- **Token Usage Comparison**:
  - Basic Generation: 299 tokens
  - RAG Generation: 355 tokens
  - Messages Generation: 596 tokens
  - RAG+Messages Generation: 1,129 tokens

This demonstrates how combining RAG with conversation history significantly increases token usage but provides more contextually relevant responses.

### Performance Analysis

| Request Type | Average Response Time (ms) | Notes |
|--------------|----------------------------|-------|
| Basic Endpoints | 1,685 | Fast responses for basic health checks |
| RAG Operations | 3,236 | Moderate processing time for document operations |
| Vector Store Operations | 2,469 | Efficient vector store management |
| Text Generation | 5,909 | Longer processing for AI text generation |
| RAG + Messages | 6,404 | Most complex operation with highest processing time |

## Adding Tests

You can add automated tests to verify responses:

1. Select a request.
2. Go to the "Tests" tab.
3. Add JavaScript code to test the response.

Example test script:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has expected fields", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('text');
    pm.expect(jsonData).to.have.property('full_response');
});
```