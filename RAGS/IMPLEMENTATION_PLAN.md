# Multi-Policy RAG Application - Implementation Plan

## Executive Summary

This document outlines the plan to create a production-ready RAG (Retrieval-Augmented Generation) application based on the `multi_policy_rag_orchestrator_v3.py` notebook. The application will process Medical and Dental policy documents, provide intelligent query routing, and be deployed in a Docker container with a Gradio web interface.

## Architecture Analysis

### Current Architecture (from notebook)

The existing implementation follows a sophisticated multi-agent RAG pattern:

```
┌────────────────────────────────┐
│  Tool-calling Orchestrator     │
│  (LLM picks the tool based on  │
│   query intent; falls back to  │
│   the other tool on NOT_FOUND) │
└──────────────┬─────────────────┘
               │ tool calls
┌──────────────┴───────────────┐
▼                              ▼
┌──────────────────┐   ┌──────────────────┐
│ search_medical_  │   │ search_dental_   │
│ policy(query)    │   │ policy(query)    │
└────────┬─────────┘   └────────┬─────────┘
         │                      │
         ▼                      ▼
┌──────────────────┐   ┌──────────────────┐
│ MedicalAgent     │   │ DentalAgent      │
│ FAISS (on disk)  │   │ FAISS (on disk)  │
└──────────────────┘   └──────────────────┘
```

### Key Components

#### 1. **PolicyAgent Class**
- Single-policy RAG specialist
- Uses FAISS vector store for semantic search
- Implements strict `NOT_FOUND` contract
- Returns grounded answers with source provenance
- Configuration:
  - Chunk size: 800 characters
  - Chunk overlap: 100 characters
  - Top-k retrieval: 4 documents

#### 2. **ToolCallingOrchestrator Class**
- LLM-driven intent-based routing
- Two bound tools: `search_medical_policy` and `search_dental_policy`
- Intelligent fallback mechanism
- Chain-of-thought tracking
- Source policy attribution

#### 3. **Vector Store Management**
- Persistent FAISS indexes (saved to disk)
- PyMuPDF for PDF loading
- OpenAI embeddings (text-embedding-3-small)
- Metadata tagging for provenance

#### 4. **User Interface**
- Gradio web interface
- Two-tab layout:
  1. Policy loading and system building
  2. Query interface with chain-of-thought display
- Real-time source snippet display

### Key Features

1. **Intent-Aware Routing**: LLM analyzes query intent to select appropriate policy
2. **Fallback Chain**: Automatic fallback to alternate policy on `NOT_FOUND`
3. **Persistent Indexes**: One-time embedding with disk persistence
4. **Provenance Tracking**: Every chunk tagged with source policy and file
5. **Strict Prompt Engineering**: Prevents hallucination with `NOT_FOUND` contract

## Implementation Strategy

### Phase 1: Project Structure Setup

Create the following directory structure:

```
RAGS/
├── app/
│   ├── __init__.py
│   ├── main.py              # Main application entry point
│   ├── orchestrator.py      # ToolCallingOrchestrator class
│   ├── agent.py             # PolicyAgent class
│   ├── config.py            # Configuration management
│   └── ui.py                # Gradio interface
├── data/
│   ├── pdfs/                # PDF documents
│   │   ├── dental_benefits_summary.pdf
│   │   └── HR_Policy_Medicalbenefits.pdf
│   └── faiss_indexes/       # Persistent vector stores (created at runtime)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .dockerignore
├── README.md
└── IMPLEMENTATION_PLAN.md
```

### Phase 2: Code Adaptation

#### Changes Required:

1. **Remove Colab-specific code**:
   - Remove `from google.colab import userdata`
   - Remove `!pip install` commands
   - Remove Colab file upload widgets

2. **Environment Configuration**:
   - Use `python-dotenv` for environment variables
   - Support `.env` file for API key configuration
   - Add configuration validation

3. **Modularization**:
   - Split monolithic script into modules
   - Separate concerns (agent, orchestrator, UI, config)
   - Add proper error handling

4. **Gradio Adjustments**:
   - Remove `share=True` (not needed for local deployment)
   - Add proper server configuration
   - Configure for Docker networking

### Phase 3: Docker Configuration

#### Dockerfile Strategy:

```dockerfile
# Base image: Python 3.11 slim
# Install system dependencies for PDF processing
# Copy requirements and install Python packages
# Copy application code
# Create data directories
# Expose Gradio port (7860)
# Set environment variables
# Run application
```

#### docker-compose.yml Strategy:

```yaml
# Service: rag-app
# Build from Dockerfile
# Mount volumes for:
#   - PDF documents (read-only)
#   - FAISS indexes (persistent)
# Environment variables from .env
# Port mapping: 7860:7860
# Restart policy: unless-stopped
```

### Phase 4: Dependencies

#### Core Dependencies:
- `langchain>=0.1.0`
- `langchain-core>=0.1.0`
- `langchain-openai>=0.0.5`
- `langchain-community>=0.0.20`
- `langchain-text-splitters>=0.0.1`
- `faiss-cpu>=1.7.4`
- `openai>=1.0.0`
- `gradio>=4.0.0`
- `python-dotenv>=1.0.0`
- `PyMuPDF>=1.23.0`
- `tiktoken>=0.5.0`

### Phase 5: Configuration Management

#### Environment Variables:
- `OPENAI_API_KEY`: OpenAI API key (required)
- `LLM_MODEL`: Model name (default: gpt-4o-mini)
- `EMBED_MODEL`: Embedding model (default: text-embedding-3-small)
- `GRADIO_SERVER_NAME`: Server host (default: 0.0.0.0)
- `GRADIO_SERVER_PORT`: Server port (default: 7860)
- `INDEX_DIR`: FAISS index directory (default: ./data/faiss_indexes)
- `PDF_DIR`: PDF documents directory (default: ./data/pdfs)

### Phase 6: Testing Strategy

#### Local Testing (Pre-Docker):
1. Install dependencies in virtual environment
2. Configure `.env` file with API key
3. Place PDF documents in `data/pdfs/`
4. Run application: `python app/main.py`
5. Test in browser at `http://localhost:7860`
6. Verify:
   - PDF loading and indexing
   - Query routing (medical vs dental)
   - Fallback mechanism
   - Source attribution
   - Chain-of-thought display

#### Docker Testing:
1. Build image: `docker-compose build`
2. Run container: `docker-compose up`
3. Access at `http://localhost:7860`
4. Verify persistent indexes across restarts
5. Test volume mounts

## Deployment Architecture

### Container Architecture:

```
┌─────────────────────────────────────────┐
│         Docker Container                │
│  ┌───────────────────────────────────┐  │
│  │     Gradio Web Server             │  │
│  │     (Port 7860)                   │  │
│  └───────────┬───────────────────────┘  │
│              │                           │
│  ┌───────────▼───────────────────────┐  │
│  │   ToolCallingOrchestrator         │  │
│  │   (LLM + Tool Routing)            │  │
│  └───────────┬───────────────────────┘  │
│              │                           │
│  ┌───────────┴───────────────────────┐  │
│  │   PolicyAgent (Medical + Dental)  │  │
│  └───────────┬───────────────────────┘  │
│              │                           │
│  ┌───────────▼───────────────────────┐  │
│  │   FAISS Vector Stores             │  │
│  │   (Persistent Volume)             │  │
│  └───────────────────────────────────┘  │
│                                          │
│  ┌───────────────────────────────────┐  │
│  │   PDF Documents                   │  │
│  │   (Read-only Volume)              │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │
         │ Port 7860
         ▼
   Host Machine
   http://localhost:7860
```

### Volume Strategy:

1. **PDF Documents Volume**:
   - Host: `./data/pdfs`
   - Container: `/app/data/pdfs`
   - Mode: Read-only
   - Purpose: Source documents

2. **FAISS Indexes Volume**:
   - Host: `./data/faiss_indexes`
   - Container: `/app/data/faiss_indexes`
   - Mode: Read-write
   - Purpose: Persistent vector stores

## README Structure

The README.md will include:

### 1. Project Overview
- Application description
- Key features
- Architecture diagram

### 2. Prerequisites
- Docker and Docker Compose
- OpenAI API key
- System requirements

### 3. Quick Start
- Clone repository
- Configure environment
- Build and run
- Access application

### 4. Architecture Details
- Component descriptions
- Data flow diagrams
- Technology stack

### 5. Configuration
- Environment variables
- Model selection
- Advanced settings

### 6. Usage Guide
- Loading policies
- Asking questions
- Understanding results
- Chain-of-thought interpretation

### 7. Development
- Local development setup
- Running without Docker
- Testing procedures

### 8. Troubleshooting
- Common issues
- Debug mode
- Log analysis

### 9. Advanced Topics
- Custom PDF documents
- Model tuning
- Performance optimization

### 10. License and Credits

## Implementation Checklist

- [x] Analyze existing architecture
- [ ] Create project directory structure
- [ ] Modularize Python code
- [ ] Create requirements.txt
- [ ] Create .env.example
- [ ] Create Dockerfile
- [ ] Create docker-compose.yml
- [ ] Create .dockerignore
- [ ] Test locally (without Docker)
- [ ] Test with Docker
- [ ] Create comprehensive README.md
- [ ] Add architecture diagrams
- [ ] Document troubleshooting steps
- [ ] Final validation

## Success Criteria

The implementation will be considered successful when:

1. ✅ Application runs in Docker container
2. ✅ Accessible at http://localhost:7860
3. ✅ Successfully loads both PDF documents
4. ✅ Creates and persists FAISS indexes
5. ✅ Correctly routes queries to appropriate policy
6. ✅ Implements fallback mechanism
7. ✅ Displays chain-of-thought reasoning
8. ✅ Shows source attribution
9. ✅ Survives container restarts (persistent indexes)
10. ✅ README provides clear deployment instructions

## Timeline Estimate

- **Phase 1** (Structure): 30 minutes
- **Phase 2** (Code Adaptation): 1-2 hours
- **Phase 3** (Docker Config): 30 minutes
- **Phase 4** (Dependencies): 15 minutes
- **Phase 5** (Configuration): 30 minutes
- **Phase 6** (Testing): 1 hour
- **Documentation**: 1-2 hours

**Total Estimated Time**: 4-6 hours

## Risk Mitigation

### Potential Issues:

1. **PDF Loading Failures**
   - Mitigation: Support multiple PDF loaders (PyMuPDF, PyPDF, PDFPlumber)
   - Fallback mechanism in code

2. **FAISS Serialization Issues**
   - Mitigation: Proper volume permissions
   - Clear error messages

3. **OpenAI API Rate Limits**
   - Mitigation: Implement retry logic
   - Add rate limit handling

4. **Memory Constraints**
   - Mitigation: Optimize chunk size
   - Monitor container resources

5. **Port Conflicts**
   - Mitigation: Configurable port mapping
   - Document port requirements

## Next Steps

Once this plan is approved, proceed with:

1. Create directory structure
2. Begin code modularization
3. Set up Docker configuration
4. Implement testing strategy
5. Create comprehensive documentation

---

**Plan Status**: Ready for Implementation
**Last Updated**: 2026-05-30
**Version**: 1.0