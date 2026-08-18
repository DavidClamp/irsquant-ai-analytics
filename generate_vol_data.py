# generate_vol_data.py - CORE MULTI-CURRENCY VOLATILITY DATA GENERATOR
import os
import json

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

expiries = [1.0, 2.0, 3.0, 4.0, 5.0]
tenors = [1.0, 2.0, 5.0, 10.0, 30.0]
maturities = [1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0]
strikes = [1.0, 2.0, 3.0, 4.0, 5.0]

def make_swaption_grid(base):
    return [[round(base + (e * 0.8) - (t * 0.15), 2) for t in tenors] for e in expiries]

def make_cap_strip(base):
    return [[round(base + (m * 0.4) + ((s - 3.0) ** 2 * 1.2), 2) for s in strikes] for m in maturities]

vol_data = {
    "swaption_sabr_grids": {
        "USD": {"expiry_nodes": expiries, "underlying_tenors": tenors, "grid_matrix": make_swaption_grid(22.5), "parameters": {"beta": 0.50, "alpha": 0.245, "rho": -0.32, "nu": 0.620}},
        "EUR": {"expiry_nodes": expiries, "underlying_tenors": tenors, "grid_matrix": make_swaption_grid(18.2), "parameters": {"beta": 0.50, "alpha": 0.195, "rho": -0.28, "nu": 0.540}},
        "GBP": {"expiry_nodes": expiries, "underlying_tenors": tenors, "grid_matrix": make_swaption_grid(20.4), "parameters": {"beta": 0.50, "alpha": 0.215, "rho": -0.30, "nu": 0.580}},
        "JPY": {"expiry_nodes": expiries, "underlying_tenors": tenors, "grid_matrix": make_swaption_grid(12.1), "parameters": {"beta": 0.50, "alpha": 0.110, "rho": -0.15, "nu": 0.310}}
    },
    "cap_flat_strips": {
        "USD": {"maturities": maturities, "strikes": strikes, "strip_matrix": make_cap_strip(24.0)},
        "EUR": {"maturities": maturities, "strikes": strikes, "strip_matrix": make_cap_strip(19.5)},
        "GBP": {"maturities": maturities, "strikes": strikes, "strip_matrix": make_cap_strip(21.2)},
        "JPY": {"maturities": maturities, "strikes": strikes, "strip_matrix": make_cap_strip(13.5)}
    }
}

# Save directly to the data sub-repository folder location
with open("data/g4_vol_surfaces.json", "w") as file_out:
    json.dump(vol_data, file_out, indent=4)

print("SUCCESS: data/g4_vol_surfaces.json created and populated with multi-currency matrices!")
