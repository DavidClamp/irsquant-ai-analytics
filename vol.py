# vol.py - UPGRADED CALIBRATED STOCHASTIC VOLATILITY ENGINE
import numpy as np
import pandas as pd
from scipy.stats import norm

class Black76Engine:
    """
    Layer 3: Non-Linear Options Pricing Core.
    Implements Black '76 formulas alongside Hagan's analytic SABR model approximation.
    Consolidated and optimized under a single static namespace layout.
    """
    @staticmethod
    def calculate_swaption_price(forward_swap, strike, annuity, vol, expiry_T, option_type='CALL'):
        if expiry_T <= 0 or vol <= 0:
            return max(0.0, (forward_swap - strike) * annuity if option_type == 'CALL' else (strike - forward_swap) * annuity)
            
        d1 = (np.log(forward_swap / strike) + 0.5 * (vol ** 2) * expiry_T) / (vol * np.sqrt(expiry_T))
        d2 = d1 - vol * np.sqrt(expiry_T)
        
        if option_type == 'CALL':
            return annuity * (forward_swap * norm.cdf(d1) - strike * norm.cdf(d2))
        return annuity * (strike * norm.cdf(-d2) - forward_swap * norm.cdf(-d1))

    @staticmethod
    def calculate_hagan_sabr_vol(F, K, expiry_T, alpha, beta, rho, nu):
        """
        Implements Hagan's analytic approximation for log-normal SABR implied volatility.
        Stabilized: Handles percentage-space variables to eliminate central node spikes.
        """
        if F <= 0 or K <= 0 or expiry_T <= 0:
            return alpha
            
        # Handle the exact ATM boundary condition using percentage space parameters
        if abs(F - K) < 1e-4:
            f_K = F ** (beta - 1.0)
            I0 = alpha * f_K
            I1 = ((1.0 - beta) ** 2 / 24.0 * alpha ** 2 / (F ** (2.0 - 2.0 * beta)) + 
                  0.25 * rho * beta * alpha * nu / (F ** (1.0 - beta)) + 
                  (2.0 - 3.0 * rho ** 2) / 24.0 * nu ** 2)
            # Re-scale to match your baseline log-normal input dimension (atm_vol)
            return (I0 * (1.0 + I1 * expiry_T)) / F
            
        # General out-of-the-money (OTM) calculation loop path
        log_f_K = np.log(F / K)
        f_K = (F * K) ** (0.5 * (beta - 1.0))
        x = (nu / alpha) * f_K * log_f_K
        
        # Calculate Hagan's auxiliary Z-parameter value block
        zeta = (nu / alpha) * ((F * K) ** (0.5 * (1.0 - beta))) * log_f_K
        
        # Map out market tail coordinates safely
        denominator = f_K * (1.0 + (log_f_K ** 2) / 24.0 * (1.0 - beta) ** 2 + (log_f_K ** 4) / 1920.0 * (1.0 - beta) ** 4)
        
        # Calculate the stochastic vol backbone geometry layer
        numerator_term = 1.0 + (((1.0 - beta) ** 2 / 24.0) * (alpha ** 2 / ((F * K) ** (1.0 - beta))) + 
                                (0.25 * rho * beta * nu * alpha / f_K) + 
                                ((2.0 - 3.0 * rho ** 2) / 24.0) * (nu ** 2)) * expiry_T
                                
        if abs(x) < 1e-5:
            return (alpha / denominator) * numerator_term
            
        fx = np.log((np.sqrt(1.0 - 2.0 * rho * zeta + zeta ** 2) + zeta - rho) / (1.0 - rho))
        return (alpha / denominator) * (zeta / fx) * numerator_term

    @staticmethod
    def generate_sabr_vs_quadratic_smiles(forward_swap, atm_vol, expiry_T):
        """
        Generates side-by-side comparative volatility curves: Parametric vs Stochastic (SABR).
        Calibrated: Operates strictly in absolute decimal space to ensure smooth smile skew geometry.
        """
        strike_offsets = np.array([-200, -100, -50, 0, 50, 100, 200]) / 10000.0
        # Strikes are maintained as clean mathematical decimal coordinates (e.g. 0.04993)
        strikes = (forward_swap / 100.0) + strike_offsets
        fwd_dec = forward_swap / 100.0
        
        # Standard G4 Volatility Backbone Calibration weights
        beta = 0.50   # Log-normal to normal blending ratio marker
        rho = -0.35   # Receiver risk premium tilt parameter
        nu = 0.40     # Vol-of-vol curve curvature weight
        
        # CALIBRATION HARMONIZATION: Scale alpha uniformly into absolute decimal coordinate space
        alpha = atm_vol * (fwd_dec) ** (1.0 - beta)
        
        quad_vols = []
        sabr_vols = []

        for K in strikes:
            dK = K - fwd_dec
            # 1. Quadratic Polynomial Loop Path
            quad_vols.append(max(0.01, atm_vol + (-0.05) * dK + 0.15 * (dK ** 2)))
            
            # 2. Stochastic SABR Loop Path (Scale F and K to percentages to stabilize coordinates)
            sabr_vols.append(max(0.01, Black76Engine.calculate_hagan_sabr_vol(forward_swap, K * 100.0, expiry_T, alpha, beta, rho, nu)))
            
        labels = ["-200bps", "-100bps", "-50bps", "ATM", "+50bps", "+100bps", "+200bps"]
        return dict(zip(labels, strikes)), dict(zip(labels, quad_vols)), dict(zip(labels, sabr_vols))

    @staticmethod
    def generate_volatility_term_structure_grid(atm_vol):
        """
        Generates an institutional 3D Volatility Term Structure Surface Grid Matrix.
        Maps Liquid Option Expiries (Rows) vs Underlying Forward Swap Lengths (Columns).
        """
        expiries = ["3M", "6M", "1Y", "2Y", "5Y", "10Y"]
        tenors = ["1Y", "2Y", "3Y", "5Y", "10Y"]
        
        grid_df = pd.DataFrame(index=expiries, columns=tenors, dtype=float)
        
        # Implements a standard square-root of time decaying front-office vol surface matrix
        expiry_years = {"3M": 0.25, "6M": 0.5, "1Y": 1.0, "2Y": 2.0, "5Y": 5.0, "10Y": 10.0}
        tenor_years = {"1Y": 1.0, "2Y": 2.0, "3Y": 3.0, "5Y": 5.0, "10Y": 10.0}
        
        for exp in expiries:
            for ten in tenors:
                t_exp = expiry_years[exp]
                t_ten = tenor_years[ten]
                # Simulates typical market term structure decay across long option horizons
                decay_factor = np.exp(-0.03 * t_exp) * (1.0 + 0.02 * np.log(t_ten))
                grid_df.loc[exp, ten] = round(atm_vol * decay_factor * 100, 2)
                
        return grid_df
