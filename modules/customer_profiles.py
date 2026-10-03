"""
Customer Profiles and Individual Value at Risk (VaR) Management.
Dynamically computes personalized spending baselines in Indian Rupees (₹)
for the 4 TKREC project team students:
1. M. Pranavi     (23R91A05H6)
2. K. Sri Nithya  (23R91A05G7)
3. K. Naresh      (23R91A05F3)
4. M. Janaki Ram  (24R95A0519)
"""
import os
import pandas as pd
import numpy as np
from typing import Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

CUSTOMER_METADATA = {
    'cust_pranavi': {
        'id': 'cust_pranavi',
        'name': 'M. Pranavi',
        'roll_no': '23R91A05H6',
        'role': 'Student Lead • Academic & Tech Projects Head',
        'account_no': '23R91A05H6',
        'file': 'person1_pranavi.csv',
        'icon': 'user-graduate',
        'badge_class': 'bg-primary',
        'description': 'Student lead managing high-value research hardware, workstation gear, certification degrees, and semester lab resources.'
    },
    'cust_janakiram': {
        'id': 'cust_janakiram',
        'name': 'M. Janaki Ram',
        'roll_no': '24R95A0519',
        'role': 'Student • Developer & Hardware Lead',
        'account_no': '24R95A0519',
        'file': 'person4_janakiram.csv',
        'icon': 'microchip',
        'badge_class': 'bg-success',
        'description': 'Lateral entry student handling freelance dev tools, cloud hosting servers, and project hardware kits.'
    },
    'cust_srinithya': {
        'id': 'cust_srinithya',
        'name': 'K. Sri Nithya',
        'roll_no': '23R91A05G7',
        'role': 'Student • Tech & Course Lead',
        'account_no': '23R91A05G7',
        'file': 'person2_srinithya.csv',
        'icon': 'laptop-code',
        'badge_class': 'bg-info',
        'description': 'Student managing technical course certifications, online food delivery, and digital subscriptions.'
    },
    'cust_naresh': {
        'id': 'cust_naresh',
        'name': 'K. Naresh',
        'roll_no': '23R91A05F3',
        'role': 'Student • Hostel & Events Head',
        'account_no': '23R91A05F3',
        'file': 'person3_naresh.csv',
        'icon': 'running',
        'badge_class': 'bg-warning',
        'description': 'Hostel student managing mess payments, sports fitness equipment, travel, and college event supplies.'
    }
}


def compute_profile_stats(customer_id: str) -> Dict[str, Any]:
    """Compute empirical VaR stats from the student's CSV dataset."""
    meta = CUSTOMER_METADATA.get(customer_id, CUSTOMER_METADATA['cust_pranavi'])
    filepath = os.path.join(DATA_DIR, meta['file'])
    
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        normal_txs = df[df['Class'] == 0]['Amount_INR']
        if len(normal_txs) == 0:
            normal_txs = df['Amount_INR']
            
        mean = float(normal_txs.mean())
        std = float(normal_txs.std())
        median = float(normal_txs.median())
        h_var95 = float(np.percentile(normal_txs, 95))
        h_var99 = float(np.percentile(normal_txs, 99))
        max_normal = float(normal_txs.max())
        total_txs = len(df)
        fraud_txs = int((df['Class'] == 1).sum())
    else:
        defaults = {
            'cust_pranavi': (12162.90, 5084.81, 22075.06, 26850.82),
            'cust_janakiram': (5188.96, 2272.65, 9586.70, 12819.11),
            'cust_srinithya': (2669.34, 1206.71, 5062.42, 6614.62),
            'cust_naresh': (1347.24, 580.07, 2446.43, 3179.51)
        }
        mean, std, h_var95, h_var99 = defaults.get(customer_id, (12000.0, 5000.0, 22000.0, 26000.0))
        median = mean * 0.90
        max_normal = h_var99 * 1.3
        total_txs = 1000
        fraud_txs = 15

    return {
        'id': meta['id'],
        'name': meta['name'],
        'roll_no': meta['roll_no'],
        'role': meta['role'],
        'account_no': meta['account_no'],
        'currency': '₹',
        'icon': meta['icon'],
        'badge_class': meta['badge_class'],
        'description': meta['description'],
        'mean_spending': round(mean, 2),
        'std_spending': round(std, 2),
        'median_spending': round(median, 2),
        'var_95': round(h_var95, 2),
        'var_99': round(h_var99, 2),
        'max_normal': round(max_normal, 2),
        'total_txs': total_txs,
        'fraud_txs': fraud_txs
    }


def get_all_customers() -> List[Dict[str, Any]]:
    """Return all 4 student profiles with computed VaR baselines."""
    return [compute_profile_stats(cid) for cid in CUSTOMER_METADATA.keys()]


def get_customer_by_id(customer_id: str) -> Dict[str, Any]:
    """Retrieve individual student profile with computed statistics."""
    if customer_id not in CUSTOMER_METADATA:
        customer_id = 'cust_pranavi'
    return compute_profile_stats(customer_id)


def compute_individual_var_score(amount: float, customer_id: str) -> Dict[str, Any]:
    """
    Calculate the personalized Value at Risk (VaR) score for a given amount against
    the selected student's empirical spending baseline in Rupees (₹).
    """
    profile = get_customer_by_id(customer_id)
    mean = profile['mean_spending']
    var_95 = profile['var_95']
    var_99 = profile['var_99']
    
    if amount >= var_99:
        score = 1.0
    elif amount >= var_95:
        score = 0.75 + 0.25 * min(1.0, (amount - var_95) / (var_99 - var_95 + 1e-9))
    elif amount >= mean:
        score = 0.50 * ((amount - mean) / (var_95 - mean + 1e-9))
    else:
        score = max(0.0, 0.20 * (amount / (mean + 1e-9)))
        
    score = float(min(max(score, 0.0), 1.0))
    deviation_ratio = round(amount / (mean + 1e-9), 2)
    
    if score >= 0.75:
        var_risk_tier = 'CRITICAL'
        var_explanation = f"Exceeds 95% individual limit (₹{var_95:,.2f}). Extreme spending spike ({deviation_ratio}x normal)."
    elif score >= 0.50:
        var_risk_tier = 'ELEVATED'
        var_explanation = f"Higher than normal average (₹{mean:,.2f}), within 95% individual limit."
    else:
        var_risk_tier = 'NORMAL'
        var_explanation = f"Routine spending consistent with {profile['name']}'s ({profile['roll_no']}) history."
        
    return {
        'customer_id': profile['id'],
        'customer_name': profile['name'],
        'customer_role': profile['role'],
        'roll_no': profile['roll_no'],
        'account_no': profile['account_no'],
        'amount': amount,
        'var_score': round(score, 4),
        'var_score_pct': round(score * 100, 2),
        'var_95': var_95,
        'var_99': var_99,
        'mean': mean,
        'deviation_ratio': deviation_ratio,
        'var_risk_tier': var_risk_tier,
        'var_explanation': var_explanation
    }
