# layouts/execution.py
from dash import dcc, html
import dash_bootstrap_components as dbc

def layout_execution(currencies):
    """Page 4 View Layout Blueprint: Trade Construction & Notional Desk."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("Trade Construction & Capital Optimization Desk", className="text-warning fw-bold mb-2"),
                html.P("Transform abstract basis point anomalies into risk-adjusted interbank swap principal notionals.", className="text-muted mb-4")
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Trade Configuration", className="text-warning mb-3"),
                    
                    html.Label("Target Trading Book Asset:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='exec-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                    
                    html.Label("Target Specific Structure:", className="text-light small fw-bold"),
                    dcc.Input(id='exec-struct-string', type='text', value='FLY: 2F1Y vs [1F1Y & 3F1Y]', className="form-control text-dark mb-4"),
                    
                    html.Label("Anchor Belly Core Principal Allocation ($):", className="text-light small fw-bold"),
                    dcc.Input(id='exec-risk-input', type='number', value=10000000, step=1, className="form-control text-dark mb-4"),
                    
                    # NEW EXECUTION DESK RATIO SLIDERS / INPUT CONTROLS:
                                        # FIXED: Changed both html.Col targets to dbc.Col to support grid widths cleanly
                    dbc.Row([
                        dbc.Col([
                            html.Label("Left Wing Weight:", className="text-light small fw-bold"),
                            dcc.Input(id='exec-ratio-short', type='number', value=0.5, step=0.05, className="form-control text-dark")
                        ], width=6),
                        dbc.Col([
                            html.Label("Right Wing Weight:", className="text-light small fw-bold"),
                            dcc.Input(id='exec-ratio-long', type='number', value=0.5, step=0.05, className="form-control text-dark")
                        ], width=6)
                    ], className="mb-4"),

                    dbc.Button("Optimize Execution Notional", id='run-exec-btn', n_clicks=0, color="warning", className="w-100 fw-bold")
                ], className="p-3 bg-dark border border-secondary rounded mb-4")
            ], width=3),
            
            dbc.Col([
                dbc.Row([
                    dbc.Col([dcc.Graph(id='exec-carry-history-canvas', style={'height': '380px'})], width=12)
                ], className="mb-4"),
                dbc.Row([
                    dbc.Col([
                        html.H5("Execution Desk Allocated Notional Matrix & Transaction Directions", className="text-warning small fw-bold mb-2"),
                        html.Div(id='exec-notional-container', className="bg-dark p-3 border border-secondary rounded text-light")
                    ], width=12)
                ])
            ], width=9)
        ])
    ])

