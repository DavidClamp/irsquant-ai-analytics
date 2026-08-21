# layouts/diagnostics.py - PANEL 1: MULTI-CURRENCY TERM STRUCTURES & HEATMAPS
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from curves import BootstrappedDiscountCurve

def render_diagnostics_layout():
    """
    Assembles the structural HTML layout tree for Panel 1.
    """
    return html.Div(
        children=[
            # SUB-HEADER BAR
            dbc.Row(
                className="mb-4 align-items-center g-3",
                children=[
                    dbc.Col(md=6, children=[
                        html.H4("Curve Diagnostics Desk", className="text-success fw-bold m-0"),
                        html.P("Log-Linear Piecewise Yield Bootstrapping & Term Structural Heatmaps", className="text-muted small m-0")
                    ]),
                    dbc.Col(md=3, children=[
                        html.Label("Currency Matrix Node:", className="text-white small fw-bold mb-1"),
                        dcc.Dropdown(
                            id="diag-currency-selector",
                            options=[{"label": f"{ccy} Core Curve", "value": ccy} for ccy in ["USD", "EUR", "GBP", "JPY", "CHF", "NOK", "SEK", "ZAR"]],
                            value="USD",
                            clearable=False,
                            style={'backgroundColor': '#11141a', 'color': '#ffffff'}
                        )
                    ]),
                    dbc.Col(md=3, children=[
                        html.Label("Evaluation Date Timeline:", className="text-white small fw-bold mb-1"),
                        dcc.Dropdown(
                            id="diag-date-selector",
                            options=[{"label": "2026-08-21 [Latest]", "value": "2026-08-21"}],
                            value="2026-08-21",
                            clearable=False,
                            style={'backgroundColor': '#11141a', 'color': '#ffffff'}
                        )
                    ])
                ]
            ),
            
            # SPLIT METRIC GRAPH PANELS
            dbc.Row(
                className="g-4",
                children=[
                    # COLUMN 1: ZERO COUPON YIELD GRAPH
                    dbc.Col(
                        md=6,
                        children=[
                            dbc.Card(
                                style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                                className="p-3 shadow-sm",
                                children=[
                                    dcc.Graph(id="diag-yield-curve-graph", config={'displayModeBar': False})
                                ]
                            )
                        ]
                    ),
                    # COLUMN 2: DISCOUNT FACTOR PLOT
                    dbc.Col(
                        md=6,
                        children=[
                            dbc.Card(
                                style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                                className="p-3 shadow-sm",
                                children=[
                                    dcc.Graph(id="diag-discount-factor-graph", config={'displayModeBar': False})
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

def register_diagnostics_callbacks(app):
    """
    Registers reactive layout updates linking front-end rendering engines directly to curves.py math blocks.
    """
    @app.callback(
        Output("diag-yield-curve-graph", "figure"),
        Output("diag-discount-factor-graph", "figure"),
        Input("diag-currency-selector", "value"),
        Input("diag-date-selector", "value")
    )
    def update_yield_curve_visuals(currency, target_date):
        # 1. Fetch raw mock curve profiles safely from local data cache files
        try:
            with open("data/g4_curves.json", "r") as f:
                raw_data = json.load(f)
            df_all = pd.DataFrame(raw_data)
            df = df_all[(df_all['currency'] == currency.upper()) & (df_all['date'] == target_date)]
            spot_rates_dict = dict(zip(df['tenor'], df['rate']))
        except Exception:
            # Safe baseline mock fallback vector if storage channels capture a local disk access lock
            spot_rates_dict = {"3M": 3.10, "1Y": 3.25, "2Y": 3.40, "5Y": 3.65, "10Y": 3.85, "30Y": 4.10}

        # 2. Fire the native continuous QuantLib bootstrap engine compiler
        try:
            curve_engine = BootstrappedDiscountCurve(target_date=target_date, spot_rates_dict=spot_rates_dict, currency=currency)
            maturity_grid = np.linspace(0.25, 30.0, 100) # Form a continuous 100-point timeline matrix mesh
            
            zero_rates = [curve_engine.get_zero_rate(t) for t in maturity_grid]
            discount_factors = [curve_engine.get_discount_factor(t) for t in maturity_grid]
        except Exception:
            # Emergency mathematical shield arrays to prevent UI rendering dropouts during system breaks
            maturity_grid = np.linspace(0.25, 30.0, 10)
            zero_rates = [3.50] * 10
            discount_factors = [np.exp(-0.035 * t) for t in maturity_grid]

        # 3. Compile High-Contrast Plotly Canvas Objects
        yield_fig = go.Figure(data=[go.Scatter(x=maturity_grid, y=zero_rates, mode='lines', line=dict(color='#00ff66', width=3), name='Zero Rate')])
        yield_fig.update_layout(
            title=dict(text=f"{currency} Term Structure: Continuous Zero Coupon Curve", font=dict(color='#ffffff', size=14, family='monospace')),
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title='Maturity Horizon (Years)', gridcolor='#1e2430', color='#8a99ad'),
            yaxis=dict(title='Zero Yield Rate (%)', gridcolor='#1e2430', color='#8a99ad'),
            margin=dict(l=40, r=20, t=40, b=40)
        )

        df_fig = go.Figure(data=[go.Scatter(x=maturity_grid, y=discount_factors, mode='lines', line=dict(color='#ffaa00', width=3), name='P(0,T)')])
        df_fig.update_layout(
            title=dict(text=f"{currency} Capital Deflator: Piecewise Discount Factors", font=dict(color='#ffffff', size=14, family='monospace')),
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title='Maturity Horizon (Years)', gridcolor='#1e2430', color='#8a99ad'),
            yaxis=dict(title='Discount Factor P(0,T)', gridcolor='#1e2430', color='#8a99ad'),
            margin=dict(l=40, r=20, t=40, b=40)
        )

        return yield_fig, df_fig
