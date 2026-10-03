"""
Database manager for the Financial Fraud Detection System.
Provides an interface for interacting with the SQLite database.
"""
import sqlite3
import pandas as pd
import json
import os
import sys

# Ensure config can be imported from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DBManager:
    """Manages database connections and operations."""
    
    def __init__(self, db_path=None):
        """
        Initialize the database manager.
        
        Args:
            db_path (str): Path to the SQLite database file. Defaults to config.DATABASE_PATH.
        """
        self.db_path = db_path or config.DATABASE_PATH
        
    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def close(self):
        """Close the database connection."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()
            
    def insert_transaction(self, data: dict):
        """
        Insert a single transaction into the database.
        
        Args:
            data (dict): Transaction data.
            
        Returns:
            int: Inserted row ID.
        """
        features_json = json.dumps(data.get('features', {}))
        
        query = '''
            INSERT INTO transactions (
                transaction_id, amount, time_stamp, features, 
                var_risk_score, ml_prediction, fraud_probability, risk_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        
        values = (
            data.get('transaction_id'),
            data.get('amount'),
            data.get('time_stamp'),
            features_json,
            data.get('var_risk_score'),
            data.get('ml_prediction'),
            data.get('fraud_probability'),
            data.get('risk_level')
        )
        
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()
        return cursor.lastrowid
        
    def insert_bulk_transactions(self, df: pd.DataFrame):
        """
        Insert multiple transactions into the database using pandas.
        
        Args:
            df (pd.DataFrame): DataFrame containing transaction data.
        """
        df.to_sql('transactions', self.conn, if_exists='append', index=False)
        
    def get_transactions(self, limit=100, offset=0, risk_level_filter=None):
        """
        Retrieve transactions with optional filtering.
        
        Args:
            limit (int): Maximum number of records to retrieve.
            offset (int): Number of records to skip.
            risk_level_filter (str): Filter by risk level (e.g., 'HIGH', 'MEDIUM', 'LOW').
            
        Returns:
            list: List of transaction dictionaries.
        """
        query = 'SELECT * FROM transactions'
        params = []
        
        if risk_level_filter:
            if risk_level_filter == 'ALERTS':
                query += " WHERE risk_level IN ('HIGH', 'MEDIUM')"
            else:
                query += ' WHERE risk_level = ?'
                params.append(risk_level_filter)
            
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    def get_transaction_by_id(self, transaction_id):
        """
        Retrieve a specific transaction by its ID.
        
        Args:
            transaction_id (str): The transaction ID.
            
        Returns:
            dict or None: Transaction dictionary if found, else None.
        """
        query = 'SELECT * FROM transactions WHERE transaction_id = ?'
        cursor = self.conn.cursor()
        cursor.execute(query, (transaction_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
        
    def insert_alert(self, transaction_id, alert_type, message):
        """
        Insert a new alert.
        
        Args:
            transaction_id (str): The related transaction ID.
            alert_type (str): Type of alert.
            message (str): Alert message.
            
        Returns:
            int: Inserted alert ID.
        """
        query = '''
            INSERT INTO alerts (transaction_id, alert_type, message) 
            VALUES (?, ?, ?)
        '''
        cursor = self.conn.cursor()
        cursor.execute(query, (transaction_id, alert_type, message))
        self.conn.commit()
        return cursor.lastrowid
        
    def get_alerts(self, unread_only=False, limit=None):
        """
        Retrieve alerts.
        
        Args:
            unread_only (bool): If True, retrieve only unread alerts.
            limit (int): Maximum number of alerts to retrieve. None for all.
            
        Returns:
            list: List of alert dictionaries.
        """
        query = 'SELECT * FROM alerts'
        params = []
        if unread_only:
            query += ' WHERE is_read = 0'
        query += ' ORDER BY created_at DESC'
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
        
    def mark_alert_read(self, alert_id):
        """
        Mark an alert as read.
        
        Args:
            alert_id (int): The alert ID.
        """
        query = 'UPDATE alerts SET is_read = 1 WHERE id = ?'
        cursor = self.conn.cursor()
        cursor.execute(query, (alert_id,))
        self.conn.commit()
        
    def log_model_performance(self, model_name, metrics: dict):
        """
        Log performance metrics for a model.
        
        Args:
            model_name (str): Name of the model.
            metrics (dict): Dictionary of performance metrics.
        """
        query = '''
            INSERT INTO model_logs (
                model_name, accuracy, precision_score, recall, f1_score, auc_roc
            ) VALUES (?, ?, ?, ?, ?, ?)
        '''
        values = (
            model_name,
            metrics.get('accuracy'),
            metrics.get('precision_score'),
            metrics.get('recall'),
            metrics.get('f1_score'),
            metrics.get('auc_roc')
        )
        cursor = self.conn.cursor()
        cursor.execute(query, values)
        self.conn.commit()
        
    def get_model_logs(self):
        """
        Retrieve all model performance logs.
        
        Returns:
            list: List of model log dictionaries.
        """
        query = 'SELECT * FROM model_logs ORDER BY trained_at DESC'
        cursor = self.conn.cursor()
        cursor.execute(query)
        return [dict(row) for row in cursor.fetchall()]
        
    def get_dashboard_stats(self):
        """
        Calculate statistics for the dashboard.
        
        Returns:
            dict: Dictionary with statistics.
        """
        stats = {
            'total_transactions': 0,
            'fraud_count': 0,
            'legitimate_count': 0,
            'high_risk_count': 0,
            'recent_alerts_count': 0
        }
        
        if not hasattr(self, 'conn') or not self.conn:
            return stats
            
        cursor = self.conn.cursor()
        
        # Get total transactions
        cursor.execute('SELECT COUNT(*) FROM transactions')
        stats['total_transactions'] = cursor.fetchone()[0]
        
        # Get fraud vs legitimate (based on ml_prediction)
        cursor.execute('SELECT ml_prediction, COUNT(*) FROM transactions GROUP BY ml_prediction')
        for row in cursor.fetchall():
            if row[0] == 1:
                stats['fraud_count'] = row[1]
            elif row[0] == 0:
                stats['legitimate_count'] = row[1]
                
        # Get high risk count
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE risk_level = 'HIGH'")
        stats['high_risk_count'] = cursor.fetchone()[0]
        
        # Get recent alerts count (unread)
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_read = 0")
        stats['recent_alerts_count'] = cursor.fetchone()[0]
        
        return stats
