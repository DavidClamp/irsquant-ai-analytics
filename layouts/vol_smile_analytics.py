# layouts/vol_smile_analytics.py - ISOLATED BACHELIER OPTION SMILE CHART ENGINE
import json
import math
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc

# Ingest your root-level mathematical solutions natively
from vol import VolatilityModelEngine
from vol_surfaces_core import VolatilitySurfaceStripper
from config import GLOBAL_UNIVERSE

def render_vol_smile_layout():
    """
    Renders an isolated visual layout panel tracking continuous 
    Bachelier smile curves over options strike delta skews.
    """
    return html.Div(
        children=[
            dbc.Row(
                className="mb-4 align-items-center",
                children=[
                    dbc.Col(md=8, children=[
                        html.H4("Volatility Smile Modeller", className="text-info fw-bold mb-1", style={'fontFamily': 'monospace'}),
                        html.P("Isolate option premium skew distortions across continuous multi-expiry Bachelier smile segments.", className="text-muted small m-0")
                    ]),
                    dbc.Col(md=4, className="text-end", children=[
                        html.Div([
                            html.Label("Currency Context:", className="text-white-50 small monospace me-2", style={'fontSize': '11px'}),
                            dcc.Dropdown(
                                id="smile-desk-currency-selector",
                                options=[{"label": f"{ccy} Smile Desk", "value": ccy} for ccy in GLOBAL_UNIVERSE],
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
                                html.Div("SMILE PARAMETER SHIFT MODEL", style={'color': '#00d2ff', 'fontWeight': 'bold', 'fontFamily': 'monospace', 'fontSize': '11px', 'marginBottom': '12px'}),
                                dbc.Row([
                                    dbc.Col(md=6, children=[
                                        html.Label("Parallel Volatility Stress Shift (bps):", className="text-white-50 small monospace d-block mb-1"),
                                        dcc.Slider(id="smile-vol-shift-slider", min=-20, max=20, step=5, value=0, marks={i: f"{i:+} bps" if i!=0 else "0" for i in range(-20, 21, 10)})
                                    ]),
                                    dbc.Col(md=6, children=[
                                        html.Label("Option Expiry Horizon Selection:", className="text-white-50 small monospace d-block mb-1"),
                                        dcc.RadioItems(
                                            id="smile-expiry-filter",
                                            options=[
                                                {"label": " Short-End (3M Expiry) ", "value": "3M"},
                                                {"label": " Belly (1Y Expiry) ", "value": "1Y"},
                                                {"label": " Long-End (5Y Expiry) ", "value": "5Y"}
                                            ],
                                            value="1Y",
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
                                html.Div("📈 PARAMETRIC DISCRETE OPTION SMILE TRACKS", style={'color': '#ffffff', 'fontWeight': 'bold', 'fontFamily': 'monospace', 'fontSize': '11px', 'marginBottom': '15px'}),
                                dcc.Graph(id="standalone-smile-plot-slot", style={'height': '380px'}, config={'displayModeBar': False})
                            ]
                        )
                    ])
                ]
            )
        ]
    )


def register_vol_smile_callbacks(app):
    """
    Decoupled callback pipeline that extracts non-parametric surface points 
    and handles option smile spline graphing without touching other layout sheets.
    """
    @app.callback(
        Output("standalone-smile-plot-slot", "figure"),
        [Input("smile-desk-currency-selector", "value"),
         Input("smile-vol-shift-slider", "value"),
         Input("smile-expiry-filter", "value")]
    )
    def update_standalone_smile_curve(selected_ccy, vol_shift, selected_expiry):
        skews = ["10D Put", "25D Put", "ATM", "25D Call", "10D Call"]
        
        try:
            stripper_instance = VolatilitySurfaceStripper(file_path="data/g4_vol_surfaces.json")
        except Exception:
            stripper_instance = None

        vols_to_plot = []
        t_str = selected_expiry.replace("M", "").replace("Y", "")
        t_factor = float(t_str) / 12.0 if "M" in selected_expiry else float(t_str)

        for sk in skews:
            if stripper_instance:
                swap_tenor_proxy = 10.0 if "10D" in sk else 5.0 if "25D" in sk else 2.0
                raw_extracted_vol = stripper_instance.get_clean_atm_volatility(
                    currency=selected_ccy,
                    target_date="2026-09-15",
                    option_expiry=t_factor,
                    swap_tenor=swap_tenor_proxy
                )
                base_vol = float(raw_extracted_vol * 100.0 if raw_extracted_vol <= 1.5 else raw_extracted_vol)
            else:
                np.random.seed(hash(selected_ccy) % 111)
                vol_multiplier = 1.25 if selected_ccy in ["ZAR", "NOK", "SEK"] else 1.0
                base_vols = {"3M": 70.2, "1Y": 75.1, "5Y": 82.3}
                skew_map = {"10D Put": 14.0, "25D Put": 5.5, "ATM": 0.0, "25D Call": 6.7, "10D Call": 16.1}
                base_vol = (base_vols[selected_expiry] + skew_map[sk]) * vol_multiplier

            vols_to_plot.append(base_vol + float(vol_shift))

        # Generate high-contrast, text-only neon line graph
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=skews, y=vols_to_plot,
            mode='lines+markers+text',
            line=dict(color='#00d2ff', width=3, shape='spline'),
            marker=dict(size=8, color='#ffffff', line=dict(color='#00d2ff', width=2)),
            text=[f"{v:.1f}v" for v in vols_to_plot], textposition='top center',
            textfont=dict(family='monospace', size=10, color='#00d2ff'),
            name=f"{selected_expiry} Horizon"
        ))

        fig.update_layout(
            paper_bgcolor='#0b0d12', plot_bgcolor='#0b0d12',
            xaxis=dict(
                title=dict(text="Option Strike Delta Skew Buckets", font=dict(color='#a0aec0', family='monospace', size=11)),
                gridcolor='#1a1f2c', tickfont=dict(color='#a0aec0', family='monospace')
            ),
            yaxis=dict(
                title=dict(text="Implied Normal Volatility (bps)", font=dict(color='#a0aec0', family='monospace', size=11)),
                gridcolor='#1a1f2c', tickfont=dict(color='#a0aec0', family='monospace'),
                range=[min(vols_to_plot) - 5, max(vols_to_plot) + 8]
            ),
            margin=dict(l=60, r=20, t=30, b=45)
        )
        return fig
