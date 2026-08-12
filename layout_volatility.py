# layout_volatility.py
from dash import dcc, html
import dash_bootstrap_components as dbc

def layout_volatility(currencies, all_dates):
    """
    Volatility View Blueprint Component.
    Keeps app.py lean by isolating your options pricing presentation matrix.
    """
    expiries = [0.25, 0.5, 1.0, 2.0, 5.0, 10.0]
    expiry_labels = ["3M Expiry", "6M Expiry", "1Y Expiry", "2Y Expiry", "5Y Expiry", "10Y Expiry"]
    
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("Implied Volatility Smile & Swaption Pricing Terminal", className="text-warning fw-bold mb-2"),
                html.P("Non-linear analytics: Black '76 pricing models mapping skew surfaces and option Greeks across custom OTM strike deltas.", className="text-muted mb-4")
            ], width=12)
        ]),
        
        dbc.Row([
            # Options and Volatility Control Sidebar Container Panel
            dbc.Col([
                html.Div([
                    html.H5("Option Configuration", className="text-warning mb-3"),
                    
                    html.Label("Select Currency Target:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='vol-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                    
                    html.Label("Review Historical Date:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='vol-date-dropdown', options=[{'label': d, 'value': d} for d in all_dates], value=all_dates[-1] if all_dates else None, className="text-dark mb-4"),
                    
                    html.Label("Swaption Expiry Horizon:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='vol-expiry-dropdown', options=[{'label': l, 'value': v} for l, v in zip(expiry_labels, expiries)], value=1.0, className="text-dark mb-4"),
                    
                    html.Label("Underlying Swap Length:", className="text-light small fw-bold"),
                    dcc.Dropdown(
                        id='vol-tenor-dropdown', 
                        options=[{'label': f"{t}Y Underlying", 'value': float(t)} for t in [1.0, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0]], 
                        value=5.0, 
                        className="text-dark mb-4"
                    ),
                    
                    html.Label("ATM Volatility Input (σ):", className="text-light small fw-bold"),
                    dcc.Input(id='vol-atm-input', type='number', value=0.25, step=0.01, min=0.01, max=1.0, className="form-control text-dark mb-4")
                ], className="p-3 bg-dark border border-secondary rounded mb-4")
            ], width=3),
            
            # Interactive Volatility Smile Skew and Price Matrix Output Canvas Blocks
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id='vol-smile-canvas', style={'height': '400px'}, className="mb-4")
                    ], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H5("Strike Dislocation & Premium Matrix Grid", className="text-warning small fw-bold mb-2"),
                        # FIXED CRITICAL LAYOUT KEY: Container ID matches callback outputs perfectly
                        html.Div(id='vol-matrix-container', className="bg-dark p-2 border border-secondary rounded")
                    ], width=12)
                ])
            ], width=9)
        ])
    ])
