"""
Machine Learning Models Module for Fraud Detection.
"""
import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, classification_report, roc_curve, ConfusionMatrixDisplay
from xgboost import XGBClassifier
import logging
from typing import Dict, Any, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ModelTrainer:
    """Class to train and evaluate ML models."""
    
    def __init__(self):
        self.models = {
            'RandomForest': RandomForestClassifier(n_estimators=50, max_depth=12, n_jobs=-1, random_state=42),
            'XGBoost': XGBClassifier(n_estimators=50, max_depth=6, n_jobs=-1, eval_metric='logloss', random_state=42),
            'DecisionTree': DecisionTreeClassifier(max_depth=10, random_state=42),
            'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42)
        }

    def train_model(self, model_name: str, X_train: pd.DataFrame, y_train: pd.Series):
        """Train a specific model by name."""
        try:
            if model_name not in self.models:
                raise ValueError(f"Model {model_name} not found.")
            model = self.models[model_name]
            logger.info(f"Training {model_name}...")
            model.fit(X_train, y_train)
            return model
        except Exception as e:
            logger.error(f"Error training model {model_name}: {str(e)}")
            raise

    def evaluate_model(self, model, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """Evaluate a trained model."""
        try:
            y_pred = model.predict(X_test)
            y_prob = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
            
            results = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1': f1_score(y_test, y_pred, zero_division=0),
                'auc_roc': roc_auc_score(y_test, y_prob),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
                'classification_report': classification_report(y_test, y_pred, output_dict=True, zero_division=0),
                'y_prob': y_prob.tolist() # Stored for ROC plotting
            }
            return results
        except Exception as e:
            logger.error(f"Error evaluating model: {str(e)}")
            raise

    def train_all_models(self, X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
        """Train and evaluate all models."""
        try:
            results = {}
            for name in self.models.keys():
                model = self.train_model(name, X_train, y_train)
                self.models[name] = model # Save trained model
                eval_res = self.evaluate_model(model, X_test, y_test)
                results[name] = eval_res
            return results
        except Exception as e:
            logger.error(f"Error training all models: {str(e)}")
            raise

    def get_best_model(self, results: Dict[str, Any]) -> Tuple[str, Any]:
        """Get the best model based on F1 score."""
        try:
            best_model_name = max(results.keys(), key=lambda k: results[k]['f1'])
            return best_model_name, self.models[best_model_name]
        except Exception as e:
            logger.error(f"Error getting best model: {str(e)}")
            raise

    def save_model(self, model, model_name: str, path: str = 'models/') -> str:
        """Save a model using joblib."""
        try:
            os.makedirs(path, exist_ok=True)
            filepath = os.path.join(path, f"{model_name}.joblib")
            joblib.dump(model, filepath)
            logger.info(f"Model saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving model: {str(e)}")
            raise

    def load_model(self, path: str):
        """Load a model using joblib."""
        try:
            model = joblib.load(path)
            logger.info(f"Model loaded from {path}")
            return model
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def get_feature_importance(self, model, feature_names: list) -> pd.DataFrame:
        """Get feature importance for tree-based models."""
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
                return df.sort_values(by='Importance', ascending=False)
            else:
                raise ValueError("Model does not have feature_importances_ attribute.")
        except Exception as e:
            logger.error(f"Error getting feature importance: {str(e)}")
            raise

    def plot_roc_curves(self, results: Dict[str, Any], X_test: pd.DataFrame, y_test: pd.Series, save_dir='static/images/'):
        """Plot and save ROC curves."""
        try:
            os.makedirs(save_dir, exist_ok=True)
            plt.figure(figsize=(10, 8))
            for name, metrics in results.items():
                if 'y_prob' in metrics:
                    fpr, tpr, _ = roc_curve(y_test, metrics['y_prob'])
                    plt.plot(fpr, tpr, label=f"{name} (AUC = {metrics['auc_roc']:.2f})")
            plt.plot([0, 1], [0, 1], 'k--')
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('ROC Curves')
            plt.legend(loc='lower right')
            save_path = os.path.join(save_dir, 'roc_curves.png')
            plt.savefig(save_path)
            plt.close()
            logger.info(f"ROC curves saved to {save_path}")
        except Exception as e:
            logger.error(f"Error plotting ROC curves: {str(e)}")
            raise

    def plot_confusion_matrices(self, results: Dict[str, Any], save_dir='static/images/'):
        """Plot and save confusion matrices."""
        try:
            os.makedirs(save_dir, exist_ok=True)
            num_models = len(results)
            fig, axes = plt.subplots(1, num_models, figsize=(5 * num_models, 5))
            if num_models == 1:
                axes = [axes]
            
            for ax, (name, metrics) in zip(axes, results.items()):
                cm = np.array(metrics['confusion_matrix'])
                disp = ConfusionMatrixDisplay(confusion_matrix=cm)
                disp.plot(ax=ax, cmap='Blues', colorbar=False)
                ax.set_title(f'{name} Confusion Matrix')
            
            plt.tight_layout()
            save_path = os.path.join(save_dir, 'confusion_matrices.png')
            plt.savefig(save_path)
            plt.close()
            logger.info(f"Confusion matrices saved to {save_path}")
        except Exception as e:
            logger.error(f"Error plotting confusion matrices: {str(e)}")
            raise

if __name__ == '__main__':
    # Standalone testing
    trainer = ModelTrainer()
    X = pd.DataFrame(np.random.rand(100, 5), columns=[f'f{i}' for i in range(5)])
    y = pd.Series(np.random.randint(0, 2, 100))
    try:
        results = trainer.train_all_models(X[:80], y[:80], X[80:], y[80:])
        print(f"Best model: {trainer.get_best_model(results)[0]}")
    except Exception as e:
        print(f"Error during test: {e}")
