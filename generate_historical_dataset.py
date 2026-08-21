# generate_historical_dataset.py - IRSQUANT ENGINE UNIFIED MARKET FEED CONSTRUCTOR
import json
import numpy as np
from datetime import datetime, timedelta

# 1. DEFINE CORE HIGH-RESOLUTION REGIMES WITH SYSTEMIC LIQUIDITY BRACKETS
# "liquidity_tier": 1 = Pristine continuous data, 2 = Minor wing dropping, 3 = Severe proxy gaps / stale nodes
ccy_baselines = {
    "USD": {"short": 4.50, "long": 3.80, "atm_vol": 22.0, "liquidity_tier": 1},
    "EUR": {"short": 3.00, "long": 2.70, "atm_vol": 18.0, "liquidity_tier": 1},
    "GBP": {"short": 4.75, "long": 4.10, "atm_vol": 20.0, "liquidity_tier": 1},
    "JPY": {"short": 0.25, "long": 1.10, "atm_vol": 14.0, "liquidity_tier": 1},
    "CHF": {"short": 1.50, "long": 1.30, "atm_vol": 15.0, "liquidity_tier": 2},
    "NOK": {"short": 4.25, "long": 3.60, "atm_vol": 19.0, "liquidity_tier": 2},
    "SEK": {"short": 3.75, "long": 3.20, "atm_vol": 19.5, "liquidity_tier": 2},
    "ZAR": {"short": 8.25, "long": 8.90, "atm_vol": 26.0, "liquidity_tier": 3}
}

tenors_list = ["3M", "1Y", "2Y", "3Y", "4Y", "5Y", "7Y", "10Y", "15Y", "20Y", "25Y", "30Y"]
expiry_nodes = [1.0, 2.0, 3.0, 4.0, 5.0]
underlying_tenors = [1.0, 2.0, 5.0, 10.0, 30.0]
strikes_list = [1.0, 2.0, 3.0, 4.0, 5.0]

# Generate a continuous 100-day historical time-series strip leading up to today [2026-08-21]
base_date = datetime(2026, 8, 21)
dates = [(base_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(100)]

curves_dataset = []
swaption_sabr_grids = {}
cap_flat_strips = {}

# Initialize multi-currency structural storage dictionaries
for ccy in ccy_baselines.keys():
    swaption_sabr_grids[ccy] = {"expiry_nodes": expiry_nodes, "underlying_tenors": underlying_tenors, "historical_data": {}}
    cap_flat_strips[ccy] = {"maturities": underlying_tenors, "strikes": strikes_list, "historical_data": {}}

# --- CORE DATA SYSTEM GENERATION LOOP ---
for idx, dt in enumerate(dates):
    # Cyclical macro economic wave factor tracking parallel shifts
    macro_wave = np.sin(idx * 0.1) * 0.20
    
    for ccy, meta in ccy_baselines.items():
        tier = meta["liquidity_tier"]
        
        # 1. BUILD SPOT INTEREST RATE CURVE RECORDS
        s_rate = meta["short"] + macro_wave
        l_rate = meta["long"] + macro_wave
        for t in tenors_list:
            t_num = 0.25 if t == "3M" else float(t.replace('Y', ''))
            weight = (t_num - 0.25) / 29.75
            rate_val = round(s_rate + weight * (l_rate - s_rate), 4)
            curves_dataset.append({
                "date": dt, "currency": ccy, "tenor": t, "rate": max(0.01, rate_val)
            })

        # 2. APPLICATION OF LIQUIDITY DRAG OVER VOLATILITY FIELDS
        # If Tier 3 (ZAR), values freeze (stale prices) except on every 4th trading day close
        if tier == 3 and idx % 4 != 0:
            # Reuses previous generated day slice to perfectly simulate data staleness
            prev_date = (base_date - timedelta(days=idx-1)).strftime("%Y-%m-%d")
            if prev_date in swaption_sabr_grids[ccy]["historical_data"]:
                swaption_sabr_grids[ccy]["historical_data"][dt] = swaption_sabr_grids[ccy]["historical_data"][prev_date]
                cap_flat_strips[ccy]["historical_data"][dt] = cap_flat_strips[ccy]["historical_data"][prev_date]
                continue

        # Generate base volatility matrix grids
        base_vol = meta["atm_vol"] + (np.cos(idx * 0.08) * 0.5)
        
        # Assemble Swaption SABR Matrices
        swaption_matrix = []
        for exp in expiry_nodes:
            row = []
            for ten in underlying_tenors:
                # Core pricing structure formula + minor slope decay factors
                vol_point = base_vol + (exp * 0.4) - (ten * 0.1)
                
                # Tier 2 & 3 Data Degradation: Drop out OTM nodes randomly (simulate missing broker data)
                if (tier == 2 and (exp == 5.0 and ten == 30.0)) or (tier == 3 and ten >= 10.0 and idx % 2 == 0):
                    vol_point = 0.0  # System drops the node to a raw zero to test system interpolation boundaries
                    
                row.append(round(max(2.0, vol_point), 2))
            swaption_matrix.append(row)
            
        # Define parametric SABR tracking variables matching the asset class profile
        sabr_params = {
            "beta": 0.50,
            "alpha": round(base_vol / 100.0, 3),
            "rho": -0.30 if tier == 1 else (-0.15 if tier == 2 else 0.0), # Illiquid blocks lose skew definitions completely
            "nu": 0.40 if tier == 1 else 0.65 # Higher fitting chaos (vol-of-vol noise) in illiquid segments
        }
        
        swaption_sabr_grids[ccy]["historical_data"][dt] = {
            "grid_matrix": swaption_matrix,
            "parameters": sabr_params
        }

        # Assemble Cap/Floor Flat Vol Strips
        cap_matrix = []
        for mat in underlying_tenors:
            row = []
            for stk in strikes_list:
                # Create a smile curve relative to absolute strike location
                smile_offset = (stk - 3.0) ** 2 * 1.2
                vol_point = (base_vol + 5.0) - (mat * 0.15) + smile_offset
                
                # Tier 3 Friction Layer: High strikes for illiquid pairs don't clear, causing database gaps
                if tier == 3 and stk == 5.0:
                    vol_point = 0.0 # Creates missing outer edge data grids
                    
                row.append(round(max(4.0, vol_point), 2))
            cap_matrix.append(row)
            
        cap_flat_strips[ccy]["historical_data"][dt] = {"strip_matrix": cap_matrix}

# --- SAVE CONSOLIDATED RAW REPOSITORIES UNTO DISK ---
with open("data/g4_curves.json", "w") as f:
    json.dump(curves_dataset, f, indent=4)

with open("data/g4_vol_surfaces.json", "w") as f:
    json.dump({
        "swaption_sabr_grids": swaption_sabr_grids,
        "cap_flat_strips": cap_flat_strips
    }, f, indent=4)

print("✅ Successfully generated unified 8-currency IRSQuant market dataset files.")
print("⚠️ Real-World Liquidity Degradation Mode Applied: Stale tracking nodes activated on ZAR, SEK, NOK assets.")
