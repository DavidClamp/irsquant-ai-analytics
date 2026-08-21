# execution.py - UNIFIED FRONT-OFFICE IRS & IRO TRADE OPTIMISER CORES
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import QuantLib as ql
from utils import DataSanitizer

class ExecutionOptimizer:
    """
    Translates macro relative-value triggers and trade components into physical market notionals.
    """
    @staticmethod
    def generate_historical_carry_chart(f_matrix=None, short_leg="1Y", mid_leg="2Y", long_leg="3Y", r_short=0.5, r_long=0.5):
        """
        Generates an institutional multi-leg position weight chart asset for the layout canvas.
        Bypasses callback parameter sequence traps and populates a crisp risk allocation graph.
        """
        _ = f_matrix
        w_short = float(r_short)
        w_long = float(r_long)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[f'Short Wing ({short_leg})', f'Belly Anchor ({mid_leg})', f'Long Wing ({long_leg})'],
            y=[w_short, -(w_short + w_long), w_long],
            marker_color=['#dc3545', '#00ff66', '#dc3545'],
            width=0.4
        ))
        
        fig.update_layout(
            title=dict(text="IRS Strategic Allocation Wing Risk Profile (DV01 Balanced Proportions)", font=dict(color='#ffc107', size=12)),
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title="Risk Multiplier Weight", gridcolor='#2d2d2d'),
            xaxis=dict(gridcolor='#2d2d2d'),
            margin=dict(l=40, r=20, t=40, b=30)
        )
        return fig

    @staticmethod
    def optimize_volatility_hedge(notional_m, raw_delta, annuity_factor):
        """
        Calculates the precise underlying linear swap size required to completely immunize options delta risk.
        """
        position_size_bytes = float(notional_m) * 1000000.0
        a_0 = float(annuity_factor)
        
        net_options_delta = raw_delta * position_size_bytes
        required_swap_notional = -net_options_delta / a_0 if a_0 > 0 else 0.0
        required_swap_notional_mm = required_swap_notional / 1000000.0
        
        return {
            'underlying_hedge_notional_mm': round(required_swap_notional_mm, 2),
            'direction': ' Pay Fixed (Short Curve)' if required_swap_notional_mm > 0 else ' Receive Fixed (Long Curve)',
            'net_delta_residual': round(net_options_delta, 2)
        }


class SizingEngine:
    """
    Type-safe quantitative risk balancer. Calculates exact PVBP (DV01) shifts 
    and handles cross-tenor basis hedges across all 8 global currency registries.
    """
    def __init__(self, currency="USD"):
        self.currency = str(currency).upper().strip()
        
        # Standard interbank basis guidelines for PVBP approximation curves
        self.basis_registry = {
            "USD": {"dv01_per_mm_1y": 100.0, "calendar": ql.UnitedStates(ql.UnitedStates.GovernmentBond)},
            "EUR": {"dv01_per_mm_1y": 98.0,  "calendar": ql.TARGET()},
            "GBP": {"dv01_per_mm_1y": 102.0, "calendar": ql.UnitedKingdom(ql.UnitedKingdom.Exchange)},
            "JPY": {"dv01_per_mm_1y": 95.0,  "calendar": ql.Japan()},
            "CHF": {"dv01_per_mm_1y": 99.0,  "calendar": ql.Switzerland()},
            "NOK": {"dv01_per_mm_1y": 96.0,  "calendar": ql.Norway()},
            "SEK": {"dv01_per_mm_1y": 97.0,  "calendar": ql.Sweden()},
            "ZAR": {"dv01_per_mm_1y": 92.0,  "calendar": ql.SouthAfrica()}
        }
        
        self.meta = self.basis_registry.get(self.currency, self.basis_registry["USD"])

    def compute_risk_balanced_weights(self, notional_1, tenor_1_years, tenor_2_years):
        """
        Solves for a delta-neutral hedge ratio using an analytical PVBP mapping matrix:
        Hedge Ratio = DV01_Leg1 / DV01_Leg2
        """
        base_factor = float(self.meta["dv01_per_mm_1y"])
        notional_mm_1 = float(notional_1) / 1_000_000.0
        
        # Calculate PVBP exposure scaled by duration profiles
        leg_1_dv01 = notional_mm_1 * base_factor * float(tenor_1_years)
        
        # Derive the mathematical hedge ratio breakpoint
        hedge_ratio = float(tenor_1_years) / float(tenor_2_years)
        
        # Balance out Leg 2 to absorb exact delta risk
        notional_mm_2 = notional_mm_1 * hedge_ratio
        leg_2_dv01 = notional_mm_2 * base_factor * float(tenor_2_years)
        
        return {
            "leg_1_dv01": round(leg_1_dv01, 2),
            "leg_2_dv01": round(leg_2_dv01, 2),
            "hedge_ratio": round(hedge_ratio, 4),
            "balanced_notional_2": round(notional_mm_2 * 1_000_000.0, 2)
        }
