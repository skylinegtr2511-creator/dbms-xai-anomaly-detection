import html

def render_shap_html(explanation, threshold=0.05):
    """
    Converts a list of SHAP explanation dictionaries into color-coded HTML.
    Red text indicates words that pushed the model toward 'Malicious'.
    HTML escaping is applied to all tokens to prevent XSS and rendering bugs.
    """
    html_str = "<div style='font-size: 18px; line-height: 1.5; font-family: monospace;'>"
    
    for item in explanation:
        raw_word = item.get("word", "")
        safe_word = html.escape(str(raw_word))
        score = item.get("score", 0.0)
        
        # If the score is positive (pushes towards malicious), color it red
        if score > threshold:
            intensity = min(int((score / 0.25) * 255), 255)
            html_str += f"<span style='color: rgb({intensity}, 0, 0); font-weight: bold; background-color: #ffe6e6; padding: 2px 4px; border-radius: 3px; margin: 2px;'>{safe_word}</span> "
        elif score < -threshold:
            # Pushes towards safe
            html_str += f"<span style='color: #0b6623; font-weight: 500; background-color: #e6f4ea; padding: 2px 4px; border-radius: 3px; margin: 2px;'>{safe_word}</span> "
        else:
            # Neutral / low impact
            html_str += f"<span style='color: #333;'>{safe_word}</span> "
            
    html_str += "</div>"
    return html_str
