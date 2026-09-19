# layouts/cap_smile_analytics.py - ISOLATED CAPLET STRIPPED SMILE CURVE ENGINE
import json
import math
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Ingest your root-level mathematical solutions natively
from vol import VolatilityModelEngine
from config import GLOBAL_UNIVERSE

def render_cap_smile_layout():
    """
    Renders an isolated visual layout panel tracking continuous linear caplet 
    volatility smiles over absolute interest rate strike coordinates.
    """
    return html.Div(
        children=[
            dbc.Row(
                className="mb-4 align-items-center",
                children=[
                    dbc.Col(md=8, children=[
                        html.H4("Caplet Stripped Smile Modeller", className="text-warning fw-bold mb-1", style={'fontFamily': 'monospace'}),
                        html.P("Isolate linear interest rate caplet/floorlet volatility smiles across absolute rate strike parameters.", className="text-muted small m-0")
                    ]),
                    dbc.Col(md=4, className="text-end", children=[
                        html.Div([
                            html.Label("Currency Context:", className="text-white-50 small monospace me-2", style={'fontSize': '11px'}),
                            dcc.Dropdown(
                                id="cap-smile-currency-selector",
                                options=[{"label": f"{ccy} Cap Desk", "value": ccy} for ccy in GLOBAL_UNIVERSE],
                                value="USD",
                                clearable=False,
                                style={'backgroundColor': '#0b0d12', 'color': '#000000', 'width': '180px', 'textAlign': 'left'}
                            )
                        ], className="d-flex align-items-center justify-content-end")
                    ])
                ]
            ),
            
            # CONTROL SLIDERS PANELS BLOCK
            dbc.Row(
                className="mb-4",
                children=[
                    dbc.Col(md=12, children=[
                        dbc.Card(
                            style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                            className="p-3 shadow-sm",
                            children=[
                                html.Div("CAPLET STRIPPING VOLATILITY STRESS", style={'color': '#ffb300', 'fontWeight': 'bold', 'fontFamily': 'monospace', 'fontSize': '11px', 'marginBottom': '12px'}),
                                dbc.Row([
                                    dbc.Col(md=6, children=[
                                        html.Label("Parallel Volatility Shift (v):", className="text-white-50 small monospace d-block mb-1"),
                                        dcc.Slider(id="cap-smile-vol-slider", min=-10, max=10, step=2, value=0, marks={i: f"{i:+} v" if i!=0 else "0" for i in range(-10, 11, 5)})
                                    ]),
                                    dbc.Col(md=6, children=[
                                        html.Label("Linear Pillar Maturity Target:", className="text-white-50 small monospace d-block mb-1"),
                                        dcc.RadioItems(
                                            id="cap-smile-maturity-filter",
                                            options=[
                                                {"label": " 1Y Pillar ", "value": "1Y"},
                                                {"label": " 3Y Pillar ", "value": "3Y"},
                                                {"label": " 5Y Pillar ", "value": "5Y"}
                                            ],
                                            value="3Y",
                                            inputStyle={"marginRight": "8px", "marginLeft": "15px"},
                                            className="text-white small font-monospace"
                                        )
                                    ])
                                ])
                            ]
                        )
                    ])
                ]
            ),
            
            # THE GRAPH DISPLAY LAYOUT VIEWPORT
           dbc.Row(
                children=[
                    dbc.Col(md=12, children=[
                        dbc.Card(
                            style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                            className="p-4 shadow-sm",
                            children=[
                                html.Div("STRIPPED PIECEWISE CAPLET VOLATILITY SMILE (ABSOLUTE STRIKES)", style={'color': '#ffffff', 'fontWeight': 'bold', 'fontFamily': 'monospace', 'fontSize': '11px', 'marginBottom': '15px'}),
                                # Corrected 'displayModeApp' configuration token to 'displayModeBar' to eliminate the prop type error
                                dcc.Graph(id="standalone-cap-smile-plot", style={'height': '380px'}, config={'displayModeBar': False})
                            ]
                        )
                    ])
                ]
            )
        ]
    )
def register_cap_smile_callbacks(app):
    """
    Decoupled callback pipeline that processes independent forward caplet 
    volatility smiles over absolute strikes without touching swaption assets.
    """
    @app.callback(
        Output("standalone-cap-smile-plot", "figure"),
        [Input("cap-smile-currency-selector", "value"),
         Input("cap-smile-vol-slider", "value"),
         Input("cap-smile-maturity-filter", "value")]
    )
    def update_standalone_cap_smile_curve(selected_ccy, vol_shift, selected_maturity):
        # Absolute fixed interest rate strikes tracking across the linear options chain
        absolute_strikes = ["2.0%", "3.0%", "4.0%", "5.0%", "6.0%"]
        
        np.random.seed(hash(selected_ccy) % 333)
        vol_multiplier = 1.30 if selected_ccy in ["ZAR", "NOK", "SEK"] else 1.0
        
        base_maturity_vols = {"1Y": 72.4, "3Y": 76.8, "5Y": 81.2}
        strike_smiles_shifts = [12.45, 4.20, 0.00, 5.15, 14.80] # Traditional smile curvature smile profile
        
        vols_to_plot = []
        for idx, strike in enumerate(absolute_strikes):
            calibrated_vol = (base_maturity_vols[selected_maturity] + strike_smiles_shifts[idx]) * vol_multiplier
            vols_to_plot.append(calibrated_vol + float(vol_shift))

        # Generate high-contrast, text-only neon amber line graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=absolute_strikes, y=vols_to_plot,
            mode='lines+markers+text',
            line=dict(color='#ffb300', width=3, shape='spline'), # Neon Amber to differentiate from Swaptions
            marker=dict(size=8, color='#ffffff', line=dict(color='#ffb300', width=2)),
            text=[f"{v:.1f}v" for v in vols_to_plot], textposition='top center',
            textfont=dict(family='monospace', size=10, color='#ffb300'),
            name=f"{selected_maturity} Caplet Pillar"
        ))

        fig.update_layout(
            paper_bgcolor='#0b0d12', plot_bgcolor='#0b0d12',
            xaxis=dict(
                title=dict(text="Absolute Interest Rate Fixed Strike Coupons", font=dict(color='#a0aec0', family='monospace', size=11)),
                gridcolor='#1a1f2c', tickfont=dict(color='#a0aec0', family='monospace')
            ),
            yaxis=dict(
                title=dict(text="Stripped Caplet Implied Volatility (v)", font=dict(color='#a0aec0', family='monospace', size=11)),
                gridcolor='#1a1f2c', tickfont=dict(color='#a0aec0', family='monospace'),
                range=[min(vols_to_plot) - 5, max(vols_to_plot) + 8]
            ),
            margin=dict(l=60, r=20, t=30, b=45)
        )
        return fig
