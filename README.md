# 🛡️ Active AI Firewall & XAI Dashboard

An Intelligent Database Firewall that intercepts SQL queries, scans them for malicious injection attacks using a PyTorch-based Convolutional Neural Network (CNN), and provides Explainable AI (XAI) insights using SHAP. Safe queries are actively routed and executed on a live Oracle Database.

## ✨ Features
* **Deep Learning Security Scan:** Evaluates incoming SQL queries via a trained CNN to detect syntax anomalies and classic injection attacks (e.g., Tautologies, UNION-based exfiltration, Piggy-backed queries).
* **Explainable AI (SHAP):** Visually highlights the exact words and characters in a blocked query that triggered the AI's malicious classification.
* **Live Oracle Integration:** Acts as an active gateway, executing validated queries directly against an Oracle 11g/12c+ database and displaying the results.
* **Streamlit Dashboard:** A sleek, user-friendly web interface for real-time monitoring and query execution.

---

## 📋 Prerequisites
Before you begin, ensure you have the following installed:
* **Python 3.8+** (Anaconda recommended)
* **Git**
* **Oracle Database** (e.g., Oracle Express Edition 11g or newer)

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/your-repo-name.git
cd your-repo-name
```

### 2. Set Up the Python Environment
It is highly recommended to use a Conda environment to manage PyTorch and other dependencies.
```bash
conda create -n dbms-xai python=3.9 -y
conda activate dbms-xai
```

Install the required Python packages:
```bash
pip install torch numpy pandas scikit-learn streamlit shap oracledb
```

### 3. Oracle Instant Client Setup (Required for Oracle 11g)
Because the `python-oracledb` library's default "Thin mode" does not support Oracle 11g, you must configure it to use "Thick mode" by installing the Oracle Instant Client.

1. **Download:** Go to the [Oracle Instant Client for Windows 64-bit download page](https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html).
2. **Select Package:** Download the **Basic Package** (ZIP file).
3. **Extract:** Create a folder on your drive (e.g., `C:\oracle` or `D:\oracle`) and extract the ZIP file there. You should end up with a path like `C:\oracle\instantclient_21_12`.
4. **Link the Path:** Open `src/utils/db_helpers.py` in this repository and ensure the `lib_dir` path perfectly matches where you extracted the client:
   ```python
   import oracledb
   
   try:
       # Update this path to match your local extraction directory
       oracledb.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_12")
   except Exception as e:
       pass
   ```

---

## 📁 Project Structure

```text
├── app.py                      # Main Streamlit dashboard application
├── data/
│   ├── raw/                    # Original SQL dataset (e.g., Modified_SQL_Dataset.csv)
│   └── processed/              # Saved vocab (sql_word2idx.json) & SHAP baseline (shap_background.npy)
├── notebooks/
│   ├── SQL_CNN_best.pth        # Trained PyTorch CNN model weights
│   └── 05_xai_implementation.ipynb # Model training and SHAP setup notebook
├── src/
│   ├── models/
│   │   └── sql_models.py       # CNN architecture class definition
│   ├── utils/
│   │   ├── data_helpers.py     # Text preprocessing and tokenization logic
│   │   └── db_helpers.py       # Oracle database connection and execution logic
│   └── xai/
│       ├── xai_helpers.py      # SHAP KernelExplainer logic
│       └── visualizations.py   # HTML/CSS rendering for SHAP text highlights
└── README.md                   # Project documentation
```

---

## 💻 How to Run the Firewall

1. Ensure your Conda environment is active:
   ```bash
   conda activate dbms-xai
   ```
2. Start the Streamlit server:
   ```bash
   streamlit run app.py
   ```
3. Open your browser to the Local URL provided in the terminal (usually `http://localhost:8501`).

### Connecting to Your Database
In the left sidebar of the dashboard, enter your Oracle credentials:
* **Username:** Your database/APEX workspace username (e.g., `system`, `admin`, or `KARTHIKEYA`).
* **Password:** Your database password (leave blank to test the AI without attempting DB execution).
* **DSN:** Your connection string (e.g., `localhost:1521/XE` for local Oracle Express Edition).

### Testing the System
Enter queries into the main text box. Try standard safe queries:
* `SELECT * FROM Student`

And then try classic malicious payloads to see the AI Firewall in action:
* `SELECT * FROM Student WHERE username = 'admin' OR 1=1 --`
* `SELECT * FROM Student WHERE id = 1'; DROP TABLE users; --`