# Multi-Policy RAG Orchestrator

A production-ready Retrieval-Augmented Generation (RAG) application that intelligently routes queries across Medical and Dental policy documents using LLM-driven tool calling and persistent vector stores.

## 🌟 Features

- **🤖 Intelligent Query Routing**: LLM analyzes query intent to select the appropriate policy (Medical or Dental)
- **🔄 Automatic Fallback**: If the first policy returns `NOT_FOUND`, automatically queries the other policy
- **💾 Persistent Vector Stores**: FAISS indexes are built once and reloaded from disk on subsequent runs
- **📊 Chain-of-Thought Display**: See the reasoning process behind each answer
- **🔍 Source Attribution**: Every answer includes source snippets with page numbers and policy labels
- **🐳 Docker Ready**: Fully containerized with Docker Compose for easy deployment
- **🎨 Modern UI**: Clean Gradio web interface with two-tab layout

## 🏗️ Architecture

```
┌────────────────────────────────┐
│  Tool-calling Orchestrator     │
│  (LLM picks tool based on      │
│   query intent; falls back to  │
│   other tool on NOT_FOUND)     │
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

1. **PolicyAgent**: Single-policy RAG specialist with strict `NOT_FOUND` contract
2. **ToolCallingOrchestrator**: LLM-driven router with automatic fallback
3. **FAISS Vector Stores**: Persistent semantic search indexes
4. **Gradio UI**: Two-tab interface for system management and queries

## 📋 Prerequisites

- **Docker & Docker Compose** (recommended) OR
- **Python 3.11+** (for local development)
- **OpenAI API Key** (required)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

1. **Clone and navigate to the repository**:
   ```bash
   cd RAGS
   ```

2. **Configure environment**:
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_key_here
   ```

3. **Ensure PDF files are in place**:
   ```bash
   # PDFs should be in data/pdfs/
   ls data/pdfs/
   # Should show: HR_Policy_Medicalbenefits.pdf, dental_benefits_summary.pdf
   ```

4. **Build and run**:
   ```bash
   docker-compose up --build
   ```

5. **Access the application**:
   Open your browser to [http://localhost:7860](http://localhost:7860)

### Option 2: Local Development

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run the application**:
   ```bash
   python -m app.main
   ```

5. **Access the application**:
   Open your browser to [http://localhost:7860](http://localhost:7860)

## 📖 Usage Guide

### Tab 1: Load Policies

1. **First Run**: Click "Build / Load System" to create FAISS indexes from PDFs
   - This takes 30-60 seconds as it embeds the documents
   - Indexes are saved to `data/faiss_indexes/`

2. **Subsequent Runs**: Indexes are automatically loaded from disk (2-5 seconds)

3. **Rebuild Indexes**: Click "Clear & Rebuild Indexes" if PDFs change

### Tab 2: Ask Questions

1. **Enter your question** in the text box
2. **Click "Ask"** or press Enter
3. **View results**:
   - **Final Answer**: The answer with policy badge (🩺 Medical or 🦷 Dental)
   - **Chain of Thought**: Step-by-step reasoning process
   - **Source Snippets**: Retrieved text chunks with page numbers

### Example Questions

- "Is a root canal covered?"
- "What is the annual out-of-pocket maximum?"
- "Does the plan cover orthodontia for adults?"
- "Are MRI scans covered?"
- "What are the copays for specialist visits?"

## ⚙️ Configuration

All configuration is managed through environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | Your OpenAI API key |
| `LLM_MODEL` | `gpt-4o-mini` | Model for routing and generation |
| `EMBED_MODEL` | `text-embedding-3-small` | Embedding model |
| `CHUNK_SIZE` | `800` | Text chunk size for splitting |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `TOP_K` | `4` | Number of chunks to retrieve |
| `GRADIO_SERVER_PORT` | `7860` | Web server port |

## 🐳 Docker Details

### Volume Mounts

- `./data/pdfs` → `/app/data/pdfs` (read-only): Source PDF documents
- `./data/faiss_indexes` → `/app/data/faiss_indexes` (read-write): Persistent indexes

### Container Management

```bash
# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up --build
```

## 🔧 Development

### Project Structure

```
RAGS/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── agent.py             # PolicyAgent implementation
│   ├── orchestrator.py      # ToolCallingOrchestrator
│   └── ui.py                # Gradio interface
├── data/
│   ├── pdfs/                # PDF documents
│   └── faiss_indexes/       # Generated indexes
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose config
└── .env                    # Environment variables
```

### Adding New Policies

1. Place PDF in `data/pdfs/`
2. Update `Config` class in `app/config.py`
3. Create new `PolicyAgent` in `app/main.py`
4. Add new tool in `app/orchestrator.py`
5. Update orchestrator system prompt

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=app tests/
```

## 🐛 Troubleshooting

### Issue: "OPENAI_API_KEY is required"
**Solution**: Ensure `.env` file exists with valid API key

### Issue: "PDF not found"
**Solution**: Verify PDFs are in `data/pdfs/` directory

### Issue: Port 7860 already in use
**Solution**: Change `GRADIO_SERVER_PORT` in `.env` or stop conflicting service

### Issue: Indexes not persisting in Docker
**Solution**: Check volume mounts in `docker-compose.yml`

### Issue: Out of memory during indexing
**Solution**: Reduce `CHUNK_SIZE` or process PDFs separately

## 📊 Performance

- **First Run**: 30-60 seconds (embedding time)
- **Subsequent Runs**: 2-5 seconds (load from disk)
- **Query Response**: 2-5 seconds (retrieval + LLM generation)
- **Memory Usage**: ~500MB-1GB

## 🔒 Security

- API keys stored in environment variables (never committed)
- PDF directory mounted read-only in Docker
- No external network access except OpenAI API
- Can run behind reverse proxy for production

## 📝 How It Works

### 1. Intent-Based Routing

The orchestrator uses an LLM with two bound tools:
- `search_medical_policy`: For medical coverage questions
- `search_dental_policy`: For dental coverage questions

The LLM analyzes the query and selects the appropriate tool.

### 2. Strict NOT_FOUND Contract

Each PolicyAgent uses a strict prompt that enforces:
- Answer only from retrieved context
- Return exactly "NOT_FOUND" if context lacks information
- Never use outside knowledge or guess

### 3. Automatic Fallback

If the first tool returns `NOT_FOUND`, the orchestrator automatically calls the other tool before giving up.

### 4. Persistent Indexes

FAISS indexes are saved to disk after first build:
- Medical: `data/faiss_indexes/medical_index/`
- Dental: `data/faiss_indexes/dental_index/`

Subsequent runs reload in seconds instead of re-embedding.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/)
- UI powered by [Gradio](https://gradio.app/)
- Vector search by [FAISS](https://github.com/facebookresearch/faiss)
- LLM by [OpenAI](https://openai.com/)

## 📧 Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

---

**Version**: 1.0.0  
**Last Updated**: 2026-05-30  
**Status**: Production Ready ✅