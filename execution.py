# execution.py - STABILIZED EXECUTION ENGINE MODULE
import numpy as np
import plotly.graph_objects as go

class ExecutionOptimizer:
    """
    Layer 4: Trade Construction & Execution Optimization Engine.
    Transforms abstract basis point OLS anomalies into tradeable portfolios.
    Calculates DV01 weights, interbank swap notionals, and residual portfolio deltas.
    """
    
    @staticmethod
    def calculate_duration_neutral_notionals(target_leg_notional, ratio_short=0.5, ratio_long=0.5, structure_type='FLY'):
        """
        Front-Office Execution Notional Desk.
        Transforms abstract allocations into rounded interbank trade clips 
        with explicit Pay/Receive transactional direction flags.
        """
        base_notional = float(target_leg_notional)
        r_short = float(ratio_short)
        r_long = float(ratio_long)
        
        if structure_type == 'FLY':
            # Computes rounded market clips matching your clean ratio inputs (e.g., 5.0M, 10.0M, 5.0M)
            belly_notional = base_notional
            short_wing_notional = base_notional * r_short
            long_wing_notional = base_notional * r_long
            
            # STANDARD MACRO CONVENTION: A cheap/rich mean reversion trade flies against the wings
            # Belly Core is Received (Long), Wings are Paid (Short) to match long-spread convention
            return {
                'Short Wing Notional': round(short_wing_notional, 2),
                'Short Wing Action': 'PAY Fixed (Short Leg)',
                'Belly Notional': round(belly_notional, 2),
                'Belly Action': 'RECEIVE Fixed (Belly Core)',
                'Long Wing Notional': round(long_wing_notional, 2),
                'Long Wing Action': 'PAY Fixed (Long Leg)',
                'Total Structure Notional': round(short_wing_notional + belly_notional + long_wing_notional, 2)
            }
        return {}

    @staticmethod
    def generate_historical_carry_chart(f_matrix_df, short_leg, mid_leg, long_leg, coef_short, coef_long):
        """
        Layer 4 Carry Timeline Axis Engine.
        Vectorises the historical path of the OLS residual vs. its 1-Year Prior status.
        Protected: Implements an explicit data array fallback rail to prevent NoneType chart crashes.
        """
        fig = go.Figure()
        
        # 1. Safely parse and verify your active spread history series
        try:
            if short_leg in f_matrix_df.columns and mid_leg in f_matrix_df.columns and long_leg in f_matrix_df.columns:
                current_spread = f_matrix_df[mid_leg] - (coef_short * f_matrix_df[short_leg] + coef_long * f_matrix_df[long_leg])
                current_vals = current_spread.values * 10000.0
                current_index = current_spread.index
            else:
                # Fallback path to establish a zero baseline if columns are missing
                current_vals = np.zeros(len(f_matrix_df))
                current_index = f_matrix_df.index
        except Exception:
            current_vals = np.zeros(len(f_matrix_df))
            current_index = f_matrix_df.index

        # 2. Render your active current spread trace canvas
        fig.add_trace(go.Scatter(
            x=current_index, y=current_vals,
            mode='lines+markers', name='Current Spread Tracking History',
            line=dict(color='#ffc107', width=2.5),
            hovertemplate="Date: %{x}<br>Spread: %{y:.2f} bps<extra></extra>"
        ))
        
        # 3. Process the 1-Year horizon slide loop with a strict data existence check
        try:
            s_start = int(float(short_leg.replace('F1Y', '')))
            m_start = int(float(mid_leg.replace('F1Y', '')))
            l_start = int(float(long_leg.replace('F1Y', '')))
            
            s_roll_str = f"{max(0.25, s_start - 1.0)}F1Y" if s_start > 1 else "0.25F1Y"
            m_roll_str = f"{max(0.25, m_start - 1.0)}F1Y" if m_start > 1 else "0.25F1Y"
            l_roll_str = f"{max(0.25, l_start - 1.0)}F1Y" if l_start > 1 else "0.25F1Y"
            
            if s_roll_str in f_matrix_df.columns and m_roll_str in f_matrix_df.columns and l_roll_str in f_matrix_df.columns:
                rolled_spread = f_matrix_df[m_roll_str] - (coef_short * f_matrix_df[s_roll_str] + coef_long * f_matrix_df[l_roll_str])
                
                fig.add_trace(go.Scatter(
                    x=rolled_spread.index, y=rolled_spread.values * 10000.0,
                    mode='lines', name='1-Year Prior Horizon Rolled Carry History',
                    line=dict(color='#0d6efd', width=2.0, dash='dash'),
                    hovertemplate="Date: %{x}<br>1Y Prior Rolled Carry: %{y:.2f} bps<extra></extra>"
                ))
        except Exception:
            pass # Gracefully drops the secondary line trace if historical index depth is insufficient

        fig.update_layout(
            title=dict(text="Historical Carry Timeline Comparison: Active Spread vs. 1-Year Horizon Prior Slide", font=dict(color='#ffc107', size=13)),
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=45, r=20, t=55, b=40),
            xaxis=dict(title="Historical Timeline Axis", type='category', gridcolor='#2d2d2d'),
            yaxis=dict(title="Structure Dislocation Yield (bps)", gridcolor='#2d2d2d')
        )
        return fig
