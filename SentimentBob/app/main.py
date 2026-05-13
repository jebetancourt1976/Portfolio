from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path

from app.models import (
    ClassificationRequest,
    BatchClassificationRequest,
    ClassificationResult,
    BatchClassificationResult,
    HealthResponse,
    LabelsResponse
)
from app.classifier import ReviewClassifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Customer Review Classification API",
    description="API for classifying customer reviews using DistilBERT",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize classifier (singleton)
classifier = None


@app.on_event("startup")
async def startup_event():
    """Initialize the classifier on startup"""
    global classifier
    try:
        logger.info("Starting up application...")
        classifier = ReviewClassifier(model_path="student_distilbert.pth")
        logger.info("Classifier initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize classifier: {str(e)}")
        # Don't fail startup, but classifier will be None


@app.get("/", response_class=FileResponse)
async def read_root():
    """Serve the main HTML page"""
    static_path = Path("app/static/index.html")
    if static_path.exists():
        return FileResponse(static_path)
    return JSONResponse(
        status_code=404,
        content={"message": "Frontend not found. Please ensure index.html exists in app/static/"}
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    model_loaded = classifier is not None and classifier.is_loaded()
    return HealthResponse(
        status="healthy" if model_loaded else "unhealthy",
        model_loaded=model_loaded,
        version="1.0.0"
    )


@app.get("/labels", response_model=LabelsResponse)
async def get_labels():
    """Get label mappings"""
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Classifier not initialized"
        )
    return LabelsResponse(labels=classifier.get_labels_map())


@app.post("/classify", response_model=ClassificationResult)
async def classify_review(request: ClassificationRequest):
    """
    Classify a single customer review
    
    - **text**: The review text to classify (1-512 characters)
    
    Returns the predicted label, label ID, and confidence score
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Classifier not initialized. Please check server logs."
        )
    
    try:
        label_id, label_name, confidence = classifier.predict(request.text)
        
        return ClassificationResult(
            text=request.text,
            label=label_name,
            label_id=label_id,
            confidence=round(confidence, 4)
        )
    
    except Exception as e:
        logger.error(f"Classification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Classification failed: {str(e)}"
        )


@app.post("/classify/batch", response_model=BatchClassificationResult)
async def classify_reviews_batch(request: BatchClassificationRequest):
    """
    Classify multiple customer reviews in batch
    
    - **reviews**: List of review texts (1-100 reviews)
    
    Returns a list of classification results for each review
    """
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Classifier not initialized. Please check server logs."
        )
    
    try:
        # Get predictions for all reviews
        predictions = classifier.predict_batch(request.reviews)
        
        # Build results
        results = []
        for text, (label_id, label_name, confidence) in zip(request.reviews, predictions):
            results.append(
                ClassificationResult(
                    text=text,
                    label=label_name,
                    label_id=label_id,
                    confidence=round(confidence, 4)
                )
            )
        
        return BatchClassificationResult(
            results=results,
            total_processed=len(results)
        )
    
    except Exception as e:
        logger.error(f"Batch classification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch classification failed: {str(e)}"
        )


# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
