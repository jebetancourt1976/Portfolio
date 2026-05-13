import torch
import torch.nn as nn
from transformers import DistilBertTokenizer, DistilBertModel
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

# Label mapping
LABELS_MAP = {
    0: "General Inquiry",
    1: "Product Issue",
    2: "Refund Issue",
    3: "Cancellation",
    4: "Praise",
    5: "Technical Support",
}


class DistilBertClassifier(nn.Module):
    """DistilBERT-based text classifier with pre_classifier layer"""
    
    def __init__(self, num_classes: int = 6, dropout: float = 0.3):
        super(DistilBertClassifier, self).__init__()
        self.distilbert = DistilBertModel.from_pretrained('distilbert-base-uncased')
        
        # Pre-classifier layer (matches training architecture)
        self.pre_classifier = nn.Linear(self.distilbert.config.hidden_size,
                                       self.distilbert.config.hidden_size)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        
        # Final classifier layer
        self.classifier = nn.Linear(self.distilbert.config.hidden_size, num_classes)
    
    def forward(self, input_ids, attention_mask):
        # Get DistilBERT outputs
        outputs = self.distilbert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state[:, 0]  # Use [CLS] token
        
        # Pass through pre_classifier → ReLU → dropout → classifier
        pooled_output = self.pre_classifier(pooled_output)
        pooled_output = self.relu(pooled_output)
        pooled_output = self.dropout(pooled_output)
        logits = self.classifier(pooled_output)
        
        return logits


class ReviewClassifier:
    """Service for loading model and performing inference"""
    
    def __init__(self, model_path: str = "student_distilbert.pth"):
        self.model_path = model_path
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.labels_map = LABELS_MAP
        self._load_model()
    
    def _load_model(self):
        """Load the trained model and tokenizer"""
        try:
            logger.info(f"Loading model from {self.model_path}")
            
            # Initialize tokenizer
            self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
            
            # Initialize model architecture
            self.model = DistilBertClassifier(num_classes=len(self.labels_map))
            
            # Load state dictionary
            state_dict = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            
            # Move model to device and set to evaluation mode
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def preprocess_text(self, text: str, max_length: int = 128) -> dict:
        """Tokenize and preprocess text for model input"""
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        return {
            'input_ids': encoding['input_ids'].to(self.device),
            'attention_mask': encoding['attention_mask'].to(self.device)
        }
    
    def predict(self, text: str) -> Tuple[int, str, float]:
        """
        Predict the label for a single review
        
        Returns:
            Tuple of (label_id, label_name, confidence)
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded")
        
        try:
            # Preprocess
            inputs = self.preprocess_text(text)
            
            # Inference
            with torch.no_grad():
                logits = self.model(
                    input_ids=inputs['input_ids'],
                    attention_mask=inputs['attention_mask']
                )
                
                # Get probabilities and prediction
                probabilities = torch.softmax(logits, dim=1)
                confidence, predicted_class = torch.max(probabilities, dim=1)
                
                label_id = predicted_class.item()
                label_name = self.labels_map[label_id]
                confidence_score = confidence.item()
            
            return label_id, label_name, confidence_score
            
        except Exception as e:
            logger.error(f"Error during prediction: {str(e)}")
            raise RuntimeError(f"Prediction failed: {str(e)}")
    
    def predict_batch(self, texts: List[str]) -> List[Tuple[int, str, float]]:
        """
        Predict labels for multiple reviews
        
        Returns:
            List of tuples (label_id, label_name, confidence)
        """
        if not self.model or not self.tokenizer:
            raise RuntimeError("Model not loaded")
        
        try:
            results = []
            
            # Process in batches for efficiency
            batch_size = 16
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                # Tokenize batch
                encodings = self.tokenizer(
                    batch_texts,
                    add_special_tokens=True,
                    max_length=128,
                    padding='max_length',
                    truncation=True,
                    return_attention_mask=True,
                    return_tensors='pt'
                )
                
                input_ids = encodings['input_ids'].to(self.device)
                attention_mask = encodings['attention_mask'].to(self.device)
                
                # Inference
                with torch.no_grad():
                    logits = self.model(input_ids=input_ids, attention_mask=attention_mask)
                    probabilities = torch.softmax(logits, dim=1)
                    confidences, predicted_classes = torch.max(probabilities, dim=1)
                
                # Collect results
                for pred_class, conf in zip(predicted_classes, confidences):
                    label_id = pred_class.item()
                    label_name = self.labels_map[label_id]
                    confidence_score = conf.item()
                    results.append((label_id, label_name, confidence_score))
            
            return results
            
        except Exception as e:
            logger.error(f"Error during batch prediction: {str(e)}")
            raise RuntimeError(f"Batch prediction failed: {str(e)}")
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.model is not None and self.tokenizer is not None
    
    def get_labels_map(self) -> dict:
        """Get the label mapping dictionary"""
        return self.labels_map

# Made with Bob
