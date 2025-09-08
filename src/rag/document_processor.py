import logging
from typing import List, Optional, Dict, Any
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config.settings import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processes documents for RAG."""
    
    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None
    ):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Size of text chunks
            chunk_overlap: Overlap between text chunks
        """
        self.chunk_size = chunk_size or settings.rag_chunk_size
        self.chunk_overlap = chunk_overlap or settings.rag_chunk_overlap
        
        logger.info(f"Initialized DocumentProcessor with chunk_size: {self.chunk_size}, chunk_overlap: {self.chunk_overlap}")
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks.
        
        Args:
            documents: List of documents to split
            
        Returns:
            List of document chunks
        """
        logger.info(f"Splitting {len(documents)} documents into chunks")
        
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
            return chunks
        except Exception as e:
            logger.error(f"Error splitting documents: {e}")
            return documents  # Return original documents if splitting fails
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process documents for RAG.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List of processed documents
        """
        logger.info(f"Processing {len(documents)} documents")
        
        # Split documents into chunks
        chunks = self.split_documents(documents)
        
        # Add metadata if needed
        for i, chunk in enumerate(chunks):
            if "chunk_id" not in chunk.metadata:
                chunk.metadata["chunk_id"] = i
        
        return chunks
    
    def get_document_metadata(self, documents: List[Document]) -> List[Dict[str, Any]]:
        """
        Extract metadata from documents.
        
        Args:
            documents: List of documents
            
        Returns:
            List of document metadata
        """
        return [doc.metadata for doc in documents]

