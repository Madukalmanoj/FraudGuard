"""
Generate realistic transaction datasets for the 4 TKREC project students in Indian Rupees (₹)
and compute their personalized Value at Risk (VaR) statistics:
1. M.Pranavi     (23R91A05H6) - HIGHEST AVERAGE (~₹12,250)
2. M.Janaki Ram  (24R95A0519) - SECOND HIGHEST (~₹5,250)
3. K.Sri Nithya  (23R91A05G7) - THIRD (~₹2,720)
4. K.Naresh      (23R91A05F3) - FOURTH (~₹1,340)
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

np.random.seed(42)

def generate_student_pranavi(n=1000):
    """
    Student 1: M. Pranavi (23R91A05H6)
    - HIGHEST AVERAGE SPENDING of all students
    - Academic & Tech Projects Lead: ₹2,000 to ₹38,000 (Lab Equipment, Laptops, Tech Accessories, Semester Labs)
    - Average spending: ~₹12,250
    """
    amounts, merchants, categories, classes = [], [], [], []
    merchants_list = [
        ('Apple Store / Imagine Store Hyderabad', 'Tech Hardware & Laptops'),
        ('Reliance Digital MegaStore Hitec City', 'Electronics & Devices'),
        ('Croma Electronics Campus Store', 'Workstation Gear'),
        ('IEEE / ACM Research Conference Fee', 'Academic Research'),
        ('Amazon Project Lab Equipment & Kits', 'Project Supplies'),
        ('TKREC Semester Lab & Cloud Resources', 'University Fees'),
        ('Coursera / edX MasterTrack Certifications', 'Higher Education'),
        ('Samsung SmartCafé Hyderabad', 'Electronics')
    ]
    start_date = datetime.now() - timedelta(days=120)
    timestamps = [start_date + timedelta(minutes=int(x)) for x in np.sort(np.random.uniform(0, 120*24*60, n))]
    
    for i in range(n):
        is_fraud = np.random.rand() < 0.015
        if is_fraud:
            amt = np.random.uniform(85000, 250000)
            m, c = ('UNKNOWN_OVERSEAS_LUXURY_PAY', 'Suspicious International Wire')
            classes.append(1)
        else:
            amt = np.random.lognormal(mean=9.32, sigma=0.42)
            amt = min(max(amt, 2000.0), 38000.0)
            m, c = merchants_list[np.random.randint(0, len(merchants_list))]
            classes.append(0)
        amounts.append(round(amt, 2))
        merchants.append(m)
        categories.append(c)
        
    return pd.DataFrame({
        'Transaction_ID': [f'TXN_PRANAVI_{i+1:04d}' for i in range(n)],
        'Customer_ID': 'cust_pranavi',
        'Customer_Name': 'M. Pranavi',
        'Roll_No': '23R91A05H6',
        'Timestamp': [t.strftime('%Y-%m-%d %H:%M:%S') for t in timestamps],
        'Category': categories,
        'Merchant': merchants,
        'Amount_INR': amounts,
        'Channel': np.random.choice(['UPI_HDFC_Pay', 'Credit_Card', 'Debit_Card', 'NetBanking'], n, p=[0.40, 0.35, 0.15, 0.10]),
        'Class': classes
    })


def generate_student_janakiram(n=1000):
    """
    Student 4: M. Janaki Ram (24R95A0519)
    - Developer & Hardware Lead: ₹1,000 to ₹18,000 (Cloud hosting, Workstations, Dev Hardware)
    - Average spending: ~₹5,250
    """
    amounts, merchants, categories, classes = [], [], [], []
    merchants_list = [
        ('AWS / DigitalOcean Cloud Infrastructure', 'Cloud Infrastructure'),
        ('GitHub Enterprise & Copilot Annual', 'Developer Tools'),
        ('Robu.in Arduino & IoT Hardware Hub', 'Project Hardware'),
        ('Croma Electronics Cyberabad', 'Electronics'),
        ('Chai & Code Cafe Cyberabad', 'Food & Dining'),
        ('MakeMyTrip Outstation Hackathon Travel', 'Travel'),
        ('Lenovo Pro Workstation Accessories', 'Hardware'),
        ('Robotics India Component Supplies', 'Robotics Hardware')
    ]
    start_date = datetime.now() - timedelta(days=120)
    timestamps = [start_date + timedelta(minutes=int(x)) for x in np.sort(np.random.uniform(0, 120*24*60, n))]
    
    for i in range(n):
        is_fraud = np.random.rand() < 0.015
        if is_fraud:
            amt = np.random.uniform(60000, 160000)
            m, c = ('UNKNOWN_FOREIGN_WIRE_TRANSFER', 'Suspicious Wire')
            classes.append(1)
        else:
            amt = np.random.lognormal(mean=8.45, sigma=0.42)
            amt = min(max(amt, 1000.0), 18000.0)
            m, c = merchants_list[np.random.randint(0, len(merchants_list))]
            classes.append(0)
        amounts.append(round(amt, 2))
        merchants.append(m)
        categories.append(c)
        
    return pd.DataFrame({
        'Transaction_ID': [f'TXN_JANAKIRAM_{i+1:04d}' for i in range(n)],
        'Customer_ID': 'cust_janakiram',
        'Customer_Name': 'M. Janaki Ram',
        'Roll_No': '24R95A0519',
        'Timestamp': [t.strftime('%Y-%m-%d %H:%M:%S') for t in timestamps],
        'Category': categories,
        'Merchant': merchants,
        'Amount_INR': amounts,
        'Channel': np.random.choice(['Credit_Card', 'UPI_GPay', 'NetBanking', 'Debit_Card'], n, p=[0.45, 0.35, 0.15, 0.05]),
        'Class': classes
    })


def generate_student_srinithya(n=1000):
    """
    Student 2: K. Sri Nithya (23R91A05G7)
    - Tech & Course Lead: ₹500 to ₹9,000 (Certifications, Subscriptions, Devices, Dining)
    - Average spending: ~₹2,720
    """
    amounts, merchants, categories, classes = [], [], [], []
    merchants_list = [
        ('Coursera / Udemy Deep Learning Courses', 'Education Tech'),
        ('Amazon Kindle & Academic Devices', 'Electronics'),
        ('Uber Premier Rides Hyderabad', 'Transit'),
        ('Swiggy / Zomato Gourmet Diners', 'Dining'),
        ('Spotify & Adobe Creative Cloud Subscriptions', 'Entertainment & Software'),
        ('Reliance Digital Tech Accessories', 'Electronics'),
        ('Coffee Day Hitec City Tech Hub', 'Dining'),
        ('BookMyShow International Concerts', 'Entertainment')
    ]
    start_date = datetime.now() - timedelta(days=120)
    timestamps = [start_date + timedelta(minutes=int(x)) for x in np.sort(np.random.uniform(0, 120*24*60, n))]
    
    for i in range(n):
        is_fraud = np.random.rand() < 0.015
        if is_fraud:
            amt = np.random.uniform(30000, 80000)
            m, c = ('OVERSEAS_GAMING_SERVER_HK', 'Suspicious Web')
            classes.append(1)
        else:
            amt = np.random.lognormal(mean=7.82, sigma=0.42)
            amt = min(max(amt, 500.0), 9000.0)
            m, c = merchants_list[np.random.randint(0, len(merchants_list))]
            classes.append(0)
        amounts.append(round(amt, 2))
        merchants.append(m)
        categories.append(c)
        
    return pd.DataFrame({
        'Transaction_ID': [f'TXN_SRINITHYA_{i+1:04d}' for i in range(n)],
        'Customer_ID': 'cust_srinithya',
        'Customer_Name': 'K. Sri Nithya',
        'Roll_No': '23R91A05G7',
        'Timestamp': [t.strftime('%Y-%m-%d %H:%M:%S') for t in timestamps],
        'Category': categories,
        'Merchant': merchants,
        'Amount_INR': amounts,
        'Channel': np.random.choice(['UPI_GPay', 'Credit_Card', 'Debit_Card', 'NetBanking'], n, p=[0.55, 0.25, 0.15, 0.05]),
        'Class': classes
    })


def generate_student_naresh(n=1000):
    """
    Student 3: K. Naresh (23R91A05F3)
    - Hostel & Events Head: ₹250 to ₹4,800 (Hostel mess catering, sports, bus pass, events)
    - Average spending: ~₹1,340
    """
    amounts, merchants, categories, classes = [], [], [], []
    merchants_list = [
        ('College Hostel Mess & Catering Hub', 'Mess & Meals'),
        ('Decathlon Sports India Hyderabad', 'Sports & Fitness'),
        ('TSRTC Express Bus Pass & Travel', 'Transit'),
        ('Jio 5G Annual Fiber & Recharge', 'Utilities'),
        ('Prasad IMAX Hyderabad Multiplex', 'Entertainment'),
        ('Apollo Pharmacy & Healthcare Store', 'Healthcare'),
        ('Zepto 10-Min Supermarket Supplies', 'Groceries'),
        ('College Fest Stage & Sound Supplies', 'College Activities')
    ]
    start_date = datetime.now() - timedelta(days=120)
    timestamps = [start_date + timedelta(minutes=int(x)) for x in np.sort(np.random.uniform(0, 120*24*60, n))]
    
    for i in range(n):
        is_fraud = np.random.rand() < 0.015
        if is_fraud:
            amt = np.random.uniform(18000, 50000)
            m, c = ('CRYPTO_CASINO_TRX_MALTA', 'Suspicious Wire')
            classes.append(1)
        else:
            amt = np.random.lognormal(mean=7.12, sigma=0.42)
            amt = min(max(amt, 250.0), 4800.0)
            m, c = merchants_list[np.random.randint(0, len(merchants_list))]
            classes.append(0)
        amounts.append(round(amt, 2))
        merchants.append(m)
        categories.append(c)
        
    return pd.DataFrame({
        'Transaction_ID': [f'TXN_NARESH_{i+1:04d}' for i in range(n)],
        'Customer_ID': 'cust_naresh',
        'Customer_Name': 'K. Naresh',
        'Roll_No': '23R91A05F3',
        'Timestamp': [t.strftime('%Y-%m-%d %H:%M:%S') for t in timestamps],
        'Category': categories,
        'Merchant': merchants,
        'Amount_INR': amounts,
        'Channel': np.random.choice(['UPI_PhonePe', 'UPI_Paytm', 'Debit_Card', 'ATM_Cash'], n, p=[0.50, 0.30, 0.15, 0.05]),
        'Class': classes
    })


def generate_all_datasets():
    df1 = generate_student_pranavi()
    df2 = generate_student_srinithya()
    df3 = generate_student_naresh()
    df4 = generate_student_janakiram()
    
    df1.to_csv(os.path.join(DATA_DIR, 'person1_pranavi.csv'), index=False)
    df2.to_csv(os.path.join(DATA_DIR, 'person2_srinithya.csv'), index=False)
    df3.to_csv(os.path.join(DATA_DIR, 'person3_naresh.csv'), index=False)
    df4.to_csv(os.path.join(DATA_DIR, 'person4_janakiram.csv'), index=False)
    
    print("Generated 4 student datasets successfully:")
    print(f"  1. M. Pranavi (23R91A05H6)   - Mean: Rs {df1[df1['Class']==0]['Amount_INR'].mean():,.2f} (HIGHEST)")
    print(f"  2. M. Janaki Ram (24R95A0519) - Mean: Rs {df4[df4['Class']==0]['Amount_INR'].mean():,.2f}")
    print(f"  3. K. Sri Nithya (23R91A05G7) - Mean: Rs {df2[df2['Class']==0]['Amount_INR'].mean():,.2f}")
    print(f"  4. K. Naresh (23R91A05F3)     - Mean: Rs {df3[df3['Class']==0]['Amount_INR'].mean():,.2f}")

if __name__ == '__main__':
    generate_all_datasets()
