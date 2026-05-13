from pydantic import BaseModel, Field, validator
from typing import List, Optional


class ClassificationRequest(BaseModel):
    """Request model for single review classification"""
    text: str = Field(..., min_length=1, max_length=512, description="Review text to classify")
    
    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()


class BatchClassificationRequest(BaseModel):
    """Request model for batch review classification"""
    reviews: List[str] = Field(..., min_items=1, max_items=100, description="List of review texts")
    
    @validator('reviews')
    def validate_reviews(cls, v):
        if not v:
            raise ValueError('Reviews list cannot be empty')
        # Strip whitespace and filter out empty strings
        cleaned = [text.strip() for text in v if text.strip()]
        if not cleaned:
            raise ValueError('All reviews are empty after stripping whitespace')
        if len(cleaned) > 100:
            raise ValueError('Maximum 100 reviews allowed per batch')
        return cleaned


class ClassificationResult(BaseModel):
    """Response model for classification result"""
    text: str = Field(..., description="Original review text")
    label: str = Field(..., description="Predicted label name")
    label_id: int = Field(..., ge=0, le=5, description="Predicted label ID (0-5)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Prediction confidence score")


class BatchClassificationResult(BaseModel):
    """Response model for batch classification"""
    results: List[ClassificationResult] = Field(..., description="List of classification results")
    total_processed: int = Field(..., description="Total number of reviews processed")


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether the model is loaded")
    version: str = Field(..., description="API version")


class LabelsResponse(BaseModel):
    """Response model for label mappings"""
    labels: dict = Field(..., description="Label ID to name mapping")

# Made with Bob
