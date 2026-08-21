# diagnostics.py - LIGHTWEIGHT IRSQUANT MULTI-CURRENCY ROUTER LAYOUT
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from utils import DataSanitizer  # Preserves your centralized data sanitization layer

def render_diagnostics_layout(master_df):
    """
    Assembles the core layout container shell for Panel 1 (Term Structures & Matrix Heatmaps).
    The underlying calculation callbacks are processed directly by the app.py engine.
    """
    # Extract unique global asset currency selectors dynamically
    available_currencies = sorted(master_df['currency'].unique()) if 'currency' in master_df.columns else ["USD"]
    
    return html.Div(
        style={'backgroundColor': '#060709', 'padding': '20px', 'minHeight': '100vh'},
        children=[
            # TOP BAR CONTROLS GRID
            dbc.Row(className="align-items-center mb-4 g-3", children=[
                dbc.Col(md=4, children=[
                    html.H3("IRSQuant Diagnostics Panel", className="text-warning fw-bold m-0"),
                    html.P("Multi-Currency Calendar-Aware Core [QuantLib Backbone]", className="text-muted small m-0")
                ]),
                dbc.Col(md=4, children=[
                    html.Label("Target Active Asset:", className="text-white small fw-bold mb-1"),
                    dcc.Dropdown(id="diag-ccy-selector", options=[{"label": f"{ccy} Sovereign Curve", "value": ccy} for ccy in available_currencies], value="USD", clearable=False, style={'backgroundColor': '#11141a', 'color': '#ffffff'})
                ]),
                dbc.Col(md=4, children=[
                    html.Label("Historical Data Timeline Anchor:", className="text-white small fw-bold mb-1"),
                    dcc.Dropdown(id="diag-date-selector", clearable=False, style={'backgroundColor': '#11141a', 'color': '#ffffff'})
                ])
            ]),
            # DYNAMIC MATRICES LAYER
            dbc.Row(className="mb-4 text-center g-3", id="diagnostics-metrics-ticker"),
            dbc.Row(className="g-4", children=[
                dbc.Col(lg=6, children=[dbc.Card(style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c'}, className="p-3 shadow-sm", children=[dcc.Graph(id="spot-yield-curve-graph", config={'displayModeBar': False})])]),
                dbc.Col(lg=6, children=[dbc.Card(style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c'}, className="p-3 shadow-sm", children=[dcc.Graph(id="implied-forward-heatmap", config={'displayModeBar': False})])])
            ])
        ]
    )
