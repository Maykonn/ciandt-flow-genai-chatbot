# Postman Collections for ciandt-flow-genai-chatbot

This folder contains Postman collections and environments for testing the CI&T Flow GenAI Chatbot API.

## Files

- `ciandt-flow-genai-chatbot.postman_collection.json`: The main Postman collection with all API endpoints
- `ciandt-flow-genai-chatbot-local.postman_environment.json`: Environment variables for local development

## How to Import

1. Open Postman
2. Click on "Import" button in the top left
3. Select "File" tab and browse to this folder
4. Select the collection and environment files
5. Click "Import"

## Setting Up the Environment

1. After importing, click on "Environments" in the sidebar
2. Select "ciandt-flow-genai-chatbot-local"
3. Update the `flowApiToken` value with your actual API token
4. Click "Save"

## Using the Collection

1. Make sure the "ciandt-flow-genai-chatbot-local" environment is selected
2. Expand the "ciandt-flow-genai-chatbot" collection
3. Start with the "Health Check" request to verify your setup
4. All requests use the `{{baseUrl}}` variable which is set in the environment

## Available Endpoints

- **Root Endpoint**: Basic check to ensure the service is running
- **Health Check**: Comprehensive health check that validates Flow API connection and RAG documents path
- **Generate Text with Flow API**: Test the text generation capabilities using the Flow API
- **Flow API Connection Test**: Test the connection to the CI&T Flow API
- **RAG Documents Path Validation**: Validate the RAG documents path
