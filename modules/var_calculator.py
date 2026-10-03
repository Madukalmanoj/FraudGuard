"""
Value at Risk (VaR) Calculator Module.
"""
import pandas as pd
import numpy as np
from scipy.stats import norm
import logging
from typing import Dict, List, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VaRCalculator:
    """Class to calculate Value at Risk for transactions."""
    
    def __init__(self, confidence_levels: List[float] = [0.95, 0.99]):
        self.confidence_levels = confidence_levels

    def calculate_historical_var(self, amounts: pd.Series, confidence: float = 0.95) -> float:
        """Calculate historical VaR."""
        try:
            return np.percentile(amounts, confidence * 100)
        except Exception as e:
            logger.error(f"Error calculating historical VaR: {str(e)}")
            raise

    def calculate_parametric_var(self, amounts: pd.Series, confidence: float = 0.95) -> float:
        """Calculate parametric VaR assuming normal distribution."""
        try:
            mean = amounts.mean()
            std = amounts.std()
            z_score = norm.ppf(confidence)
            return mean + z_score * std
        except Exception as e:
            logger.error(f"Error calculating parametric VaR: {str(e)}")
            raise

    def compute_risk_score(self, amount: float, var_95: float, var_99: float, mean: float, std: float) -> float:
        """Score 0-1 based on how extreme the amount is relative to VaR thresholds."""
        try:
            if amount >= var_99:
                return 1.0
            elif amount >= var_95:
                return 0.75 + 0.25 * ((amount - var_95) / (var_99 - var_95 + 1e-9))
            elif amount >= mean:
                return 0.5 * ((amount - mean) / (var_95 - mean + 1e-9))
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Error computing risk score: {str(e)}")
            raise

    def add_var_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add VaR and risk score features to the dataframe."""
        try:
            amounts = df['Amount']
            var_95 = self.calculate_historical_var(amounts, 0.95)
            var_99 = self.calculate_historical_var(amounts, 0.99)
            mean = amounts.mean()
            std = amounts.std()
            
            df_out = df.copy()
            df_out['var_95'] = var_95
            df_out['var_99'] = var_99
            
            df_out['var_risk_score'] = df_out['Amount'].apply(
                lambda x: self.compute_risk_score(x, var_95, var_99, mean, std)
            )
            return df_out
        except Exception as e:
            logger.error(f"Error adding VaR features: {str(e)}")
            raise

    def get_var_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Return VaR values, mean, std, and risk distribution."""
        try:
            amounts = df['Amount']
            var_95 = self.calculate_historical_var(amounts, 0.95)
            var_99 = self.calculate_historical_var(amounts, 0.99)
            
            if 'var_risk_score' not in df.columns:
                df = self.add_var_features(df)
                
            risk_dist = pd.cut(df['var_risk_score'], bins=[-0.1, 0.3, 0.7, 1.0], labels=['Low', 'Medium', 'High']).value_counts().to_dict()
            
            return {
                'var_95': var_95,
                'var_99': var_99,
                'mean': amounts.mean(),
                'std': amounts.std(),
                'risk_distribution': risk_dist
            }
        except Exception as e:
            logger.error(f"Error getting VaR summary: {str(e)}")
            raise

if __name__ == '__main__':
    # Standalone testing
    var_calc = VaRCalculator()
    df = pd.DataFrame({'Amount': np.random.lognormal(mean=2, sigma=1, size=1000)})
    try:
        df_var = var_calc.add_var_features(df)
        print(var_calc.get_var_summary(df_var))
    except Exception as e:
        print(f"Error during test: {e}")
