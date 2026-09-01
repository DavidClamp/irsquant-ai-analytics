# utils/ai_parser.py - ISOLATED NLP EXTRACTION ENGINE FOR SWAP CURVES
import re
from config import GLOBAL_UNIVERSE


def parse_macro_intent(prompt_text, default_ccy="USD"):
    """
    Parses unstructured trader prompts to extract structural filtration boundaries.
    Safe, regex-driven, and isolated from frontend layout trees.
    """
    if not prompt_text:
        return default_ccy, 0.0, "System idling. Awaiting front-office macro commands..."

    p_clean = str(prompt_text).upper().strip()
    target_ccy = default_ccy
    z_threshold = 0.0

    # 1. Parse target currency book tokens dynamically (with explicit UK/G4 spelling fallback rules)
    # Allows a user to type conversational terms like "London", "Euro", or "Yen" smoothly
    currency_aliases = {
        "USD": ["USD", "DOLLAR", "FED", "STATES", "AMERICA"],
        "EUR": ["EUR", "EURO", "ECB", "EUROPE"],
        "GBP": ["GBP", "STERLING", "CABLE", "BOE", "LONDON", "POUND"],
        "JPY": ["JPY", "YEN", "BOJ", "TOKYO", "JAPAN"],
        "CHF": ["CHF", "SWISSIE", "SNB", "FRANC"],
        "NOK": ["NOK", "NORGES", "KRONER", "NORWAY"],
        "SEK": ["SEK", "RIKSBANK", "SWEDEN", "KRONA"],
        "ZAR": ["ZAR", "SARB", "RAND", "AFRICA"]
    }

    found_ccy = False
    for ccy, aliases in currency_aliases.items():
        for alias in aliases:
            if alias in p_clean:
                target_ccy = ccy
                found_ccy = True
                break
        if found_ccy:
            break

    # 2. Extract numeric Z-score filter thresholds (e.g. "1.5", "2", "0.5")
    threshold_match = re.search(r"(\d+\.\d+|\d+)", p_clean)
    if threshold_match:
        z_threshold = float(threshold_match.group(1))
    else:
        # Assign institutional default baseline trigger constraints if no explicit number is typed
        z_threshold = 1.25 if "CHEAP" in p_clean or "RICH" in p_clean or "ANOMALY" in p_clean else 0.0

    reasoning_log = (
        f"🤖 AI Macro Intent Extracted ▸ Currency Group Filter: [{target_ccy}] | "
        f"Minimum Absolute Z-Score Constraint: ≥ {z_threshold:.2f} σ. Processing OLS matrix residuals..."
    )

    return target_ccy, z_threshold, reasoning_log
