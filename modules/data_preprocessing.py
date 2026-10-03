"""
Data Preprocessing Module for Financial Fraud Detection.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataPreprocessor:
    """Class for preprocessing transaction data."""
    
    def __init__(self):
        pass

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Fill or drop null values."""
        try:
            return df.dropna()
        except Exception as e:
            logger.error(f"Error handling missing values: {str(e)}")
            raise

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows."""
        try:
            return df.drop_duplicates()
        except Exception as e:
            logger.error(f"Error removing duplicates: {str(e)}")
            raise

    def scale_features(self, df: pd.DataFrame, columns=['Amount', 'Time']) -> Tuple[pd.DataFrame, StandardScaler]:
        """Scale specified features using StandardScaler."""
        try:
            scaler = StandardScaler()
            df_scaled = df.copy()
            existing_cols = [col for col in columns if col in df_scaled.columns]
            if existing_cols:
                df_scaled[existing_cols] = scaler.fit_transform(df_scaled[existing_cols])
            return df_scaled, scaler
        except Exception as e:
            logger.error(f"Error scaling features: {str(e)}")
            raise

    def split_data(self, df: pd.DataFrame, target='Class', test_size=0.2, random_state=42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        """Stratified split of data into train and test sets."""
        try:
            X = df.drop(columns=[target])
            y = df[target]
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            return X_train, X_test, y_train, y_test
        except Exception as e:
            logger.error(f"Error splitting data: {str(e)}")
            raise

    def apply_smote(self, X_train: pd.DataFrame, y_train: pd.Series) -> Tuple[pd.DataFrame, pd.Series]:
        """Apply SMOTE to handle class imbalance."""
        try:
            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
            return X_resampled, y_resampled
        except Exception as e:
            logger.error(f"Error applying SMOTE: {str(e)}")
            raise

    def preprocess_pipeline(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Run all preprocessing steps in sequence."""
        try:
            df = self.handle_missing_values(df)
            df = self.remove_duplicates(df)
            
            df_scaled, scaler = self.scale_features(df)
            
            if 'transaction_id' in df_scaled.columns:
                df_scaled = df_scaled.drop(columns=['transaction_id'])
                
            X_train, X_test, y_train, y_test = self.split_data(df_scaled)
            X_train_resampled, y_train_resampled = self.apply_smote(X_train, y_train)
            
            return {
                'X_train': X_train_resampled,
                'X_test': X_test,
                'y_train': y_train_resampled,
                'y_test': y_test,
                'scaler': scaler
            }
        except Exception as e:
            logger.error(f"Error in preprocess pipeline: {str(e)}")
            raise

if __name__ == '__main__':
    # Standalone testing
    preprocessor = DataPreprocessor()
    df = pd.DataFrame({
        'Time': [0, 1, 2, 3],
        'Amount': [100, 200, 300, 400],
        'Class': [0, 0, 0, 1],
        'V1': [1, 2, 3, 4]
    })
    try:
        results = preprocessor.preprocess_pipeline(df)
        print("Preprocessing successful.")
        print("X_train shape:", results['X_train'].shape)
    except Exception as e:
        print(f"Error during test: {e}")
