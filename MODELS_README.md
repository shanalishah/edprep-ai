# ML Models Setup Guide

## Overview
The ML models for the IELTS Master Platform are not included in this repository due to GitHub's file size limitations (some models exceed 100MB). This guide explains how to set up the models for local development and deployment.

## Model Files Required

The following model files are needed for the application to function properly:

### Core Models
- `backend/models/Production_Elastic_Net_model.pkl` (~50MB)
- `backend/models/Production_Gradient_Boosting_model.pkl` (~50MB)
- `backend/models/Production_Random_Forest_model.pkl` (~150MB)
- `backend/models/production_scaler.pkl`
- `backend/models/production_tfidf_vectorizer.pkl`

### Strict Models (for advanced scoring)
- `backend/models/strict_best_models.pkl`
- `backend/models/strict_feature_columns.pkl`
- `backend/models/strict_tfidf_vectorizer.pkl`

### Individual Criteria Models
Each criteria folder should contain:
- `elastic_net_model.pkl`
- `elastic_net_scaler.pkl`
- `extra_trees_model.pkl`
- `gradient_boosting_model.pkl`
- `random_forest_model.pkl`
- `ridge_model.pkl`
- `ridge_scaler.pkl`

**Criteria folders:**
- `backend/models/strict_coherence_cohesion/`
- `backend/models/strict_grammatical_range/`
- `backend/models/strict_lexical_resource/`
- `backend/models/strict_overall_band_score/`
- `backend/models/strict_task_achievement/`

## Setup Instructions

### Option 1: Download from Original Source
If you have access to the original model files, copy them to the appropriate directories in `backend/models/`.

### Option 2: Train New Models
If you need to train new models:

1. **Prepare Training Data**: Ensure you have the IELTS essay dataset
2. **Run Training Scripts**: Use the existing training infrastructure
3. **Place Models**: Save trained models in the correct directories

### Option 3: Use Fallback Mode
The application can run in fallback mode without ML models:
- Set `USE_ML_MODELS=false` in your `.env` file
- The system will use rule-based scoring instead

## Environment Configuration

Update your `.env` file:

```env
# ML Models Configuration
MODELS_DIR="/path/to/your/models"
USE_ML_MODELS=true
FALLBACK_TO_RULE_BASED=true
```

## Verification

To verify models are working:

1. Start the application: `./start.sh`
2. Check the health endpoint: `http://localhost:8000/health`
3. Submit a test essay to verify scoring works

## File Structure

```
backend/models/
├── Production_*.pkl          # Core production models
├── production_*.pkl          # Preprocessing models
├── strict_*.pkl             # Strict model components
└── strict_*/                # Individual criteria models
    ├── elastic_net_model.pkl
    ├── extra_trees_model.pkl
    ├── gradient_boosting_model.pkl
    ├── random_forest_model.pkl
    ├── ridge_model.pkl
    └── *_scaler.pkl
```

## Troubleshooting

### Models Not Found
- Check `MODELS_DIR` path in `.env`
- Verify file permissions
- Ensure all required models are present

### Large File Warnings
- Some models are large (>50MB) but within GitHub's limits
- Consider using Git LFS for very large models
- Use cloud storage for production deployments

### Performance Issues
- Models are loaded on startup
- Consider model caching for production
- Monitor memory usage with large models

## Security Notes

- Never commit actual model files to version control
- Use secure storage for production model files
- Implement proper access controls for model downloads
- Consider model encryption for sensitive deployments

