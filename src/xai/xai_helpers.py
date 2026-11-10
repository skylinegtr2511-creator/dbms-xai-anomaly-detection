import numpy as np
import shap
from src.utils.data_helpers import encode_query

_explainer_cache = None

def get_or_create_explainer(predict_fn, background_data):
    """
    Returns a cached KernelExplainer instance or creates a new one if not yet initialized.
    """
    global _explainer_cache
    if _explainer_cache is None:
        _explainer_cache = shap.KernelExplainer(predict_fn, background_data)
    return _explainer_cache

def explain_sql_prediction(query, word2idx, predict_fn, background_data, explainer=None, sort_by_impact=False):
    """
    Generates SHAP impact scores for a given SQL query to explain the model's prediction.
    
    Args:
        query: The raw SQL string.
        word2idx: Dictionary mapping tokens to integers.
        predict_fn: Prediction wrapper function returning probabilities.
        background_data: Background queries matrix for SHAP reference.
        explainer: Optional pre-initialized SHAP explainer.
        sort_by_impact: If True, sort words by descending score. If False, keep original order.
    
    Returns:
        List of dicts: [{"word": token, "score": float_score}, ...]
    """
    # 1. Obtain explainer
    if explainer is None:
        explainer = get_or_create_explainer(predict_fn, background_data)
        
    # 2. Encode the query
    encoded_query = encode_query(query, word2idx)
    query_numpy = np.array([encoded_query])
    
    # 3. Calculate SHAP values
    shap_values = explainer.shap_values(query_numpy)
    
    # Handle SHAP output format differences across versions (list of classes vs 2D array)
    if isinstance(shap_values, list):
        shap_matrix = shap_values[-1] if len(shap_values) > 1 else shap_values[0]
    else:
        shap_matrix = shap_values
        
    if isinstance(shap_matrix, np.ndarray) and shap_matrix.ndim > 1:
        scores = shap_matrix[0]
    else:
        scores = shap_matrix
    
    # 4. Map scores to words
    idx2word = {idx: word for word, idx in word2idx.items()}
    tokens = [idx2word.get(idx, '<PAD>') for idx in encoded_query]
    
    explanation = []
    for word, score in zip(tokens, scores):
        if word != '<PAD>':
            explanation.append({"word": word.strip(), "score": float(score)})
            
    if sort_by_impact:
        explanation.sort(key=lambda x: x["score"], reverse=True)
        
    return explanation
