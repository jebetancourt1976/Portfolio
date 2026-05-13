// API Base URL
const API_BASE = window.location.origin;

// DOM Elements
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const singleForm = document.getElementById('singleForm');
const singleReview = document.getElementById('singleReview');
const charCount = document.getElementById('charCount');
const classifyBtn = document.getElementById('classifyBtn');
const singleResult = document.getElementById('singleResult');
const batchForm = document.getElementById('batchForm');
const batchReviews = document.getElementById('batchReviews');
const reviewCount = document.getElementById('reviewCount');
const batchBtn = document.getElementById('batchBtn');
const batchResult = document.getElementById('batchResult');

// Check system health on load
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();
        
        if (data.model_loaded) {
            statusIndicator.className = 'status-indicator healthy';
            statusText.textContent = 'System ready • Model loaded successfully';
        } else {
            statusIndicator.className = 'status-indicator unhealthy';
            statusText.textContent = 'System unavailable • Model not loaded';
        }
    } catch (error) {
        statusIndicator.className = 'status-indicator unhealthy';
        statusText.textContent = 'System error • Cannot connect to API';
        console.error('Health check failed:', error);
    }
}

// Update character count
singleReview.addEventListener('input', () => {
    const length = singleReview.value.length;
    charCount.textContent = `${length} / 512 characters`;
    
    if (length > 450) {
        charCount.style.color = '#f59e0b';
    } else {
        charCount.style.color = '#64748b';
    }
});

// Update review count
batchReviews.addEventListener('input', () => {
    const reviews = batchReviews.value.split('\n').filter(line => line.trim());
    const count = reviews.length;
    reviewCount.textContent = `${count} review${count !== 1 ? 's' : ''}`;
    
    if (count > 100) {
        reviewCount.style.color = '#ef4444';
        reviewCount.textContent += ' (max 100)';
    } else {
        reviewCount.style.color = '#64748b';
    }
});

// Show loading state
function setLoading(button, isLoading) {
    const btnText = button.querySelector('.btn-text');
    const spinner = button.querySelector('.spinner');
    
    if (isLoading) {
        button.disabled = true;
        btnText.style.display = 'none';
        spinner.style.display = 'block';
    } else {
        button.disabled = false;
        btnText.style.display = 'block';
        spinner.style.display = 'none';
    }
}

// Show error message
function showError(container, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = `Error: ${message}`;
    container.appendChild(errorDiv);
    
    setTimeout(() => errorDiv.remove(), 5000);
}

// Get label class
function getLabelClass(labelId) {
    return `label-${labelId}`;
}

// Format confidence
function formatConfidence(confidence) {
    return `${(confidence * 100).toFixed(2)}%`;
}

// Handle single review classification
singleForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const text = singleReview.value.trim();
    if (!text) return;
    
    setLoading(classifyBtn, true);
    singleResult.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/classify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Classification failed');
        }
        
        const data = await response.json();
        
        // Display result
        document.getElementById('resultText').textContent = `"${data.text}"`;
        
        const labelBadge = document.getElementById('resultLabel');
        labelBadge.textContent = data.label;
        labelBadge.className = `label-badge ${getLabelClass(data.label_id)}`;
        
        document.getElementById('resultConfidence').textContent = 
            `Confidence: ${formatConfidence(data.confidence)}`;
        
        singleResult.style.display = 'block';
        
    } catch (error) {
        showError(singleForm, error.message);
        console.error('Classification error:', error);
    } finally {
        setLoading(classifyBtn, false);
    }
});

// Handle batch classification
batchForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const reviews = batchReviews.value
        .split('\n')
        .map(line => line.trim())
        .filter(line => line);
    
    if (reviews.length === 0) return;
    
    if (reviews.length > 100) {
        showError(batchForm, 'Maximum 100 reviews allowed per batch');
        return;
    }
    
    setLoading(batchBtn, true);
    batchResult.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/classify/batch`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ reviews })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Batch classification failed');
        }
        
        const data = await response.json();
        
        // Display results in table
        document.getElementById('totalProcessed').textContent = data.total_processed;
        
        const tbody = document.getElementById('resultsTableBody');
        tbody.innerHTML = '';
        
        data.results.forEach((result, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${escapeHtml(result.text)}</td>
                <td>
                    <span class="label-badge ${getLabelClass(result.label_id)}">
                        ${result.label}
                    </span>
                </td>
                <td>${formatConfidence(result.confidence)}</td>
            `;
            tbody.appendChild(row);
        });
        
        batchResult.style.display = 'block';
        
        // Scroll to results
        batchResult.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        
    } catch (error) {
        showError(batchForm, error.message);
        console.error('Batch classification error:', error);
    } finally {
        setLoading(batchBtn, false);
    }
});

// Utility function to escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
checkHealth();

// Refresh health status every 30 seconds
setInterval(checkHealth, 30000);

// Made with Bob
