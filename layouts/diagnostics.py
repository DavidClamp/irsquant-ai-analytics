# layouts/diagnostics.py
from dash import dcc, html
import dash_bootstrap_components as dbc

def layout_diagnostics(currencies, all_dates):
    """Page 1 View Layout Blueprint."""
    return html.Div([
        dbc.Row([
            dbc.Col([
                html.H3("G4 Sovereign Swap Curve Term Structure Analytics Snapshot", className="text-warning fw-bold mb-2"),
                html.P("Real-time pricing dashboard plotting continuous horizontal step functions and forward yield intensity blocks.", className="text-muted mb-4")
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H5("Curve Controls", className="text-warning mb-3"),
                    html.Label("Select Currency Matrix Target:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='diag-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                    html.Label("Review Historical Date Node:", className="text-light small fw-bold"),
                    dcc.Dropdown(id='diag-date-dropdown', options=[{'label': d, 'value': d} for d in all_dates], value=all_dates[-1] if all_dates else None, className="text-dark mb-4")
                ], className="p-3 bg-dark border border-secondary rounded")
            ], width=3),
            dbc.Col([
                dcc.Graph(id='diag-term-structure-snapshot', className="mb-4"),
                html.H5("Continuous Implied Forward Block Matrix Surface Grid (%)", className="text-warning small fw-bold mb-2"),
                dcc.Graph(id='diag-matrix-heatmap', style={'height': '450px'})
            ], width=9)
        ])
    ])
