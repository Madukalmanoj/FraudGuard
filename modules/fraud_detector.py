"""
Fraud Detector Module using ML and VaR.
"""
import pandas as pd
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FraudDetector:
    """Class to combine ML predictions with VaR risk scores for fraud detection."""
    
    def __init__(self, model, var_calculator, fraud_threshold: float = 0.5, var_threshold: float = 0.7):
        self.model = model
        self.var_calculator = var_calculator
        self.fraud_threshold = fraud_threshold
        self.var_threshold = var_threshold

    def predict_single(self, transaction_features: Dict[str, Any]) -> Dict[str, Any]:
        """Predict fraud for a single transaction."""
        try:
            df = pd.DataFrame([transaction_features])
            features_for_model = df.drop(columns=['transaction_id'], errors='ignore')
            
            prob = self.model.predict_proba(features_for_model)[0][1] if hasattr(self.model, 'predict_proba') else float(self.model.predict(features_for_model)[0])
            ml_pred = 1 if prob >= self.fraud_threshold else 0
            
            var_score = transaction_features.get('var_risk_score', 0.0)
            
            risk_level = self.classify_risk(ml_pred, prob, var_score)
            
            return {
                'prediction': ml_pred,
                'fraud_probability': prob,
                'var_risk_score': var_score,
                'risk_level': risk_level
            }
        except Exception as e:
            logger.error(f"Error predicting single transaction: {str(e)}")
            raise

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Predict fraud for a batch of transactions and add columns to df."""
        try:
            df_out = df.copy()
            features_for_model = df_out.drop(columns=['transaction_id', 'var_95', 'var_99', 'var_risk_score', 'Class'], errors='ignore')
            
            probs = self.model.predict_proba(features_for_model)[:, 1] if hasattr(self.model, 'predict_proba') else self.model.predict(features_for_model)
            df_out['fraud_probability'] = probs
            df_out['ml_prediction'] = (probs >= self.fraud_threshold).astype(int)
            
            if 'var_risk_score' not in df_out.columns:
                df_out = self.var_calculator.add_var_features(df_out)
                
            df_out['risk_level'] = df_out.apply(
                lambda row: self.classify_risk(row['ml_prediction'], row['fraud_probability'], row['var_risk_score']), axis=1
            )
            
            return df_out
        except Exception as e:
            logger.error(f"Error predicting batch: {str(e)}")
            raise

    def classify_risk(self, ml_prediction: int, fraud_probability: float, var_risk_score: float) -> str:
        """Classify risk into HIGH, MEDIUM, LOW based on combined ML and personal VaR."""
        try:
            ml_flag = ml_prediction == 1
            var_critical = var_risk_score >= 0.85
            var_medium = var_risk_score >= self.var_threshold
            
            if (ml_flag and var_medium) or var_critical or (ml_flag and fraud_probability >= 0.75):
                return 'HIGH'
            elif ml_flag or var_medium:
                return 'MEDIUM'
            else:
                return 'LOW'
        except Exception as e:
            logger.error(f"Error classifying risk: {str(e)}")
            raise

    def generate_alert(self, transaction_id: str, risk_level: str, fraud_probability: float) -> Dict[str, Any]:
        """Create alert data for high/medium risk."""
        try:
            if risk_level in ['HIGH', 'MEDIUM']:
                return {
                    'transaction_id': transaction_id,
                    'risk_level': risk_level,
                    'fraud_probability': fraud_probability,
                    'alert_message': f"Alert: Transaction {transaction_id} flagged as {risk_level} risk."
                }
            return {}
        except Exception as e:
            logger.error(f"Error generating alert: {str(e)}")
            raise

if __name__ == '__main__':
    # Standalone testing
    class MockModel:
        def predict_proba(self, X):
            import numpy as np
            return np.array([[0.1, 0.9]] * len(X))
    class MockVarCalc:
        def add_var_features(self, df):
            df['var_risk_score'] = 0.8
            return df
            
    detector = FraudDetector(MockModel(), MockVarCalc())
    df = pd.DataFrame({'Amount': [1000], 'f1': [1.0]})
    try:
        res = detector.predict_batch(df)
        print(res)
    except Exception as e:
        print(f"Error during test: {e}")
