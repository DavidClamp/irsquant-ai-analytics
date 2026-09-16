# utils/generate_test_vol_data.py - GENERATE REALISTIC FIXED-INCOME VOLATILITY DATASETS
import json
import os

def build_pristine_volatility_dataset_registers():
    """
    Generates 4 fully linked, realistic volatility JSON files inside the data/ directory,
    modelling an institutional USD Swaption/Option volatility surface regime.
    """
    os.makedirs("data", exist_ok=True)
    
    expiries = ["1M", "3M", "6M", "1Y", "2Y", "5Y"]
    tenors = ["1Y", "2Y", "3Y", "5Y", "10Y", "30Y"]
    skews = ["10D Put", "25D Put", "ATM", "25D Call", "10D Call"]
    
    # 🗃️ FILE 1: data/vol_data.json - Raw Voice/Broker Interbank Run Matrix
    # Simulates raw broker quotes in normal volatility (basis points per annum)
    raw_broker_run = {
        "currency": "USD",
        "asset_class": "Rates_Swaption",
        "pricing_session": "NY_Close_1600",
        "data_feed": [
            {
                "expiry": exp,
                "underlying_tenor": ten,
                "atm_vol_bps": round(70.0 + (i * 2.5) - (j * 0.8), 2),
                "risk_reversal_25d": -3.5,
                "strangle_25d": 4.2
            }
            for i, exp in enumerate(expiries) for j, ten in enumerate(tenors)
        ]
    }
    
    # 🗃️ FILE 2: data/g4_vol_surfaces.json - Historical Organized Grid Matrices
    # Simulates a rolling multi-day non-parametric volatility grid snapshot archive
    historical_snapshot = {
        "USD": {
            "2026-09-14": {exp: [round(base + shift, 1) for shift in [14.0, 5.5, 0.0, 6.7, 16.1]] 
                           for exp, base in [("1M", 68.5), ("3M", 70.2), ("6M", 72.4), ("1Y", 75.1), ("2Y", 78.6), ("5Y", 82.3)]},
            "2026-09-15": {exp: [round(base + shift, 1) for shift in [13.8, 5.2, 0.0, 6.5, 15.8]] 
                           for exp, base in [("1M", 69.1), ("3M", 70.8), ("6M", 73.0), ("1Y", 75.7), ("2Y", 79.1), ("5Y", 82.8)]}
        }
    }
    
    # 🗃️ FILE 3: data/live_vol_surface.json - Today's Live Active Grid Session (Matches layouts/vol_surface.py)
    # The active cross-sectional surface matrix mapping expiries straight to explicit skew buckets
    live_surface_grid = []
    base_vols = {"1M": 68.5, "3M": 70.2, "6M": 72.4, "1Y": 75.1, "2Y": 78.6, "5Y": 82.3}
    skew_shifts = [14.0, 5.5, 0.0, 6.7, 16.1]  # Forms a distinct, high-convexity smile curvature
    
    for exp in expiries:
        for s_idx, sk in enumerate(skews):
            calculated_vol = base_vols[exp] + skew_shifts[s_idx]
            live_surface_grid.append({
                "currency": "USD",
                "expiry": exp,
                "skew_bucket": sk,
                "implied_normal_vol_bps": round(calculated_vol, 2)
            })
            
    # 🗃️ FILE 4: data/calibrated_sabr_surfaces.json - Smooth Parametric Backbone Registry
    # Pre-calibrated Hagan model coefficients derived directly from our optimization routines
    sabr_parameters = {
        "1M": {"alpha": 0.00685, "beta": 0.0, "rho": -0.1250, "nu": 0.4420, "residual_error": 1.25e-6},
        "3M": {"alpha": 0.00702, "beta": 0.0, "rho": -0.1180, "nu": 0.4280, "residual_error": 9.8e-7},
        "6M": {"alpha": 0.00724, "beta": 0.0, "rho": -0.1040, "nu": 0.4150, "residual_error": 1.12e-6},
        "1Y": {"alpha": 0.00751, "beta": 0.0, "rho": -0.0920, "nu": 0.3980, "residual_error": 8.4e-7},
        "2Y": {"alpha": 0.00786, "beta": 0.0, "rho": -0.0810, "nu": 0.3840, "residual_error": 2.15e-6},
        "5Y": {"alpha": 0.00823, "beta": 0.0, "rho": -0.0650, "nu": 0.3620, "residual_error": 3.4e-6}
    }
    
    # Commit all structured profiles directly to system disk registers
    configs = [
        ("data/vol_data.json", raw_broker_run),
        ("data/g4_vol_surfaces.json", historical_snapshot),
        ("data/live_vol_surface.json", live_surface_grid),
        ("data/calibrated_sabr_surfaces.json", sabr_parameters)
    ]
    
    for path, data in configs:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"✔ Successfully written realistic test data to: {path}")
        
    print("\n🎉 Success: Full-curve structural volatility dataset registries successfully locked down.")

if __name__ == "__main__":
    build_pristine_volatility_dataset_registers()
