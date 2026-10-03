"""
Flask Web Application for Financial Fraud Detection System.
Integrates all modules: Data Collection, Preprocessing, VaR, ML Models, Fraud Detection.
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import pandas as pd
import numpy as np
import os
import sys
import json
import uuid
import joblib
from datetime import datetime

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from database.db_manager import DBManager
from modules.alerts import AlertManager
from modules.data_collection import DataCollector
from modules.data_preprocessing import DataPreprocessor
from modules.var_calculator import VaRCalculator
from modules.ml_models import ModelTrainer
from modules.fraud_detector import FraudDetector
from modules.customer_profiles import get_all_customers, get_customer_by_id, compute_individual_var_score
from modules.statement_parser import parse_uploaded_file, parse_raw_text, evaluate_statement_transactions

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Ensure directories exist
os.makedirs(os.path.join(app.root_path, 'static', 'images'), exist_ok=True)
os.makedirs(config.MODEL_DIR, exist_ok=True)


def get_trained_model():
    """Load the best trained model if available."""
    best_model_path = os.path.join(config.MODEL_DIR, 'best_model.joblib')
    if os.path.exists(best_model_path):
        return joblib.load(best_model_path)
    return None


def get_scaler():
    """Load the saved scaler if available."""
    scaler_path = os.path.join(config.MODEL_DIR, 'scaler.joblib')
    if os.path.exists(scaler_path):
        return joblib.load(scaler_path)
    return None


def get_var_stats():
    """Load saved VaR statistics for scoring new transactions."""
    var_stats_path = os.path.join(config.MODEL_DIR, 'var_stats.joblib')
    if os.path.exists(var_stats_path):
        return joblib.load(var_stats_path)
    return None


# Transaction type risk multipliers (simulates real-world risk patterns)
TX_TYPE_RISK = {
    'online_purchase': 0.3,
    'pos_payment': 0.1,
    'atm_withdrawal': 0.4,
    'wire_transfer': 0.6,
    'international': 0.7,
}


def build_features_from_simple_input(amount, tx_type, merchant, location):
    """
    Convert simple user inputs into the 30-feature vector (Time, V1-V28, Amount)
    that the ML model expects. Uses the transaction metadata to create realistic 
    feature patterns.
    """
    np.random.seed(int(amount * 100) % 2**31)

    # Base features — normally distributed around 0 (like PCA components)
    features = {}
    features['Time'] = np.random.uniform(0, 172792)  # Random time in dataset range

    # Generate V1-V28 features with risk-influenced patterns
    risk_factor = TX_TYPE_RISK.get(tx_type, 0.3)

    # Higher amounts + higher risk types shift features toward fraud patterns
    amount_risk = min(amount / 35000.0, 1.0)  # Normalize amount influence for higher baselines
    combined_risk = (risk_factor + amount_risk) / 2.0

    for i in range(1, 29):
        if combined_risk > 0.5:
            # Fraud-like patterns: V1-V7 tend to be more negative for fraud
            if i <= 7:
                features[f'V{i}'] = np.random.normal(-2.0 * combined_risk, 1.5)
            elif i <= 14:
                features[f'V{i}'] = np.random.normal(combined_risk, 1.0)
            else:
                features[f'V{i}'] = np.random.normal(0, 0.5)
        else:
            # Normal patterns
            features[f'V{i}'] = np.random.normal(0, 1.0)

    features['Amount'] = amount
    return features


@app.context_processor
def inject_alerts_count():
    """Inject unread alerts count to all templates for the navbar badge."""
    try:
        with DBManager() as db:
            alerts = db.get_alerts(unread_only=True)
            return dict(unread_alerts_count=len(alerts))
    except Exception:
        return dict(unread_alerts_count=0)


# ─── ROUTES ─────────────────────────────────────────────

@app.route('/')
def dashboard():
    """Render the main dashboard."""
    try:
        with DBManager() as db:
            stats = db.get_dashboard_stats()
            recent_alerts = db.get_alerts(limit=5)
            recent_transactions = db.get_transactions(limit=10)
            customers = get_all_customers()

            return render_template('index.html',
                                   stats=stats,
                                   recent_alerts=recent_alerts,
                                   recent_transactions=recent_transactions,
                                   customers=customers)
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "error")
        return render_template('index.html',
                               stats={'total_transactions': 0, 'fraud_count': 0,
                                      'legitimate_count': 0, 'high_risk_count': 0,
                                      'recent_alerts_count': 0},
                               recent_alerts=[], recent_transactions=[],
                               customers=get_all_customers())


@app.route('/profiles')
def profiles():
    """Redirect to unified Individual Payments with embedded benchmarks."""
    return redirect(url_for('individual_payments') + '#benchmarks')


@app.route('/make_transaction', methods=['GET', 'POST'])
@app.route('/individual_payments', methods=['GET', 'POST'])
def individual_payments():
    """Handle individual payment simulation and statement auditing with customer-specific VaR in Rupees (₹)."""
    customers = get_all_customers()
    selected_customer = request.args.get('customer', 'cust_pranavi')
    active_subtab = request.args.get('tab', 'single')
    result = None
    statement_results = None
    scanned_filename = None

    if request.method == 'POST':
        payment_mode = request.form.get('payment_mode', 'single')
        customer_id = request.form.get('customer_id', 'cust_pranavi')
        selected_customer = customer_id

        # Check if this is a statement file upload or raw text scan
        if payment_mode == 'statement' or ('document_file' in request.files and request.files['document_file'].filename != '') or ('raw_text' in request.form and request.form['raw_text'].strip()):
            active_subtab = 'statement'
            try:
                save_to_db = bool(request.form.get('save_to_db', True))
                uploaded_file = request.files.get('document_file')
                raw_txs = []
                
                if uploaded_file and uploaded_file.filename != '':
                    scanned_filename = uploaded_file.filename
                    raw_txs = parse_uploaded_file(uploaded_file, scanned_filename)
                else:
                    raw_text = request.form.get('raw_text', '').strip()
                    if raw_text:
                        scanned_filename = f"Pasted Statement ({get_customer_by_id(customer_id)['name']})"
                        raw_txs = parse_raw_text(raw_text)

                if not raw_txs:
                    flash("⚠️ No valid transactions found in the provided document or text.", "warning")
                else:
                    statement_results = evaluate_statement_transactions(raw_txs, selected_customer_id=customer_id, save_to_db=save_to_db)
                    if statement_results['fraud_count'] > 0:
                        flash(f"🚨 Statement Audit Complete: Detected {statement_results['fraud_count']} Critical Fraud & {statement_results['suspicious_count']} Suspicious anomalies for {get_customer_by_id(customer_id)['name']}!", "danger")
                    else:
                        flash(f"✅ Statement Audit Complete: All {statement_results['total_count']} transactions cleared within safe limits for {get_customer_by_id(customer_id)['name']}!", "success")
            except Exception as e:
                flash(f"Error auditing statement: {str(e)}", "error")
        else:
            # Single transaction mode
            active_subtab = 'single'
            try:
                amount = float(request.form.get('amount', 0))
                merchant = request.form.get('merchant', 'Unknown')
                tx_type = request.form.get('tx_type', 'pos_payment')
                location = request.form.get('location', 'Unknown')

                # Calculate individual customer VaR in Rupees (₹)
                cust_var = compute_individual_var_score(amount, customer_id)
                var_score = cust_var['var_score']

                model = get_trained_model()
                if model is None:
                    flash("⚠️ No trained model found.", "warning")
                    return render_template('individual_payments.html', result=None, statement_results=None, customers=customers, selected_customer=selected_customer, active_subtab=active_subtab)

                features = build_features_from_simple_input(amount, tx_type, merchant, location)
                df = pd.DataFrame([features])

                scaler = get_scaler()
                if scaler:
                    try:
                        df[['Amount', 'Time']] = scaler.transform(df[['Amount', 'Time']])
                    except Exception:
                        pass

                df['var_risk_score'] = var_score
                feature_cols = ['Time'] + [f'V{i}' for i in range(1, 29)] + ['Amount', 'var_risk_score']
                X_pred = df[feature_cols]

                if hasattr(model, 'predict_proba'):
                    fraud_prob = float(model.predict_proba(X_pred)[0][1])
                else:
                    fraud_prob = float(model.predict(X_pred)[0])

                ml_prediction = 1 if fraud_prob >= config.FRAUD_THRESHOLD else 0

                var_calc = VaRCalculator()
                detector = FraudDetector(model, var_calc)
                risk_level = detector.classify_risk(ml_prediction, fraud_prob, var_score)

                tx_id = f"TXN_{uuid.uuid4().hex[:8].upper()}"
                tx_record = {
                    'transaction_id': tx_id,
                    'amount': amount,
                    'time_stamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'features': {
                        'customer_id': customer_id,
                        'customer_name': cust_var['customer_name'],
                        'merchant': merchant,
                        'type': tx_type,
                        'location': location
                    },
                    'var_risk_score': round(var_score, 4),
                    'ml_prediction': ml_prediction,
                    'fraud_probability': round(fraud_prob, 4),
                    'risk_level': risk_level
                }

                with DBManager() as db:
                    db.insert_transaction(tx_record)
                    if ml_prediction == 1 or risk_level in ['HIGH', 'MEDIUM']:
                        alert = AlertManager.generate_fraud_alert(tx_id, risk_level, fraud_prob, amount)
                        db.insert_alert(tx_id, alert['alert_type'], alert['message'])

                result = {
                    'transaction_id': tx_id,
                    'customer_id': customer_id,
                    'customer_name': cust_var['customer_name'],
                    'customer_role': cust_var['customer_role'],
                    'customer_mean': cust_var['mean'],
                    'customer_var95': cust_var['var_95'],
                    'deviation_ratio': cust_var['deviation_ratio'],
                    'amount': amount,
                    'merchant': merchant,
                    'prediction': 'Fraudulent' if ml_prediction == 1 else 'Legitimate',
                    'probability': round(fraud_prob * 100, 2),
                    'var_score': round(var_score * 100, 2),
                    'risk_level': risk_level
                }
            except Exception as e:
                flash(f"Error processing transaction: {str(e)}", "error")

    return render_template('individual_payments.html', 
                           result=result, 
                           statement_results=statement_results, 
                           scanned_filename=scanned_filename, 
                           customers=customers, 
                           selected_customer=selected_customer, 
                           active_subtab=active_subtab)



@app.route('/scan_document', methods=['GET', 'POST'])
def scan_document():
    """Redirect to unified Individual Payments statement & PDF scanner."""
    return redirect(url_for('individual_payments', tab='statement'))


@app.route('/download_sample/<filename>')
def download_sample(filename):
    """Download pre-generated sample statement files for live demo."""
    sample_dir = os.path.join(app.root_path, 'sample_statements')
    return send_from_directory(sample_dir, filename, as_attachment=True)


@app.route('/api/load_sample/<sample_type>')
def api_load_sample(sample_type):
    """API endpoint to load sample text for one-click demo."""
    sample_dir = os.path.join(app.root_path, 'sample_statements')
    mapping = {
        'pranavi_pdf': ('sample_statement_pranavi.pdf', 'cust_pranavi'),
        'naresh_txt': ('sample_statement_naresh.txt', 'cust_naresh'),
        'janakiram_csv': ('sample_statement_janakiram.csv', 'cust_janakiram'),
        'srinithya_json': ('sample_statement_srinithya.json', 'cust_srinithya'),
    }
    
    if sample_type not in mapping:
        return jsonify({'status': 'error', 'message': 'Unknown sample type'}), 404
        
    filename, cust_id = mapping[sample_type]
    filepath = os.path.join(sample_dir, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.pdf':
        from modules.statement_parser import parse_pdf
        with open(filepath, 'rb') as f:
            txs = parse_pdf(f)
        content = "ACCOUNT STATEMENT - M. Pranavi (23R91A05H6)\n" + "\n".join(
            f"{t['date']} | {t['merchant']} | Rs {t['amount']:,.2f} | {t['tx_type']}" for t in txs
        )
    else:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
    return jsonify({
        'status': 'success',
        'filename': filename,
        'customer_id': cust_id,
        'content': content
    })


@app.route('/transactions')
def transactions():
    """Render the transaction history page."""
    page = int(request.args.get('page', 1))
    risk_level = request.args.get('risk_level', None)

    limit = 50
    offset = (page - 1) * limit

    try:
        with DBManager() as db:
            txs = db.get_transactions(limit=limit, offset=offset, risk_level_filter=risk_level)
            return render_template('transactions.html', transactions=txs, page=page)
    except Exception as e:
        flash(f"Error loading transactions: {str(e)}", "error")
        return render_template('transactions.html', transactions=[], page=page)


@app.route('/analytics')
def analytics():
    """Render the model analytics page."""
    try:
        with DBManager() as db:
            logs = db.get_model_logs()
            return render_template('analytics.html', model_logs=logs)
    except Exception as e:
        flash(f"Error loading analytics: {str(e)}", "error")
        return render_template('analytics.html', model_logs=[])


@app.route('/alerts')
def alerts_page():
    """Redirect to unified Transactions & Security Alerts ledger."""
    return redirect(url_for('transactions', risk_level='ALERTS'))


@app.route('/alerts/mark_read/<int:alert_id>', methods=['POST'])
def mark_alert_read(alert_id):
    """Mark a specific alert as read."""
    try:
        with DBManager() as db:
            db.mark_alert_read(alert_id)
            flash("Alert marked as read.", "success")
    except Exception as e:
        flash(f"Error updating alert: {str(e)}", "error")

    return redirect(url_for('alerts_page'))


@app.route('/train')
def train_model():
    """Trigger the full ML training pipeline."""
    try:
        # Step 1: Load data
        collector = DataCollector()
        df = collector.load_data(config.DATA_PATH)
        if df is None:
            flash("❌ Dataset not found. Please place creditcard.csv in the data/ folder.", "error")
            return redirect(url_for('analytics'))

        df = collector.generate_transaction_ids(df)

        # Step 2: Add VaR features & save stats for later predictions
        var_calc = VaRCalculator()
        amounts = df['Amount']
        var_stats = {
            'var_95': var_calc.calculate_historical_var(amounts, 0.95),
            'var_99': var_calc.calculate_historical_var(amounts, 0.99),
            'mean': float(amounts.mean()),
            'std': float(amounts.std())
        }
        joblib.dump(var_stats, os.path.join(config.MODEL_DIR, 'var_stats.joblib'))
        df = var_calc.add_var_features(df)

        # Step 3: Preprocess
        preprocessor = DataPreprocessor()
        df_for_model = df.drop(columns=['transaction_id', 'var_95', 'var_99'], errors='ignore')
        df_scaled, scaler = preprocessor.scale_features(df_for_model, columns=['Amount', 'Time'])
        joblib.dump(scaler, os.path.join(config.MODEL_DIR, 'scaler.joblib'))

        X_train, X_test, y_train, y_test = preprocessor.split_data(df_scaled, target='Class')
        if len(X_train) > 50000:
            fraud_mask = (y_train == 1)
            legit_indices = y_train[~fraud_mask].sample(n=min(40000, sum(~fraud_mask)), random_state=42).index
            fraud_indices = y_train[fraud_mask].index
            selected_indices = legit_indices.union(fraud_indices)
            X_train_sub = X_train.loc[selected_indices]
            y_train_sub = y_train.loc[selected_indices]
        else:
            X_train_sub, y_train_sub = X_train, y_train

        X_train_res, y_train_res = preprocessor.apply_smote(X_train_sub, y_train_sub)

        # Step 4: Train all 4 models
        trainer = ModelTrainer()
        results = trainer.train_all_models(X_train_res, y_train_res, X_test, y_test)

        # Step 5: Save best model
        best_name, best_model = trainer.get_best_model(results)
        trainer.save_model(best_model, 'best_model', config.MODEL_DIR)
        for name in trainer.models:
            trainer.save_model(trainer.models[name], name, config.MODEL_DIR)

        # Step 6: Generate plots
        try:
            trainer.plot_roc_curves(results, X_test, y_test,
                                    save_dir=os.path.join(app.root_path, 'static', 'images'))
            trainer.plot_confusion_matrices(results,
                                            save_dir=os.path.join(app.root_path, 'static', 'images'))
        except Exception:
            pass

        # Step 7: Log metrics & store sample predictions
        with DBManager() as db:
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
            var_scores = df.loc[X_sample.index, 'var_risk_score'].values if 'var_risk_score' in df.columns else np.zeros(sample_size)

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

        flash(f"✅ Training complete! Best model: {best_name} "
              f"(F1: {results[best_name]['f1']:.4f}, AUC: {results[best_name]['auc_roc']:.4f}). "
              f"{alert_count} alerts generated from {sample_size} test transactions.", "success")

    except FileNotFoundError:
        flash("❌ Dataset not found! Please place 'creditcard.csv' in the data/ folder.", "error")
    except Exception as e:
        flash(f"❌ Training error: {str(e)}", "error")

    return redirect(url_for('analytics'))


@app.route('/api/stats')
def api_stats():
    """JSON API endpoint for dashboard statistics."""
    try:
        with DBManager() as db:
            return jsonify(db.get_dashboard_stats())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    from setup_db import setup_database
    setup_database()
    app.run(debug=config.DEBUG, port=5000)
