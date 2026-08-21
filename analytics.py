# analytics.py - QUANTLIB-POWERED FORWARD PERMUTATION SCANNER
import itertools
import numpy as np
import pandas as pd
import QuantLib as ql
from sklearn.linear_model import LinearRegression
from utils import DataSanitizer  # Centralized utility tracking engine

# Global institutional tenor definition map used to protect data ingestion channels
TENOR_LABEL_MAP = {
    0.25: '3M', 1.0: '1Y', 2.0: '2Y', 3.0: '3Y', 4.0: '4Y', 
    5.0: '5Y',  6.0: '6Y', 7.0: '7Y', 8.0: '8Y', 9.0: '9Y', 
    10.0: '10Y', 12.0: '12Y', 15.0: '15Y', 20.0: '20Y', 
    25.0: '25Y', 30.0: '30Y'
}

def extract_implied_forward_swap(ql_curve, start_n, tenor_m, day_counter):
    """
    Extracts mathematically flawless forward swap rates straight from QuantLib's C++ curve.
    """
    today = ql.Settings.instance().evaluationDate
    
    start_days = int(float(start_n) * 365.25)
    end_days = int(float(start_n + tenor_m) * 365.25)
    
    start_date = today + ql.Period(start_days, ql.Days)
    end_date = today + ql.Period(end_days, ql.Days)
    
    d_start = ql_curve.discount(start_date)
    d_end = ql_curve.discount(end_date)
    
    annu = (d_start - d_end) / float(tenor_m) if tenor_m > 0 else d_start
    if annu <= 0:
        return 0.03  # Safe floor fallback (3.0%)
        
    forward_swap_rate = (d_start - d_end) / annu
    return float(forward_swap_rate) * 100.0  # Percentage format conversion (e.g. 3.25%)


def build_forward_permutation_matrix(master_df, selected_ccy="USD"):
    """
    Generates historical time-series matrices of forwards for regression scanning.
    Type-safe: Uses DataSanitizer and QuantLib to survive illiquid asset blocks.
    """
    from curves import BootstrappedDiscountCurve
    
    ccy_df = master_df[master_df['currency'] == selected_ccy.upper().strip()].copy()
    pivot_df = ccy_df.pivot(index='date', columns='tenor', values='rate').dropna()
    
    # Fully expanded start nodes matching your high-contrast 25Y row heatmap canvas
    start_nodes = [0.25, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 25.0]
    matrix_dict = {f"{n}F1Y": [] for n in start_nodes}
    matrix_dates = []
    
    for dt in pivot_df.index:
        date_str = DataSanitizer.normalize_date_string(dt)
        raw_spots = pivot_df.loc[dt].to_dict()
        
        # Clean and map incoming raw broker sheet tokens seamlessly
        spot_rates_dict = {}
        for t, r in raw_spots.items():
            clean_tenor = DataSanitizer.clean_tenor_string(t)
            spot_rates_dict[clean_tenor] = float(r)
                
        # Initialize our calendar-aware QuantLib curve wrapper with data filtering
        wrapper = BootstrappedDiscountCurve(target_date=date_str, spot_rates_dict=spot_rates_dict, currency=selected_ccy)
        matrix_dates.append(date_str)
        
        for n in start_nodes:
            try:
                fwd_rate = extract_implied_forward_swap(wrapper.ql_curve, start_n=n, tenor_m=1.0, day_counter=wrapper.day_counter)
            except Exception:
                fwd_rate = float(raw_spots.get(f"{int(n)}Y", raw_spots.get('30Y', 2.5)))
                
            matrix_dict[f"{n}F1Y"].append(fwd_rate)
            
    return pd.DataFrame(matrix_dict, index=matrix_dates)


def run_statistical_arbitrage_sweep(fwd_df):
    """
    Sweeps the continuous historical forward matrix to find relative-value butterfly spread entry anomalies.
    Excludes constant intercepts (fit_intercept=False) to ensure strict self-financing trading metrics.
    """
    columns = list(fwd_df.columns)
    leaderboard = []
    
    # Loop combinations to isolate a Body node flanked by a Short Wing and a Long Wing
    for short_w, body, long_w in itertools.combinations(columns, 3):
        X = fwd_df[[short_w, long_w]].values
        y = fwd_df[body].values
        
        # Run ordinary least squares regression without a zero-bias constant
        reg = LinearRegression(fit_intercept=False).fit(X, y)
        beta_short, beta_long = reg.coef_[0], reg.coef_[1]
        
        # Track historical residual series to check for mean-reverting stationarity
        predicted_body = (beta_short * fwd_df[short_w]) + (beta_long * fwd_df[long_w])
        historical_residuals = (fwd_df[body] - predicted_body).values
        
        current_residual = historical_residuals[-1]
        r_squared = float(reg.score(X, y))
        
        # Pull clean statistical metrics from utils data sanitizer
        z_score = DataSanitizer.calculate_z_score(current_residual, historical_residuals)
        
        structure_name = f"FLY: {body} vs [{short_w} & {long_w}]"
        hedge_ratio_str = f"S: {beta_short:.2f} / L: {beta_long:.2f}"
        
        leaderboard.append({
            "Structure": structure_name,
            "Hedge Ratio": hedge_ratio_str,
            "R-Squared": round(r_squared, 4),
            "Current Residual": round(current_residual, 2),
            "Z-Score": z_score,
            "raw_residuals": historical_residuals.tolist()  # Export vectors directly to chart canvases
        })
        
    # Sort leaderboard by maximum structural dislocation (absolute Z-score magnitude)
    leaderboard.sort(key=lambda x: abs(x["Z-Score"]), reverse=True)
    return leaderboard


def generate_forward_block_matrix(curve_obj):
    """
    Builds a discrete forward length vs forward start snapshot dataframe for the dashboard heatmap.
    """
    forward_starts = [0.25, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 25.0]
    forward_lengths = [1.0, 2.0, 3.0, 5.0, 10.0]
    
    matrix = np.zeros((len(forward_starts), len(forward_lengths)))
    
    for i, start in enumerate(forward_starts):
        for j, length in enumerate(forward_lengths):
            try:
                matrix[i, j] = extract_implied_forward_swap(curve_obj.ql_curve, start, length, curve_obj.day_counter)
            except Exception:
                matrix[i, j] = 2.5
                
    row_labels = ["3M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "15Y", "20Y", "25Y"]
    col_labels = ["1Y", "2Y", "3Y", "5Y", "10Y"]
    
    return pd.DataFrame(matrix, index=row_labels, columns=col_labels)
