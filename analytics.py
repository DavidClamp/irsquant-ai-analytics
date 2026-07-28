# analytics.py
import itertools
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def extract_implied_forward_swap(curve_obj, start_n, tenor_m):
    r"""
    Extracts the forward-starting swap rate from Layer 1 discount factors.
    Formula: F(n, m) = [ P(0, n) - P(0, n + m) ] / \sum_{i=1}^{m} P(0, n + i)
    """
    p_start = curve_obj.get_discount_factor(start_n)
    p_end = curve_obj.get_discount_factor(start_n + tenor_m)
    
    annuity = curve_obj.get_annuity_factor(start_n=start_n, tenor_m=tenor_m, payment_freq=1.0)
    
    if annuity == 0.0:
        return 0.0
        
    forward_swap_rate = (p_start - p_end) / annuity
    return forward_swap_rate

def build_forward_permutation_matrix(dates_index, master_df, selected_ccy, forward_tenor=1.0):
    """
    Loops historically across all dates to build a complete time-series matrix 
    of forward-starting swap rates for the chosen currency.
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
            
    f_matrix_df = pd.DataFrame(matrix_dict, index=matrix_dates)
    return f_matrix_df

def run_systematic_butterfly_scan(f_matrix_df):
    """
    Layer 2 Strategy Engine: Runs a zero-constant linear regression across 3 distinct nodes.
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
        
        model = LinearRegression(fit_intercept=False)
        model.fit(X, y)
        
        residuals = y - model.predict(X)
        current_residual = residuals[-1]
        z_score = (current_residual - residuals.mean()) / residuals.std()
        r2 = model.score(X, y)
        
        struct_name = f"FLY: {mid_f} vs [{short_f} & {long_f}]"
        series_storage[struct_name] = pd.Series(residuals, index=f_matrix_df.index)
        
        scan_results.append({
            'Structure': struct_name,
            'Hedge Ratio (Short)': round(model.coef_[0], 2),
            'Hedge Ratio (Long)': round(model.coef_[1], 2),
            'R-Squared': round(r2, 4),
            'Current Residual (bps)': round(current_residual * 10000, 2),
            'Z-Score (Outlier)': round(z_score, 2)
        })
        
    rank_df = pd.DataFrame(scan_results)
    if not rank_df.empty:
        rank_df = rank_df.sort_values(by='Z-Score (Outlier)', key=abs, ascending=False)
        
    return rank_df, series_storage
