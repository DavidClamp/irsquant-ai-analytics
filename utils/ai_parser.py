# utils/ai_parser.py - ISOLATED NLP EXTRACTION ENGINE FOR SWAP CURVES
import re
from config import GLOBAL_UNIVERSE

def parse_macro_intent(prompt_text, default_ccy="ALL"):
    """
    Parses unstructured trader prompts to extract structural filtration boundaries.
    Safe, regex-driven, and isolated from frontend layout trees.
    """
    if not prompt_text:
        return default_ccy, 0.0, "System idling. Awaiting front-office macro commands..."
        
    p_clean = str(prompt_text).upper().strip()
    target_ccy = default_ccy
    z_threshold = 0.0
    
    # 1. Parse target currency book tokens dynamically
    for ccy in GLOBAL_UNIVERSE:
        if ccy in p_clean:
            target_ccy = ccy
            break
            
    # 2. Extract numeric Z-score filter thresholds (e.g., "1.5", "2", "0.5")
    threshold_match = re.search(r"(\d+\.\d+|\d+)", p_clean)
    if threshold_match:
        z_threshold = float(threshold_match.group(1))
        
    reasoning_log = (
        f"🤖 AI Macro Intent Extracted ▸ Currency Group Filter: [{target_ccy}] | "
        f"Minimum Absolute Z-Score Constraint: ≥ {z_threshold:.2f} σ. Processing OLS matrix residuals..."
    )
    
    return target_ccy, z_threshold, reasoning_log
