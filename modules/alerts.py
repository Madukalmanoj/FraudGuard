"""
Alerts module for generating and managing fraud alerts.
"""
from datetime import datetime

class AlertManager:
    """Manages fraud and risk alerts."""
    
    @staticmethod
    def generate_fraud_alert(transaction_id, risk_level, fraud_probability, amount):
        """
        Generate alert data for a high-risk or fraudulent transaction.
        
        Args:
            transaction_id (str): ID of the transaction.
            risk_level (str): Assessed risk level (e.g., HIGH).
            fraud_probability (float): Probability of fraud (0 to 1).
            amount (float): Transaction amount.
            
        Returns:
            dict: Alert data.
        """
        return {
            'transaction_id': transaction_id,
            'alert_type': f"{risk_level}_RISK_FRAUD",
            'message': AlertManager.format_alert_message(risk_level, fraud_probability, amount),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @staticmethod
    def format_alert_message(risk_level, fraud_probability, amount):
        """
        Format a human-readable alert message.
        
        Args:
            risk_level (str): Assessed risk level.
            fraud_probability (float): Probability of fraud.
            amount (float): Transaction amount.
            
        Returns:
            str: Alert message.
        """
        prob_percent = round(fraud_probability * 100, 2)
        return f"Suspicious transaction detected! Risk Level: {risk_level}, Fraud Probability: {prob_percent}%, Amount: ₹{amount:,.2f}."

    @staticmethod
    def get_risk_summary(db_manager):
        """
        Return summary statistics by risk level from the database.
        
        Args:
            db_manager (DBManager): Initialized database manager.
            
        Returns:
            dict: Summary statistics.
        """
        stats = {
            'HIGH': 0,
            'MEDIUM': 0,
            'LOW': 0,
            'total_fraud': 0,
            'avg_risk_score': 0.0
        }
        
        if not db_manager.conn:
            return stats
            
        cursor = db_manager.conn.cursor()
        
        # Risk level counts
        cursor.execute("SELECT risk_level, COUNT(*) FROM transactions GROUP BY risk_level")
        for row in cursor.fetchall():
            if row[0] in stats:
                stats[row[0]] = row[1]
                
        # Fraud rate
        cursor.execute("SELECT COUNT(*) FROM transactions WHERE ml_prediction = 1")
        fraud_count = cursor.fetchone()
        if fraud_count:
            stats['total_fraud'] = fraud_count[0]
            
        # Avg risk score (VaR)
        cursor.execute("SELECT AVG(var_risk_score) FROM transactions")
        avg_score = cursor.fetchone()
        if avg_score and avg_score[0] is not None:
            stats['avg_risk_score'] = round(avg_score[0], 4)
            
        return stats

    @staticmethod
    def get_recent_alerts(db_manager, limit=20):
        """
        Get latest alerts from the database.
        
        Args:
            db_manager (DBManager): Initialized database manager.
            limit (int): Maximum number of alerts.
            
        Returns:
            list: List of alerts.
        """
        if not db_manager.conn:
            return []
            
        query = "SELECT * FROM alerts ORDER BY created_at DESC LIMIT ?"
        cursor = db_manager.conn.cursor()
        cursor.execute(query, (limit,))
        return [dict(row) for row in cursor.fetchall()]
