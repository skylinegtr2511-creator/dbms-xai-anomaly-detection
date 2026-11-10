# 🛡️ Hybrid AI Threat Detection & Database Firewall (DBMS-XAI)

An intelligent hybrid threat detection system featuring:
1. **Active AI Database Firewall (SQL Injection Protection):** Intercepts SQL queries, scans them using a Deep Learning Convolutional Neural Network (CNN) with multi-scale kernels, provides Explainable AI (XAI) token-level attribution using SHAP, and safely routes approved queries to a live Oracle Database.
2. **Infrastructure Server Log Anomaly Scanner:** Monitors supercomputer / enterprise server logs (BGL format) using an LSTM recurrent neural network to detect kernel panics, TLB errors, and system faults in real time.

---

## ✨ Features

- **Active SQL Injection Firewall:**
  - Evaluates incoming SQL queries via a trained `SQLCNN` model (or `SQLLSTM`) to detect tautologies, UNION-based exfiltration, piggy-backed queries, and syntax evasion attacks.
  - Sub-millisecond neural inference with tokenization designed for database grammars.
- **Explainable AI (SHAP):**
  - Model-agnostic `KernelExplainer` visualizes exact tokens, quotes, comments, or clauses that triggered malicious classifications.
  - Safe HTML rendering with automated XSS escaping and color-coded impact scores (Red = Malicious, Green = Safe indicator).
- **Live Oracle Database Integration:**
  - Active execution gateway executing verified queries directly on an Oracle 11g/12c/19c/21c/23ai database.
  - Supports Oracle Thick Mode (via Oracle Instant Client) with automatic environment variable configuration and fallback to Thin Mode.
- **BGL Server Log Anomaly Scanner:**
  - Deep Learning LSTM network parsing and classifying Blue Gene/L system logs.
  - Real-time classification of operational events vs. critical hardware/kernel failures.
- **Interactive Streamlit Dashboard:**
  - Multi-tab web interface featuring both the Active SQL Firewall and Server Log Scanner.

---

## 📋 Prerequisites

- **Python 3.9+** (Python 3.10 recommended)
- **Git**
- **Oracle Database** (Oracle XE 11g/19c/21c or Enterprise Edition, optional for live DB queries)
- **Oracle Instant Client** (required if connecting to Oracle 11g in Thick mode)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/dbms-xai-anomaly-detection.git
cd dbms-xai-anomaly-detection
```

### 2. Set Up the Python Environment
Using Conda:
```bash
conda create -n dbms-xai python=3.10 -y
conda activate dbms-xai
```

Or using Python venv:
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Oracle Instant Client Setup (Optional for Live DB Execution)
If executing live queries against Oracle 11g (which requires Thick mode), download the [Oracle Instant Client Basic Package](https://www.oracle.com/database/technologies/instant-client/downloads.html) and extract it to a folder (e.g. `C:\oracle\instantclient_21_12`).

Set the environment variable:
```powershell
# Windows PowerShell:
$env:ORACLE_CLIENT_DIR = "C:\oracle\instantclient_21_12"

# Linux / Bash:
export ORACLE_CLIENT_DIR="/opt/oracle/instantclient_21_12"
```

If not set, `src/utils/db_helpers.py` will fall back to default locations or standard thin mode.

---

## 📁 Project Structure

```text
├── app.py                                # Main Streamlit dashboard (Tabs 1 & 2)
├── requirements.txt                      # Project dependencies
├── .gitignore                            # Git exclusion rules (keeps processed vocabs)
├── README.md                             # Documentation
│
├── data/
│   ├── raw/                              # Raw datasets (BGL.log, Modified_SQL_Dataset.csv)
│   └── processed/
│       ├── sql_word2idx.json             # Vocabulary index for SQL models
│       ├── log_word2idx.json             # Vocabulary index for Log LSTM
│       └── shap_background.npy           # Background reference samples for SHAP
│
├── notebooks/
│   ├── 01_sql_preprocessing.ipynb       # SQL dataset preparation, vocab building & training
│   ├── 02_bgl_preprocessing.ipynb       # BGL log parsing, leakage-free windowing & artifact export
│   ├── 03_model_prototyping.ipynb        # Model architecture comparison (SQLCNN vs SQLLSTM)
│   ├── 04_evaluation.ipynb               # SQL CNN test set evaluation and confusion matrix
│   ├── 05_xai_implementation.ipynb      # SHAP explainability setup and token attribution
│   ├── 06_log_anomaly_detection.ipynb    # End-to-end BGL LSTM training, evaluation & inference
│   ├── SQL_CNN_best.pth                  # Trained weights for SQL CNN classifier
│   ├── SQL_LSTM_best.pth                 # Trained weights for SQL LSTM classifier
│   └── log_lstm_best.pth                 # Trained weights for BGL Log LSTM classifier
│
└── src/
    ├── __init__.py
    ├── models/
    │   ├── __init__.py
    │   ├── sql_models.py                 # SQLCNN and SQLLSTM PyTorch definitions
    │   └── log_models.py                 # LogAnomalyLSTM PyTorch definition
    ├── utils/
    │   ├── __init__.py
    │   ├── data_helpers.py               # SQL tokenization, vocabulary, and padding helpers
    │   └── db_helpers.py                 # Oracle connection, Thick mode init & safe execution
    └── xai/
        ├── __init__.py
        ├── xai_helpers.py                # SHAP KernelExplainer caching and attribution scoring
        └── visualizations.py             # HTML/CSS generation with XSS escaping for text highlights
```

---

## 💻 How to Run the Dashboard

1. Activate your Python environment:
   ```bash
   conda activate dbms-xai
   ```
2. Start the Streamlit application from the project root:
   ```bash
   streamlit run app.py
   ```
3. Open your browser at `http://localhost:8501`.

### Tab 1: Active SQL Firewall
- **Test Safe Query:**
  ```sql
  SELECT employee_id, first_name, salary FROM employees WHERE department_id = 10
  ```
  *(Marked SAFE; optionally executed on Oracle DB if credentials are entered in the sidebar)*.
- **Test Malicious Query:**
  ```sql
  SELECT * FROM users WHERE username = 'admin' OR 1=1 --
  ```
  *(BLOCKED by AI Firewall; SHAP visual explanation highlights `=` and `--` syntax)*.

### Tab 2: Server Log Monitor
- **Test Normal Log:**
  ```text
  RAS KERNEL INFO instruction cache parity error corrected
  ```
  *(Result: NORMAL KERNEL EVENT)*.
- **Test Critical Failure Log:**
  ```text
  RAS KERNEL FATAL data TLB error interrupt
  ```
  *(Result: CRITICAL ANOMALY DETECTED)*.
