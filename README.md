﻿# AI Log Classifier

This project is a machine learning-based log classifier that reads logs from AWS S3, classifies them into `error`, `warning`, or `info`, and sends email alerts if any error-class log lines are detected. It uses a supervised learning approach with a TF-IDF vectorizer and logistic regression classifier. The model is trained and tracked using MLflow.

![alt text](image-1.png)
## Project Overview

- Classifies log lines pulled from S3 buckets
- Triggers email alerts for high-severity logs
- Trains on labeled logs stored in structured S3 folders
- Supports experiment tracking with MLflow
- Uses modular components for training, classification, and alerting

## Model and Training Design

### Vectorizer: TfidfVectorizer
- Converts sparse log text into numerical features
- Keeps frequent keywords, penalizes common noise
- Suitable for log data with repetition and structure

### Classifier: LogisticRegression
- Fast, interpretable, and effective for small- to medium-scale text classification
- Works well with TF-IDF features
- Provides strong precision and recall without requiring complex tuning

### Why not deep learning?
- Log lines are typically short and structured
- A shallow model generalizes well and is easy to retrain
- Lower latency, smaller model size, and simpler deployment

## Training Workflow (train.py)

1. Load labeled log files from S3 using folder structure:
logs/
├── error/
├── warning/
└── info/

2. Extract labels from folder names (`error`, `warning`, `info`)
3. Vectorize the log text using TF-IDF
4. Train logistic regression on the vectorized text
5. Split training and test sets (default: 70/30)
6. Evaluate model using precision, recall, and F1-score
7. Save model (`log_classifier.pkl`) and vectorizer (`vectorizer.pkl`)
8. Log the experiment and metrics to MLflow

## Classification Workflow (main.py)

- Load saved model and vectorizer from disk
- Read live or batch logs from S3
- Predict class for each log line
- Compare predicted class to the configured alerting class list
- If matched, send email notification with log sample

## Configuration

Example `config.yaml`:

## MLflow Visualization
We track each training run with MLflow to compare model performance and hyperparameters.

![alt text](image.png)

## How to use :
1. Train the Model
- python scripts/train.py
2. Run the Classifier
- python scripts/main.py

# This will:
- Pull the latest logs from S3
- Classify each line
- Send alerts if any line matches configured error classes

