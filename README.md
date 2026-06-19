# 🚀 Jorge Betancourt - AI/ML Engineering Portfolio

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![ML](https://img.shields.io/badge/ML-PyTorch%20%7C%20Scikit--learn-orange?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat-square&logo=docker)
![LangChain](https://img.shields.io/badge/LangChain-RAG-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success?style=flat-square)

---

## 👨‍💻 About Me

**Senior Data Scientist and AI Engineer** with extensive experience building production-grade machine learning systems. Specialized in **customer analytics**, **sentiment analysis**, and **intelligent document processing** using state-of-the-art NLP and deep learning techniques.

**Core Expertise:**
- End-to-end ML pipeline development and deployment
- Customer behavior prediction and churn analysis
- RAG (Retrieval-Augmented Generation) systems
- Containerized ML applications with Docker
- Production-ready APIs with FastAPI and Gradio

**Technical Stack:** Python • PyTorch • Scikit-learn • Transformers • LangChain • FAISS • FastAPI • Gradio • Docker • Pandas • NumPy

**Track Record:** Proven ability to deliver data-driven insights that create measurable business impact through scalable, production-ready AI solutions.

---

## 📚 How to Use This Portfolio

This portfolio showcases **4 production-ready AI/ML projects**, each with complete documentation, deployment instructions, and working code. Each project demonstrates different aspects of modern ML engineering:

- **Click project titles** to navigate to detailed documentation
- **Docker-ready**: All projects include containerization for easy deployment
- **Well-documented**: Comprehensive READMEs with setup instructions
- **Production-grade**: Real-world applications with proper error handling and testing

---

## 🚀 Featured Projects

### 1. 📊 [Customer Churn & Category Profitability Analysis](./CustomerAndCategoryDeepDive)

**Advanced ML solution for customer retention and business optimization**

A comprehensive machine learning system that predicts customer churn with exceptional accuracy and analyzes product category profitability to drive strategic business decisions.

**Key Achievements:**
- 🎯 **99.77% ROC-AUC** - Industry-leading churn prediction accuracy
- 📈 **99.06% Accuracy** with 100% precision (zero false positives)
- 💰 **$33.9M Revenue Analyzed** across multiple product categories
- 🎨 **Interactive Gradio Dashboard** for real-time predictions

**Technologies:** Python • Scikit-learn • Gradient Boosting • Pandas • Gradio • Plotly

**Features:**
- Real-time churn risk prediction with confidence scores
- Category and subcategory profitability analysis
- Trend identification (gaining/losing categories)
- Personalized retention recommendations
- Feature importance analysis

**Status:** ✅ Production Ready | [View Documentation](./CustomerAndCategoryDeepDive/README.md)

---

### 2. 🤖 [Multi-Policy RAG Orchestrator](./RAGS)

**Intelligent document querying system with LLM-driven routing**

A production-ready Retrieval-Augmented Generation application that intelligently routes queries across Medical and Dental policy documents using LLM tool calling and persistent FAISS vector stores.

**Key Features:**
- 🧠 **Intelligent Query Routing** - LLM analyzes intent and selects appropriate policy
- 🔄 **Automatic Fallback** - Queries alternate policy if first returns NOT_FOUND
- 💾 **Persistent Vector Stores** - FAISS indexes built once, reloaded in seconds
- 📊 **Chain-of-Thought Display** - Transparent reasoning process
- 🎯 **Source Attribution** - Every answer includes page numbers and policy labels

**Technologies:** Python • LangChain • OpenAI GPT-4 • FAISS • Gradio • Docker

**Architecture Highlights:**
- Tool-calling orchestrator with strict NOT_FOUND contract
- Persistent vector indexes for fast retrieval
- Clean separation of concerns (Agent → Orchestrator → UI)
- Docker Compose for easy deployment

**Status:** ✅ Production Ready | [View Documentation](./RAGS/README.md) | [Architecture Details](./RAGS/ARCHITECTURE.md)

---

### 3. 🎯 [Customer Review Classification API](./SentimentBob)

**AI-powered review classification with DistilBERT**

A containerized web application using a fine-tuned DistilBERT transformer model to classify customer reviews into 6 categories with high accuracy and confidence scores.

**Key Features:**
- 🤖 **Fine-tuned DistilBERT** - State-of-the-art transformer model
- 📊 **6 Classification Categories** - General Inquiry, Product Issue, Refund, Cancellation, Praise, Technical Support
- ⚡ **Single & Batch Processing** - Classify up to 100 reviews at once
- 🎨 **Responsive Web UI** - Modern HTML/CSS/JavaScript interface
- 🔌 **RESTful API** - Well-documented endpoints with OpenAPI docs

**Technologies:** Python • PyTorch • Transformers • DistilBERT • FastAPI • Docker

**API Endpoints:**
- `POST /classify` - Single review classification
- `POST /classify/batch` - Batch processing (up to 100 reviews)
- `GET /health` - System health check
- `GET /labels` - Available classification labels

**Status:** ✅ Production Ready | [View Documentation](./SentimentBob/README.md) | [Quick Start Guide](./SentimentBob/QUICKSTART.md)

---

### 4. 🏗️ [Big Data & AI Infrastructure](./BigData%20and%20AI)

**Architecture and design documentation for scalable AI systems**

Comprehensive documentation on architecting big data and AI infrastructure for enterprise-scale deployments.

**Contents:**
- 📄 [Architecting Big Data & AI Infrastructure.pdf](./BigData%20and%20AI/Architecting%20Big%20Data%20&%20AI%20Infrastructure.pdf)

**Topics Covered:**
- Scalable data pipeline design
- ML infrastructure best practices
- Cloud deployment strategies
- Performance optimization techniques

**Status:** 📚 Documentation

---

## 🛠️ Technologies & Tools

### **Languages & Frameworks**
- **Python 3.8+** - Primary development language
- **FastAPI** - High-performance API framework
- **Gradio** - Interactive ML web interfaces

### **Machine Learning & AI**
- **PyTorch** - Deep learning framework
- **Scikit-learn** - Classical ML algorithms
- **Transformers (Hugging Face)** - Pre-trained models
- **LangChain** - LLM application framework
- **OpenAI GPT-4** - Large language models

### **Data & Vector Stores**
- **Pandas & NumPy** - Data manipulation
- **FAISS** - Vector similarity search
- **Plotly & Matplotlib** - Data visualization

### **Deployment & DevOps**
- **Docker & Docker Compose** - Containerization
- **Git & GitHub** - Version control
- **RESTful APIs** - Service architecture

---

## 📂 Repository Structure

```
Portfolio/
├── README.md                          # This file
├── .gitignore                         # Git ignore patterns
├── LICENSE                            # MIT License
├── Jorge_Betancourt_ResumeOpt2026.pdf # Professional resume
├── BigData and AI/                    # Infrastructure documentation
├── CustomerAndCategoryDeepDive/       # Churn prediction & profitability
├── RAGS/                              # Multi-policy RAG system
└── SentimentBob/                      # Review classification API
```

---

## 📄 Additional Resources

- 📋 **Resume**: [Jorge_Betancourt_ResumeOpt2026.pdf](./Jorge_Betancourt_ResumeOpt2026.pdf)
- 📜 **License**: [MIT License](./LICENSE)
- 💼 **GitHub**: [@jebetancourt1976](https://github.com/jebetancourt1976)

---

## 🤝 Let's Connect

I'm always interested in discussing AI/ML projects, collaboration opportunities, or consulting engagements.

- 📧 **Email**: Available upon request
- 💼 **LinkedIn**: [Connect with me](https://linkedin.com/in/jorge-betancourt)
- 🐙 **GitHub**: [@jebetancourt1976](https://github.com/jebetancourt1976)

---

## 📊 Project Statistics

| Project | Type | Status | Key Metric |
|---------|------|--------|------------|
| Customer Churn Analysis | ML Pipeline | ✅ Production | 99.77% ROC-AUC |
| RAG Orchestrator | LLM Application | ✅ Production | Multi-policy routing |
| Review Classification | NLP API | ✅ Production | 6-class classification |
| Big Data Infrastructure | Documentation | 📚 Reference | Architecture guide |

---

## 📝 License

This portfolio is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

<div align="center">

**Built with ❤️ using Python, PyTorch, LangChain, and Docker**

*Last Updated: June 2026*

⭐ **If you find these projects interesting, please consider starring this repository!** ⭐

</div>