# Multi-Policy RAG Application - Architecture Documentation

## System Architecture Overview

This document provides detailed architectural diagrams and explanations for the Multi-Policy RAG (Retrieval-Augmented Generation) application.

## High-Level Architecture

```mermaid
graph TB
    User[User Browser] -->|HTTP Request| Gradio[Gradio Web Interface]
    Gradio -->|Query| Orchestrator[Tool-Calling Orchestrator]
    
    Orchestrator -->|Intent Analysis| LLM[OpenAI GPT-4o-mini]
    LLM -->|Tool Selection| Orchestrator
    
    Orchestrator -->|Route Query| MedTool[search_medical_policy]
    Orchestrator -->|Route Query| DenTool[search_dental_policy]
    
    MedTool -->|Invoke| MedAgent[Medical PolicyAgent]
    DenTool -->|Invoke| DenAgent[Dental PolicyAgent]
    
    MedAgent -->|Semantic Search| MedVS[Medical FAISS Index]
    DenAgent -->|Semantic Search| DenVS[Dental FAISS Index]
    
    MedVS -->|Retrieve Chunks| MedAgent
    DenVS -->|Retrieve Chunks| DenAgent
    
    MedAgent -->|Context + Prompt| LLM
    DenAgent -->|Context + Prompt| LLM
    
    LLM -->|Answer/NOT_FOUND| MedAgent
    LLM -->|Answer/NOT_FOUND| DenAgent
    
    MedAgent -->|Result| Orchestrator
    DenAgent -->|Result| Orchestrator
    
    Orchestrator -->|Final Answer| Gradio
    Gradio -->|HTML Response| User
    
    style Orchestrator fill:#e1f5ff
    style LLM fill:#fff4e1
    style MedAgent fill:#e8f5e9
    style DenAgent fill:#e8f5e9
    style MedVS fill:#f3e5f5
    style DenVS fill:#f3e5f5
```

## Component Architecture

### 1. Gradio Web Interface Layer

```mermaid
graph LR
    subgraph "Gradio UI"
        Tab1[Tab 1: Load Policies]
        Tab2[Tab 2: Ask Questions]
        
        Tab1 --> Upload[File Upload]
        Tab1 --> Build[Build System Button]
        Tab1 --> Rebuild[Rebuild Indexes Button]
        Tab1 --> Demo[NOT_FOUND Demo Button]
        
        Tab2 --> Input[Question Input]
        Tab2 --> Ask[Ask Button]
        Tab2 --> Answer[Answer Display]
        Tab2 --> COT[Chain of Thought]
        Tab2 --> Sources[Source Snippets]
    end
    
    style Tab1 fill:#e3f2fd
    style Tab2 fill:#e8f5e9
```

**Responsibilities:**
- User interaction and input collection
- File upload handling
- Result visualization
- Chain-of-thought display
- Source attribution presentation

### 2. Orchestrator Layer

```mermaid
graph TB
    subgraph "ToolCallingOrchestrator"
        Init[Initialize with LLM + Tools]
        Receive[Receive User Query]
        System[Apply System Prompt]
        
        Receive --> System
        System --> LLMCall[LLM Tool Selection]
        
        LLMCall --> Decision{Tool Selected?}
        Decision -->|Medical| CallMed[Call search_medical_policy]
        Decision -->|Dental| CallDen[Call search_dental_policy]
        
        CallMed --> CheckMed{Result Found?}
        CallDen --> CheckDen{Result Found?}
        
        CheckMed -->|Yes| Return[Return Answer]
        CheckMed -->|NOT_FOUND| Fallback1[Call search_dental_policy]
        
        CheckDen -->|Yes| Return
        CheckDen -->|NOT_FOUND| Fallback2[Call search_medical_policy]
        
        Fallback1 --> CheckFB1{Result Found?}
        Fallback2 --> CheckFB2{Result Found?}
        
        CheckFB1 -->|Yes| Return
        CheckFB1 -->|NOT_FOUND| NotFound[Return: Not found in any policy]
        
        CheckFB2 -->|Yes| Return
        CheckFB2 -->|NOT_FOUND| NotFound
    end
    
    style LLMCall fill:#fff4e1
    style Return fill:#c8e6c9
    style NotFound fill:#ffcdd2
```

**Key Features:**
- Intent-based routing using LLM tool calling
- Automatic fallback mechanism
- Chain-of-thought tracking
- Source policy attribution
- Max iteration safety net

### 3. PolicyAgent Layer

```mermaid
graph TB
    subgraph "PolicyAgent Medical/Dental"
        Query[Receive Query]
        Query --> Retrieve[Retrieve Top-K Documents]
        Retrieve --> Format[Format Context]
        Format --> Prompt[Apply Strict Prompt Template]
        
        Prompt --> LLMGen[LLM Generation]
        
        LLMGen --> Parse[Parse Response]
        Parse --> Check{Contains NOT_FOUND?}
        
        Check -->|Yes| SetNotFound[Set found=False]
        Check -->|No| SetFound[Set found=True]
        
        SetNotFound --> Package[Package Result]
        SetFound --> Package
        
        Package --> AddMeta[Add Source Metadata]
        AddMeta --> Return[Return Result Dict]
    end
    
    style Retrieve fill:#e1f5ff
    style LLMGen fill:#fff4e1
    style Return fill:#c8e6c9
```

**Strict Prompt Contract:**
```
RULES:
1. If context contains answer → provide factual answer + quote
2. If context lacks information → return exactly "NOT_FOUND"
3. Never use outside knowledge
4. Never guess
```

### 4. Vector Store Layer

```mermaid
graph LR
    subgraph "FAISS Vector Store Management"
        Check{Index Exists?}
        Check -->|Yes| Load[Load from Disk]
        Check -->|No| Build[Build New Index]
        
        Build --> LoadPDF[Load PDF with PyMuPDF]
        LoadPDF --> Split[Split into Chunks]
        Split --> Tag[Tag with Metadata]
        Tag --> Embed[Generate Embeddings]
        Embed --> Create[Create FAISS Index]
        Create --> Save[Save to Disk]
        
        Load --> Ready[Index Ready]
        Save --> Ready
    end
    
    style Load fill:#c8e6c9
    style Build fill:#fff4e1
    style Ready fill:#e1f5ff
```

**Chunking Strategy:**
- Chunk size: 800 characters
- Overlap: 100 characters
- Separators: `\n\n`, `\n`, `. `, ` `, ``
- Metadata: policy label, source file, page number

## Data Flow Diagrams

### Query Processing Flow

```mermaid
sequenceDiagram
    participant User
    participant Gradio
    participant Orchestrator
    participant LLM
    participant MedAgent
    participant DenAgent
    participant FAISS
    
    User->>Gradio: Submit Question
    Gradio->>Orchestrator: answer(question)
    
    Orchestrator->>LLM: System Prompt + Question
    LLM->>Orchestrator: Tool Call: search_dental_policy
    
    Orchestrator->>DenAgent: ask(question)
    DenAgent->>FAISS: Retrieve top-4 chunks
    FAISS->>DenAgent: Return chunks
    
    DenAgent->>LLM: Strict Prompt + Context + Question
    LLM->>DenAgent: "NOT_FOUND"
    
    DenAgent->>Orchestrator: {answer: "NOT_FOUND", found: false}
    
    Note over Orchestrator: Fallback triggered
    
    Orchestrator->>MedAgent: ask(question)
    MedAgent->>FAISS: Retrieve top-4 chunks
    FAISS->>MedAgent: Return chunks
    
    MedAgent->>LLM: Strict Prompt + Context + Question
    LLM->>MedAgent: "Coverage details..."
    
    MedAgent->>Orchestrator: {answer: "...", found: true, sources: [...]}
    Orchestrator->>Gradio: Final result with COT
    Gradio->>User: Display answer + sources
```

### Index Building Flow

```mermaid
sequenceDiagram
    participant User
    participant Gradio
    participant System
    participant Loader
    participant Splitter
    participant Embeddings
    participant FAISS
    participant Disk
    
    User->>Gradio: Upload PDFs + Click Build
    Gradio->>System: build_system(medical_pdf, dental_pdf)
    
    System->>System: Check if indexes exist
    
    alt Indexes exist
        System->>Disk: Load indexes
        Disk->>System: Return indexes
    else Indexes don't exist
        System->>Loader: Load PDF
        Loader->>System: Return pages
        
        System->>Splitter: Split into chunks
        Splitter->>System: Return chunks
        
        System->>System: Tag chunks with metadata
        
        System->>Embeddings: Generate embeddings
        Embeddings->>System: Return vectors
        
        System->>FAISS: Create index
        FAISS->>System: Return index
        
        System->>Disk: Save index
    end
    
    System->>Gradio: System ready
    Gradio->>User: Display success message
```

## Docker Deployment Architecture

```mermaid
graph TB
    subgraph "Host Machine"
        Browser[Web Browser]
        PDFDir[./data/pdfs/]
        IndexDir[./data/faiss_indexes/]
    end
    
    subgraph "Docker Container"
        subgraph "Application Layer"
            Gradio[Gradio Server :7860]
            Main[main.py]
            Orch[orchestrator.py]
            Agent[agent.py]
            Config[config.py]
        end
        
        subgraph "Data Layer"
            PDFMount[/app/data/pdfs/]
            IndexMount[/app/data/faiss_indexes/]
        end
        
        subgraph "Dependencies"
            LangChain[LangChain]
            FAISS[FAISS-CPU]
            OpenAI[OpenAI SDK]
            PyMuPDF[PyMuPDF]
        end
    end
    
    Browser -->|http://localhost:7860| Gradio
    PDFDir -.->|Volume Mount Read-Only| PDFMount
    IndexDir -.->|Volume Mount Read-Write| IndexMount
    
    Main --> Orch
    Main --> Agent
    Main --> Config
    Orch --> Agent
    
    Agent --> LangChain
    Agent --> FAISS
    Agent --> OpenAI
    Agent --> PyMuPDF
    
    Agent --> PDFMount
    Agent --> IndexMount
    
    style Browser fill:#e3f2fd
    style Gradio fill:#c8e6c9
    style PDFMount fill:#fff9c4
    style IndexMount fill:#fff9c4
```

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.11+ | Application runtime |
| LLM | OpenAI GPT-4o-mini | Latest | Query routing & generation |
| Embeddings | text-embedding-3-small | Latest | Document vectorization |
| Vector Store | FAISS | 1.7.4+ | Semantic search |
| Web Framework | Gradio | 4.0+ | User interface |
| PDF Processing | PyMuPDF | 1.23+ | Document loading |
| Orchestration | LangChain | 0.1+ | RAG pipeline |
| Containerization | Docker | 20.10+ | Deployment |

### Python Dependencies

```
langchain>=0.1.0
langchain-core>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.20
langchain-text-splitters>=0.0.1
faiss-cpu>=1.7.4
openai>=1.0.0
gradio>=4.0.0
python-dotenv>=1.0.0
PyMuPDF>=1.23.0
tiktoken>=0.5.0
```

## Security Considerations

### API Key Management
- API keys stored in environment variables
- Never committed to version control
- `.env.example` provided as template
- Docker secrets support (optional)

### Volume Permissions
- PDF directory: Read-only mount
- Index directory: Read-write with proper permissions
- No sensitive data in logs

### Network Security
- Container exposes only port 7860
- No external network access required (except OpenAI API)
- Can run behind reverse proxy

## Performance Characteristics

### Embedding Performance
- **First Run**: 30-60 seconds per PDF (embedding time)
- **Subsequent Runs**: 2-5 seconds (load from disk)
- **Memory Usage**: ~500MB-1GB depending on document size

### Query Performance
- **Retrieval**: 50-100ms (FAISS search)
- **LLM Generation**: 1-3 seconds (OpenAI API)
- **Total Response Time**: 2-5 seconds typical

### Scalability
- **Documents**: Tested with 2 policies, scales to 10+
- **Concurrent Users**: 5-10 (Gradio limitation)
- **Index Size**: ~10-50MB per policy

## Monitoring and Observability

### Logging Strategy
```python
# Application logs
- INFO: System initialization
- INFO: Index loading/building
- INFO: Query processing
- DEBUG: Tool calls and responses
- ERROR: Failures and exceptions

# Chain of Thought
- Captured in UI for each query
- Shows decision-making process
- Useful for debugging routing
```

### Health Checks
- Container health: Gradio server responsive
- Index health: Files exist and loadable
- API health: OpenAI connectivity

## Future Enhancements

### Potential Improvements
1. **Multi-tenancy**: Support multiple policy sets
2. **Authentication**: User login and access control
3. **Analytics**: Query logging and analysis
4. **Caching**: Response caching for common queries
5. **Streaming**: Real-time response streaming
6. **API Mode**: REST API alongside web UI
7. **Advanced Retrieval**: Hybrid search, reranking
8. **Model Selection**: Support multiple LLM providers

---

**Document Version**: 1.0  
**Last Updated**: 2026-05-30  
**Status**: Planning Phase