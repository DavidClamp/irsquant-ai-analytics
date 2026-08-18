# layouts/swaption_analytics.py - HIGH CONTRAST IRO SWAPTION SURFACE VIEW
from dash import dcc, html
import dash_bootstrap_components as dbc

def layout_swaption_analytics(currencies):
    """Page 3 View Layout Blueprint: IRO Swaption 3D SABR Surface Desk with high-contrast labels."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("IRO Swaption 3D Implied Volatility Surface Desk", className="text-warning fw-bold mb-2"),
                html.P("Extract and visualize parametric Hagan SABR volatility models across multi-currency interest rate swaption matrices.", className="text-muted mb-4")
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Surface Configuration", className="text-warning fw-bold mb-4"),
                    
                    html.Label("Target Trading Book Asset:", className="text-white small fw-bold mb-2 d-block"),
                    dcc.Dropdown(id='swaption-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                    
                    html.H6("Calibrated SABR Parameters", className="text-warning small fw-bold mt-2 mb-3"),
                    html.Div(id='swaption-sabr-parameters-box', className="bg-opacity-10 bg-light p-3 border border-secondary rounded text-white fw-bold")
                ], className="p-3 bg-dark border border-secondary rounded")
            ], width=3),
            
            dbc.Col([
                dcc.Graph(id='swaption-3d-canvas', style={'height': '550px'}, className="mb-4")
            ], width=9)
        ])
    ], className="pb-5 mb-5")
