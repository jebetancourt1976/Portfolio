# 🎯 Customer Review Classification API

A containerized web application that uses a fine-tuned DistilBERT model to classify customer reviews into 6 categories. Built with FastAPI backend and a responsive HTML/JavaScript frontend, all running in Docker.

## 📋 Features

- **AI-Powered Classification**: Uses DistilBERT transformer model for accurate review classification
- **6 Classification Categories**:
  - 🔵 General Inquiry
  - 🔴 Product Issue
  - 🟠 Refund Issue
  - 🟣 Cancellation
  - 🟢 Praise
  - 🔷 Technical Support
- **Single & Batch Processing**: Classify one review or up to 100 reviews at once
- **Real-time Results**: Instant classification with confidence scores
- **Responsive UI**: Clean, modern interface that works on all devices
- **Docker Containerized**: Easy deployment with Docker and Docker Compose
- **RESTful API**: Well-documented API endpoints with automatic OpenAPI docs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Container                      │
│  ┌────────────────────────────────────────────────────┐ │
│  │           FastAPI Application (Port 8000)          │ │
│  │                                                    │ │
│  │  ┌──────────────┐      ┌──────────────────────┐  │ │
│  │  │   Frontend   │◄────►│   API Endpoints      │  │ │
│  │  │  HTML/CSS/JS │      │  /classify           │  │ │
│  │  └──────────────┘      │  /classify/batch     │  │ │
│  │                        │  /health             │  │ │
│  │                        │  /labels             │  │ │
│  │                        └──────────┬───────────┘  │ │
│  │                                   │              │ │
│  │                        ┌──────────▼───────────┐  │ │
│  │                        │  Review Classifier   │  │ │
│  │                        │  (DistilBERT Model)  │  │ │
│  │                        └──────────────────────┘  │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
SentimentBob/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Pydantic models
│   ├── classifier.py            # Model loading & inference
│   └── static/
│       ├── index.html           # Frontend UI
│       ├── styles.css           # Styling
│       └── script.js            # Frontend logic
├── student_distilbert.pth       # Pre-trained model weights
├── customer_tickets_large.xls   # Sample data
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container definition
├── docker-compose.yml           # Container orchestration
├── .dockerignore               # Docker ignore patterns
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### Installation & Running

1. **Clone or navigate to the project directory**:
   ```bash
   cd SentimentBob
   ```

2. **Build and start the container**:
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build the Docker image
   - Install all dependencies
   - Load the DistilBERT model
   - Start the API server on port 8000

3. **Access the application**:
   - **Web Interface**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

### Stopping the Application

```bash
docker-compose down
```

## 🔧 API Endpoints

### Health Check
```http
GET /health
```
Returns system status and model loading state.

**Response**:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### Get Labels
```http
GET /labels
```
Returns the label mapping dictionary.

**Response**:
```json
{
  "labels": {
    "0": "General Inquiry",
    "1": "Product Issue",
    "2": "Refund Issue",
    "3": "Cancellation",
    "4": "Praise",
    "5": "Technical Support"
  }
}
```

### Classify Single Review
```http
POST /classify
Content-Type: application/json

{
  "text": "Great service, thank you!"
}
```

**Response**:
```json
{
  "text": "Great service, thank you!",
  "label": "Praise",
  "label_id": 4,
  "confidence": 0.9823
}
```

### Classify Batch Reviews
```http
POST /classify/batch
Content-Type: application/json

{
  "reviews": [
    "Great service, thank you!",
    "My device won't turn on",
    "I want my money back immediately"
  ]
}
```

**Response**:
```json
{
  "results": [
    {
      "text": "Great service, thank you!",
      "label": "Praise",
      "label_id": 4,
      "confidence": 0.9823
    },
    {
      "text": "My device won't turn on",
      "label": "Technical Support",
      "label_id": 5,
      "confidence": 0.9567
    },
    {
      "text": "I want my money back immediately",
      "label": "Refund Issue",
      "label_id": 2,
      "confidence": 0.9234
    }
  ],
  "total_processed": 3
}
```

## 💻 Development

### Running Without Docker

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Testing the API with curl

**Single classification**:
```bash
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "Great service, thank you!"}'
```

**Batch classification**:
```bash
curl -X POST "http://localhost:8000/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{"reviews": ["Great service!", "My device is broken"]}'
```

## 🎨 Frontend Features

- **Single Review Classification**: Input one review and get instant results
- **Batch Processing**: Process up to 100 reviews at once
- **Real-time Validation**: Character count and review count tracking
- **Color-coded Labels**: Each category has a distinct color
- **Confidence Scores**: See how confident the model is about each prediction
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Error Handling**: Clear error messages for better user experience

## 🔒 Security Features

- Non-root user in Docker container
- Input validation and sanitization
- CORS middleware configured
- Health checks for container monitoring
- No sensitive data exposure

## 📊 Model Information

- **Architecture**: DistilBERT (distilbert-base-uncased)
- **Task**: Multi-class text classification
- **Classes**: 6 categories
- **Input**: Text reviews (max 512 characters)
- **Output**: Label, label ID, and confidence score

## 🐛 Troubleshooting

### Model Not Loading
- Ensure `student_distilbert.pth` exists in the project root
- Check Docker logs: `docker-compose logs`
- Verify the model file is not corrupted

### Port Already in Use
- Change the port in `docker-compose.yml`:
  ```yaml
  ports:
    - "8080:8000"  # Use 8080 instead of 8000
  ```

### Container Won't Start
- Check Docker logs: `docker-compose logs review-classifier`
- Ensure Docker has enough memory allocated (at least 4GB recommended)
- Verify all files are present in the project directory

## 📝 License

This project is provided as-is for educational and commercial use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Support

For issues or questions, please check the logs or create an issue in the repository.

---

**Built with ❤️ using FastAPI, PyTorch, and DistilBERT**