def render_shap_html(explanation):
    """
    Converts a list of SHAP explanation dictionaries into color-coded HTML.
    Red text indicates words that pushed the model toward 'Malicious'.
    """
    html_str = "<div style='font-size: 18px; line-height: 1.5; font-family: monospace;'>"
    
    for item in explanation:
        word = item["word"]
        score = item["score"]
        
        # If the score is highly positive (malicious), color it red
        if score > 0.05:
            # The higher the score, the more intense the red/bolding
            intensity = min(int((score / 0.25) * 255), 255)
            html_str += f"<span style='color: rgb({intensity}, 0, 0); font-weight: bold; background-color: #ffe6e6; padding: 2px; border-radius: 3px; margin: 2px;'>{word}</span> "
        else:
            # Normal words stay standard gray/black
            html_str += f"<span style='color: #333;'>{word}</span> "
            
    html_str += "</div>"
    return html_str