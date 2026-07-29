# app.py
import os
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Clean institutional imports from Layer 2
from analytics import (
    build_forward_permutation_matrix, 
    run_systematic_butterfly_scan, 
    extract_forward_curve_snapshot
)

# ==========================================
# 1. DATABASE INGESTION MAPPING
# ==========================================
json_path = os.path.join(os.path.dirname(__file__), 'g4_curves.json')
if not os.path.exists(json_path):
    raise FileNotFoundError(f"Missing essential dataset file: {json_path}")

master_df = pd.read_json(json_path)
master_df['date'] = pd.to_datetime(master_df['date'])

currencies = master_df['currency'].unique().tolist()
dates = master_df['date'].unique()

# ==========================================
# 2. PLATFORM WIREFRAME INITIALIZATION
# ==========================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
server = app.server

# Shared Navigation Header Component Matrix
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Diagnostic Charts", href="/page-diagnostics", className="nav-link text-warning fw-bold px-3")),
        dbc.NavItem(dcc.Link("Systematic RV Scanner", href="/page-scanner", className="nav-link text-muted px-3")),
    ],
    brand="IRSQuant Analytical Platform", brand_href="/", color="dark", dark=True, className="border-bottom border-secondary mb-4 px-4"
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Container(id='page-content', fluid=True)
])

# ==========================================
# 3. PAGE VIEW CONFIGURATION BLUEPRINTS
# ==========================================

# Page 1 View: Term Structure Snapshots Control Panel Layout
layout_diagnostics = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Implied Forward Curve Snapshot Terminal", className="text-warning fw-bold mb-2"),
            html.P("Discrete block matrix monitoring tool tracking forward curves across chosen maturities and days.", className="text-muted mb-4")
        ], width=12)
    ]),
    dbc.Row([
        # Configuration Sidebar
        dbc.Col([
            html.Div([
                html.H5("Data Filters", className="text-warning mb-3"),
                html.Label("Select Currency:", className="text-light small fw-bold"),
                dcc.Dropdown(id='diag-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                
                html.Label("Select Historical Date:", className="text-light small fw-bold"),
                dcc.Dropdown(
                    id='diag-date-dropdown', 
                    options=[{'label': str(pd.to_datetime(d).strftime('%Y-%m-%d')), 'value': str(pd.to_datetime(d).strftime('%Y-%m-%d'))} for d in dates], 
                    value=str(pd.to_datetime(dates[-1]).strftime('%Y-%m-%d')), 
                    className="text-dark mb-4"
                ),
                
                html.Label("Forward Contract Tenor Length:", className="text-light small fw-bold"),
                dcc.Dropdown(
                    id='diag-tenor-dropdown', 
                    options=[{'label': '1-Year Forwards', 'value': 1.0}, {'label': '2-Year Forwards', 'value': 2.0}, {'label': '5-Year Forwards', 'value': 5.0}], 
                    value=1.0, className="text-dark"
                )
            ], className="p-3 bg-dark border border-secondary rounded mb-4")
        ], width=3),
        # Display Canvas
        dbc.Col([
            dcc.Graph(id='diag-twin-canvas', style={'height': '520px'})
        ], width=9)
    ])
])

# Page 2 View: RV Strategy Alpha Scanner Table Layout
layout_scanner = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Systematic 3-Node Forward Butterfly Scanner", className="text-warning fw-bold mb-2"),
            html.P("Linear regression rankings console backed by real JSON data states.", className="text-muted mb-4")
        ], width=12)
    ]),
    dbc.Row([
        dbc.Col([
            html.Div([
                html.H5("Scan Trigger", className="text-warning mb-3"),
                dcc.Dropdown(id='scan-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                dbc.Button("Execute Curve Matrix Sweep", id='run-scan-btn', color="warning", className="w-100 fw-bold py-2")
            ], className="p-3 bg-dark border border-secondary rounded mb-4")
        ], width=3),
        dbc.Col([
            dcc.Graph(id='scan-anomaly-canvas', style={'height': '400px'}, className="mb-4"),
            html.Div(id='scan-table-container', className="bg-dark p-2 border border-secondary rounded")
        ], width=9)
    ])
])

# ==========================================
# 4. CORE INTERFACE PROCESSING CALLFLOWS
# ==========================================

# URL Routing Driver Callback: SECURED AND ARTIFACT DEBT CLEANED
@app.callback(
    Output('page-content', 'children'), 
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/page-scanner':
        return layout_scanner
    # Explicitly routes any unmapped inputs or "/" to the snapshot terminal layout
    return layout_diagnostics

# Render Term Snapshot Callback: Plots horizontal forward blocks along the horizon axes
@app.callback(
    Output('diag-twin-canvas', 'figure'),
    [Input('diag-ccy-dropdown', 'value'),
     Input('diag-date-dropdown', 'value'),
     Input('diag-tenor-dropdown', 'value')]
)
def render_term_structure_forward_steps(selected_ccy, selected_date, forward_tenor):
    if not selected_date:
        return go.Figure()
        
    x_starts, x_ends, y_rates = extract_forward_curve_snapshot(master_df, selected_ccy, selected_date, forward_tenor)
    fig = go.Figure()
    
    for i in range(len(y_rates)):
        # Institutional horizontal block step shape mapping track
        fig.add_trace(go.Scatter(
            x=[x_starts[i], x_ends[i]], y=[y_rates[i], y_rates[i]],
            mode='lines+markers', name=f'{x_starts[i]}Y Forward',
            line=dict(color='#ffc107', width=3.5),
            marker=dict(size=7, symbol='square', color='#ffc107'),
            hovertemplate=f"Contract: {x_starts[i]}Y -> {x_ends[i]}Y<br>Yield: %{{y}}%<extra></extra>"
        ))
        if i < len(y_rates) - 1:
            fig.add_trace(go.Scatter(
                x=[x_ends[i], x_starts[i+1]], y=[y_rates[i], y_rates[i+1]],
                mode='lines', line=dict(color='#454d55', width=1.5, dash='dash'), hoverinfo='skip'
            ))

    fig.update_layout(
        title=dict(text=f"Implied Forward Curve Term Snapshot ({selected_ccy} | {int(forward_tenor)}Y Forwards | {selected_date})", font=dict(color='#ffc107', size=16)),
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
        margin=dict(l=55, r=40, t=65, b=55),
        xaxis=dict(title="Maturity Horizon Timeline (Years out from Today)", gridcolor='#2d2d2d', tickmode='linear', dtick=1.0, range=[0, max(x_ends) + 0.5] if x_ends else [0, 11]),
        yaxis=dict(title="Forward Yield Rate (%)", gridcolor='#2d2d2d')
    )
    return fig

# Strategy Sweep Callback: Invokes linear model regressions and draws the alpha table grid
@app.callback(
    [Output('scan-anomaly-canvas', 'figure'), Output('scan-table-container', 'children')],
    [Input('run-scan-btn', 'n_clicks'), Input('scan-ccy-dropdown', 'value')]
)
def execute_interface_butterfly_sweep(n_clicks, selected_ccy):
    f_matrix = build_forward_permutation_matrix(dates, master_df, selected_ccy=selected_ccy, forward_tenor=1.0)
    rank_df, series_storage = run_systematic_butterfly_scan(f_matrix)
    if rank_df.empty: 
        return go.Figure(), html.Div("Empty DataFrame")
    
    best_fly = rank_df.iloc[0]['Structure']
    best_series = series_storage[best_fly]
    
    fig = make_subplots(rows=1, cols=2, column_widths=[0.6, 0.4])
    fig.add_trace(go.Scatter(x=best_series.index, y=best_series.values * 10000, mode='lines+markers', line_shape='hv', line=dict(color='#ffc107', width=1.5)), row=1, col=1)
    fig.add_trace(go.Histogram(x=best_series.values * 10000, nbinsx=10, marker_color='#0d6efd'), row=1, col=2)
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    
    table = dash_table.DataTable(
        data=rank_df.to_dict('records'), columns=[{"name": i, "id": i} for i in rank_df.columns], 
        sort_action="native", page_size=10, style_table={'overflowX': 'auto'}, 
        style_header={'backgroundColor': '#212529', 'color': '#ffc107', 'fontWeight': 'bold'}, 
        style_cell={'backgroundColor': '#1a1a1a', 'color': '#f8f9fa', 'textAlign': 'center', 'fontSize': '12px'},
        style_data_conditional=[{
            'if': {'filter_query': '{Z-Score (Outlier)} > 2.00 || {Z-Score (Outlier)} < -2.00'},
            'backgroundColor': '#3a2512', 'color': '#ffc107'
        }]
    )
    return fig, table

# ==========================================
# 5. APPLICATION THREAD EXECUTION ENTRY
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)
