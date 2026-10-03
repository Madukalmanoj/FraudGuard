"""
Train all ML models and save the best one.
Run this script once to train and persist models for the Flask app.
"""
import os
import sys
import joblib
import numpy as np
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from modules.data_collection import DataCollector
from modules.data_preprocessing import DataPreprocessor
from modules.var_calculator import VaRCalculator
from modules.ml_models import ModelTrainer
from modules.fraud_detector import FraudDetector
from modules.alerts import AlertManager
from database.db_manager import DBManager
from setup_db import setup_database

def train():
    print("=" * 60)
    print("  Financial Fraud Detection — Model Training Pipeline")
    print("=" * 60)

    # Step 0: Setup DB
    setup_database()

    # Step 1: Load data
    print("\n[1/7] Loading dataset...")
    collector = DataCollector()
    df = collector.load_data(config.DATA_PATH)
    if df is None:
        print("ERROR: Dataset not found at", config.DATA_PATH)
        return
    df = collector.generate_transaction_ids(df)
    profile = collector.get_data_profile(df)
    print(f"  [OK] Loaded {profile['shape'][0]:,} transactions, {profile['shape'][1]} features")
    print(f"  [OK] Fraud: {profile['class_distribution'].get(1, 0)}, Legitimate: {profile['class_distribution'].get(0, 0)}")

    # Step 2: Compute VaR features
    print("\n[2/7] Computing Value at Risk scores...")
    var_calc = VaRCalculator()
    amounts = df['Amount']
    var_stats = {
        'var_95': var_calc.calculate_historical_var(amounts, 0.95),
        'var_99': var_calc.calculate_historical_var(amounts, 0.99),
        'mean': float(amounts.mean()),
        'std': float(amounts.std())
    }
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    joblib.dump(var_stats, os.path.join(config.MODEL_DIR, 'var_stats.joblib'))
    df = var_calc.add_var_features(df)
    print(f"  [OK] VaR-95: ${var_stats['var_95']:.2f}, VaR-99: ${var_stats['var_99']:.2f}")

    # Step 3: Preprocess
    print("\n[3/7] Preprocessing data...")
    preprocessor = DataPreprocessor()
    df_for_model = df.drop(columns=['transaction_id', 'var_95', 'var_99'], errors='ignore')
    df_scaled, scaler = preprocessor.scale_features(df_for_model, columns=['Amount', 'Time'])
    joblib.dump(scaler, os.path.join(config.MODEL_DIR, 'scaler.joblib'))

    X_train, X_test, y_train, y_test = preprocessor.split_data(df_scaled, target='Class')
    print(f"  [OK] Train: {len(X_train):,} samples, Test: {len(X_test):,} samples")

    # Subsample majority class for training to 40,000 samples, keeping 100% of fraud cases
    if len(X_train) > 50000:
        fraud_mask = (y_train == 1)
        legit_indices = y_train[~fraud_mask].sample(n=min(40000, sum(~fraud_mask)), random_state=42).index
        fraud_indices = y_train[fraud_mask].index
        selected_indices = legit_indices.union(fraud_indices)
        X_train_sub = X_train.loc[selected_indices]
        y_train_sub = y_train.loc[selected_indices]
        print(f"  [OK] Training subset: {len(X_train_sub):,} samples ({sum(fraud_mask)} fraud + {len(legit_indices)} legitimate)")
    else:
        X_train_sub, y_train_sub = X_train, y_train

    print("  [..] Applying SMOTE for class balancing...")
    X_train_res, y_train_res = preprocessor.apply_smote(X_train_sub, y_train_sub)
    print(f"  [OK] After SMOTE: {len(X_train_res):,} samples (balanced)")

    # Step 4: Train all 4 models
    print("\n[4/7] Training ML models...")
    trainer = ModelTrainer()
    results = trainer.train_all_models(X_train_res, y_train_res, X_test, y_test)

    print("\n  +---------------------+----------+-----------+--------+--------+---------+")
    print("  | Model               | Accuracy | Precision | Recall |   F1   | AUC-ROC |")
    print("  +---------------------+----------+-----------+--------+--------+---------+")
    for name, m in results.items():
        print(f"  | {name:<19} |  {m['accuracy']:.4f}  |   {m['precision']:.4f}  | {m['recall']:.4f} | {m['f1']:.4f} |  {m['auc_roc']:.4f} |")
    print("  +---------------------+----------+-----------+--------+--------+---------+")

    # Step 5: Save best model
    print("\n[5/7] Saving models...")
    best_name, best_model = trainer.get_best_model(results)
    trainer.save_model(best_model, 'best_model', config.MODEL_DIR)
    for name in trainer.models:
        trainer.save_model(trainer.models[name], name, config.MODEL_DIR)
    print(f"  [OK] Best model: {best_name} (F1={results[best_name]['f1']:.4f})")

    # Step 6: Generate plots
    print("\n[6/7] Generating plots...")
    try:
        save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images')
        os.makedirs(save_dir, exist_ok=True)
        trainer.plot_roc_curves(results, X_test, y_test, save_dir=save_dir)
        trainer.plot_confusion_matrices(results, save_dir=save_dir)
        print(f"  [OK] ROC curves saved to static/images/roc_curves.png")
        print(f"  [OK] Confusion matrices saved to static/images/confusion_matrices.png")
    except Exception as e:
        print(f"  [!!] Plot generation warning: {e}")

    # Step 7: Store results in database
    print("\n[7/7] Storing results in database...")
    with DBManager() as db:
        # Log model metrics
        for model_name, metrics in results.items():
            db.log_model_performance(model_name, {
                'accuracy': metrics['accuracy'],
                'precision_score': metrics['precision'],
                'recall': metrics['recall'],
                'f1_score': metrics['f1'],
                'auc_roc': metrics['auc_roc']
            })

        # Store sample predictions
        detector = FraudDetector(best_model, var_calc)
        sample_size = min(500, len(X_test))
        X_sample = X_test.iloc[:sample_size]

        if hasattr(best_model, 'predict_proba'):
            probs = best_model.predict_proba(X_sample)[:, 1]
        else:
            probs = best_model.predict(X_sample).astype(float)

        predictions = (probs >= config.FRAUD_THRESHOLD).astype(int)
        var_scores = df.loc[X_sample.index, 'var_risk_score'].values

        alert_count = 0
        for idx in range(sample_size):
            risk_level = detector.classify_risk(
                int(predictions[idx]), float(probs[idx]),
                float(var_scores[idx]) if idx < len(var_scores) else 0.0
            )
            tx_id = f"TXN_{uuid.uuid4().hex[:8].upper()}"
            scaled_amt = float(X_sample.iloc[idx].get('Amount', 0))
            amount_val = round(float(scaled_amt * scaler.scale_[0] + scaler.mean_[0]), 2)

            tx_record = {
                'transaction_id': tx_id,
                'amount': amount_val,
                'time_stamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'features': {},
                'var_risk_score': round(float(var_scores[idx]) if idx < len(var_scores) else 0.0, 4),
                'ml_prediction': int(predictions[idx]),
                'fraud_probability': round(float(probs[idx]), 4),
                'risk_level': risk_level
            }
            try:
                db.insert_transaction(tx_record)
            except Exception:
                pass

            if risk_level in ['HIGH', 'MEDIUM']:
                alert = AlertManager.generate_fraud_alert(tx_id, risk_level, float(probs[idx]), amount_val)
                db.insert_alert(tx_id, alert['alert_type'], alert['message'])
                alert_count += 1

        print(f"  [OK] {sample_size} test transactions stored in DB")
        print(f"  [OK] {alert_count} fraud alerts generated")

    print("\n" + "=" * 60)
    print(f"  [**] TRAINING COMPLETE!")
    print(f"  Best Model: {best_name}")
    print(f"  F1 Score: {results[best_name]['f1']:.4f}")
    print(f"  AUC-ROC: {results[best_name]['auc_roc']:.4f}")
    print(f"  Models saved to: {config.MODEL_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    train()
