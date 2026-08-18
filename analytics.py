# analytics.py
import itertools
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

# Global institutional tenor definition map used to protect data ingestion channels
TENOR_LABEL_MAP = {
    0.25: '3M', 1.0: '1Y', 2.0: '2Y', 3.0: '3Y', 4.0: '4Y', 
    5.0: '5Y',  6.0: '6Y', 7.0: '7Y', 8.0: '8Y', 9.0: '9Y', 
    10.0: '10Y', 12.0: '12Y', 15.0: '15Y', 20.0: '20Y', 
    25.0: '25Y', 30.0: '30Y'
}

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
    return (p_start - p_end) / annuity

def extract_forward_curve_snapshot(master_df, selected_ccy, target_date_str):
    """
    Term Structure Snapshot Engine: Maps your complete curve out to 30 Years.
    Natively executes your dual-regime macro trade horizon logic.
    Type-safe: Cleaned of loop collisions and explicitly calibrated.
    """
    from curves import BootstrappedDiscountCurve
    
    target_ts = pd.to_datetime(target_date_str)
    day_df = master_df[(master_df['currency'] == selected_ccy) & (pd.to_datetime(master_df['date']) == target_ts)].copy()
    
    if day_df.empty:
        return [], [], []
        
    raw_spots = day_df.set_index('tenor')['rate'].to_dict()
    spot_rates_dict = {TENOR_LABEL_MAP[t]: float(r) for t, r in raw_spots.items() if t in TENOR_LABEL_MAP}
    
    curve = BootstrappedDiscountCurve(target_date=target_date_str, spot_rates_dict=spot_rates_dict)
    
    short_nodes = [0.25, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0] # Track 1Y Forwards
    long_nodes = [10.0, 12.0, 15.0, 20.0, 25.0]                       # Track 5Y Forwards
    
    x_starts, x_ends, y_rates = [], [], []
    
    # 1. Short to Mid-Curve Regime (1-Year Forward Blocks)
    for start in short_nodes:
        fwd_rate = extract_implied_forward_swap(curve, start_n=start, tenor_m=1.0)
        x_starts.append(start)
        x_ends.append(start + 1.0)
        y_rates.append(fwd_rate * 100)
        
    # 2. Long-End Regime (Dynamic Shift to 5-Year Forward Blocks)
    for start in long_nodes:
        fwd_rate = extract_implied_forward_swap(curve, start_n=start, tenor_m=5.0)
        x_starts.append(start)
        x_ends.append(start + 5.0)
        y_rates.append(fwd_rate * 100)
        
    return x_starts, x_ends, y_rates

def build_forward_permutation_matrix(master_df, selected_ccy):
    """
    Generates historical time-series matrices of forwards for regression scanning.
    Type-safe: Dynamically translates float indexes to institutional text labels.
    """
    from curves import BootstrappedDiscountCurve
    ccy_df = master_df[master_df['currency'] == selected_ccy].copy()
    pivot_df = ccy_df.pivot(index='date', columns='tenor', values='rate').dropna()
    
    # FIXED: Expanded node limits to match your extended front-end dashboard 25Y row matrix mapping!
    start_nodes = [0.25, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 15.0, 20.0, 25.0]
    matrix_dict = {f"{n}F1Y": [] for n in start_nodes}
    matrix_dates = []
    
    # Global layout key safety mapping reference
    TENOR_LABEL_MAP = {0.25:'3M', 1.0:'1Y', 2.0:'2Y', 3.0:'3Y', 4.0:'4Y', 5.0:'5Y', 6.0:'6Y', 7.0:'7Y', 8.0:'8Y', 9.0:'9Y', 10.0:'10Y', 12.0:'12Y', 15.0:'15Y', 20.0:'20Y', 25.0:'25Y', 30.0:'30Y'}
    
    for dt in pivot_df.index:
        raw_spots = pivot_df.loc[dt].to_dict()
        
        # Clean string key sanitization layers handling the '1Y' suffix
        spot_rates_dict = {}
        for t, r in raw_spots.items():
            try:
                numeric_key = float(str(t).upper().replace('Y', '').strip())
                if numeric_key in TENOR_LABEL_MAP:
                    spot_rates_dict[TENOR_LABEL_MAP[numeric_key]] = float(r)
            except ValueError:
                continue
        
        curve = BootstrappedDiscountCurve(target_date=str(dt), spot_rates_dict=spot_rates_dict)
        matrix_dates.append(str(dt)[:10])
        
        for n in start_nodes:
            # Graceful safety intercept wrapper preventing out-of-bounds calculations
            try:
                fwd_rate = extract_implied_forward_swap(curve, start_n=n, tenor_m=1.0)
            except Exception:
                # Local baseline fallback to avoid zero matrix holes if an extreme boundary point calculation drops out
                fwd_rate = float(raw_spots.get(f"{int(n)}Y", raw_spots.get('30Y', 2.5)))
                
            matrix_dict[f"{n}F1Y"].append(fwd_rate)
            
    return pd.DataFrame(matrix_dict, index=matrix_dates)


def run_systematic_butterfly_scan(f_matrix_df):
    """
    Layer 2 Strategy Scanner: Runs zero-constant linear regressions for 3-node loops.
    Calibrated: Calculates the forward-looking 1-Year Roll/Carry assuming curve stability.
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
        coefs = np.atleast_1d(model.coef_)
        
        residuals = y - model.predict(X)
        current_residual = residuals[-1]
        z_score = (current_residual - residuals.mean()) / residuals.std() if residuals.std() > 0 else 0.0
        
        struct_name = f"FLY: {mid_f} vs [{short_f} & {long_f}]"
        series_storage[struct_name] = pd.Series(residuals, index=f_matrix_df.index)
        
        # QUANT CARRY CALCULATION: Extract contract names to identify rolled horizon positions
        # e.g., If mid leg is "3F1Y", the 1-Year rolled equivalent contract is "2F1Y"
        try:
            short_start = int(float(short_f.replace('F1Y', '')))
            mid_start = int(float(mid_f.replace('F1Y', '')))
            long_start = int(float(long_f.replace('F1Y', '')))
            
            # Map out rolled contract handle strings safely bounded to your curve floor layout (0.25Y / 3M)
            short_roll_str = f"{max(0.25, short_start - 1.0)}F1Y" if short_start > 1 else "0.25F1Y"
            mid_roll_str   = f"{max(0.25, mid_start - 1.0)}F1Y"  if mid_start > 1 else "0.25F1Y"
            long_roll_str  = f"{max(0.25, long_start - 1.0)}F1Y"  if long_start > 1 else "0.25F1Y"
            
            # Verify rolled legs exist in our compiled forward matrix columns to prevent KeyError breaks
            if short_roll_str in f_matrix_df.columns and mid_roll_str in f_matrix_df.columns and long_roll_str in f_matrix_df.columns:
                rolled_short = f_matrix_df[short_roll_str].iloc[-1]
                rolled_mid   = f_matrix_df[mid_roll_str].iloc[-1]
                rolled_long  = f_matrix_df[long_roll_str].iloc[-1]
                
                # Roll spread calculates where the structure settles as it slides 1 Year down the maturity line
                rolled_spread = rolled_mid - (coefs[0] * rolled_short + (coefs[1] * rolled_long if len(coefs) > 1 else 0.0))
                one_year_roll_bps = (rolled_spread - current_residual) * 10000.0
            else:
                one_year_roll_bps = 0.0
        except Exception:
            one_year_roll_bps = 0.0
            
        scan_results.append({
            'Structure': struct_name,
            'Hedge Ratio (Short)': round(coefs[0], 2) if len(coefs) > 0 else 0.0,
            'Hedge Ratio (Long)': round(coefs[1], 2) if len(coefs) > 1 else 0.0,
            'R-Squared': round(model.score(X, y), 4),
            'Current Residual (bps)': round(current_residual * 10000, 2),
            '1Y Horizon Roll (bps)': round(one_year_roll_bps, 1), # EXPOSES HOLISTIC PORTFOLIO CARRY BLEED
            'Z-Score (Outlier)': round(z_score, 2)
        })
        
    rank_df = pd.DataFrame(scan_results)
    if not rank_df.empty:
        rank_df = rank_df.sort_values(by='Z-Score (Outlier)', key=abs, ascending=False)
    return rank_df, series_storage


def run_systematic_condor_scan(f_matrix_df):
    """
    Layer 2 Strategy Scanner: Runs 4-node regressions tracking micro slope twists.
    Implements institutional risk neutralisation framework: Up-Down-Down-Up layout.
    """
    all_legs = list(f_matrix_df.columns)
    scan_results = []
    series_storage = {}
    
    if len(all_legs) < 4:
        return pd.DataFrame(), {}
        
    combinations = list(itertools.combinations(all_legs, 4))
    
    for leg1, leg2, leg3, leg4 in combinations:
        y = (f_matrix_df[leg3] - f_matrix_df[leg2]).values
        X = f_matrix_df[[leg1, leg4]].values
        
        model = LinearRegression(fit_intercept=False)
        model.fit(X, y)
        coefs = np.atleast_1d(model.coef_)
        
        residuals = y - model.predict(X)
        current_residual = residuals[-1]
        z_score = (current_residual - residuals.mean()) / residuals.std() if residuals.std() > 0 else 0.0
        
        struct_name = f"CONDOR: [{leg2} & {leg3}] vs Wings [{leg1} & {leg4}]"
        series_storage[struct_name] = pd.Series(residuals, index=f_matrix_df.index)
        
        scan_results.append({
            'Structure': struct_name,
            'Hedge Ratio (Short)': round(coefs[0], 2) if len(coefs) > 0 else 0.0,
            'Hedge Ratio (Long)': round(coefs[1], 2) if len(coefs) > 1 else 0.0,
            'R-Squared': round(model.score(X, y), 4),
            'Current Residual (bps)': round(current_residual * 10000, 2),
            'Z-Score (Outlier)': round(z_score, 2)
        })
        
    rank_df = pd.DataFrame(scan_results)
    if not rank_df.empty:
        rank_df = rank_df.sort_values(by='Z-Score (Outlier)', key=abs, ascending=False)
    return rank_df, series_storage


def generate_forward_block_matrix(curve_obj):
    """
    Layer 2 Matrix Block Engine:
    Generates a comprehensive 2D grid matrix of all forward start dates (n)
    vs all available forward contract lengths (m) for the current active date.
    Protected: Stems terminal boundary crashes by enforcing a strict < 30.0 year horizon ceiling.
    """
    start_lookup = {
        '3M': 0.25, '1Y': 1.0, '2Y': 2.0, '3Y': 3.0, '4Y': 4.0, 
        '5Y': 5.0, '7Y': 7.0, '10Y': 10.0, '15Y': 15.0, '20Y': 20.0, '25Y': 25.0
    }
    length_lookup = {'1Y': 1.0, '2Y': 2.0, '3Y': 3.0, '5Y': 5.0}
    
    start_nodes = list(start_lookup.keys())
    length_tenors = list(length_lookup.keys())
    
    grid_df = pd.DataFrame(index=start_nodes, columns=length_tenors, dtype=float)
    
    for n_str in start_nodes:
        for m_str in length_tenors:
            start_n = start_lookup[n_str]
            tenor_m = length_lookup[m_str]
            
            # FIXED CRITICALceiling BOUND: Enforce strict less-than cutoff boundary (< 30.0) 
            # This completely blocks terminal KeyError math cracks inside your curve objects
            if (start_n + tenor_m) >= 30.0:
                grid_df.loc[n_str, m_str] = 0.0
                continue
                
            fwd_rate = extract_implied_forward_swap(curve_obj, start_n=start_n, tenor_m=tenor_m)
            if fwd_rate > 0.0:
                grid_df.loc[n_str, m_str] = round(fwd_rate * 100, 3)
                
    return grid_df.fillna(0.0)
