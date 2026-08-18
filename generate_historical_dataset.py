# generate_historical_dataset.py - 5-YEAR COORDINATED HISTORICAL RATES & VOL GENERATOR
import os
import json
import datetime
import numpy as np

# Ensure data repository directory exists
os.makedirs("data", exist_ok=True)

# 1. Setup Time Horizon (5 Years of daily trading steps ~ 1250 periods)
start_date = datetime.date(2021, 8, 18)
total_days = 1250
date_list = [str(start_date + datetime.timedelta(days=i)) for i in range(total_days)]

currencies = ["USD", "EUR", "GBP", "JPY"]

tenors = [0.25, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0]
expiries = [1.0, 2.0, 3.0, 4.0, 5.0]
strikes = [1.0, 2.0, 3.0, 4.0, 5.0]

# Coordinated Macro Cycles: Smooth sine wave simulating a rate tightening/easing regime
# Peak tightening around day 300-400 (high flat rates), easing around day 900 (low steep rates)
macro_cycle = np.sin(np.linspace(0, 3 * np.pi, total_days)) 

curves_dataset = []
vol_dataset = {
    "swaption_sabr_grids": {ccy: {"expiry_nodes": expiries, "underlying_tenors": tenors, "historical_data": {}} for ccy in currencies},
    "cap_flat_strips": {ccy: {"maturities": tenors, "strikes": strikes, "historical_data": {}} for ccy in currencies}
}

print("Generating 5 years of noise-free synchronized fixed-income data...")

for idx, date_str in enumerate(date_list):
    cycle_val = macro_cycle[idx]  # Ranges from -1.0 to +1.0
    
    for ccy in currencies:
        # Base market levels per currency
        ccy_shift = {"USD": 2.5, "EUR": 1.5, "GBP": 2.0, "JPY": 0.2}[ccy]
        vol_base = {"USD": 22.0, "EUR": 16.0, "GBP": 19.0, "JPY": 10.0}[ccy]
        
        # --- LAYER 1 & 2: GENERATE CURVE NODE DATA ---
        # Short rate moves aggressively with the macro cycle; long rate is more stable (steepening/flattening)
        short_rate = max(0.1, ccy_shift + (cycle_val * 1.5))
        long_rate = max(0.5, ccy_shift + 1.2 + (cycle_val * 0.4))
        
        # Interpolate a smooth curve across the tenors for this day
        rates_dict = {}
        for t in tenors:
            weight = (t - 0.25) / 29.75 if t > 0.25 else 0.0
            interpolated_rate = round(short_rate + weight * (long_rate - short_rate), 4)
            
            # Create a label string matching the exact key signatures expected by your app
            tenor_str = "3M" if t == 0.25 else f"{int(t)}Y"
            rates_dict[tenor_str] = interpolated_rate
            
            curves_dataset.append({
                "date": date_str,
                "currency": ccy,
                "tenor": tenor_str,
                "rate": interpolated_rate
            })
            
        # --- LAYER 3: GENERATE ALIGNED SKEWS & VOLATILITY MATRICES ---
        # Rule: Volatility expands during tightening cycles (high cycle_val), compresses during easing
        current_vol_level = max(5.0, vol_base + (cycle_val * 4.0))
        
        # Generate Swaption Grid (Expiry x Underlying Tenor)
        # Smooth macro shape: vol decays down the tenor line (mean reversion of long forwards)
        swaption_matrix = [
            [round(current_vol_level + (e * 0.5) - (t * 0.1), 2) for t in tenors]
            for e in expiries
        ]
        
        # Dynamic SABR parameter alignment: Skew (rho) becomes more negative as rates rise
        current_rho = round(-0.25 - (cycle_val * 0.07), 2)
        vol_dataset["swaption_sabr_grids"][ccy]["historical_data"][date_str] = {
            "grid_matrix": swaption_matrix,
            "parameters": {"beta": 0.50, "alpha": round(current_vol_level/100, 3), "rho": current_rho, "nu": round(0.45 + (cycle_val * 0.1), 3)}
        }
        
        # Generate Cap Strip Grid (Maturity x Strike)
        # Smile curve shape modeled via a pure parabolic quadratic function around an ATM strike of 3.0%
        cap_matrix = [
            [round(current_vol_level + (m * 0.3) + ((s - 3.0) ** 2 * 1.0), 2) for s in strikes]
            for m in tenors
        ]
        vol_dataset["cap_flat_strips"][ccy]["historical_data"][date_str] = {
            "strip_matrix": cap_matrix
        }

# Save Curve Dataset
with open("data/g4_curves.json", "w") as f:
    json.dump(curves_dataset, f, indent=2)

# Save Volatility Surface Dataset
with open("data/g4_vol_surfaces.json", "w") as f:
    json.dump(vol_dataset, f, indent=4)

print(f"SUCCESS: Generated {total_days} days of synchronized data matrices inside 'data/' directory!")
