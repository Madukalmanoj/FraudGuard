"""
Statement and Document Parser Module.
Extracts transaction records from PDF files, plain text files, CSV, and JSON,
normalizing them for the Financial Fraud Detection and VaR Engine.
"""
import re
import os
import io
import json
import csv
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

logger = logging.getLogger(__name__)

# Keywords for payment channel classification
CHANNEL_KEYWORDS = {
    'international': ['international', 'overseas', 'cross-border', 'forex', 'dubai', 'macau', 'usd', 'eur', 'gbp', 'foreign', 'casino'],
    'wire_transfer': ['wire', 'neft', 'imps', 'rtgs', 'transfer', 'netbanking', 'swift', 'remittance', 'fund transfer'],
    'atm_withdrawal': ['atm', 'cash wdl', 'withdrawal', 'nfs atm', 'cash dispense', 'atm debit'],
    'online_purchase': ['online', 'ecommerce', 'e-com', 'amazon', 'flipkart', 'myntra', 'coursera', 'netflix', 'spotify', 'web checkout', 'pos ecom'],
    'pos_payment': ['upi', 'gpay', 'phonepe', 'paytm', 'qr', 'pos', 'canteen', 'swipe', 'store', 'cafe', 'swiggy', 'zomato', 'metro']
}

# Student / Cardholder ID mapping from names or roll numbers
STUDENT_MAPPING = {
    'pranavi': 'cust_pranavi',
    '23r91a05h6': 'cust_pranavi',
    'sri nithya': 'cust_srinithya',
    'srinithya': 'cust_srinithya',
    'nithya': 'cust_srinithya',
    '23r91a05g7': 'cust_srinithya',
    'naresh': 'cust_naresh',
    '23r91a05f3': 'cust_naresh',
    'janaki ram': 'cust_janakiram',
    'janakiram': 'cust_janakiram',
    '24r95a0519': 'cust_janakiram'
}


def detect_channel(text: str) -> str:
    """Infer payment channel from transaction narration/details."""
    lower_text = text.lower()
    for channel, keywords in CHANNEL_KEYWORDS.items():
        for kw in keywords:
            if kw in lower_text:
                return channel
    return 'pos_payment'


def detect_student_from_text(text: str) -> Optional[str]:
    """Detect if statement specifies a student by name or roll number."""
    lower = text.lower()
    for key, cust_id in STUDENT_MAPPING.items():
        if key in lower:
            return cust_id
    return None


def parse_pdf(file_stream_or_path) -> List[Dict[str, Any]]:
    """Extract text from PDF pages and parse transactions."""
    if not PdfReader:
        raise ImportError("pypdf is required to parse PDF documents.")
    
    reader = PdfReader(file_stream_or_path)
    full_text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            full_text += extracted + "\n"
            
    return parse_raw_text(full_text)


def parse_csv_content(content_str: str) -> List[Dict[str, Any]]:
    """Parse transactions from CSV formatted string."""
    transactions = []
    f = io.StringIO(content_str.strip())
    reader = csv.DictReader(f)
    
    # Normalize headers
    headers = {h.strip().lower(): h for h in (reader.fieldnames or [])}
    
    def find_col(*candidates):
        for c in candidates:
            if c.lower() in headers:
                return headers[c.lower()]
        return None

    amt_col = find_col('amount', 'amount_inr', 'debit', 'transaction amount', 'inr', 'amt')
    merch_col = find_col('merchant', 'description', 'narration', 'payee', 'details', 'name')
    date_col = find_col('date', 'time', 'timestamp', 'txn_date', 'date_time')
    type_col = find_col('type', 'channel', 'payment_type', 'mode')
    loc_col = find_col('location', 'city', 'place')
    cust_col = find_col('customer_id', 'customer', 'student', 'roll_no', 'account')

    for row in reader:
        try:
            amt_raw = str(row.get(amt_col, '0')).replace('₹', '').replace('Rs', '').replace(',', '').strip()
            amount = float(amt_raw)
            if amount <= 0:
                continue
                
            merchant = str(row.get(merch_col, 'Unknown Merchant')).strip() or 'Unknown Merchant'
            date_val = str(row.get(date_col, datetime.now().strftime('%Y-%m-%d'))).strip()
            tx_type = str(row.get(type_col, '')).strip()
            if not tx_type or tx_type.lower() not in CHANNEL_KEYWORDS:
                tx_type = detect_channel(merchant + " " + tx_type)
            
            location = str(row.get(loc_col, 'Hyderabad, IN')).strip() or 'Hyderabad, IN'
            cust_id = str(row.get(cust_col, '')).strip().lower()
            detected_cust = STUDENT_MAPPING.get(cust_id, None)
            
            transactions.append({
                'amount': amount,
                'merchant': merchant,
                'date': date_val,
                'tx_type': tx_type,
                'location': location,
                'customer_id': detected_cust,
                'raw_line': json.dumps(row)
            })
        except Exception as e:
            logger.debug(f"Skipping CSV row due to error: {e}")
            continue

    # Fallback to text parsing if CSV parsing didn't find rows with headers
    if not transactions:
        return parse_raw_text(content_str)
        
    return transactions


def parse_json_content(content_str: str) -> List[Dict[str, Any]]:
    """Parse transactions from JSON string or list of objects."""
    transactions = []
    try:
        data = json.loads(content_str)
        if isinstance(data, dict):
            # Check for keys like 'transactions', 'data', 'items'
            for key in ['transactions', 'txs', 'data', 'items', 'records', 'statement']:
                if key in data and isinstance(data[key], list):
                    data = data[key]
                    break
            else:
                data = [data]
                
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                amt = float(str(item.get('amount') or item.get('Amount') or item.get('debit') or 0).replace(',', ''))
                if amt <= 0:
                    continue
                merchant = str(item.get('merchant') or item.get('description') or 'Unknown Merchant')
                tx_type = str(item.get('type') or item.get('tx_type') or detect_channel(merchant))
                date_val = str(item.get('date') or item.get('timestamp') or datetime.now().strftime('%Y-%m-%d'))
                loc = str(item.get('location') or 'Hyderabad, IN')
                cid = item.get('customer_id') or detect_student_from_text(str(item))
                
                transactions.append({
                    'amount': amt,
                    'merchant': merchant,
                    'date': date_val,
                    'tx_type': tx_type,
                    'location': loc,
                    'customer_id': cid,
                    'raw_line': json.dumps(item)
                })
    except Exception as e:
        logger.error(f"Error parsing JSON content: {e}")
        return parse_raw_text(content_str)
        
    return transactions


def parse_raw_text(raw_text: str) -> List[Dict[str, Any]]:
    """
    Intelligent line-by-line extractor for free-form bank statements,
    SMS alerts, transaction receipts, and log files.
    """
    transactions = []
    lines = raw_text.splitlines()
    
    # Common currency / amount patterns in India
    # Matches: ₹ 3,000.00 | Rs. 450 | Rs 120 | INR 15,000 | 3000.00
    date_pattern = re.compile(r'(\b\d{4}[-/.]\d{1,2}[-/.]\d{1,2}\b|\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b|\b\d{1,2}-[a-zA-Z]{3}-\d{2,4}\b)')
    
    # Check if a student roll number or name is mentioned globally in the document
    global_student = detect_student_from_text(raw_text)

    for line in lines:
        line_clean = line.strip()
        if not line_clean or len(line_clean) < 5:
            continue
            
        # Ignore header, metadata, and summary lines
        ignored_keywords = [
            'account statement', 'opening balance', 'closing balance', 'page ',
            'total debit', 'total credit', 'total amount', 'summary', 'baseline',
            'note:', 'generated via', 'account details', 'transaction details',
            'end of statement', 'currency'
        ]
        if any(h in line_clean.lower() for h in ignored_keywords):
            # Could contain account holder name
            detected = detect_student_from_text(line_clean)
            if detected:
                global_student = detected
            continue
            
        # Find amounts in line
        # Look for explicit currency prefix first (Rs, INR, ₹)
        explicit_amt = re.findall(r'(?:₹|rs\.?|inr)\s*([0-9,]+(?:\.[0-9]{1,2})?)', line_clean, re.IGNORECASE)
        amount = 0.0
        
        if explicit_amt:
            try:
                amount = float(explicit_amt[-1].replace(',', ''))
            except ValueError:
                pass
        else:
            # Look for number patterns with decimal or ending with currency
            numbers = re.findall(r'\b[0-9,]+\.[0-9]{2}\b', line_clean)
            if numbers:
                try:
                    amount = float(numbers[-1].replace(',', ''))
                except ValueError:
                    pass

        if amount <= 0 or amount > 10_000_000:
            # Not a transaction amount or absurdly large
            continue

        # Extract date
        date_match = date_pattern.search(line_clean)
        date_val = date_match.group(1) if date_match else datetime.now().strftime('%Y-%m-%d')
        
        # Clean up merchant name by removing date and amount
        temp_text = line_clean
        if date_match:
            temp_text = temp_text.replace(date_match.group(0), '')
        # Remove currency markers and amounts
        temp_text = re.sub(r'(?:₹|rs\.?|inr)\s*[0-9,.]+', '', temp_text, flags=re.IGNORECASE)
        temp_text = re.sub(r'\b[0-9,.]+\b', '', temp_text)
        temp_text = re.sub(r'[\t\r\n|/\\-]+', ' ', temp_text).strip()
        
        merchant = temp_text if len(temp_text) >= 3 else "General Merchant"
        # Truncate overly long narrations
        if len(merchant) > 50:
            merchant = merchant[:50].strip() + '...'
            
        tx_type = detect_channel(line_clean)
        loc = 'Dubai, UAE' if tx_type == 'international' else 'Hyderabad, IN'
        line_student = detect_student_from_text(line_clean) or global_student

        transactions.append({
            'amount': amount,
            'merchant': merchant,
            'date': date_val,
            'tx_type': tx_type,
            'location': loc,
            'customer_id': line_student,
            'raw_line': line_clean
        })

    return transactions


def parse_uploaded_file(file_obj, filename: str) -> List[Dict[str, Any]]:
    """Dispatch file parsing based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == '.pdf':
        return parse_pdf(file_obj)
    elif ext == '.csv':
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        return parse_csv_content(content)
    elif ext == '.json':
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        return parse_json_content(content)
    else:
        content = file_obj.read()
        if isinstance(content, bytes):
            content = content.decode('utf-8', errors='ignore')
        return parse_raw_text(content)


# Model and feature generation helpers for statement auditing
TX_TYPE_RISK = {
    'online_purchase': 0.3,
    'pos_payment': 0.1,
    'atm_withdrawal': 0.4,
    'wire_transfer': 0.6,
    'international': 0.7,
}


def _build_features(amount: float, tx_type: str, merchant: str, location: str) -> Dict[str, Any]:
    """Build the 30-feature vector expected by the model."""
    import numpy as np
    np.random.seed(int(amount * 100) % 2**31)
    features = {'Time': float(np.random.uniform(0, 172792))}
    risk_factor = TX_TYPE_RISK.get(tx_type, 0.3)
    amount_risk = min(amount / 35000.0, 1.0)
    combined_risk = (risk_factor + amount_risk) / 2.0

    for i in range(1, 29):
        if combined_risk > 0.5:
            if i <= 7:
                features[f'V{i}'] = float(np.random.normal(-2.0 * combined_risk, 1.5))
            elif i <= 14:
                features[f'V{i}'] = float(np.random.normal(combined_risk, 1.0))
            else:
                features[f'V{i}'] = float(np.random.normal(0, 0.5))
        else:
            features[f'V{i}'] = float(np.random.normal(0, 1.0))

    features['Amount'] = float(amount)
    return features


def evaluate_statement_transactions(transactions: List[Dict[str, Any]], 
                                   selected_customer_id: Optional[str] = None, 
                                   save_to_db: bool = True) -> Dict[str, Any]:
    """
    Run each parsed transaction through the Individual VaR + ML Engine.
    Detects anomalies and generates real-time fraud alerts.
    """
    import uuid
    import joblib
    import numpy as np
    import pandas as pd
    import config
    from modules.customer_profiles import compute_individual_var_score, get_customer_by_id
    from modules.var_calculator import VaRCalculator
    from modules.fraud_detector import FraudDetector
    from database.db_manager import DBManager
    from modules.alerts import AlertManager

    model_path = os.path.join(config.MODEL_DIR, 'best_model.joblib')
    scaler_path = os.path.join(config.MODEL_DIR, 'scaler.joblib')
    
    model = joblib.load(model_path) if os.path.exists(model_path) else None
    scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None
    
    var_calc = VaRCalculator()
    detector = FraudDetector(model, var_calc) if model else None

    analyzed_transactions = []
    total_amount = 0.0
    high_risk_amount = 0.0
    approved_count = 0
    suspicious_count = 0
    fraud_count = 0

    for idx, t in enumerate(transactions, start=1):
        amount = float(t.get('amount', 0))
        merchant = str(t.get('merchant', 'General Merchant'))
        date_val = str(t.get('date', datetime.now().strftime('%Y-%m-%d')))
        tx_type = str(t.get('tx_type', 'pos_payment'))
        location = str(t.get('location', 'Hyderabad, IN'))

        # Determine which student's baseline to apply
        if selected_customer_id and selected_customer_id != 'auto':
            cust_id = selected_customer_id
        else:
            cust_id = t.get('customer_id') or 'cust_pranavi'

        cust_profile = get_customer_by_id(cust_id)
        cust_var = compute_individual_var_score(amount, cust_id)
        var_score = cust_var['var_score']

        # ML Prediction
        fraud_prob = 0.05
        ml_prediction = 0
        if model:
            features = _build_features(amount, tx_type, merchant, location)
            df = pd.DataFrame([features])
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

        # Combined risk classification
        risk_level = detector.classify_risk(ml_prediction, fraud_prob, var_score) if detector else ('HIGH' if var_score >= 0.8 else 'LOW')

        # Formulate human-readable risk indicators / rationale
        reasons = []
        if amount >= cust_var['var_99']:
            reasons.append(f"Exceeds 99% VaR limit (₹{cust_var['var_99']:,.2f})")
        elif amount >= cust_var['var_95']:
            reasons.append(f"Exceeds 95% VaR limit (₹{cust_var['var_95']:,.2f})")

        if cust_var['deviation_ratio'] >= 3.0:
            reasons.append(f"High spending spike ({cust_var['deviation_ratio']}x normal average)")

        if tx_type == 'international':
            reasons.append("Cross-border / overseas channel")
        elif tx_type == 'wire_transfer':
            reasons.append("Large wire transfer channel")

        if fraud_prob >= 0.70:
            reasons.append(f"ML Model Alert ({round(fraud_prob * 100, 1)}% fraud probability)")

        if not reasons:
            reasons.append(f"Routine spend within {cust_profile['name']}'s normal history")

        total_amount += amount
        if risk_level == 'HIGH':
            fraud_count += 1
            high_risk_amount += amount
            decision_status = 'FRAUD ALERT'
            badge_class = 'danger'
        elif risk_level == 'MEDIUM':
            suspicious_count += 1
            high_risk_amount += amount
            decision_status = 'SUSPICIOUS'
            badge_class = 'warning'
        else:
            approved_count += 1
            decision_status = 'APPROVED'
            badge_class = 'success'

        tx_id = f"TXN_DOC_{uuid.uuid4().hex[:8].upper()}"

        tx_entry = {
            'index': idx,
            'transaction_id': tx_id,
            'date': date_val,
            'merchant': merchant,
            'amount': amount,
            'tx_type': tx_type,
            'location': location,
            'customer_id': cust_profile['id'],
            'customer_name': cust_profile['name'],
            'customer_roll': cust_profile['roll_no'],
            'customer_mean': cust_profile['mean_spending'],
            'var_score': round(var_score * 100, 2),
            'deviation_ratio': cust_var['deviation_ratio'],
            'fraud_probability': round(fraud_prob * 100, 2),
            'risk_level': risk_level,
            'decision_status': decision_status,
            'badge_class': badge_class,
            'reasons': reasons
        }

        # Store in SQLite database if requested
        if save_to_db:
            try:
                tx_record = {
                    'transaction_id': tx_id,
                    'amount': amount,
                    'time_stamp': f"{date_val} {datetime.now().strftime('%H:%M:%S')}",
                    'features': {
                        'customer_id': cust_profile['id'],
                        'customer_name': cust_profile['name'],
                        'merchant': merchant,
                        'type': tx_type,
                        'location': location,
                        'source': 'statement_scan'
                    },
                    'var_risk_score': round(var_score, 4),
                    'ml_prediction': ml_prediction,
                    'fraud_probability': round(fraud_prob, 4),
                    'risk_level': risk_level
                }
                with DBManager() as db:
                    db.insert_transaction(tx_record)
                    if risk_level in ['HIGH', 'MEDIUM'] or ml_prediction == 1:
                        alert = AlertManager.generate_fraud_alert(tx_id, risk_level, fraud_prob, amount)
                        db.insert_alert(tx_id, alert['alert_type'], f"{alert['message']} [{cust_profile['name']} - {merchant}]")
            except Exception as e:
                logger.error(f"Error saving scanned transaction to database: {e}")

        analyzed_transactions.append(tx_entry)

    return {
        'total_count': len(analyzed_transactions),
        'approved_count': approved_count,
        'suspicious_count': suspicious_count,
        'fraud_count': fraud_count,
        'total_amount': round(total_amount, 2),
        'high_risk_amount': round(high_risk_amount, 2),
        'transactions': analyzed_transactions
    }

