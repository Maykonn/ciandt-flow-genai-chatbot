# Postman Collections for CI&T Flow GenAI Chatbot

This folder contains Postman collections and environments for testing the CI&T Flow GenAI Chatbot API.

## Files

- `ciandt-flow-genai-chatbot.postman_collection.json`: The main Postman collection with all API endpoints
- `ciandt-flow-genai-chatbot-local.postman_environment.json`: Environment variables for local development

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