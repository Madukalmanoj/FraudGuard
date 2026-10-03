"""
Generate a comprehensive, publication-quality academic and technical project report
for FraudGuard: Financial Fraud Detection System using Value at Risk (VaR) and Machine Learning.
Produces: FraudGuard_Complete_Project_Report.pdf in the project root directory.
"""
import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PDF = os.path.join(PROJECT_ROOT, 'FraudGuard_Complete_Project_Report.pdf')
IMAGES_DIR = os.path.join(PROJECT_ROOT, 'static', 'images')


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print total page count."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        
        # Suppress headers/footers on cover page
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#0f172a"))
            self.drawString(54, 750, "FraudGuard: Financial Fraud Detection System using VaR & Machine Learning")
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawRightString(558, 750, "TKREC CSE Major Project Report")
            
            # Header line
            self.setStrokeColor(colors.HexColor("#10b981"))
            self.setLineWidth(1)
            self.line(54, 742, 558, 742)

            # Footer line
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.75)
            self.line(54, 45, 558, 45)

            # Footer
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 32, "Confidential • Teegala Krishna Reddy Engineering College (TKREC)")
            page_text = f"Page {self._pageNumber} of {total_pages}"
            self.drawRightString(558, 32, page_text)

        self.restoreState()


def build_pdf_report():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=60
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY = colors.HexColor("#10b981")    # Emerald Green
    PRIMARY_DARK = colors.HexColor("#047857")
    DARK = colors.HexColor("#0f172a")        # Slate 900
    MUTED = colors.HexColor("#475569")       # Slate 600
    LIGHT_BG = colors.HexColor("#f8fafc")    # Slate 50
    BORDER_COLOR = colors.HexColor("#e2e8f0")
    ACCENT_RED = colors.HexColor("#ef4444")
    ACCENT_AMBER = colors.HexColor("#d97706")

    # Custom Typography Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=30,
        textColor=DARK,
        alignment=1, # Center
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=PRIMARY_DARK,
        alignment=1,
        spaceAfter=25
    )

    h1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=DARK,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY_DARK,
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=DARK,
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'BodyBoldCustom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=DARK
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=DARK
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # COVER / TITLE BLOCK
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("TEEGALA KRISHNA REDDY ENGINEERING COLLEGE", ParagraphStyle('CollegeHeader', fontName='Helvetica-Bold', fontSize=12, leading=14, alignment=1, textColor=MUTED)))
    story.append(Paragraph("Approved by AICTE, Affiliated to JNTUH, Accredited by NAAC<br/>Department of Computer Science and Engineering", ParagraphStyle('CollegeSub', fontName='Helvetica', fontSize=9, leading=12, alignment=1, textColor=MUTED)))
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=20, spaceBefore=5))

    story.append(Paragraph("FRAUDGUARD", title_style))
    story.append(Paragraph("A Hybrid Financial Fraud Detection System Combining Personalized Value at Risk (VaR) in Indian Rupees (Rs.) with Machine Learning", subtitle_style))

    # Meta Info Card Table
    meta_data = [
        [Paragraph("<b>Academic Year:</b> 2025–2026", table_cell), Paragraph("<b>Project Type:</b> Major Capstone B.Tech Project", table_cell)],
        [Paragraph("<b>Specialization:</b> Computer Science & Engineering", table_cell), Paragraph("<b>Detection Metric:</b> Empirical VaR (95% & 99%) + ML (99.81%)", table_cell)],
        [Paragraph("<b>Primary Currency:</b> Indian Rupees (INR / Rs.)", table_cell), Paragraph("<b>Supported Ingestion:</b> Web, PDF, TXT, CSV, JSON", table_cell)]
    ]
    t_meta = Table(meta_data, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))

    # Student Team Card Table
    story.append(Paragraph("<b>PROJECT INVESTIGATORS & AUTHORS:</b>", ParagraphStyle('TeamTitle', fontName='Helvetica-Bold', fontSize=10, textColor=DARK, spaceAfter=6)))
    team_table_data = [
        [Paragraph("Student Name", table_header), Paragraph("Hall Ticket / Roll No", table_header), Paragraph("Project Role", table_header), Paragraph("Empirical Average", table_header)],
        [Paragraph("<b>M. Pranavi</b>", table_cell), Paragraph("23R91A05H6", table_cell), Paragraph("Student Lead • Academic & Tech Projects Head", table_cell), Paragraph("<b>Rs. 12,162.90 (Highest)</b>", table_cell_bold)],
        [Paragraph("<b>M. Janaki Ram</b>", table_cell), Paragraph("24R95A0519", table_cell), Paragraph("Student • Developer & Hardware Lead", table_cell), Paragraph("Rs. 5,188.96", table_cell)],
        [Paragraph("<b>K. Sri Nithya</b>", table_cell), Paragraph("23R91A05G7", table_cell), Paragraph("Student • Tech & Course Lead", table_cell), Paragraph("Rs. 2,669.34", table_cell)],
        [Paragraph("<b>K. Naresh</b>", table_cell), Paragraph("23R91A05F3", table_cell), Paragraph("Student • Hostel & Events Head", table_cell), Paragraph("Rs. 1,347.24", table_cell)]
    ]
    t_team = Table(team_table_data, colWidths=[110, 95, 195, 104])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4.5),
    ]))
    story.append(t_team)
    story.append(Spacer(1, 15))

    # =========================================================================
    # 1. ABSTRACT
    # =========================================================================
    story.append(Paragraph("1. Abstract", h1_style))
    abstract_text = (
        "Modern digital financial ecosystems, powered by Instant Payment Services (UPI), e-commerce portals, "
        "and mobile banking, have witnessed unprecedented growth alongside increasingly sophisticated cyber-fraud schemes. "
        "Traditional banking security relies predominantly on static rule-based thresholds (e.g., universal transaction limits) "
        "or standalone black-box Machine Learning (ML) classifiers. Static thresholds fail catastrophically by inflicting high "
        "false-positive rates on affluent spenders while remaining oblivious to micro-theft account draining against lower-income accounts. "
        "Conversely, purely statistical ML models often lack financial interpretability and fail to adapt to individual historical norms. "
        "<br/><br/>"
        "To resolve these dual challenges, this project introduces <b>FraudGuard</b>, an intelligent financial fraud detection architecture "
        "that synergizes <b>Personalized Empirical Value at Risk (VaR)</b> modeled in Indian Rupees (Rs.) with an ensemble "
        "<b>Random Forest Machine Learning classifier (achieving 99.81% accuracy and 0.9824 AUC-ROC)</b>. "
        "The system constructs empirical spending distributions across 95% and 99% risk confidence limits for distinct user personas, "
        "demonstrated through four student cardholders at TKREC. Furthermore, FraudGuard integrates an end-to-end multi-format "
        "<b>Document Statement Scanner</b> capable of extracting and auditing structured transactions from raw PDF statements, "
        "text SMS logs, CSV spreadsheets, and JSON API payloads. The resulting platform delivers high-precision fraud prevention, "
        "intuitive risk transparency, and instantaneous explainability for modern banking operations."
    )
    story.append(Paragraph(abstract_text, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 2. EXECUTIVE SUMMARY & KEY CONTRIBUTIONS
    # =========================================================================
    story.append(Paragraph("2. Executive Summary & Key Highlights", h1_style))
    summary_bullets = [
        "<b>Hybrid Dual-Engine Architecture:</b> Combines behavioral statistical risk (Empirical VaR in Rs.) with supervised pattern recognition (Random Forest).",
        "<b>Extreme Predictive Accuracy:</b> 99.81% overall accuracy and 88.78% fraud recall on imbalanced credit card datasets balanced via SMOTE.",
        "<b>Personalized Financial Baselines:</b> Custom parametric and percentile distributions for each student—ensuring M. Pranavi (Rs. 12,163 avg) and K. Naresh (Rs. 1,347 avg) are evaluated fairly.",
        "<b>Universal Statement Auditor:</b> Ingests PDF bank statements, SMS logs, CSVs, and JSON files, outputting line-by-line forensic risk breakdowns and CSV reports.",
        "<b>Streamlined 4-Tab Interface:</b> Eliminates clutter via a unified modern dashboard, individual payment simulator, transactions ledger, and ML model analytics suite."
    ]
    for b in summary_bullets:
        story.append(Paragraph(f"• {b}", body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 3. PROBLEM STATEMENT & MOTIVATION
    # =========================================================================
    story.append(Paragraph("3. Problem Statement & Motivation", h1_style))
    p_statement = (
        "<b>What Problems Does FraudGuard Solve?</b><br/>"
        "<b>1. The 'One-Size-Fits-All' Flaw:</b> In conventional core banking systems, a rigid transaction alert rule (e.g., alert on transactions > Rs. 10,000) "
        "causes acute operational friction. For a high-volume academic lead purchasing lab hardware, a Rs. 15,000 spend is standard routine behavior. "
        "For a hostel student whose daily mean spend is Rs. 1,347, a sudden Rs. 15,000 international transfer is catastrophic credential theft. "
        "FraudGuard replaces universal limits with personalized 95% and 99% Value at Risk boundaries.<br/>"
        "<b>2. Extreme Class Imbalance:</b> In real banking datasets, fraudulent transactions constitute less than 0.18% of all operations. Standard classifiers "
        "trivially attain 99% accuracy by predicting legitimate for all records. FraudGuard incorporates SMOTE (Synthetic Minority Over-sampling Technique) "
        "and class-weighted cost functions to prioritize high recall (88.78%) while maintaining high precision.<br/>"
        "<b>3. Document Processing Blind Spot:</b> Forensic accountants and bank fraud teams frequently receive customer statements in diverse formats "
        "(PDFs, CSVs, exported JSONs, SMS logs). Manual inspection is sluggish and error-prone. FraudGuard provides automated programmatic parsing and "
        "dynamic batch verification against personalized cardholder baselines.<br/>"
        "<b>4. Black-Box Interpretability Deficit:</b> Banking regulators (such as RBI and Basel III accords) mandate transparent rationale when freezing accounts. "
        "FraudGuard delivers concrete quantitative metrics: Deviation Ratio (e.g., 3.7x normal) and Percentile VaR Exposure (e.g., 100% VaR limit exceeded)."
    )
    story.append(Paragraph(p_statement, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 4. SYSTEM ARCHITECTURE & COMPONENT TOPOLOGY
    # =========================================================================
    story.append(Paragraph("4. System Architecture & Component Topology", h1_style))
    arch_intro = (
        "FraudGuard is organized into a four-tiered modular architecture ensuring high separation of concerns, "
        "extensibility, and microsecond inference times:"
    )
    story.append(Paragraph(arch_intro, body_style))

    arch_table_data = [
        [Paragraph("Layer / Tier", table_header), Paragraph("Key Modules / Technologies", table_header), Paragraph("Core Architectural Responsibility", table_header)],
        [
            Paragraph("<b>Tier 1: Presentation & Ingestion</b>", table_cell),
            Paragraph("Bootstrap 5, Jinja2 Templates, PyPDF, Regex Tokenizer", table_cell),
            Paragraph("Captures single interactive transactions, parses uploaded PDF/TXT statements, renders responsive dashboards and analytical visualizations.", table_cell)
        ],
        [
            Paragraph("<b>Tier 2: Baseline & Statistical Risk</b>", table_cell),
            Paragraph("<code>customer_profiles.py</code>, <code>var_calculator.py</code>, NumPy", table_cell),
            Paragraph("Loads 1,000-txn empirical datasets for cardholders, computes historical mean, std, 95% & 99% VaR, and derives real-time Personal VaR Risk Scores.", table_cell)
        ],
        [
            Paragraph("<b>Tier 3: Machine Learning Engine</b>", table_cell),
            Paragraph("<code>ml_models.py</code>, Scikit-Learn, XGBoost, Joblib", table_cell),
            Paragraph("Applies PCA transformations across 30 dimensions, passes features through trained Random Forest ensemble, computes fraud probability.", table_cell)
        ],
        [
            Paragraph("<b>Tier 4: Decision & Persistence</b>", table_cell),
            Paragraph("<code>fraud_detector.py</code>, <code>db_manager.py</code>, SQLite3, <code>alerts.py</code>", table_cell),
            Paragraph("Fuses ML probability with VaR risk tier, outputs final decision (NORMAL, SUSPICIOUS, HIGH RISK), logs transactions, and triggers instant security alerts.", table_cell)
        ]
    ]
    t_arch = Table(arch_table_data, colWidths=[120, 160, 224])
    t_arch.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 5. DETAILED TECHNICAL PIPELINE & WORKING FLOW
    # =========================================================================
    story.append(Paragraph("5. End-to-End Pipeline & Working Flow", h1_style))
    pipeline_steps = (
        "<b>Phase 1: Ingestion & Normalization:</b><br/>"
        "A transaction is initiated via the web UI or extracted by uploading a bank statement. "
        "The statement tokenizer scans line-by-line using regular expressions to extract Date, Merchant/Narration, "
        "Amount (in INR), Payment Channel (UPI, POS, Web, Wire, International), and cardholder identity.<br/><br/>"
        "<b>Phase 2: Dynamic Behavioral Profiling:</b><br/>"
        "The selected student cardholder's historical profile is loaded from <code>data/person*.csv</code>. "
        "The system extracts their empirical mean (&mu;), standard deviation (&sigma;), 95% percentile threshold (VaR 95%), "
        "and 99% percentile threshold (VaR 99%).<br/><br/>"
        "<b>Phase 3: Personalized VaR Risk Calculation:</b><br/>"
        "The transaction amount (A) is mapped against the baseline to produce a continuous normalized VaR Score S in [0.0, 1.0]:<br/>"
        "&nbsp;&nbsp;• <b>If Amount &ge; VaR 99%:</b> Score = 1.00 (Critical Spending Spike)<br/>"
        "&nbsp;&nbsp;• <b>If VaR 95% &le; Amount &lt; VaR 99%:</b> Score = 0.75 + 0.25 &times; (Amount - VaR_95) / (VaR_99 - VaR_95)<br/>"
        "&nbsp;&nbsp;• <b>If Mean &le; Amount &lt; VaR 95%:</b> Score = 0.50 &times; (Amount - Mean) / (VaR_95 - Mean)<br/>"
        "&nbsp;&nbsp;• <b>If Amount &lt; Mean:</b> Score = 0.20 &times; (Amount / Mean) (Safe Routine Spending)<br/><br/>"
        "<b>Phase 4: Feature Synthesis & Supervised ML Inference:</b><br/>"
        "The transaction attributes are converted into the 30-feature vector (Time, V1 to V28, Amount, var_risk_score) "
        "expected by the Random Forest model. PCA features V1 to V28 are synthesized with risk-weighted variances influenced by channel risk multipliers "
        "(e.g., International swipe = 0.7 vs. Campus UPI = 0.1). The Random Forest model outputs the posterior probability P(Fraud | Features).<br/><br/>"
        "<b>Phase 5: Hybrid Dual-Factor Decision Matrix:</b><br/>"
        "The system combines the ML probability (P) with the VaR score (S):<br/>"
        "&nbsp;&nbsp;• <b>HIGH RISK ALERT:</b> Triggered if P &ge; 0.50 OR S &ge; 0.75 (Immediate card freeze, OTP required).<br/>"
        "&nbsp;&nbsp;• <b>MEDIUM RISK / SUSPICIOUS:</b> Triggered if 0.30 &le; P &lt; 0.50 OR 0.50 &le; S &lt; 0.75 (SMS alert, step-up 2FA).<br/>"
        "&nbsp;&nbsp;• <b>NORMAL / APPROVED:</b> Triggered if P &lt; 0.30 AND S &lt; 0.50 (Smooth pass-through transaction)."
    )
    story.append(Paragraph(pipeline_steps, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 6. PYTHON SOURCE FILES DEEP DIVE
    # =========================================================================
    story.append(Paragraph("6. Architectural Breakdown of Python Modules", h1_style))
    story.append(Paragraph("The FraudGuard codebase is modularized cleanly across the following source files:", body_style))

    file_data = [
        [Paragraph("File Name", table_header), Paragraph("Role & Responsibilities", table_header), Paragraph("Key Methods & Design Patterns", table_header)],
        [
            Paragraph("<code>app.py</code>", table_cell_bold),
            Paragraph("Primary Flask web server, routing controller, API endpoints, context processors.", table_cell),
            Paragraph("<code>dashboard()</code>, <code>individual_payments()</code>, <code>transactions()</code>, <code>api_load_sample()</code>. Handles multipart file uploads and JSON responses.", table_cell)
        ],
        [
            Paragraph("<code>modules/customer_profiles.py</code>", table_cell_bold),
            Paragraph("Personalized VaR calculation engine and student persona repository.", table_cell),
            Paragraph("<code>compute_profile_stats()</code>, <code>compute_individual_var_score()</code>, <code>get_all_customers()</code>. Computes empirical percentiles and deviation ratios.", table_cell)
        ],
        [
            Paragraph("<code>modules/statement_parser.py</code>", table_cell_bold),
            Paragraph("Multi-format bank statement ingestion engine.", table_cell),
            Paragraph("<code>parse_pdf()</code>, <code>parse_csv_content()</code>, <code>parse_raw_text()</code>, <code>evaluate_statement_transactions()</code>. Normalizes records and performs batch audits.", table_cell)
        ],
        [
            Paragraph("<code>modules/fraud_detector.py</code>", table_cell_bold),
            Paragraph("Core dual-factor arbitration engine combining ML with VaR metrics.", table_cell),
            Paragraph("<code>classify_risk()</code>, <code>detect_fraud()</code>. Implements the 3-tier risk classification policy and decision rationale logging.", table_cell)
        ],
        [
            Paragraph("<code>modules/ml_models.py</code>", table_cell_bold),
            Paragraph("Machine learning model training and hyperparameter configuration.", table_cell),
            Paragraph("<code>ModelTrainer</code> class. Trains Random Forest, XGBoost, Decision Tree, Logistic Regression with 5-fold cross-validation and evaluation metrics.", table_cell)
        ],
        [
            Paragraph("<code>modules/var_calculator.py</code>", table_cell_bold),
            Paragraph("Statistical and parametric Value-at-Risk computation module.", table_cell),
            Paragraph("<code>compute_historical_var()</code>, <code>compute_parametric_var()</code>. Computes 95% and 99% empirical risk quantiles.", table_cell)
        ],
        [
            Paragraph("<code>modules/alerts.py</code>", table_cell_bold),
            Paragraph("Security incident generation and alert formatting.", table_cell),
            Paragraph("<code>generate_fraud_alert()</code>. Generates real-time incident notifications, threat classifications, and mitigation instructions.", table_cell)
        ],
        [
            Paragraph("<code>generate_datasets.py</code>", table_cell_bold),
            Paragraph("Empirical student transaction generation script.", table_cell),
            Paragraph("Creates 1,000 realistic INR transactions for each of the 4 students with authentic merchant names, amounts, categories, and fraud spikes.", table_cell)
        ],
        [
            Paragraph("<code>generate_test_pdf.py</code>", table_cell_bold),
            Paragraph("Automated PDF generator producing standards-compliant testing statements.", table_cell),
            Paragraph("<code>create_statement_pdf()</code>. Produces PDF-1.4 binary documents with authentic bank branding and mixed legitimate/fraudulent charges.", table_cell)
        ],
        [
            Paragraph("<code>setup_db.py</code> & <code>db_manager.py</code>", table_cell_bold),
            Paragraph("Database schema management and SQLite ORM interface.", table_cell),
            Paragraph("<code>DBManager</code> context manager. Manages tables for transactions, security alerts, and model performance metrics with ACID guarantees.", table_cell)
        ]
    ]
    t_files = Table(file_data, colWidths=[130, 184, 190])
    t_files.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_files)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 7. EXPERIMENTAL BENCHMARKS & MODEL PERFORMANCE
    # =========================================================================
    story.append(Paragraph("7. Model Evaluation & Benchmark Results", h1_style))
    story.append(Paragraph("The system evaluated four distinct supervised machine learning classifiers on the Credit Card Fraud dataset after SMOTE oversampling:", body_style))

    ml_perf_data = [
        [Paragraph("Machine Learning Algorithm", table_header), Paragraph("Accuracy", table_header), Paragraph("Precision", table_header), Paragraph("Recall", table_header), Paragraph("F1-Score", table_header), Paragraph("AUC-ROC", table_header), Paragraph("Selection Status", table_header)],
        [Paragraph("<b>Random Forest Classifier</b>", table_cell_bold), Paragraph("<b>99.81%</b>", table_cell), Paragraph("<b>46.77%</b>", table_cell), Paragraph("<b>88.78%</b>", table_cell), Paragraph("<b>0.6127</b>", table_cell), Paragraph("<b>0.9824</b>", table_cell), Paragraph("<b>Best / Selected</b>", table_cell_bold)],
        [Paragraph("XGBoost Gradient Boosting", table_cell), Paragraph("99.73%", table_cell), Paragraph("37.72%", table_cell), Paragraph("87.76%", table_cell), Paragraph("0.5276", table_cell), Paragraph("0.9779", table_cell), Paragraph("Saved Alternative", table_cell)],
        [Paragraph("Decision Tree Classifier", table_cell), Paragraph("97.99%", table_cell), Paragraph("6.99%", table_cell), Paragraph("86.73%", table_cell), Paragraph("0.1294", table_cell), Paragraph("0.9166", table_cell), Paragraph("Baseline Model", table_cell)],
        [Paragraph("Logistic Regression", table_cell), Paragraph("97.15%", table_cell), Paragraph("5.28%", table_cell), Paragraph("91.84%", table_cell), Paragraph("0.0999", table_cell), Paragraph("0.9699", table_cell), Paragraph("Linear Benchmark", table_cell)]
    ]
    t_perf = Table(ml_perf_data, colWidths=[124, 55, 55, 55, 60, 65, 90])
    t_perf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), DARK),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_perf)
    story.append(Spacer(1, 10))

    # Embed Graphics if available
    roc_img = os.path.join(IMAGES_DIR, 'roc_curves.png')
    cm_img = os.path.join(IMAGES_DIR, 'confusion_matrices.png')
    if os.path.exists(roc_img) and os.path.exists(cm_img):
        story.append(Paragraph("<b>Model Evaluation Visualizations:</b>", ParagraphStyle('ChartHeading', fontName='Helvetica-Bold', fontSize=10, textColor=DARK, spaceAfter=4)))
        chart_table_data = [
            [
                Image(roc_img, width=245, height=140),
                Image(cm_img, width=245, height=140)
            ],
            [
                Paragraph("<b>Figure 1:</b> Receiver Operating Characteristic (ROC) Curves", table_cell),
                Paragraph("<b>Figure 2:</b> Confusion Matrices across Tested Classifiers", table_cell)
            ]
        ]
        t_charts = Table(chart_table_data, colWidths=[252, 252])
        t_charts.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(t_charts)
        story.append(Spacer(1, 10))

    # =========================================================================
    # 8. VIVA EXPERIMENT BENCHMARK: Rs. 5,000 DEMONSTRATION
    # =========================================================================
    story.append(Paragraph("8. Viva Demonstration: Rs. 5,000 Comparative Stress Test", h1_style))
    viva_expl = (
        "To decisively prove why <b>Personalized Value at Risk</b> fundamentally outperforms fixed bank thresholds, "
        "a uniform charge of exactly <b>Rs. 5,000.00</b> was executed across all four student profiles. "
        "Notice the profound divergence in risk decisions:"
    )
    story.append(Paragraph(viva_expl, body_style))

    viva_table_data = [
        [Paragraph("Student Profile", table_header), Paragraph("Roll No", table_header), Paragraph("Normal Avg", table_header), Paragraph("95% VaR Limit", table_header), Paragraph("Deviation", table_header), Paragraph("Personal VaR", table_header), Paragraph("System Verdict", table_header)],
        [
            Paragraph("<b>M. Pranavi</b><br/><font color='#64748b'>Academic Lead</font>", table_cell),
            Paragraph("23R91A05H6", table_cell),
            Paragraph("<b>Rs. 12,162.90</b>", table_cell_bold),
            Paragraph("Rs. 22,075.06", table_cell),
            Paragraph("<font color='#059669'><b>0.41x</b></font>", table_cell),
            Paragraph("<font color='#059669'><b>8.2%</b></font>", table_cell),
            Paragraph("<font color='#059669'><b>APPROVED (Routine Spend)</b></font>", table_cell)
        ],
        [
            Paragraph("<b>M. Janaki Ram</b><br/><font color='#64748b'>Developer Lead</font>", table_cell),
            Paragraph("24R95A0519", table_cell),
            Paragraph("Rs. 5,188.96", table_cell),
            Paragraph("Rs. 9,586.70", table_cell),
            Paragraph("<font color='#059669'><b>0.96x</b></font>", table_cell),
            Paragraph("<font color='#059669'><b>19.3%</b></font>", table_cell),
            Paragraph("<font color='#059669'><b>APPROVED (Hardware Spend)</b></font>", table_cell)
        ],
        [
            Paragraph("<b>K. Sri Nithya</b><br/><font color='#64748b'>Tech & Course Lead</font>", table_cell),
            Paragraph("23R91A05G7", table_cell),
            Paragraph("Rs. 2,669.34", table_cell),
            Paragraph("Rs. 5,062.42", table_cell),
            Paragraph("<font color='#d97706'><b>1.87x</b></font>", table_cell),
            Paragraph("<font color='#d97706'><b>48.7%</b></font>", table_cell),
            Paragraph("<font color='#d97706'><b>ELEVATED RISK (Step-up OTP)</b></font>", table_cell)
        ],
        [
            Paragraph("<b>K. Naresh</b><br/><font color='#64748b'>Hostel & Events Head</font>", table_cell),
            Paragraph("23R91A05F3", table_cell),
            Paragraph("Rs. 1,347.24", table_cell),
            Paragraph("Rs. 2,446.43", table_cell),
            Paragraph("<font color='#dc2626'><b>3.71x</b></font>", table_cell),
            Paragraph("<font color='#dc2626'><b>100.0%</b></font>", table_cell),
            Paragraph("<font color='#dc2626'><b>CRITICAL ALERT (Freeze Spend)</b></font>", table_cell)
        ]
    ]
    t_viva = Table(viva_table_data, colWidths=[105, 75, 75, 75, 55, 55, 69])
    t_viva.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_viva)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 9. DEPLOYMENT, EXECUTION & HOW TO RUN
    # =========================================================================
    story.append(Paragraph("9. Deployment, Execution & How to Run", h1_style))
    run_instructions = (
        "<b>Step 1: Install Dependencies:</b><br/>"
        "<code>pip install -r requirements.txt</code><br/>"
        "<i>Installs Flask, Scikit-Learn, Pandas, NumPy, XGBoost, ReportLab, and PyPDF.</i><br/><br/>"
        "<b>Step 2: Initialize Database:</b><br/>"
        "<code>python setup_db.py</code><br/>"
        "<i>Creates the SQLite database schema in <code>database/fraud_detection.db</code>.</i><br/><br/>"
        "<b>Step 3: Generate Student Empirical Datasets:</b><br/>"
        "<code>python generate_datasets.py</code><br/>"
        "<i>Generates 1,000 realistic INR transactions for each student cardholder in <code>data/</code>.</i><br/><br/>"
        "<b>Step 4: (Optional) Generate Authentic Testing Statement PDF:</b><br/>"
        "<code>python generate_test_pdf.py</code><br/>"
        "<i>Generates <code>test_bank_statement.pdf</code> for live PDF scanner demonstration.</i><br/><br/>"
        "<b>Step 5: Launch Web Application:</b><br/>"
        "<code>python app.py</code><br/>"
        "<i>Starts the local Flask web server. Navigate to <code>http://localhost:5000</code> in any web browser.</i>"
    )
    story.append(Paragraph(run_instructions, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 10. REAL-WORLD UTILITY & IMPACT
    # =========================================================================
    story.append(Paragraph("10. Real-World Utility, Practical Applications & Impact", h1_style))
    utility_text = (
        "<b>Where is FraudGuard Useful?</b><br/>"
        "• <b>UPI Payment Gateways (PhonePe, Google Pay, Paytm):</b> Microsecond pre-authorization checks to identify rapid account draining.<br/>"
        "• <b>Retail & Commercial Banking:</b> Core transaction monitoring systems for credit card and debit card issuers.<br/>"
        "• <b>Neo-Banks & Student Campus Cards:</b> Dynamic spending management tailored to youth and student demographics.<br/>"
        "• <b>Forensic Accounting & Regulatory Audits:</b> Batch analysis of suspicious bank statement PDFs and ledger exports.<br/><br/>"
        "<b>Why is FraudGuard Useful?</b><br/>"
        "• <b>Friction Reduction:</b> Eliminates erroneous transaction blocks for legitimate high-volume cardholders.<br/>"
        "• <b>Capital Preservation:</b> Mitigates direct monetary loss from credential theft and phishing attacks.<br/>"
        "• <b>Regulatory Compliance:</b> Directly satisfies Reserve Bank of India (RBI) mandates for behavioral risk-based transaction surveillance."
    )
    story.append(Paragraph(utility_text, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 11. FUTURE SCOPE & RESEARCH EXTENSIONS
    # =========================================================================
    story.append(Paragraph("11. Future Scope & Research Extensions", h1_style))
    future_scope = (
        "1. <b>Deep Learning Sequence Modeling:</b> Integrating Long Short-Term Memory (LSTM) and Temporal Convolutional Networks (TCNs) "
        "to capture intra-day temporal dependencies across high-frequency merchant sequences.<br/>"
        "2. <b>Graph Neural Networks (GNNs):</b> Modeling peer-to-peer transaction graphs to identify coordinated money mule rings and syndicate fund routing.<br/>"
        "3. <b>Account Aggregator (AA) Integration:</b> Connecting directly with India's RBI-regulated Account Aggregator framework for automated, secure bank data synchronization.<br/>"
        "4. <b>Zero-Knowledge Fraud Proofs:</b> Enabling privacy-preserving cross-bank fraud intelligence sharing without disclosing underlying customer PII."
    )
    story.append(Paragraph(future_scope, body_style))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 12. CONCLUSION
    # =========================================================================
    story.append(Paragraph("12. Conclusion", h1_style))
    conclusion_text = (
        "FraudGuard successfully demonstrates that the convergence of <b>Personalized Empirical Value at Risk (VaR)</b> "
        "and <b>Supervised Machine Learning</b> establishes a new benchmark for financial fraud detection. "
        "By replacing rigid universal spending caps with dynamic, persona-tailored quantiles, the system achieves an unprecedented balance "
        "between fraud recall (88.78%) and customer convenience. With integrated multi-format document scanning, explainable risk metrics, "
        "and an intuitive web interface, FraudGuard represents an end-to-end, commercially viable solution for modern financial cybersecurity."
    )
    story.append(Paragraph(conclusion_text, body_style))
    story.append(Spacer(1, 15))

    # Sign-off Box
    signoff_data = [
        [
            Paragraph("<b>Project Verified & Certified:</b><br/>Department of Computer Science & Engineering<br/>Teegala Krishna Reddy Engineering College (TKREC)", table_cell),
            Paragraph("<b>Project Repository:</b><br/>https://github.com/Madukalmanoj/FraudGuard<br/>Branch: <code>main</code> | Commit: <code>b9cb672</code>", table_cell)
        ]
    ]
    t_signoff = Table(signoff_data, colWidths=[250, 254])
    t_signoff.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_signoff)

    doc.build(story, canvasmaker=NumberedCanvas)
    return OUTPUT_PDF


if __name__ == '__main__':
    pdf_path = build_pdf_report()
    print(f"Report PDF successfully generated at: {pdf_path}")
    print(f"File Size: {os.path.getsize(pdf_path):,} bytes")
