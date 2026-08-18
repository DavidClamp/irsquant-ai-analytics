# layouts/cap_analytics.py - HIGH CONTRAST CAP/FLOORLET SURFACE STRIP VIEW
from dash import dcc, html
import dash_bootstrap_components as dbc

def layout_cap_analytics(currencies):
    """Page 4 View Layout Blueprint: Cap/Floorlet Implied Volatility Surface Strip Desk with high-contrast labels."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("Cap/Floorlet Linear Volatility Strip Desk", className="text-info fw-bold mb-2"),
                html.P("Strip and visualize continuous flat volatility curves across absolute strike rate vectors and maturities.", className="text-muted mb-4")
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Surface Configuration", className="text-info fw-bold mb-4"),
                    
                    html.Label("Target Trading Book Asset:", className="text-white small fw-bold mb-2 d-block"),
                    dcc.Dropdown(id='cap-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                    
                    html.Div([
                        html.H6("Model Specifications", className="text-info small fw-bold mb-3"),
                        html.P([html.Strong("Pricing Basis: ", className="text-white"), "Act/360 Continuous"], className="small mb-2"),
                        html.P([html.Strong("Volatility Model: ", className="text-white"), "Log-Normal Linear Strip"], className="small mb-0")
                    ], className="bg-opacity-10 bg-light p-3 border border-secondary rounded text-light")
                ], className="p-3 bg-dark border border-secondary rounded")
            ], width=3),
            
            dbc.Col([
                dcc.Graph(id='cap-3d-canvas', style={'height': '550px'}, className="mb-4")
            ], width=9)
        ])
    ], className="pb-5 mb-5")
