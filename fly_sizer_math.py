# fly_sizer_math.py - FIXED HORIZONTAL POSITIONING PROPERTY
import numpy as np
import pandas as pd
import plotly.graph_objects as go

class ExecutionOptimizer:
    """
    Translates macro relative-value triggers and trade components into physical market notionals.
    """
    @staticmethod
    def generate_historical_carry_chart(f_matrix=None, short_leg="1Y", mid_leg="2Y", long_leg="3Y", r_short=0.5, r_long=0.5):
        """
        Generates an institutional horizontal risk allocation bar chart asset.
        """
        s_lbl, m_lbl, l_lbl = str(short_leg).upper().strip(), str(mid_leg).upper().strip(), str(long_leg).upper().strip()
        categories = [f"Short Wing ({s_lbl})", f"Belly Anchor ({m_lbl})", f"Long Wing ({l_lbl})"]
        weights = [float(r_short), -1.00, float(r_long)]
        
        color_map = ['#ff1a75' if w > 0 else '#00ff66' for w in weights]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=weights, 
            y=categories, 
            orientation='h',
            marker=dict(color=color_map, line=dict(color='#1a1f2c', width=1)),
            text=[f"+{w:.2f}x" if w > 0 else f"{w:.2f}x" for w in weights],
            textposition='inside', 
            insidetextanchor='middle',  # 🛡️ FIXED: Aligns text inside without triggering Plotly property errors
            textfont=dict(family='monospace', size=11, color='#ffffff')
        ))
        
        fig.update_layout(
            paper_bgcolor='#0b0d12', plot_bgcolor='#0b0d12',
            margin=dict(l=10, r=10, t=10, b=10), height=180, showlegend=False,
            xaxis=dict(showgrid=True, gridcolor='#161b26', zeroline=True, zerolinecolor='#ffc107'),
            yaxis=dict(showgrid=False, tickfont=dict(family='monospace', size=10, color='#ffffff'))
        )
        return fig
