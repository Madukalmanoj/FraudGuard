"""
Generate an authentic testing transaction statement PDF in the root working folder.
Designed for demonstrating the PDF Scanner and Fraud Detection engine in viva/presentations.
Configured for M. Pranavi (23R91A05H6) - Student Lead with Highest Average Spending (~₹12,163).
"""
import os
import sys

OUTPUT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_bank_statement.pdf')
SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample_statements')
SAMPLE_PRANAVI_PDF = os.path.join(SAMPLE_DIR, 'sample_statement_pranavi.pdf')


def create_statement_pdf(filepath: str):
    """
    Generate a valid, standards-compliant PDF-1.4 bank statement document
    with clear bank branding, student cardholder details, and mixed test transactions.
    """
    # Header & Statement Content lines
    lines = [
        "STATE BANK OF INDIA - ELECTRONIC ACCOUNT STATEMENT",
        "TKREC CAMPUS BRANCH, HYDERABAD - 501510",
        "================================================================================",
        "ACCOUNT DETAILS",
        "Cardholder Name : M. Pranavi                   Account No    : 23R91A05H6",
        "Student ID      : 23R91A05H6                   Account Type  : Student Lead Academic Plus",
        "Branch          : TKREC Hyderabad Campus       Currency      : Indian Rupees (INR)",
        "Statement Range : 01-Oct-2026 to 08-Oct-2026   Status        : Active",
        "================================================================================",
        "",
        "TRANSACTION DETAILS",
        "--------------------------------------------------------------------------------",
        "Date        Narration / Merchant Details                 Channel     Debit (INR)",
        "--------------------------------------------------------------------------------",
        "01-10-2026  Apple Store Hyderabad Campus Care            POS         Rs 8500.00",
        "01-10-2026  Reliance Digital Workstation Display         POS         Rs 14200.00",
        "02-10-2026  IEEE Research Conference Delegate Fee        NetBanking  Rs 6500.00",
        "02-10-2026  Croma Electronics Ergonomic Keyboard         POS         Rs 3400.00",
        "03-10-2026  TKREC Cloud & Lab Cluster Access             UPI         Rs 5800.00",
        "04-10-2026  Amazon AI Robotics Sensor Supplies           UPI         Rs 11250.00",
        "05-10-2026  Coursera edX MasterTrack Machine Learning    UPI         Rs 15900.00",
        "06-10-2026  Samsung SmartCafe Galaxy Tab Stylus          POS         Rs 9800.00",
        "07-10-2026  Oxford Springer Academic Journal Books       UPI         Rs 4650.00",
        "08-10-2026  Overseas Zurich Wire Transfer Anomaly        Intl        Rs 95000.00",
        "--------------------------------------------------------------------------------",
        "",
        "SUMMARY & FRAUD MONITORING NOTICE",
        "Total Debited Amount: Rs 175,000.00  | Total Transactions: 10",
        "Routine Spending Baseline: ~Rs 12,163.00 per transaction (95% VaR Limit: Rs 22,075.00)",
        "Note: Automated FraudGuard Engine monitors anomalous spending spikes and",
        "cross-border transactions using Personalized Value at Risk (VaR) & Machine Learning.",
        "================================================================================",
        "Generated via FraudGuard Banking Security System - TKREC CSE Department"
    ]

    # Build PDF stream
    # 72 points per inch, page size 612 x 792 (US Letter)
    stream_content = "BT\n/F1 10 Tf\n45 745 Td\n15 TL\n"
    for line in lines:
        safe_line = line.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')
        stream_content += f"({safe_line}) '\n"
    stream_content += "ET\n"

    stream_bytes = stream_content.encode('latin1')
    stream_len = len(stream_bytes)

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")

    offsets = []

    # 1 0 obj Catalog
    offsets.append(len(pdf))
    pdf.extend(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")

    # 2 0 obj Pages
    offsets.append(len(pdf))
    pdf.extend(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")

    # 3 0 obj Page
    offsets.append(len(pdf))
    pdf.extend(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n")

    # 4 0 obj Stream
    offsets.append(len(pdf))
    pdf.extend(f"4 0 obj\n<< /Length {stream_len} >>\nstream\n".encode('ascii'))
    pdf.extend(stream_bytes)
    pdf.extend(b"\nendstream\nendobj\n")

    # 5 0 obj Font (Standard Helvetica / Courier)
    offsets.append(len(pdf))
    pdf.extend(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj\n")

    # xref table
    xref_pos = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets) + 1}\n".encode('ascii'))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets:
        pdf.extend(f"{off:010d} 00000 n \n".encode('ascii'))

    pdf.extend(f"trailer\n<< /Size {len(offsets) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode('ascii'))

    with open(filepath, 'wb') as f:
        f.write(pdf)

    return filepath


if __name__ == '__main__':
    created_path = create_statement_pdf(OUTPUT_FILE)
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    create_statement_pdf(SAMPLE_PRANAVI_PDF)
    print(f"Testing PDF successfully created at: {created_path}")
    print(f"Sample PDF also updated at: {SAMPLE_PRANAVI_PDF}")
    print(f"File Size: {os.path.getsize(created_path)} bytes")
