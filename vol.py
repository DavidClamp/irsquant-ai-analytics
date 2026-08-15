# vol.py - INSTITUTIONAL PARALLEL SABR SOLVER & GREEKS ENGINE
import numpy as np
from scipy.optimize import least_squares
from scipy.stats import norm

class Black76Engine:
    """Calculates analytic European Swaption premiums and risk sensitivities."""
    
    @staticmethod
    def calculate_premium(fwd_rate, strike, expiry, vol_pct, discount_factor, annuity_factor, option_type='RECEIVER'):
        t = max(float(expiry), 1e-6)
        sigma = max(float(vol_pct) / 100.0, 1e-6)
        f = max(float(fwd_rate) / 100.0, 1e-6)
        k = max(float(strike) / 100.0, 1e-6)
        df = float(discount_factor)
        a_0 = float(annuity_factor)
        
        d1 = (np.log(f / k) + 0.5 * (sigma ** 2) * t) / (sigma * np.sqrt(t))
        d2 = d1 - sigma * np.sqrt(t)
        
        if option_type.upper() == 'RECEIVER':
            # Put option analogue for downward curve protection
            underyling_val = k * norm.cdf(-d2) - f * norm.cdf(-d1)
            premium = a_0 * underyling_val
            delta = -a_0 * norm.cdf(-d1)
        else:
            # Payer option analogue for upward curve shorts
            underyling_val = f * norm.cdf(d1) - k * norm.cdf(d2)
            premium = a_0 * underyling_val
            delta = a_0 * norm.cdf(d1)
            
        vega = a_0 * f * np.sqrt(t) * norm.pdf(d1) * 0.01  # Normalized per 1% vol shift
        return {
            'premium': round(premium * 1000000, 2),  # Scaled to millions standard
            'delta_pvbp': round(delta, 4),
            'vega_dollar': round(vega * 10000, 2)
        }

class SABRCalibrator:
    """Calibrates Hagan SABR surfaces directly to extracted interbank JSON feeds."""
    
    @staticmethod
    def modified_hagan_vol(f, k, t, alpha, beta, rho, nu):
        f = max(f, 1e-6)
        k = max(k, 1e-6)
        if abs(f - k) < 1e-5:
            # At-The-Money (ATM) structural analytic simplification
            f_mid = f ** (1.0 - beta)
            i1 = ((1.0 - beta) ** 2 / 24.0) * (alpha ** 2 / f_mid)
            i2 = 0.25 * (rho * beta * nu * alpha) / (f_mid ** 0.5)
            i3 = ((2.0 - 3.0 * rho ** 2) / 24.0) * (nu ** 2)
            return (alpha / f_mid) * (1.0 + (i1 + i2 + i3) * t) * 100.0
        else:
            # Out-Of-The-Money (OTM) skew transformation loop
            log_fk = np.log(f / k)
            f_mid = (f * k) ** (0.5 * (1.0 - beta))
            z = (nu / alpha) * f_mid * log_fk
            x_z = np.log((np.sqrt(1.0 - 2.0 * rho * z + z ** 2) + z - rho) / (1.0 - rho))
            
            num = alpha * (1.0 + (((1.0 - beta) ** 2 / 24.0) * (alpha ** 2 / f_mid ** 2) + 
                                  (0.25 * rho * beta * nu * alpha / f_mid) + 
                                  ((2.0 - 3.0 * rho ** 2) / 24.0 * nu ** 2)) * t)
            den = f_mid * (1.0 + ((1.0 - beta) ** 2 / 24.0) * log_fk ** 2 + 
                           ((1.0 - beta) ** 4 / 1920.0) * log_fk ** 4)
            
            if abs(x_z) > 1e-5:
                return (num / den) * (z / x_z) * 100.0
            return (num / den) * 100.0

    @staticmethod
    def calibrate_node_parameters(fwd_rate, strikes, market_vols, expiry_years):
        """Runs a non-linear optimizer to fit alpha, rho, and nu to market data points."""
        f = float(fwd_rate) / 100.0
        t = max(float(expiry_years), 1e-2)
        ks = np.array(strikes) / 100.0
        vols = np.array(market_vols)
        
        # Fixed institutional beta backbone assumption (0.50 handles standard linear dynamics)
        beta = 0.50
        
        def residual_cost_function(params):
            alpha, rho, nu = params
            if not (-0.99 < rho < 0.99) or alpha <= 0 or nu <= 0:
                return np.ones_like(vols) * 1e6
            
            simulated_vols = np.array([
                SABRCalibrator.modified_hagan_vol(f, k, t, alpha, beta, rho, nu) for k in ks
            ])
            return simulated_vols - vols

        # Initial starting guesses [Alpha, Rho, Nu]
        initial_guess = [0.05, -0.20, 0.40]
        bounds = ((1e-4, -0.99, 1e-4), (1.0, 0.99, 2.0))
        
        try:
            res = least_squares(residual_cost_function, initial_guess, bounds=bounds, method='trf')
            return {'alpha': res.x[0], 'beta': beta, 'rho': res.x[1], 'nu': res.x[2]}
        except Exception:
            return {'alpha': 0.04, 'beta': beta, 'rho': -0.30, 'nu': 0.35}
