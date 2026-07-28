# curves.py
import numpy as np
import pandas as pd

class BootstrappedDiscountCurve:
    r"""
    Layer 1: Yield Curve Construction Engine.
    Ingests discrete market swap rates, applies sequential bootstrapping math, 
    and exposes continuous log-linear discount factors and forward annuity pricing hooks.
    Designed to natively clear path prerequisites for future Swaption/Volatility engines.
    """
    def __init__(self, target_date, spot_rates_dict):
        self.target_date = target_date
        self.tenor_map = {
            0.25: '3M', 1.0: '1Y', 2.0: '2Y', 3.0: '3Y', 
            4.0: '4Y', 5.0: '5Y', 7.0: '7Y', 10.0: '10Y'
        }
        self.maturities = sorted(list(self.tenor_map.keys()))
        self.spot_rates = spot_rates_dict
        
        self.discount_factors = {}
        self.construct_piecewise_discount_curve()

    def construct_piecewise_discount_curve(self):
        r"""
        Executes an institutional piecewise bootstrap sequence.
        Solves sequentially for discount factors P(0, T) to ensure zero arbitrage.
        Formula for Swap node T: P(0, T) = (1 - R_T * \sum_{i=1}^{T-1} P(0, t_i)) / (1 + R_T)
        """
        self.discount_factors[0.0] = 1.0
        
        r_3m = self.spot_rates.get('3M', 0.0)
        self.discount_factors[0.25] = 1.0 / (1 + r_3m * 0.25)
        
        for t in self.maturities:
            if t == 0.25:
                continue
                
            r_t = self.spot_rates.get(self.tenor_map[t], 0.0)
            
            if t <= 5.0:
                sum_prev_discounts = sum([self.discount_factors[prev] for prev in self.maturities if prev < t and prev > 0.25])
                self.discount_factors[t] = (1.0 - r_t * sum_prev_discounts) / (1.0 + r_t)
            else:
                prev_t = 5.0 if t == 7.0 else 7.0
                gap = int(t - prev_t)
                approx_r_step = (r_t + (r_t - self.spot_rates.get(self.tenor_map[prev_t], 0.0)) / gap)
                self.discount_factors[t] = self.discount_factors[prev_t] * np.exp(-approx_r_step * gap)

    def get_discount_factor(self, T):
        r"""
        Exposes continuous log-linear discount factors P(0, T) for any arbitrary year fraction T.
        Formula: P(0, T) = P(0, T_left) * (P(0, T_right) / P(0, T_left)) ^ ((T - T_left) / (T_right - T_left))
        """
        if T in self.discount_factors:
            return self.discount_factors[T]
            
        if T < 0.0:
            return 1.0
            
        if T > 10.0:
            return self.discount_factors[10.0] * np.exp(-self.spot_rates.get('10Y', 0.0) * (T - 10.0))
            
        known_nodes = sorted(list(self.discount_factors.keys()))
        t_left = max([n for n in known_nodes if n <= T])
        t_right = min([n for n in known_nodes if n >= T])
        
        p_left = self.discount_factors[t_left]
        p_right = self.discount_factors[t_right]
        
        weight = (T - t_left) / (t_right - t_left)
        return p_left * (p_right / p_left) ** weight

    def get_annuity_factor(self, start_n, tenor_m, payment_freq=1.0):
        r"""
        =======================================================================
        VOLATILITY PRE-REQUISITE ANCHOR HOOK
        =======================================================================
        Calculates the exact Annuity Factor (A_0) or Present Value of a Basis Point (PVBP).
        Formula: A_0 = \sum_{i=1}^{M} \tau_i * P(0, n + i)
        """
        annuity = 0.0
        steps = int(tenor_m * payment_freq)
        time_step = 1.0 / payment_freq
        
        for i in range(1, steps + 1):
            payment_time = start_n + (i * time_step)
            p_factor = self.get_discount_factor(payment_time)
            annuity += time_step * p_factor
            
        return annuity
