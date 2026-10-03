"""
Data Collection Module for Financial Fraud Detection.
"""
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCollector:
    """Class for collecting and validating transaction data."""
    
    def __init__(self):
        pass

    def load_data(self, filepath: str) -> pd.DataFrame:
        """
        Load CSV data and validate columns.
        
        Args:
            filepath: Path to the CSV file.
            
        Returns:
            pd.DataFrame: Loaded dataframe.
        """
        try:
            logger.info(f"Loading data from {filepath}")
            df = pd.read_csv(filepath)
            expected_columns = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount', 'Class']
            missing_cols = [col for col in expected_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Missing expected columns: {missing_cols}")
            logger.info("Data loaded and validated successfully.")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise

    def get_data_profile(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Return shape, null counts, class distribution, and basic stats.
        
        Args:
            df: Input dataframe.
            
        Returns:
            Dict containing data profile.
        """
        try:
            profile = {
                'shape': df.shape,
                'null_counts': df.isnull().sum().to_dict(),
                'class_distribution': df['Class'].value_counts().to_dict() if 'Class' in df.columns else {},
                'basic_stats': df.describe().to_dict()
            }
            return profile
        except Exception as e:
            logger.error(f"Error generating data profile: {str(e)}")
            raise

    def generate_transaction_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add a unique 'transaction_id' column to the dataframe.
        
        Args:
            df: Input dataframe.
            
        Returns:
            Dataframe with 'transaction_id'.
        """
        try:
            df = df.copy()
            df['transaction_id'] = [f'TXN_{i:06d}' for i in range(1, len(df) + 1)]
            return df
        except Exception as e:
            logger.error(f"Error generating transaction IDs: {str(e)}")
            raise

if __name__ == '__main__':
    # Standalone testing
    collector = DataCollector()
    dummy_data = pd.DataFrame({
        'Time': [0.0, 1.0],
        'Amount': [100.0, 50.0],
        'Class': [0, 1]
    })
    for i in range(1, 29):
        dummy_data[f'V{i}'] = [0.0, 0.0]
    
    try:
        dummy_data.to_csv('dummy.csv', index=False)
        df = collector.load_data('dummy.csv')
        print(collector.get_data_profile(df))
        df_with_ids = collector.generate_transaction_ids(df)
        print(df_with_ids.head())
    except Exception as e:
        print(f"Error during test: {e}")
