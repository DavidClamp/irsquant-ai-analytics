# layouts/volatility.py - VOLATILITY TRADING DESK BLUEPRINT
from dash import dcc, html
import dash_bootstrap_components as dbc

def layout_volatility(currencies, all_dates):
    """Page 3 View Layout Blueprint: Implied Volatility Surfaces & Options Trade Ticket."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("Implied Volatility Core & Options Position Sheet", className="text-warning fw-bold mb-2"),
                html.P("Calibrate parametric SABR surfaces to live swaption arrays and manage options desk exposures.", className="text-muted mb-4")
            ], width=12)
        ]),
        
        # TOP ROW: 3D GRAPH CANVAS AND TICKER SELECTION
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Surface Controls", className="text-warning mb-3"),
                    html.Label("Target Asset Currency:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='vol-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                    
                    html.Label("Calibration Anchor Date:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='vol-date-dropdown', options=[{'label': d, 'value': d} for d in all_dates], value=all_dates[-1] if all_dates else None, className="text-dark mb-4"),
                    
                    dbc.Button("Calibrate SABR Surface", id='run-vol-btn', n_clicks=0, color="warning", className="w-100 fw-bold")
                ], className="p-3 bg-dark border border-secondary rounded h-100")
            ], width=3),
            
            dbc.Col([
                dcc.Graph(id='vol-3d-surface-canvas', style={'height': '400px'})
            ], width=9)
        ], className="mb-4"),
        
        # BOTTOM ROW: OPTIONS TRADING SHEET TICKET
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Options Desk Order Ticket", className="text-warning mb-3"),
                    dbc.Row([
                        dbc.Col([
                            html.Label("Option Type:", className="text-light small"),
                            dcc.Dropdown(id='trade-option-type', options=[{'label': 'Payer (Call)', 'value': 'PAYER'}, {'label': 'Receiver (Put)', 'value': 'RECEIVER'}], value='RECEIVER', className="text-dark mb-2")
                        ], width=3),
                        dbc.Col([
                            html.Label("Expiry (Yrs):", className="text-light small"),
                            dcc.Input(id='trade-expiry-input', type='number', value=1.0, step=0.25, className="form-control text-dark mb-2")
                        ], width=3),
                        dbc.Col([
                            html.Label("Strike Rate (%):", className="text-light small"),
                            dcc.Input(id='trade-strike-input', type='number', value=4.75, step=0.05, className="form-control text-dark mb-2")
                        ], width=3),
                        dbc.Col([
                            html.Label("Position Volume ($M Notional):", className="text-light small"),
                            dcc.Input(id='trade-volume-input', type='number', value=10.0, step=1.0, className="form-control text-dark mb-2")
                        ], width=3),
                    ]),
                    dbc.Button("Calculate Risk Metrics & Book Trade", id='run-book-btn', n_clicks=0, color="success", className="mt-2 fw-bold w-100")
                ], className="p-3 bg-dark border border-secondary rounded mb-4")
            ], width=12)
        ]),
        
        # REAL-TIME TRADE SHEET AGGREGATOR DISPLAY
        dbc.Row([
            dbc.Col([
                html.H5("Active Volatility Position Sheet Analytics", className="text-warning small fw-bold mb-2"),
                html.Div(id='vol-trade-sheet-container', className="bg-dark p-3 border border-secondary rounded text-light")
            ], width=12)
        ])
    ])
