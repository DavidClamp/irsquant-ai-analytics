# vol.py - INSTITUTIONAL MULTI-ASSET IMPLIED VOLATILITY MATRIX CORE
import numpy as np
from scipy.stats import norm

class VolatilityModelEngine:
    """Analytical engine separating forward Swaptions from dense Cap/Floor structures."""
    
    @staticmethod
    def evaluate_swaption_leg(fwd_rate, strike, expiry, vol_pct, df, a_0, call_put='PUT'):
        """Computes premium and precise underlying swap delta for forward options."""
        t = max(float(expiry), 1e-6)
        sigma = max(float(vol_pct) / 100.0, 1e-6)
        f = max(float(fwd_rate) / 100.0, 1e-6)
        k = max(float(strike) / 100.0, 1e-6)
        
        d1 = (np.log(f / k) + 0.5 * (sigma ** 2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)
        
        if call_put.upper() == 'PUT':  # Receiver Swaption
            premium = a_0 * (k * norm.cdf(-d2) - f * norm.cdf(-d1))
            raw_delta = -a_0 * norm.cdf(-d1)
        else:  # Payer Swaption
            premium = a_0 * (f * norm.cdf(d1) - k * norm.cdf(d2))
            raw_delta = a_0 * norm.cdf(d1)
            
        vega = a_0 * f * np.sqrt(t) * norm.pdf(d1) * 0.01
        return {'premium': premium, 'raw_delta': raw_delta, 'vega': vega}

    @staticmethod
    def evaluate_cap_floor(fwd_rate_array, strike, tenors, vol_pct, df_array, call_put='CALL'):
        """Prices Caps/Floors as an aggregated chain of forward-starting Caplets/Floorlets."""
        strike_val = max(float(strike) / 100.0, 1e-6)
        sigma = max(float(vol_pct) / 100.0, 1e-6)
        
        total_premium = 0.0
        total_delta = 0.0
        
        # Loop through each discrete payment index window (e.g., quarterly or semi-annual resets)
        for i, t in enumerate(tenors):
            fwd = max(float(fwd_rate_array[i]) / 100.0, 1e-6)
            df = float(df_array[i])
            tau = 0.5  # Semi-annual fraction assumption standard
            
            d1 = (np.log(fwd / strike_val) + 0.5 * (sigma ** 2) * t) / (sigma * np.sqrt(t))
            d2 = d1 - sigma * np.sqrt(t)
            
            if call_put.upper() == 'CALL':  # Caplet
                opt_val = df * tau * (fwd * norm.cdf(d1) - strike_val * norm.cdf(d2))
                caplet_delta = df * tau * norm.cdf(d1)
            else:  # Floorlet
                opt_val = df * tau * (strike_val * norm.cdf(-d2) - fwd * norm.cdf(-d1))
                caplet_delta = -df * tau * norm.cdf(-d1)
                
            total_premium += opt_val
            total_delta += caplet_delta
            
        return {'premium': total_premium, 'raw_delta': total_delta}

class SABRCalibrator:
    """Parametric Hagan SABR smile process mapping function core."""
    @staticmethod
    def modified_hagan_vol(f, k, t, alpha, beta, rho, nu):
        f = max(f, 1e-6)
        k = max(k, 1e-6)
        log_fk = np.log(f / k) if abs(f - k) > 1e-5 else 1e-5
        f_mid = (f * k) ** (0.5 * (1.0 - beta))
        z = (nu / alpha) * f_mid * log_fk
        x_z = np.log((np.sqrt(1.0 - 2.0 * rho * z + z ** 2) + z - rho) / (1.0 - rho)) if abs(z) > 1e-5 else 1e-5
        
        num = alpha * (1.0 + (((1.0 - beta) ** 2 / 24.0) * (alpha ** 2 / f_mid ** 2) + 
                              (0.25 * rho * beta * nu * alpha / f_mid) + 
                              ((2.0 - 3.0 * rho ** 2) / 24.0 * nu ** 2)) * t)
        den = f_mid * (1.0 + ((1.0 - beta) ** 2 / 24.0) * log_fk ** 2)
        
        if abs(log_fk) < 1e-5:
            return (alpha / f_mid) * (1.0 + (((1.0 - beta) ** 2 / 24.0) * (alpha ** 2 / f_mid) + 0.25 * rho * beta * nu * alpha / (f_mid ** 0.5) + (2.0 - 3.0 * rho ** 2) / 24.0 * nu ** 2) * t) * 100.0
            
        # FIXED: Added stabilizer clamp to x_z lookup to guarantee total insulation against division crashes
        denom_clamp = x_z if abs(x_z) > 1e-7 else 1e-7
        return (num / den) * (z / denom_clamp) * 100.0
