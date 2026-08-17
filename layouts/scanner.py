# layouts/scanner.py - SYSTEMATIC SCANNER VIEW BLUEPRINT
from dash import dcc, html
import dash_bootstrap_components as dbc

def layout_scanner(currencies):
    """Page 2 View Layout Blueprint: Multi-Node OLS Arbitrage Interface Skel."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("Systematic Multi-Node Cross-Sectional Scanner Console", className="text-warning fw-bold mb-2"),
                html.P("OLS zero-intercept linear regressions identifying structural tail-risk anomalies across permutation matrices.", className="text-muted mb-4")
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Scanner Configuration", className="text-warning mb-3"),
                    html.Label("Select Target Currency Block:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='scan-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                    html.Label("Arbitrage Structure Engine:", className="text-light small fw-bold"),
                    dcc.RadioItems(id='scan-type-toggle', options=[{'label': ' 3-Node Butterfly (FLY)', 'value': 'BUTTERFLY'}, {'label': ' 4-Node Condor Twist', 'value': 'CONDOR'}], value='BUTTERFLY', labelStyle={'display': 'block', 'color': 'white', 'paddingBottom': '10px'}, className="mb-4"),
                    dbc.Button("Execute Curve Matrix Sweep", id='run-scan-btn', n_clicks=0, color="warning", className="w-100 fw-bold")
                ], className="p-3 bg-dark border border-secondary rounded")
            ], width=3),
            dbc.Col([
                dbc.Row([
                    dbc.Col([dcc.Graph(id='scan-anomaly-canvas', style={'height': '350px'}, className="mb-4")], width=12)
                ]),
                dbc.Row([
                    dbc.Col([
                        html.H5("Relative Value Dislocation Anomaly Leaderboard", className="text-warning small fw-bold mb-2"),
                        html.Div(id='scan-table-container', className="bg-dark p-2 border border-secondary rounded")
                    ], width=12)
                ])
            ], width=9)
        ])
    ])
