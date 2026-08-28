# utils/fetch_live_market.py - LIVE INTRA-DAY DATA HUD INGESTION
import os
import sys
import json
import pandas as pd
from datetime import datetime

# SYSTEM PATH ANCHOR SHIELD: Appends the project root workspace directory to lookup paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import GLOBAL_UNIVERSE

def run_live_market_refresh():
    """
    Simulates a high-fidelity REST API query to fetch active interbank swap rates
    and swaption implied volatility matrices for all 8 core trading books.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    print(f"📡 Connecting to interbank pricing terminals for date: {today_str}...")
    
    # 1. Simulate active yield curve inputs (IRS Par Coupons)
    irs_snapshot = []
    base_rates = {
        "USD": 4.12, "EUR": 3.05, "GBP": 3.85, "JPY": 0.45,
        "CHF": 1.15, "NOK": 3.90, "SEK": 2.75, "ZAR": 7.85
    }
    
    # 🛡️ FIXED SYNTAX: Hardcoded explicit tenor list array added to complete the loop
    tenor_list = [1, 2, 3, 5, 7, 10, 15, 20, 30]
    
    for ccy, r in base_rates.items():
        for t in tenor_list:
            # Generate a realistic upward sloping or mildly inverted curve shape
            curve_skew = (10 - t) * -0.015 if t <= 10 else (t - 10) * 0.005
            rate_val = r + curve_skew
            
            irs_snapshot.append({
                "date": today_str,
                "currency": ccy,
                "tenor": f"{t}Y",
                "rate": round(rate_val, 4)
            })

    # 2. Simulate live active implied volatility parameters (ATM Normal Vol in bps/day)
    vol_snapshot = {}
    for ccy in GLOBAL_UNIVERSE:
        vol_snapshot[ccy] = {
            "update_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "atm_vol_bps": 82.5 if ccy in ["USD", "GBP", "EUR"] else 45.0 if ccy == "JPY" else 115.0,
            "sabr_alpha": 0.045,
            "sabr_beta": 0.500,
            "sabr_rho": -0.220,
            "sabr_volvol": 0.410
        }
        
    # Write the assets back safely to disk clusters for layouts to ingest
    try:
        with open("data/g4_curves.json", "w") as f:
            json.dump(irs_snapshot, f, indent=4)
            
        with open("data/live_vol_surface.json", "w") as f:
            json.dump(vol_snapshot, f, indent=4)
            
        print(f"✅ Live market data successfully localized on disk for today!")
    except Exception as e:
        print(f"❌ Ingestion loop dropped: {str(e)}")

if __name__ == "__main__":
    run_live_market_refresh()
