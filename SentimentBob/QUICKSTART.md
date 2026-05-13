# 🚀 Quick Start Guide

Get the Customer Review Classification API up and running in 3 simple steps!

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually comes with Docker Desktop)

## Step 1: Build and Start 🏗️

Open a terminal in the project directory and run:

```bash
docker-compose up --build
```

**What happens:**
- Docker builds the container image (~2-3 minutes first time)
- Installs Python dependencies
- Loads the DistilBERT model
- Starts the API server on port 8000

**Wait for this message:**
```
review-classifier-api  | INFO:     Application startup complete.
review-classifier-api  | INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 2: Access the Application 🌐

Open your web browser and go to:

### 🎨 Web Interface
**http://localhost:8000**

Use the beautiful web interface to:
- Classify single reviews
- Process batch reviews
- See real-time results with confidence scores

### 📚 API Documentation
**http://localhost:8000/docs**

Interactive API documentation where you can:
- Test all endpoints
- See request/response schemas
- Try example requests

### 🏥 Health Check
**http://localhost:8000/health**

Verify the system is running and model is loaded.

## Step 3: Test the API 🧪

### Option A: Use the Web Interface
1. Go to http://localhost:8000
2. Enter a review like "Great service, thank you!"
3. Click "Classify Review"
4. See the result with label and confidence score

### Option B: Use the Test Script
```bash
python test_api.py
```

This runs automated tests to verify all functionality.

### Option C: Use curl
```bash
# Single classification
curl -X POST "http://localhost:8000/classify" \
  -H "Content-Type: application/json" \
  -d '{"text": "Great service, thank you!"}'

# Batch classification
curl -X POST "http://localhost:8000/classify/batch" \
  -H "Content-Type: application/json" \
  -d '{"reviews": ["Great service!", "My device is broken", "I want a refund"]}'
```

## 🎯 Example Classifications

Try these sample reviews:

| Review | Expected Label |
|--------|---------------|
| "Great service, thank you!" | Praise |
| "My device won't turn on" | Technical Support |
| "I want my money back immediately" | Refund Issue |
| "How do I cancel my subscription?" | Cancellation |
| "The product is broken" | Product Issue |
| "What are your business hours?" | General Inquiry |

## 🛑 Stopping the Application

Press `Ctrl+C` in the terminal, then run:

```bash
docker-compose down
```

## 🔄 Restarting

To start again (without rebuilding):

```bash
docker-compose up
```

## 📊 Monitoring

View logs in real-time:

```bash
docker-compose logs -f
```

Check container status:

```bash
docker-compose ps
```

## ⚠️ Troubleshooting

### Port 8000 already in use?
Edit `docker-compose.yml` and change:
```yaml
ports:
  - "8080:8000"  # Use port 8080 instead
```

Then access at http://localhost:8080

### Model not loading?
- Ensure `student_distilbert.pth` exists in the project directory
- Check logs: `docker-compose logs`
- Verify file is not corrupted

### Container won't start?
- Ensure Docker has at least 4GB RAM allocated
- Check Docker Desktop settings
- Try: `docker-compose down` then `docker-compose up --build`

## 🎉 Success!

If you see the web interface and can classify reviews, you're all set!

For more details, see [README.md](README.md)

---

**Need help?** Check the logs with `docker-compose logs` or refer to the full README.