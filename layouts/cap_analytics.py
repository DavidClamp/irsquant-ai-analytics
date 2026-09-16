# layouts/cap_analytics.py - G4 & EM MULTI-CURRENCY INTEREST RATE CAP/FLOOR MATRIX DESK
import json
import math
import numpy as np
from dash import html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc

# INGEST MASTER MULTI-CURRENCY SPECIFICATIONS NATIVELY
from config import GLOBAL_UNIVERSE

def render_cap_layout():
    """
    Renders an institutional front-office pricing grid tool for Interest Rate Caps and Floors
    across the active 8-currency portfolio universe.
    """
    currency_dropdown_options = [
        {"label": f"{ccy} Cap/Floor Universe", "value": ccy} for ccy in GLOBAL_UNIVERSE
    ]

    return html.Div(
        children=[
            dbc.Row(
                className="mb-4 align-items-center",
                children=[
                    dbc.Col(md=8, children=[
                        html.H4("🛡️ Interest Rate Cap & Floor Analytics Desk", className="text-info fw-bold mb-1"),
                        html.P("Price long-dated linear options chains, evaluate premium cushions, and track aggregated portfolio delta vectors.", className="text-muted small m-0")
                    ]),
                    
                    # SYSTEM AUTOMATED MULTI-CURRENCY DROPDOWN SELECTOR
                    dbc.Col(md=4, className="text-end", children=[
                        html.Div([
                            html.Label("Currency Context:", className="text-white-50 small monospace me-2", style={'fontSize': '11px'}),
                            html.Div(
                                dcc.Dropdown(
                                    id="cap-desk-currency-selector",
                                    options=currency_dropdown_options,
                                    value="USD", 
                                    clearable=False,
                                    multi=False, 
                                    searchable=False,
                                    style={'backgroundColor': '#0b0d12', 'color': '#000000', 'width': '180px', 'textAlign': 'left'}
                                ),
                                style={'display': 'inline-block', 'zIndex': '9999', 'position': 'relative'}
                            )
                        ], className="d-flex align-items-center justify-content-end")
                    ])
                ]
            ),
            
            # Interactive Cap/Floor Parameter Selection Overlay
            dbc.Row(
                className="mb-4",
                children=[
                    dbc.Col(md=12, children=[
                        dbc.Card(
                            style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                            className="p-3 shadow-sm",
                            children=[
                                html.Div("⚙️ DESK STRIKE SELECTOR & STRUCTURE SWITCHES", style={'color': '#00d2ff', 'fontWeight': 'bold', 'fontFamily': 'monospace', 'fontSize': '11px', 'marginBottom': '12px'}),
                                dbc.Row([
                                    dbc.Col(md=4, children=[
                                        html.Label("Structure Type Selection:", className="text-white-50 small monospace d-block mb-1"),
                                        dcc.RadioItems(
                                            id="cap-floor-structure-toggle",
                                            options=[
                                                {"label": " 📈 Cap (Protect Payer/Short Leg)", "value": "CALL"},
                                                {"label": " 📉 Floor (Protect Receiver/Long Leg)", "value": "PUT"}
                                            ],
                                            value="CALL",
                                            inputStyle={"marginRight": "8px", "marginLeft": "15px"},
                                            className="text-white small font-monospace"
                                        )
                                    ]),
                                    dbc.Col(md=4, children=[
                                        html.Label("Absolute Option Strike Rate (%):", className="text-white-50 small monospace d-block mb-1"),
                                        dcc.Slider(
                                            id="cap-strike-slider", 
                                            min=2.0, max=6.0, step=0.5, value=4.0, 
                                            marks={i: f"{i:.1f}%" for i in np.arange(2.0, 6.1, 1.0)}
                                        )
                                    ]),
                                    dbc.Col(md=4, children=[
                                        html.Label("Flat Implied Volatility Stress Shift (vols):", className="text-white-50 small monospace d-block mb-1"),
                                        dcc.Slider(
                                            id="cap-vol-stress-slider", 
                                            min=-15, max=15, step=5, value=0, 
                                            marks={i: f"{i:+} v" if i!=0 else "0" for i in range(-15, 16, 5)}
                                        )
                                    ])
                                ])
                            ]
                        )
                    ])
                ]
            ),
            
            # Focused Analytics Grid Canvas Slot
            dbc.Row(
                children=[
                    dbc.Col(md=12, children=[
                        dbc.Card(
                            style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                            className="p-4 shadow-sm",
                            children=[
                                html.Div(
                                    "📊 AGGREGATED PORTFOLIO STRIKE CHAINS (CAPLET / FLOORLET VECTOR SUMS IN BPS)", 
                                    style={'color': '#ffffff', 'fontWeight': 'bold', 'fontFamily': 'monospace', 'fontSize': '11px', 'marginBottom': '15px'}
                                ),
                                html.Div(id="cap-analytics-table-slot")
                            ]
                        )
                    ])
                ]
            )
        ]
    )
