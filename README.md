# FraudGuard: Financial Fraud Detection System using Value at Risk (VaR) & Machine Learning

A financial security and fraud detection web application that integrates **Personalized Value at Risk (VaR)** with **Machine Learning (Random Forest - 99.81% Accuracy)** to identify anomalous payment spikes and fraudulent transactions in Indian Rupees (`₹`).

Developed for **Teegala Krishna Reddy Engineering College (TKREC)**, Department of Computer Science and Engineering.

---

## 👥 Project Team

| Student Name | Roll Number | Role | Empirical Avg Spend |
| :--- | :--- | :--- | :---: |
| **M. Pranavi** | `23R91A05H6` | Student Lead • Academic & Tech Projects Head | **₹12,162.90** *(Highest)* |
| **M. Janaki Ram** | `24R95A0519` | Student • Developer & Hardware Lead | **₹5,188.96** |
| **K. Sri Nithya** | `23R91A05G7` | Student • Tech & Course Lead | **₹2,669.34** |
| **K. Naresh** | `23R91A05F3` | Student • Hostel & Events Head | **₹1,347.24** |

---

## 🌟 Key Features

1. **Personalized Value-at-Risk (VaR) in Indian Rupees (`₹`)**:
   - Rather than static universal spending limits, the system dynamically models 95% and 99% empirical VaR thresholds tailored to each cardholder's historical spending profile.
   - Accurately detects spending spikes, channel abnormalities, and high-risk deviations.

2. **Bank Statement & PDF Scanner**:
   - Directly upload electronic bank statements (`.pdf`, `.txt`, `.csv`, `.json`) or paste raw SMS transaction alerts.
   - Batch audits multi-record statements against personal student baselines and flags anomalous transactions with individual risk breakdowns.
   - Includes ready-to-test bank statement: `test_bank_statement.pdf`.

3. **High-Precision ML Classification (99.81% Accuracy)**:
   - Trained and benchmarked on real financial transaction patterns:
     - **Random Forest**: 99.81% Accuracy, 0.9824 AUC-ROC (Primary Model)
     - **XGBoost**: 99.73% Accuracy, 0.9779 AUC-ROC
     - **Decision Tree**: 97.99% Accuracy
     - **Logistic Regression**: 97.15% Accuracy

4. **Clean, Streamlined 4-Tab Interface**:
   - **Dashboard (`/`)**: High-level KPI counters, risk distribution donut chart, system operational status, and recent security feed.
   - **Individual Payments & Statement Auditor (`/individual_payments`)**: Student profile selector, single payment simulator, statement auditor, 1-click quick scenarios, and comparative viva benchmark table.
   - **Transactions & Alerts (`/transactions`)**: Searchable audit ledger with quick risk filtering pills (`All`, `🚨 Flagged Alerts`, `High Risk`, `Medium Risk`, `Safe`).
   - **Model Analytics (`/analytics`)**: Detailed ML evaluation with confusion matrices and comparative metrics.

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.9+ installed
- Pip package manager

### 2. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/Madukalmanoj/FraudGuard.git
cd FraudGuard
pip install -r requirements.txt
```

### 3. Initialize Database & Student Datasets
```bash
# Set up SQLite database
python setup_db.py

# Generate empirical student transaction profiles
python generate_datasets.py

# (Optional) Generate testing statement PDF
python generate_test_pdf.py
```

### 4. Run the Web Application
```bash
python app.py
```
Open your browser and navigate to: **`http://localhost:5000`**

---

## 🔬 Comparative Benchmark Experiment

A uniform ₹5,000 transaction evaluated across all 4 students demonstrates how Personalized VaR adapts dynamically:

| Cardholder | Roll No | Normal Avg | 95% VaR Limit | Charged | Deviation | Personal VaR | System Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **M. Pranavi** | `23R91A05H6` | ₹12,162.90 | ₹22,075.06 | ₹5,000 | 0.41x | 8.2% | ✅ **APPROVED (Routine Academic Spend)** |
| **M. Janaki Ram** | `24R95A0519` | ₹5,188.96 | ₹9,586.70 | ₹5,000 | 0.96x | 19.3% | ✅ **APPROVED (Routine Hardware Spend)** |
| **K. Sri Nithya** | `23R91A05G7` | ₹2,669.34 | ₹5,062.42 | ₹5,000 | 1.87x | 48.7% | ⚠️ **ELEVATED (Step-up 2FA / OTP)** |
| **K. Naresh** | `23R91A05F3` | ₹1,347.24 | ₹2,446.43 | ₹5,000 | 3.71x | 100.0% | 🚨 **CRITICAL ALERT (Freeze / Hold)** |

---

## 📂 Project Structure

```
FraudGuard/
├── app.py                      # Main Flask application and API routing
├── config.py                   # System configuration and model paths
├── requirements.txt            # Python dependencies
├── setup_db.py                 # Database initialization script
├── train.py                    # Model training pipeline
├── generate_datasets.py        # Generates student empirical datasets
├── generate_test_pdf.py        # Generates test bank statement PDF
├── test_bank_statement.pdf     # Sample bank statement document
├── data/                       # Student empirical transaction CSVs
├── database/                   # SQLite schema and DB manager
├── models/                     # Saved ML joblib models and scalers
├── modules/
│   ├── customer_profiles.py    # Personalized VaR calculations
│   ├── statement_parser.py     # PDF, TXT, CSV, JSON statement extraction
│   ├── fraud_detector.py       # Hybrid VaR + ML detection engine
│   ├── ml_models.py            # Model definitions and trainers
│   ├── var_calculator.py       # Statistical Value-at-Risk engine
│   └── alerts.py               # Security alert generator
├── sample_statements/          # Demo statements for each student
├── static/                     # CSS stylesheets and UI assets
└── templates/                  # Responsive Bootstrap 5 HTML templates
```

---

## 📜 License
Developed for academic submission and demonstration at TKREC.
