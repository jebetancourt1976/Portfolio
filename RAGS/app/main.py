"""
Main entry point for Multi-Policy RAG Application.
Initializes the system and launches the Gradio interface.
"""

import sys
import logging
from pathlib import Path

from langchain_openai import ChatOpenAI

from .config import Config
from .agent import PolicyAgent, build_or_load_vectorstore
from .orchestrator import ToolCallingOrchestrator
from .ui import create_interface


def setup_logging(config: Config) -> None:
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def initialize_system(config: Config) -> ToolCallingOrchestrator:
    """
    Initialize the RAG system with agents and orchestrator.
    
    Args:
        config: Configuration object
        
    Returns:
        Initialized orchestrator
    """
    logger = logging.getLogger(__name__)
    
    logger.info("Initializing Multi-Policy RAG System...")
    logger.info(config.display_config())
    
    # Initialize LLM
    llm = ChatOpenAI(model=config.LLM_MODEL, temperature=0)
    logger.info(f"LLM initialized: {config.LLM_MODEL}")
    
    # Build or load vector stores
    logger.info("Building/loading vector stores...")
    
    med_vs = build_or_load_vectorstore(
        config.get_medical_pdf_path(),
        "Medical",
        config.get_medical_index_path(),
        config
    )
    
    den_vs = build_or_load_vectorstore(
        config.get_dental_pdf_path(),
        "Dental",
        config.get_dental_index_path(),
        config
    )
    
    # Create policy agents
    logger.info("Creating policy agents...")
    medical_agent = PolicyAgent("Medical", med_vs, llm, k=config.TOP_K)
    dental_agent = PolicyAgent("Dental", den_vs, llm, k=config.TOP_K)
    
    # Create orchestrator
    logger.info("Creating tool-calling orchestrator...")
    orchestrator = ToolCallingOrchestrator(medical_agent, dental_agent, llm)
    
    logger.info("✅ System initialization complete!")
    return orchestrator


def main() -> None:
    """Main entry point for the application."""
    # Load and validate configuration
    is_valid, error = Config.validate()
    if not is_valid:
        print(f"❌ Configuration error: {error}")
        print("\nPlease ensure:")
        print("1. OPENAI_API_KEY is set in .env file or environment")
        print("2. PDF files are in data/pdfs/ directory")
        sys.exit(1)
    
    # Setup logging
    setup_logging(Config)
    logger = logging.getLogger(__name__)
    
    try:
        # Initialize system
        orchestrator = initialize_system(Config)
        
        # Create and launch Gradio interface
        logger.info("Launching Gradio interface...")
        demo = create_interface(orchestrator, Config)
        
        demo.launch(
            server_name=Config.GRADIO_SERVER_NAME,
            server_port=Config.GRADIO_SERVER_PORT,
            share=Config.GRADIO_SHARE,
            show_error=True
        )
        
    except KeyboardInterrupt:
        logger.info("\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
