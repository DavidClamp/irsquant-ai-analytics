# layouts/volatility.py 
from dash import dcc, html
import dash_bootstrap_components as dbc

def layout_volatility(currencies, all_dates):
    """Page 3 View Layout Blueprint: Split Asset IRO Scanner and IRS/IRO Trade Optimiser Desk."""
    # FIXED: Added 'pb-5' and 'mb-5' classes to completely eliminate browser frame clipping at the bottom
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("IRS & IRO Relative-Value Trade Optimiser Desk", className="text-warning fw-bold mb-2"),
                html.P("Analyze multi-currency IRO volatility surfaces to isolate structural skews and calibrate delta-neutral IRS hedges.", className="text-muted mb-4")
            ], width=12)
        ]),
        
        # SURFACE CONTROLS AND MULTI-ASSET CORE MESH CANVAS
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Trade Optimiser Setup", className="text-warning mb-3"),
                    html.Label("Target Asset Currency:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='vol-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                    
                    html.Label("Historical Pricing Anchor:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='vol-date-dropdown', options=[{'label': d, 'value': d} for d in all_dates], value=all_dates[-1] if all_dates else None, className="text-dark mb-4"),
                    
                    html.Label("Target Volatility Strategy:", className="text-light small fw-bold"),
                    dcc.RadioItems(id='vol-strategy-select', options=[
                        {'label': ' Long IRO Straddle (Pure Vol Buy)', 'value': 'STRADDLE'},
                        {'label': ' IRO Volatility Arbitrage (Swaption vs. Cap)', 'value': 'VOL_ARB'}
                    ], value='STRADDLE', labelStyle={'display': 'block', 'color': 'white', 'paddingBottom': '10px'}, className="mb-4"),
                    
                    dbc.Button("Calibrate IRS & IRO Trade Optimiser", id='run-vol-btn', n_clicks=0, color="warning", className="w-100 fw-bold")
                ], className="p-3 bg-dark border border-secondary rounded h-100")
            ], width=3),
            
            dbc.Col([
                dcc.Graph(id='vol-3d-surface-canvas', style={'height': '400px'})
            ], width=9)
        ], className="mb-4"),
        
        # EXPANDED: VOLATILITY STRUCTURING MATRIX BACKTEST VIEW
        dbc.Row([
            dbc.Col([
                html.H5("IRO Strategy Sizing & IRS Delta-Hedge Parameters", className="text-warning small fw-bold mb-2"),
                html.Div(id='vol-trade-sheet-container', className="bg-dark p-3 border border-secondary rounded text-light")
            ], width=12)
        ])
    ], className="pb-5 mb-5") 
