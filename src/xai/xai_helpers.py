import numpy as np
import shap
from src.utils.data_helpers import encode_query

def explain_sql_prediction(query, word2idx, predict_fn, background_data):
    """
    Generates SHAP impact scores for a given SQL query to explain the model's prediction.
    """
    # 1. Initialize the explainer
    explainer = shap.KernelExplainer(predict_fn, background_data)
    
    # 2. Encode the query
    encoded_query = encode_query(query, word2idx)
    query_numpy = np.array([encoded_query])
    
    # 3. Calculate SHAP values
    shap_values = explainer.shap_values(query_numpy)
    
    # 4. Map scores to words
    idx2word = {idx: word for word, idx in word2idx.items()}
    tokens = [idx2word.get(idx, '<PAD>') for idx in encoded_query]
    
    explanation = []
    for word, score in zip(tokens, shap_values[0]):
        if word != '<PAD>':
            # Store as dictionary for easy rendering in Streamlit
            explanation.append({"word": word.strip(), "score": float(score)})
            
    # Sort by highest impact (most malicious) first
    explanation.sort(key=lambda x: x["score"], reverse=True)
    
    return explanation