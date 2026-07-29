# analytics.py
import itertools
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def extract_implied_forward_swap(curve_obj, start_n, tenor_m):
    r"""
    Calculates a forward-starting swap rate from bootstrapped discount factors.
    Formula: F(n, m) = [ P(0, n) - P(0, n + m) ] / \sum_{i=1}^{m} P(0, n + i)
    """
    p_start = curve_obj.get_discount_factor(start_n)
    p_end = curve_obj.get_discount_factor(start_n + tenor_m)
    
    # Query Layer 1 curve for the exact forward Annuity Factor (PVBP)
    annuity = curve_obj.get_annuity_factor(start_n=start_n, tenor_m=tenor_m, payment_freq=1.0)
    
    if annuity == 0.0:
        return 0.0
        
    return (p_start - p_end) / annuity

def extract_forward_curve_snapshot(master_df, selected_ccy, target_date_str, forward_tenor=1.0):
    """
    Term Structure Snapshot Engine: Extracts an entire curve's shape for a single day.
    Returns the coordinates needed to plot horizontal forward blocks along the maturity horizon.
    """
    from curves import BootstrappedDiscountCurve
    
    # Filter dataset to the chosen currency and date slice
    day_df = master_df[(master_df['currency'] == selected_ccy) & (master_df['date'] == target_date_str)].copy()
    if day_df.empty:
        return [], [], []
        
    spot_rates_dict = day_df.set_index('tenor')['rate'].to_dict()
    
    # Instantiate Layer 1 bootstrapping engine
    curve = BootstrappedDiscountCurve(target_date=target_date_str, spot_rates_dict=spot_rates_dict)
    
    # Standard G4 curve start delay nodes
    tenor_map = {'3M': 0.25, '1Y': 1.0, '2Y': 2.0, '3Y': 3.0, '4Y': 4.0, '5Y': 5.0, '7Y': 7.0}
    
    x_starts, x_ends, y_rates = [], [], []
    for node, start_years in tenor_map.items():
        fwd_rate = extract_implied_forward_swap(curve, start_n=start_years, tenor_m=forward_tenor)
        x_starts.append(start_years)
        x_ends.append(start_years + forward_tenor)
        y_rates.append(fwd_rate * 100) # Convert to percentage points for accurate visual scaling
        
    return x_starts, x_ends, y_rates

def build_forward_permutation_matrix(dates_index, master_df, selected_ccy, forward_tenor=1.0):
    """
    Generates a historical time-series matrix of 1-Year forwards across all available dates.
    Used to supply data vectors directly into the linear regression model.
    """
    from curves import BootstrappedDiscountCurve
    
    ccy_df = master_df[master_df['currency'] == selected_ccy].copy()
    pivot_df = ccy_df.pivot(index='date', columns='tenor', values='rate').dropna()
    
    tenor_map = {'3M': 0.25, '1Y': 1.0, '2Y': 2.0, '3Y': 3.0, '4Y': 4.0, '5Y': 5.0, '7Y': 7.0}
    start_nodes = list(tenor_map.keys())
    
    matrix_dict = {f"{node}F{int(forward_tenor)}Y": [] for node in start_nodes}
    matrix_dates = []
    
    for dt in pivot_df.index:
        spot_rates_dict = pivot_df.loc[dt].to_dict()
        curve = BootstrappedDiscountCurve(target_date=dt, spot_rates_dict=spot_rates_dict)
        matrix_dates.append(dt)
        
        for node in start_nodes:
            start_n = tenor_map[node]
            fwd_rate = extract_implied_forward_swap(curve, start_n=start_n, tenor_m=forward_tenor)
            matrix_dict[f"{node}F{int(forward_tenor)}Y"].append(fwd_rate)
            
    return pd.DataFrame(matrix_dict, index=matrix_dates)

def run_systematic_butterfly_scan(f_matrix_df):
    """
    Executes a zero-constant linear regression across 3 distinct nodes to locate
    relative value curvature anomalies, ranking them by absolute rolling Z-score.
    """
    all_legs = list(f_matrix_df.columns)
    scan_results = []
    series_storage = {}
    
    if len(all_legs) < 3:
        return pd.DataFrame(), {}
        
    combinations = list(itertools.combinations(all_legs, 3))
    
    for short_f, mid_f, long_f in combinations:
        X = f_matrix_df[[short_f, long_f]].values
        y = f_matrix_df[mid_f].values
        
        # Enforce zero-intercept constraint to eliminate the constant premium assumption
        model = LinearRegression(fit_intercept=False)
        model.fit(X, y)
        
        coefs = np.atleast_1d(model.coef_)
        
        residuals = y - model.predict(X)
        current_residual = residuals[-1]
        z_score = (current_residual - residuals.mean()) / residuals.std()
        r2 = model.score(X, y)
        
        struct_name = f"FLY: {mid_f} vs [{short_f} & {long_f}]"
        series_storage[struct_name] = pd.Series(residuals, index=f_matrix_df.index)
        
        scan_results.append({
            'Structure': struct_name,
            'Hedge Ratio (Short)': round(coefs[0], 2),
            'Hedge Ratio (Long)': round(coefs[1], 2) if len(coefs) > 1 else round(coefs[0], 2),
            'R-Squared': round(r2, 4),
            'Current Residual (bps)': round(current_residual * 10000, 2),
            'Z-Score (Outlier)': round(z_score, 2)
        })
        
    rank_df = pd.DataFrame(scan_results)
    if not rank_df.empty:
        rank_df = rank_df.sort_values(by='Z-Score (Outlier)', key=abs, ascending=False)
        
    return rank_df, series_storage
