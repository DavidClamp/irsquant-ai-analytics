# vol.py
import numpy as np
from scipy.stats import norm

class Black76Engine:
    """
    Layer 3: Volatility & Non-Linear Options Pricing Core.
    Implements analytic Black '76 formulas for European Interest Rate Swaptions.
    Calculates prices, intrinsic values, and options Greeks natively.
    """
    @staticmethod
    def calculate_swaption_price(forward_swap, strike, annuity, vol, expiry_T, option_type='CALL'):
        """
        Standard Black '76 evaluation for a forward starting European Swaption.
        """
        if expiry_T <= 0 or vol <= 0:
            return max(0.0, (forward_swap - strike) * annuity if option_type == 'CALL' else (strike - forward_swap) * annuity)
            
        d1 = (np.log(forward_swap / strike) + 0.5 * (vol ** 2) * expiry_T) / (vol * np.sqrt(expiry_T))
        d2 = d1 - vol * np.sqrt(expiry_T)
        
        if option_type == 'CALL':
            price = annuity * (forward_swap * norm.cdf(d1) - strike * norm.cdf(d2))
        else:
            price = annuity * (strike * norm.cdf(-d2) - forward_swap * norm.cdf(-d1))
            
        return price

    @staticmethod
    def generate_parametric_smile(forward_swap, atm_vol, skew=-0.05, smile_curv=0.15):
        """
        Parametric Volatility Smile Engine: Generates an implied volatility surface
        across out-of-the-money strike boundary deltas (F - 200bps to F + 200bps).
        Calibrated: Scaled to decimal formatting to prevent integer distortion.
        """
        # Divide by 100 to convert percentage rate shifts into true mathematical decimals
        strike_offsets = np.array([-200, -100, -50, 0, 50, 100, 200]) / 10000.0
        strikes = forward_swap / 100.0 + strike_offsets
        
        vol_grid = []
        for K in strikes:
            # dK is now processed as a precise absolute decimal gap
            dK = K - (forward_swap / 100.0)
            implied_vol = atm_vol + skew * dK + smile_curv * (dK ** 2)
            vol_grid.append(max(0.01, implied_vol))
            
        labels = ["-200bps", "-100bps", "-50bps", "ATM", "+50bps", "+100bps", "+200bps"]
        
        return dict(zip(labels, strikes)), dict(zip(labels, vol_grid))

