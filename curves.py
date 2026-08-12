# curves.py
import numpy as np
import pandas as pd

class BootstrappedDiscountCurve:
    r"""
    Layer 1: Precision Yield Curve Construction Engine.
    Ingests your complete G10 swap curve structure up to 30 Years.
    Sequentially bootstraps discount factors P(0, T) using log-linear decay
    to map gaps cleanly across unquoted structural horizons.
    """
    def __init__(self, target_date, spot_rates_dict):
        self.target_date = target_date
        
        # Explicit mapping of your 15 institutional market tenors
        self.tenor_map = {
            0.25: '3M', 1.0: '1Y', 2.0: '2Y', 3.0: '3Y', 4.0: '4Y', 
            5.0: '5Y',  6.0: '6Y', 7.0: '7Y', 8.0: '8Y', 9.0: '9Y', 
            10.0: '10Y', 12.0: '12Y', 15.0: '15Y', 20.0: '20Y', 
            25.0: '25Y', 30.0: '30Y'
        }
        self.maturities = sorted(list(self.tenor_map.keys()))
        self.spot_rates = spot_rates_dict  # e.g., {'3M': 4.5, '30Y': 5.2}
        
        # Force fill any missing intermediate tenors to protect bootstrap logic
        self._linear_interpolate_missing_spots()
        
        self.discount_factors = {}
        self.construct_piecewise_discount_curve()

    def _linear_interpolate_missing_spots(self):
        """
        Internal Guard Rail: Fills missing intermediate tenors (like 6Y, 8Y, 9Y)
        via linear interpolation to protect cumulative bootstrap loops.
        """
        known_tenors = []
        known_rates = []
        
        for t, label in self.tenor_map.items():
            if label in self.spot_rates and self.spot_rates[label] > 0.0:
                known_tenors.append(t)
                known_rates.append(self.spot_rates[label])
                
        if not known_tenors:
            return
            
        for t, label in self.tenor_map.items():
            if label not in self.spot_rates or self.spot_rates[label] == 0.0:
                # Interpolate from nearest known coordinates
                interpolated_rate = np.interp(t, known_tenors, known_rates)
                self.spot_rates[label] = float(interpolated_rate)

    def construct_piecewise_discount_curve(self):
        r"""
        Executes a piecewise bootstrap sequence.
        Solves for discrete nodes and handles wide long-end gaps.
        Formula: P(0, T) = (1 - R_T * \sum P(0, t_i)) / (1 + R_T)
        """
        self.discount_factors[0.0] = 1.0
        
        # 1. Money Market Node (3M Cash) - Convert percentage rate to decimal fraction
        r_3m = self.spot_rates.get('3M', 0.0) / 100.0
        self.discount_factors[0.25] = 1.0 / (1.0 + r_3m * 0.25)
        
        # 2. Sequential Bootstrapping Loop
        for t in self.maturities:
            if t == 0.25:
                continue
                
            r_t = self.spot_rates.get(self.tenor_map[t], 0.0) / 100.0
            
            # For tightly quoted continuous annual tenors (1Y through 10Y)
            if t <= 10.0:
                sum_prev_discounts = sum([self.discount_factors[prev] for prev in self.maturities if prev < t and prev > 0.25])
                self.discount_factors[t] = (1.0 - r_t * sum_prev_discounts) / (1.0 + r_t)
            
            # For sparse long-end broker tenors (12Y, 15Y, 20Y, 25Y, 30Y)
            else:
                prev_t = max([n for n in self.maturities if n < t])
                gap = t - prev_t
                
                r_prev = self.spot_rates.get(self.tenor_map[prev_t], 0.0) / 100.0
                approx_r_step = r_prev + ((r_t - r_prev) / gap)
                
                self.discount_factors[t] = self.discount_factors[prev_t] * np.exp(-approx_r_step * gap)

    def get_discount_factor(self, T):
        r"""
        Exposes continuous log-linear discount factors P(0, T) for any arbitrary year fraction T.
        Essential for pricing custom options or forward start maturities.
        """
        if T in self.discount_factors:
            return self.discount_factors[T]
        if T < 0.0:
            return 1.0
        if T > 30.0:
            return self.discount_factors[30.0] * np.exp(-(self.spot_rates.get('30Y', 0.0) / 100.0) * (T - 30.0))
            
        known_nodes = sorted(list(self.discount_factors.keys()))
        t_left = max([n for n in known_nodes if n <= T])
        t_right = min([n for n in known_nodes if n >= T])
        
        p_left = self.discount_factors[t_left]
        p_right = self.discount_factors[t_right]
        
        weight = (T - t_left) / (t_right - t_left)
        return p_left * (p_right / p_left) ** weight

    def get_annuity_factor(self, start_n, tenor_m, payment_freq=1.0):
        r"""
        Calculates the exact Annuity Factor (A_0) or PVBP across a forward contract window.
        Formula: A_0 = \sum_{i=1}^{M} \tau_i * P(0, n + i)
        """
        annuity = 0.0
        steps = int(tenor_m * payment_freq)
        time_step = 1.0 / payment_freq
        
        for i in range(1, steps + 1):
            payment_time = start_n + (i * time_step)
            annuity += time_step * self.get_discount_factor(payment_time)
            
        return annuity
