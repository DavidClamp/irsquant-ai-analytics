# execution.py - FRONT OFFICE PRINCIPAL SIZING ENGINE
import plotly.graph_objects as go
import numpy as np

class ExecutionOptimizer:
    """
    Layer 4: Trade Construction & Execution Optimization Engine.
    Converts targeted basis-point risk allocations ($ PVBP) into exact
    interbank swap principal notionals in Millions ($mm) at their specific forward rates.
    """
    
    @staticmethod
    def calculate_front_office_ticket(curve_obj, target_dv01, short_leg, mid_leg, long_leg, r_short=0.5, r_long=0.5):
        """
        Calculates exact swap notionals in millions ($mm) required to express a target DV01 risk.
        Extracts individual forward swap interest rates and solves for net structure spread.
        """
        # Parse tenors cleanly from standard format handles (e.g. "1F1Y")
        t_short = float(short_leg.replace('F1Y', ''))
        t_mid = float(mid_leg.replace('F1Y', ''))
        t_long = float(long_leg.replace('F1Y', ''))
        
        # 1. Compute Annuity Factors (PVBP per $1mm Notional = Annuity * 100)
        a_short = curve_obj.get_annuity_factor(start_n=t_short, tenor_m=1.0, payment_freq=1.0)
        a_mid   = curve_obj.get_annuity_factor(start_n=t_mid, tenor_m=1.0, payment_freq=1.0)
        a_long  = curve_obj.get_annuity_factor(start_n=t_long, tenor_m=1.0, payment_freq=1.0)
        
        pvbp_short_per_mm = a_short * 100.0
        pvbp_mid_per_mm   = a_mid * 100.0
        pvbp_long_per_mm  = a_long * 100.0
        
        # 2. Allocate targeted dollar risk across structural positions
        dv01_mid_target = float(target_dv01)
        dv01_short_target = dv01_mid_target * float(r_short)
        dv01_long_target = dv01_mid_target * float(r_long)
        
        # 3. Convert target dollar risk to actual Forward Swap Notional in Millions ($mm)
        notional_short_mm = dv01_short_target / pvbp_short_per_mm if pvbp_short_per_mm > 0 else 0.0
        notional_mid_mm   = dv01_mid_target / pvbp_mid_per_mm if pvbp_mid_per_mm > 0 else 0.0
        notional_long_mm  = dv01_long_target / pvbp_long_per_mm if pvbp_long_per_mm > 0 else 0.0
        
        # 4. Extract continuous forward swap interest rates from discount structures
        p_s_start, p_s_end = curve_obj.get_discount_factor(t_short), curve_obj.get_discount_factor(t_short + 1.0)
        f_short = ((p_s_start - p_s_end) / a_short) * 100.0 if a_short > 0 else 0.0
        
        p_m_start, p_m_end = curve_obj.get_discount_factor(t_mid), curve_obj.get_discount_factor(t_mid + 1.0)
        f_mid = ((p_m_start - p_m_end) / a_mid) * 100.0 if a_mid > 0 else 0.0
        
        p_l_start, p_l_end = curve_obj.get_discount_factor(t_long), curve_obj.get_discount_factor(t_long + 1.0)
        f_long = ((p_l_start - p_l_end) / a_long) * 100.0 if a_long > 0 else 0.0
        
        # 5. Resolve net weighted butterfly structural yield spread in basis points (bps)
        net_spread_bps = (f_mid - (float(r_short) * f_short + float(r_long) * f_long)) * 100.0
        
        return {
            'notional_short_mm': round(notional_short_mm, 2),
            'rate_short': round(f_short, 3),
            'notional_mid_mm': round(notional_mid_mm, 2),
            'rate_mid': round(f_mid, 3),
            'notional_long_mm': round(notional_long_mm, 2),
            'rate_long': round(f_long, 3),
            'net_spread_bps': round(net_spread_bps, 2)
        }

    @staticmethod
    def generate_historical_carry_chart(f_matrix_df, short_leg, mid_leg, long_leg, coef_short, coef_long):
        """Generates the interactive carrier tracking timeline canvas."""
        fig = go.Figure()
        try:
            if short_leg in f_matrix_df.columns and mid_leg in f_matrix_df.columns and long_leg in f_matrix_df.columns:
                current_spread = f_matrix_df[mid_leg] - (coef_short * f_matrix_df[short_leg] + coef_long * f_matrix_df[long_leg])
                current_vals = current_spread.values * 10000.0
                current_index = current_spread.index
            else:
                current_vals = np.zeros(len(f_matrix_df))
                current_index = f_matrix_df.index
        except Exception:
            current_vals = np.zeros(len(f_matrix_df))
            current_index = f_matrix_df.index

        fig.add_trace(go.Scatter(x=current_index, y=current_vals, mode='lines+markers', name='Current Spread History', line=dict(color='#ffc107', width=2.5)))
        
        fig.update_layout(
            title=dict(text="Historical Carry Timeline: Structure Dislocation (bps)", font=dict(color='#ffc107', size=13)),
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=45, r=20, t=55, b=40),
            xaxis=dict(title="Historical Timeline Axis", type='category', gridcolor='#2d2d2d'),
            yaxis=dict(title="Structure Dislocation Yield (bps)", gridcolor='#2d2d2d')
        )
        return fig
