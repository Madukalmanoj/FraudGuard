"""
Generate sample statement documents for testing and presentation demonstration.
Updated to match the higher student spending baselines:
1. sample_statement_pranavi.pdf   - M. Pranavi (Highest Avg ~₹12,163)
2. sample_statement_janakiram.csv - M. Janaki Ram (Avg ~₹5,189)
3. sample_statement_srinithya.json - K. Sri Nithya (Avg ~₹2,669)
4. sample_statement_naresh.txt    - K. Naresh (Avg ~₹1,347)
"""
import os
from generate_test_pdf import create_statement_pdf

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_statements')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. PDF Statement for M. Pranavi (Highest average spender)
pdf_path = os.path.join(OUTPUT_DIR, 'sample_statement_pranavi.pdf')
create_statement_pdf(pdf_path)
print("Generated PDF:", pdf_path)

# 2. Text / Log Statement for K. Naresh (Hostel & Events Head, Avg ~₹1,347)
naresh_txt_lines = """STATE BANK E-ALERT NOTIFICATION LOG
Cardholder: K. Naresh (23R91A05F3) - TKREC Hostel & Events Head
Currency: Indian Rupees (INR)

2026-10-01 | College Hostel Catering & Mess Pass | Rs 1450.00 | UPI
2026-10-01 | Decathlon Sports Gear & Fitness Band | Rs 1200.00 | POS
2026-10-02 | TSRTC Express Monthly Pass Renewal | Rs 950.00 | UPI
2026-10-02 | College Fest Sound System Rental Supplies | Rs 1800.00 | UPI
2026-10-03 | Zepto Hostel Monthly Provisions & Supplies | Rs 1150.00 | POS
2026-10-04 | Overseas Crypto Wire Transaction Malta | Rs 28000.00 | International
"""
txt_path = os.path.join(OUTPUT_DIR, 'sample_statement_naresh.txt')
with open(txt_path, 'w', encoding='utf-8') as f:
    f.write(naresh_txt_lines)
print("Generated TXT:", txt_path)

# 3. CSV Statement for M. Janaki Ram (Developer / Hardware Lead, Avg ~₹5,189)
janakiram_csv = """Date,Merchant,Amount_INR,Channel,Location,Student
2026-10-01,Robu.in Embedded Microcontrollers & IoT Kit,4850.00,pos_payment,Hyderabad IN,M. Janaki Ram (24R95A0519)
2026-10-02,AWS Cloud Hosting Dedicated Server,5200.00,online_purchase,Hyderabad IN,M. Janaki Ram (24R95A0519)
2026-10-03,GitHub Enterprise & Copilot Annual Team,4600.00,online_purchase,Hyderabad IN,M. Janaki Ram (24R95A0519)
2026-10-04,Robotics Sensors & Workstation Hub,6150.00,pos_payment,Hyderabad IN,M. Janaki Ram (24R95A0519)
2026-10-05,Electronics Components High-Speed Kit,3950.00,pos_payment,Hyderabad IN,M. Janaki Ram (24R95A0519)
"""
csv_path = os.path.join(OUTPUT_DIR, 'sample_statement_janakiram.csv')
with open(csv_path, 'w', encoding='utf-8') as f:
    f.write(janakiram_csv)
print("Generated CSV:", csv_path)

# 4. JSON API Statement for K. Sri Nithya (Tech & Course Lead, Avg ~₹2,669)
srinithya_json = """[
  {
    "date": "2026-10-01",
    "merchant": "Coursera Deep Learning & AI Specialization",
    "amount": 2850.00,
    "type": "online_purchase",
    "location": "Hyderabad, IN",
    "customer_id": "cust_srinithya"
  },
  {
    "date": "2026-10-02",
    "merchant": "Amazon Kindle Academic Device Accessories",
    "amount": 2100.00,
    "type": "pos_payment",
    "location": "Hyderabad, IN",
    "customer_id": "cust_srinithya"
  },
  {
    "date": "2026-10-03",
    "merchant": "Adobe Creative Cloud Annual Student Plan",
    "amount": 3400.00,
    "type": "online_purchase",
    "location": "Hyderabad, IN",
    "customer_id": "cust_srinithya"
  },
  {
    "date": "2026-10-04",
    "merchant": "Swiggy Gourmet Dinner & Coffee Day Hitec",
    "amount": 1950.00,
    "type": "online_purchase",
    "location": "Hyderabad, IN",
    "customer_id": "cust_srinithya"
  }
]"""
json_path = os.path.join(OUTPUT_DIR, 'sample_statement_srinithya.json')
with open(json_path, 'w', encoding='utf-8') as f:
    f.write(srinithya_json)
print("Generated JSON:", json_path)
