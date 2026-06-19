"""
Configuration management for Multi-Policy RAG Application.
Loads settings from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
    EMBED_MODEL: str = os.getenv("EMBED_MODEL", "text-embedding-3-small")
    
    # Directory Configuration
    BASE_DIR: Path = Path(__file__).parent.parent
    INDEX_DIR: Path = BASE_DIR / os.getenv("INDEX_DIR", "data/faiss_indexes")
    PDF_DIR: Path = BASE_DIR / os.getenv("PDF_DIR", "data/pdfs")
    
    # File Configuration
    MEDICAL_PDF: str = os.getenv("MEDICAL_PDF", "HR_Policy_Medicalbenefits.pdf")
    DENTAL_PDF: str = os.getenv("DENTAL_PDF", "dental_benefits_summary.pdf")
    
    # Server Configuration
    GRADIO_SERVER_NAME: str = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    GRADIO_SERVER_PORT: int = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    GRADIO_SHARE: bool = os.getenv("GRADIO_SHARE", "false").lower() == "true"
    
    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    TOP_K: int = int(os.getenv("TOP_K", "4"))
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "4"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> tuple[bool, Optional[str]]:
        """
        Validate configuration.
        Returns (is_valid, error_message).
        """
        if not cls.OPENAI_API_KEY:
            return False, "OPENAI_API_KEY is required. Set it in .env file or environment."
        
        # Create directories if they don't exist
        cls.INDEX_DIR.mkdir(parents=True, exist_ok=True)
        cls.PDF_DIR.mkdir(parents=True, exist_ok=True)
        
        # Check if PDF files exist
        medical_path = cls.PDF_DIR / cls.MEDICAL_PDF
        dental_path = cls.PDF_DIR / cls.DENTAL_PDF
        
        if not medical_path.exists():
            return False, f"Medical PDF not found: {medical_path}"
        
        if not dental_path.exists():
            return False, f"Dental PDF not found: {dental_path}"
        
        return True, None
    
    @classmethod
    def get_medical_pdf_path(cls) -> Path:
        """Get full path to medical PDF."""
        return cls.PDF_DIR / cls.MEDICAL_PDF
    
    @classmethod
    def get_dental_pdf_path(cls) -> Path:
        """Get full path to dental PDF."""
        return cls.PDF_DIR / cls.DENTAL_PDF
    
    @classmethod
    def get_medical_index_path(cls) -> Path:
        """Get path to medical FAISS index."""
        return cls.INDEX_DIR / "medical_index"
    
    @classmethod
    def get_dental_index_path(cls) -> Path:
        """Get path to dental FAISS index."""
        return cls.INDEX_DIR / "dental_index"
    
    @classmethod
    def display_config(cls) -> str:
        """Return configuration summary as string."""
        return f"""
Configuration:
--------------
LLM Model: {cls.LLM_MODEL}
Embedding Model: {cls.EMBED_MODEL}
Medical PDF: {cls.get_medical_pdf_path()}
Dental PDF: {cls.get_dental_pdf_path()}
Index Directory: {cls.INDEX_DIR}
Chunk Size: {cls.CHUNK_SIZE}
Chunk Overlap: {cls.CHUNK_OVERLAP}
Top-K Retrieval: {cls.TOP_K}
Server: {cls.GRADIO_SERVER_NAME}:{cls.GRADIO_SERVER_PORT}
"""

# Made with Bob
