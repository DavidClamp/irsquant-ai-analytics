# test_pipeline.py
import numpy as np
import pandas as pd
from analytics import build_forward_permutation_matrix, run_systematic_butterfly_scan

# 1. Generate clean market dataset with absolute uniqueness constraints
np.random.seed(42)
dates = pd.date_range(end="2026-06-03", periods=100, freq='B')
currencies = ['USD', 'JPY']
tenors = ['3M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

simulated_rows = []
for ccy in currencies:
    base = 0.045 if ccy == 'USD' else 0.005
    # Generate distinct random walk paths across time loops
    paths = {t: base + (int(''.join(filter(str.isdigit, str(t)))) / 100 if 'Y' in t else 0) + np.cumsum(np.random.normal(0, 0.001, 100)) for t in tenors}
    
    # Inject a massive curve anomaly at the tail of the USD curve to verify the scanner
    if ccy == 'USD':
        paths['3Y'][-15:] += 0.0150
        
    for idx, dt in enumerate(dates):
        for t in tenors:
            simulated_rows.append({
                'date': dt, 
                'currency': ccy, 
                'tenor': t, 
                'rate': paths[t][idx]
            })

mock_master_df = pd.DataFrame(simulated_rows)

print("=== Running Layer 1 + Layer 2 Pipeline Test ===")
# Build 1-Year Forward Starting Swap Matrix using Layer 1 objects
f_matrix = build_forward_permutation_matrix(dates, mock_master_df, selected_ccy='USD', forward_tenor=1.0)
print(f"✓ Forward Matrix Shape: {f_matrix.shape} (Dates x Forward Legs)")

# Run Zero-Constant Regression Sweeper
rank_df, series_storage = run_systematic_butterfly_scan(f_matrix)
print(f"✓ Total Butterfly Combinations Scanned: {len(rank_df)}")
print("\nTop Ranked Dislocated Anomalies Found:")
print(rank_df[['Structure', 'Z-Score (Outlier)', 'Current Residual (bps)']].head(5).to_string(index=False))
