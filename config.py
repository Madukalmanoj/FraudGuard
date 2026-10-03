"""
Configuration settings for the Financial Fraud Detection System.
"""
import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'fraud_detection.db')

# Data configuration
DATA_PATH = os.path.join(BASE_DIR, 'data', 'creditcard.csv')

# Model configuration
MODEL_DIR = os.path.join(BASE_DIR, 'models/')

# Value at Risk (VaR) parameters
VAR_CONFIDENCE_LEVELS = [0.95, 0.99]

# Thresholds
FRAUD_THRESHOLD = 0.5
VAR_THRESHOLD = 0.7

# Risk levels mapping
RISK_LEVELS = {
    'HIGH': (0.7, 1.0),
    'MEDIUM': (0.4, 0.7),
    'LOW': (0.0, 0.4)
}

# Flask Application configuration
SECRET_KEY = 'super-secret-key'
DEBUG = True
