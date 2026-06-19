# Multi-Policy RAG Application - Project Structure

## Directory Layout

```
RAGS/
├── app/                                    # Application source code
│   ├── __init__.py                        # Package initialization
│   ├── main.py                            # Application entry point
│   ├── config.py                          # Configuration management
│   ├── agent.py                           # PolicyAgent class
│   ├── orchestrator.py                    # ToolCallingOrchestrator class
│   └── ui.py                              # Gradio interface components
│
├── data/                                   # Data directory
│   ├── pdfs/                              # PDF documents (source)
│   │   ├── dental_benefits_summary.pdf
│   │   └── HR_Policy_Medicalbenefits.pdf
│   └── faiss_indexes/                     # Vector store indexes (generated)
│       ├── medical_index/                 # Medical policy FAISS index
│       └── dental_index/                  # Dental policy FAISS index
│
├── docs/                                   # Documentation
│   ├── IMPLEMENTATION_PLAN.md             # Implementation strategy
│   ├── ARCHITECTURE.md                    # Architecture diagrams
│   └── PROJECT_STRUCTURE.md               # This file
│
├── tests/                                  # Test files (optional)
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_orchestrator.py
│   └── test_integration.py
│
├── .env.example                           # Environment variables template
├── .dockerignore                          # Docker build exclusions
├── .gitignore                             # Git exclusions
├── docker-compose.yml                     # Docker Compose configuration
├── Dockerfile                             # Docker image definition
├── README.md                              # Main documentation
├── requirements.txt                       # Python dependencies
└── multi_policy_rag_orchestrator_v3.py   # Original notebook (reference)
```

## File Descriptions

### Application Files (`app/`)

#### `app/__init__.py`
```python
"""
Multi-Policy RAG Application Package
Provides intelligent query routing across medical and dental policy documents.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .agent import PolicyAgent
from .orchestrator import ToolCallingOrchestrator
from .config import Config

__all__ = ["PolicyAgent", "ToolCallingOrchestrator", "Config"]
```

#### `app/main.py`
**Purpose**: Application entry point
**Responsibilities**:
- Initialize configuration
- Set up logging
- Build or load vector stores
- Initialize orchestrator
- Launch Gradio interface
- Handle graceful shutdown

**Key Functions**:
- `main()`: Entry point
- `setup_logging()`: Configure logging
- `initialize_system()`: Build agents and orchestrator
- `run_server()`: Start Gradio server

#### `app/config.py`
**Purpose**: Configuration management
**Responsibilities**:
- Load environment variables
- Validate configuration
- Provide configuration access
- Set defaults

**Configuration Parameters**:
```python
class Config:
    # API Configuration
    OPENAI_API_KEY: str
    LLM_MODEL: str = "gpt-4o-mini"
    EMBED_MODEL: str = "text-embedding-3-small"
    
    # Directory Configuration
    INDEX_DIR: Path = Path("./data/faiss_indexes")
    PDF_DIR: Path = Path("./data/pdfs")
    
    # File Configuration
    MEDICAL_PDF: str = "HR_Policy_Medicalbenefits.pdf"
    DENTAL_PDF: str = "dental_benefits_summary.pdf"
    
    # Server Configuration
    GRADIO_SERVER_NAME: str = "0.0.0.0"
    GRADIO_SERVER_PORT: int = 7860
    GRADIO_SHARE: bool = False
    
    # RAG Configuration
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 4
    MAX_ITERATIONS: int = 4
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
```

#### `app/agent.py`
**Purpose**: PolicyAgent implementation
**Responsibilities**:
- Manage single-policy RAG specialist
- Handle vector store operations
- Implement strict NOT_FOUND contract
- Return grounded answers with sources

**Key Classes**:
```python
class PolicyAgent:
    """Single-policy RAG specialist"""
    
    def __init__(self, name, vectorstore, llm, k=4, prompt_template=STRICT_PROMPT)
    def ask(self, question: str) -> dict
    def _format_docs(self, docs) -> str
```

**Helper Functions**:
```python
def build_or_load_vectorstore(pdf_path, label, index_path, config) -> FAISS
def clear_indexes(config)
```

#### `app/orchestrator.py`
**Purpose**: ToolCallingOrchestrator implementation
**Responsibilities**:
- LLM-driven intent-based routing
- Tool management and execution
- Fallback mechanism
- Chain-of-thought tracking

**Key Classes**:
```python
class ToolCallingOrchestrator:
    """LLM-driven orchestrator with tool calling"""
    
    def __init__(self, medical_agent, dental_agent, llm)
    def answer(self, question: str, max_iters: int = 4) -> dict
    def _run_tool_with_sources(self, name: str, query: str) -> dict
```

**Tool Definitions**:
```python
@tool
def search_medical_policy(query: str) -> str

@tool
def search_dental_policy(query: str) -> str
```

#### `app/ui.py`
**Purpose**: Gradio interface components
**Responsibilities**:
- UI layout and components
- Event handlers
- Result formatting
- User interaction

**Key Functions**:
```python
def create_interface(orchestrator, config) -> gr.Blocks
def ui_build(medical_file, dental_file) -> str
def ui_rebuild(medical_file, dental_file) -> str
def ui_ask(question: str) -> tuple
def ui_demo() -> str
```

### Configuration Files

#### `.env.example`
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Model Configuration
LLM_MODEL=gpt-4o-mini
EMBED_MODEL=text-embedding-3-small

# Server Configuration
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860

# Directory Configuration
INDEX_DIR=./data/faiss_indexes
PDF_DIR=./data/pdfs

# PDF Files
MEDICAL_PDF=HR_Policy_Medicalbenefits.pdf
DENTAL_PDF=dental_benefits_summary.pdf

# RAG Configuration
CHUNK_SIZE=800
CHUNK_OVERLAP=100
TOP_K=4

# Logging
LOG_LEVEL=INFO
```

#### `requirements.txt`
```
# Core Dependencies
langchain>=0.1.0
langchain-core>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.20
langchain-text-splitters>=0.0.1

# Vector Store
faiss-cpu>=1.7.4

# LLM Provider
openai>=1.0.0

# Web Interface
gradio>=4.0.0

# Configuration
python-dotenv>=1.0.0

# PDF Processing
PyMuPDF>=1.23.0

# Utilities
tiktoken>=0.5.0
```

#### `Dockerfile`
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY data/pdfs/ ./data/pdfs/

# Create directory for indexes
RUN mkdir -p ./data/faiss_indexes

# Expose Gradio port
EXPOSE 7860

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860

# Run application
CMD ["python", "-m", "app.main"]
```

#### `docker-compose.yml`
```yaml
version: '3.8'

services:
  rag-app:
    build: .
    container_name: multi-policy-rag
    ports:
      - "7860:7860"
    volumes:
      - ./data/pdfs:/app/data/pdfs:ro
      - ./data/faiss_indexes:/app/data/faiss_indexes:rw
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7860"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### `.dockerignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Documentation
docs/
*.md
!README.md

# Git
.git/
.gitignore

# Environment
.env
.env.local

# Tests
tests/
*.pytest_cache/

# Notebooks
*.ipynb
.ipynb_checkpoints/

# OS
.DS_Store
Thumbs.db

# Indexes (will be generated)
data/faiss_indexes/

# Logs
*.log
```

#### `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/
*.swp

# Generated indexes
data/faiss_indexes/

# Logs
*.log

# OS
.DS_Store
```

### Documentation Files

#### `README.md`
**Sections**:
1. Project Overview
2. Features
3. Architecture
4. Prerequisites
5. Quick Start
6. Configuration
7. Usage Guide
8. Development
9. Troubleshooting
10. License

#### `IMPLEMENTATION_PLAN.md`
- Detailed implementation strategy
- Phase-by-phase breakdown
- Timeline estimates
- Risk mitigation

#### `ARCHITECTURE.md`
- System architecture diagrams
- Component descriptions
- Data flow diagrams
- Technology stack

## Data Directory Structure

### `data/pdfs/`
**Purpose**: Source PDF documents
**Contents**:
- `dental_benefits_summary.pdf`: Dental policy document
- `HR_Policy_Medicalbenefits.pdf`: Medical policy document

**Characteristics**:
- Read-only in Docker
- Version controlled (optional)
- Can be replaced/updated

### `data/faiss_indexes/`
**Purpose**: Persistent vector store indexes
**Contents**:
- `medical_index/`: FAISS index for medical policy
  - `index.faiss`: Vector index
  - `index.pkl`: Metadata
- `dental_index/`: FAISS index for dental policy
  - `index.faiss`: Vector index
  - `index.pkl`: Metadata

**Characteristics**:
- Generated at runtime
- Persisted across restarts
- Not version controlled
- Read-write in Docker

## Module Dependencies

```
main.py
├── config.py
├── agent.py
│   ├── langchain_openai (ChatOpenAI, OpenAIEmbeddings)
│   ├── langchain_community (PyMuPDFLoader, FAISS)
│   └── langchain_text_splitters (RecursiveCharacterTextSplitter)
├── orchestrator.py
│   ├── agent.py (PolicyAgent)
│   ├── langchain_core (tool, messages)
│   └── langchain_openai (ChatOpenAI)
└── ui.py
    ├── gradio
    ├── orchestrator.py (ToolCallingOrchestrator)
    └── agent.py (build_or_load_vectorstore, clear_indexes)
```

## Build and Deployment Flow

```
1. Development
   ├── Edit source files in app/
   ├── Test locally with Python
   └── Validate functionality

2. Docker Build
   ├── docker-compose build
   ├── Copy app/ to container
   ├── Copy data/pdfs/ to container
   ├── Install dependencies
   └── Create image

3. Docker Run
   ├── docker-compose up
   ├── Mount volumes
   ├── Load environment variables
   ├── Start application
   └── Expose port 7860

4. Runtime
   ├── Check for existing indexes
   ├── Build indexes if needed
   ├── Initialize orchestrator
   ├── Launch Gradio server
   └── Accept user queries
```

## File Size Estimates

| Component | Estimated Size |
|-----------|---------------|
| Source Code (app/) | ~50 KB |
| Dependencies (installed) | ~500 MB |
| PDF Documents | ~2-5 MB |
| FAISS Indexes | ~10-50 MB per policy |
| Docker Image | ~1.5 GB |
| Container Runtime | ~2 GB |

## Version Control Strategy

### Files to Track
- All source code (`app/`)
- Configuration templates (`.env.example`)
- Docker files (`Dockerfile`, `docker-compose.yml`)
- Documentation (`*.md`)
- Requirements (`requirements.txt`)
- PDF documents (optional)

### Files to Ignore
- Environment files (`.env`)
- Generated indexes (`data/faiss_indexes/`)
- Python cache (`__pycache__/`)
- IDE files (`.vscode/`, `.idea/`)
- Logs (`*.log`)

---

**Document Version**: 1.0  
**Last Updated**: 2026-05-30  
**Status**: Planning Phase