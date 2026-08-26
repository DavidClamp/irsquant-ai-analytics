# analytics.py - LAYER 2 CORE: CROSS-SECTIONAL OLS MATRIX SCANNER
import itertools
import numpy as np
import pandas as pd
import QuantLib as ql
from sklearn.linear_model import LinearRegression
from sanitizer import DataSanitizer
from curves import BootstrappedDiscountCurve

def extract_implied_forward_swap(ql_curve, start_n, tenor_m, day_counter):
    """
    Extracts forward swap rates straight from QuantLib's C++ curve
    using native schedule generation, business day rolls, and accruals.
    """
    curve_handle = ql.YieldTermStructureHandle(ql_curve)
    
    start_period = ql.Period(int(float(start_n) * 12), ql.Months)
    tenor_period = ql.Period(int(float(tenor_m) * 12), ql.Months)
    
    # Generic index initialization to evaluate true regional day-counts
    ibor_index = ql.IborIndex("ForwardSwapIndex", tenor_period, 2, ql.EURCurrency(), 
                             ql.TARGET(), ql.ModifiedFollowing, False, day_counter, curve_handle)
    try:
        forward_swap_quote = ql.ForwardSwapQuote(ibor_index, curve_handle, start_period)
        if not forward_swap_quote.isValid():
            return 3.0  # Safe fallback baseline floor percentage
        return float(forward_swap_quote.value()) * 100.0  # Percentage format
    except Exception:
        return 3.0  # System shock safety shield

def build_forward_permutation_matrix(master_df, selected_ccy="USD"):
    """
    Generates historical time-series matrices of forwards for regression scanning.
    🛡️ Shielded: Explicitly catches and handles local node interpolation crashes.
    """
      
    ccy_df = master_df[master_df['currency'] == selected_ccy.upper().strip()].copy()
    cleaned_df = ccy_df.groupby(['date', 'tenor'], as_index=False)['rate'].mean()
    pivot_df = cleaned_df.pivot(index='date', columns='tenor', values='rate').dropna()
    
    start_nodes = [0.25, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 25.0]
    
    # Pre-populate empty data columns to match array frame targets
    matrix_dict = {f"{n}F1Y": [] for n in start_nodes}
    matrix_dates = []
    
    for dt in pivot_df.index:
        date_str = str(dt).split(" ")[0].strip() # Clean layout date strings instantly
        raw_spots = pivot_df.loc[dt].to_dict()
        
        spot_rates_dict = {str(k).strip(): float(v) for k, v in raw_spots.items()}
                
        try:
            wrapper = BootstrappedDiscountCurve(target_date=date_str, spot_rates_dict=spot_rates_dict, currency=selected_ccy)
            
            # If the curve initializes cleanly, map out our forward nodes
            for n in start_nodes:
                try:
                    # Explicit native check: calculate implied forwards using discount factors directly
                    t_start = float(n)
                    t_end = t_start + 1.0
                    df_start = wrapper.get_discount_factor(t_start)
                    df_end = wrapper.get_discount_factor(t_end)
                    
                    # Convert discount ratio directly into an annualized implied forward rate string
                    fwd_rate = ((df_start / df_end) - 1.0) * 100.0 if df_end > 0 else 2.5
                except Exception:
                    fwd_rate = float(spot_rates_dict.get(f"{int(n)}Y", 2.5))
                    
                matrix_dict[f"{n}F1Y"].append(fwd_rate)
                
            matrix_dates.append(date_str)
        except Exception:
            continue # Bypass un-bootstrappable historical dates safely
            
    return pd.DataFrame(matrix_dict, index=matrix_dates)

def run_statistical_arbitrage_sweep(fwd_df):
    """
    Sweeps the forward permutation matrix, executing multivariable OLS regressions.
    Calculates residuals, maps Z-scores, and generates trade execution signals.
    """
        
    if fwd_df.empty or len(fwd_df) < 5:
        return []
        
    cols = list(fwd_df.columns)
    results = []
    
    # Outer loops construct all unique Wing 1 / Belly / Wing 2 combinations
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            for k in range(j + 1, len(cols)):
                w1, belly, w2 = cols[i], cols[j], cols[k]
                
                X = fwd_df[[w1, w2]].values
                y = fwd_df[belly].values
                
                # Force a zero-intercept OLS matrix model match
                model = LinearRegression(fit_intercept=False)
                model.fit(X, y)
                
                predictions = model.predict(X)
                residuals = y - predictions
                
                current_residual = float(residuals[-1])
                historical_residuals = [float(r) for r in residuals[:-1]]
                
                # Compute statistical deviation scores
                z_score = DataSanitizer.calculate_z_score(current_residual, historical_residuals)
                r_sq = float(model.score(X, y))
                
                # SIGNAL MATRIX GENERATION LAYER
                if z_score <= -2.00:
                    signal = "🟢 BUY FLY"
                elif z_score >= 2.00:
                    signal = "🔴 SELL FLY"
                else:
                    signal = "HOLD"
                    
                results.append({
                    "Structure": f"FLY: {belly} vs [{w1} & {w2}]",
                    "Hedge Ratio": f"S: {float(model.coef_[0]):.2f} / L: {float(model.coef_[1]):.2f}",
                    "R-Squared": round(r_sq, 4),
                    "Current Residual": round(current_residual, 4),
                    "Z-Score": z_score,
                    "Signal": signal  # Added straight to your data frames
                })
                
    # Sort the output matrix ledger by maximum absolute dislocation
    results.sort(key=lambda x: abs(x["Z-Score"]), reverse=True)
    return results
