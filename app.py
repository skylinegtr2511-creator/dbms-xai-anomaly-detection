import streamlit as st
import torch
import json
import numpy as np
import os
import sys

# Add project root to sys path so we can import src modules
sys.path.append(os.path.abspath('.'))

from src.models.sql_models import SQLCNN
from src.utils.data_helpers import encode_query
from src.utils.db_helpers import execute_safe_query
from src.xai.xai_helpers import explain_sql_prediction
from src.xai.visualizations import render_shap_html

# -----------------------------------------
# 1. Resource Loading (Cached for Speed)
# -----------------------------------------
@st.cache_resource
def load_resources():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load Vocabulary
    with open('data/processed/sql_word2idx.json', 'r') as f:
        word2idx = json.load(f)
        
    # Load Model
    model = SQLCNN(vocab_size=len(word2idx)).to(device)
    model.load_state_dict(torch.load('notebooks/SQL_CNN_best.pth', map_location=device, weights_only=True))
    model.eval()
    
    # Load SHAP Background
    background_data = np.load('data/processed/shap_background.npy')
    
    return device, word2idx, model, background_data

device, word2idx, model, background_data = load_resources()

# Wrapper for SHAP to make predictions
def predict_fn(queries_numpy):
    tensor = torch.tensor(queries_numpy, dtype=torch.long).to(device)
    with torch.no_grad():
        raw_logits = model(tensor).squeeze(1)
        preds = torch.sigmoid(raw_logits).cpu().numpy()
    return preds

# -----------------------------------------
# 2. Streamlit UI Layout
# -----------------------------------------
st.set_page_config(page_title="AI DB Firewall", layout="wide")
st.title("🛡️ Active AI Firewall & XAI Dashboard")
st.markdown("This system intercepts SQL queries, scans them using a Deep Learning CNN, and blocks injection attacks while explaining its reasoning via SHAP.")

# Sidebar for Database Configuration
st.sidebar.header("Oracle DB Configuration")
db_user = st.sidebar.text_input("Username", value="admin")
db_password = st.sidebar.text_input("Password", type="password")
db_dsn = st.sidebar.text_input("DSN (e.g., localhost:1521/XEPDB1)", value="localhost:1521/XEPDB1")

# Main Query Input
st.subheader("Query Execution")
query = st.text_area("Enter your SQL Query here:", height=150, placeholder="SELECT * FROM employees WHERE id = 1...")

if st.button("Execute Query", type="primary"):
    if not query.strip():
        st.warning("Please enter a SQL query.")
    else:
        with st.spinner("Analyzing query with AI Firewall..."):
            # 1. AI Security Scan
            encoded = encode_query(query, word2idx)
            test_numpy = np.array([encoded])
            malicious_prob = predict_fn(test_numpy)[0]
            
            # 2. Determine Action based on Probability
            threshold = 0.5
            
            if malicious_prob > threshold:
                st.error(f"🚨 **QUERY BLOCKED:** Malicious Probability is {malicious_prob * 100:.2f}%")
                
                # Trigger Explainable AI (SHAP)
                st.subheader("🧠 Explainable AI (Why was this blocked?)")
                with st.spinner("Generating SHAP interpretation..."):
                    explanation = explain_sql_prediction(query, word2idx, predict_fn, background_data)
                    html_explanation = render_shap_html(explanation)
                    
                    st.markdown("**Highlighted Syntax (Red = Malicious intent)**")
                    st.markdown(html_explanation, unsafe_allow_html=True)
                    
            else:
                st.success(f"✅ **QUERY SAFE:** Malicious Probability is {malicious_prob * 100:.2f}%")
                
                # Execute on Oracle
                st.subheader("📊 Database Execution")
                if db_password: # Only run if password is provided
                    result = execute_safe_query(query, db_user, db_password, db_dsn)
                    
                    if result["status"] == "success":
                        if "data" in result:
                            st.dataframe(result["data"])
                        else:
                            st.info(result["message"])
                    else:
                        st.error(f"Database Error: {result['message']}")
                else:
                    st.info("Query passed security scan! (Enter DB password in the sidebar to execute on Oracle).")