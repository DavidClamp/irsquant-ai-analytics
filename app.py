# app.py
import os
import json
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Clean institutional imports from your Layer 2 analytics engine
from analytics import (
    build_forward_permutation_matrix,
    run_systematic_butterfly_scan,
    run_systematic_condor_scan,
    extract_forward_curve_snapshot,
    generate_forward_block_matrix
)

# Resolve local path string directory to the database file
json_path = os.path.join(os.path.dirname(__file__), 'g4_curves.json')
if not os.path.exists(json_path):
    raise FileNotFoundError(f"Missing essential dataset file: {json_path}")

# Vectorize and load multi-tenor curves
master_df = pd.read_json(json_path)
master_df['date'] = pd.to_datetime(master_df['date'])

# Extract curve variables for component dropdown binding loops
currencies = master_df['currency'].unique().tolist()
dates = master_df['date'].unique()
# Initialize the Dash application server thread container
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
server = app.server

# Shared Navigation Banner Component Matrix
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Term Structure Snapshots", href="/page-diagnostics", className="nav-link text-warning fw-bold px-3")),
        dbc.NavItem(dcc.Link("Systematic RV Scanner", href="/page-scanner", className="nav-link text-muted px-3")),
    ],
    brand="IRSQuant Analytical Platform",
    brand_href="/",
    color="dark",
    dark=True,
    className="border-bottom border-secondary mb-4 px-4"
)

## app.py - DYNAMIC ROOT ROUTING INFRASTRUCTURE
def serve_layout():
    return html.Div([
        dcc.Location(id='url', refresh=False),
        navbar,
        dbc.Container(id='page-content', fluid=True)
    ])

app.layout = serve_layout 
# Force validation across independent runtime views
app.config.suppress_callback_exceptions = True
#  Blueprint: Term Horizon Snapshot Terminal (Upgraded to 30Y Dynamic View)
layout_diagnostics = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Implied Forward Curve Term Snapshot Console", className="text-warning fw-bold mb-2"),
            html.P("Dual-Regime Monitoring Engine: 1Y Forwards (0Y-10Y Horizon) | 5Y Forwards (10Y-30Y Horizon).", className="text-muted mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        # Strategic selection filters configuration sidebar
        dbc.Col([
            html.Div([
                html.H5("Curve Configuration", className="text-warning mb-3"),
                
                html.Label("Select Currency Target:", className="text-light small fw-bold"),
                dcc.Dropdown(id='diag-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                
                html.Label("Review Historical Date:", className="text-light small fw-bold"),
                dcc.Dropdown(id='diag-date-dropdown', placeholder="Loading latest date matrix...", className="text-dark")
            ], className="p-3 bg-dark border border-secondary rounded mb-4")
        ], width=3),

        # Dual-Regime continuous canvas and accompanying matrix block surface panel
        dbc.Col([
            dcc.Graph(id='diag-twin-canvas', style={'height': '420px'}, className="mb-4"),
            html.H5("Continuous Implied Forward Block Matrix Surface Grid (%)", className="text-warning small fw-bold mb-2"),
            dcc.Graph(id='diag-matrix-heatmap', style={'height': '320px'})
        ], width=9)     
    ])
])
# Page 2 Blueprint: Cross-Sectional Alpha Arbitrage Scanner Terminal
layout_scanner = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Systematic Multi-Node Forward Curve Arbitrage Scanner", className="text-warning fw-bold mb-2"),
            html.P("Zero-constant multivariable linear regressions monitoring systematic anomalies.", className="text-muted mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        # Execution control panel sidebar trigger block
        dbc.Col([
            html.Div([
                html.H5("Scan Trigger Matrix", className="text-warning mb-3"),
                
                html.Label("Select Target Currency Block:", className="text-light small fw-bold"),
                dcc.Dropdown(id='scan-ccy-dropdown', options=[{'label': c, 'value': c} for c in currencies], value='USD', className="text-dark mb-4"),
                
                # Upgraded Feature: Structure Type Selection Toggle Matrix
                html.Label("Select Structure Matrix Type:", className="text-light small fw-bold mb-2"),
                dcc.RadioItems(
                    id='scan-type-toggle',
                    options=[
                        {'label': ' 3-Node Butterfly Scan (Body vs Wings)', 'value': 'FLY'},
                        {'label': ' 4-Node Condor Scan (Up-Down-Down-Up Twist)', 'value': 'CONDOR'}
                    ],
                    value='FLY',
                    labelStyle={'display': 'block', 'color': '#f8f9fa', 'fontSize': '13px'},
                    className="mb-4"
                ),
                
                dbc.Button("Execute Curve Matrix Sweep", id='run-scan-btn', color="warning", className="w-100 fw-bold py-2")
            ], className="p-3 bg-dark border border-secondary rounded mb-4")
        ], width=3),
        
        # Interactive analytics charts canvas view area
        dbc.Col([
            dcc.Graph(id='scan-anomaly-canvas', style={'height': '400px'}, className="mb-4"),
            html.Div(id='scan-table-container', className="bg-dark p-2 border border-secondary rounded")
        ], width=9)
    ])
])

# URL Routing Callback: Controls active view container mapping
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-scanner':
        return layout_scanner
    return layout_diagnostics  # Default fallback routes index directly to Page 1 snapshot terminal

# app.py - UNIFIED MULTI-PAGE LAYOUT DATA FLOW HOTFIX 6

@app.callback(
    [Output('diag-date-dropdown', 'options'), Output('diag-date-dropdown', 'value')],
    Input('diag-ccy-dropdown', 'value')
)
def auto_populate_and_default_to_latest_date(selected_ccy):
    if master_df.empty or not selected_ccy:
        return [], None
        
    # Isolate and coerce dates strictly to string objects to prevent layout serialization hangs
    ccy_df = master_df[master_df['currency'] == selected_ccy].copy()
    ccy_df['date_str'] = ccy_df['date'].dt.strftime('%Y-%m-%d')
    unique_dates = sorted(ccy_df['date_str'].unique())
    
    if not unique_dates:
        return [], None
        
    date_options = [{'label': d, 'value': d} for d in unique_dates]
    latest_date_value = unique_dates[-1] # Grabs the absolute newest date string automatically
    
    return date_options, latest_date_value

# Consolidated Page 1 Step-Snapshot Curve Renderer Core with String Formatting Gates
@app.callback(
    Output('diag-twin-canvas', 'figure'),
    [Input('diag-ccy-dropdown', 'value'), Input('diag-date-dropdown', 'value')]
)
def render_term_structure_forward_steps(selected_ccy, selected_date):
    # Guard against startup initialization states while dropdown mounts
    if not selected_date or selected_date == "Loading latest date matrix...":
        return go.Figure()
        
    # ACTIVATION: Call your imported purple function to pull the dual-regime coordinates
    # Cleaned of the dead view_mode parameter to match your optimized analytics layer perfectly
    x_starts, x_ends, y_rates = extract_forward_curve_snapshot(master_df, selected_ccy, str(selected_date))
    
    if not y_rates:
        return go.Figure()
        
    fig = go.Figure()
    
    # Restructure elements into continuous single trace vectors
    x_timeline = []
    y_stepped_rates = []
    for i in range(len(y_rates)):
        x_timeline.extend([x_starts[i], x_ends[i]])
        y_stepped_rates.extend([y_rates[i], y_rates[i]])
        
    # Single continuous institutional trace utilizing 'hv' 90-degree step functions
    fig.add_trace(go.Scatter(
        x=x_timeline, y=y_stepped_rates,
        mode='lines+markers', line_shape='hv', name='Forward Curve',
        line=dict(color='#ffc107', width=3.5),
        marker=dict(size=6, symbol='square', color='#ffc107'),
        hovertemplate="Maturity Horizon: %{x}Y out<br>Forward Yield Rate: %{y:.2f}%<extra></extra>"
    ))

    # Canvas properties styling configuration array - AXIS TERMINATED LOCKED AT 31.0 YEARS
    fig.update_layout(
        title=dict(text=f"Institutional Forward Curve Term Structure Snapshot ({selected_ccy} | Dual Horizon | {selected_date})", font=dict(color='#ffc107', size=14)),
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
        margin=dict(l=55, r=40, t=65, b=55),
        xaxis=dict(
            title="Maturity Curve Horizon Timeline (Years out from Present Day)", 
            gridcolor='#2d2d2d', tickmode='linear', dtick=2.0,
            range=[0, 31.0] # HARD LOCKED: Frames the curve horizon out past 30 Years beautifully
        ),
        yaxis=dict(title="Forward Implied Interest Yield Rate (%)", gridcolor='#2d2d2d')
    )
    return fig


# app.py - PART 7: CONSOLIDATED CHANNELS CALLBACK
@app.callback(
    [Output('scan-anomaly-canvas', 'figure'), Output('scan-table-container', 'children')],
    [Input('run-scan-btn', 'n_clicks'), Input('scan-ccy-dropdown', 'value'), Input('scan-type-toggle', 'value')]
)
# CONSOLIDATED SCANNER CALLBACK CORRECTION
def execute_interface_regression_sweep(_, selected_ccy, selected_scan_type):
    # 1. Build the baseline forward contract data matrix
    # CLEANED ACCURATELY TO MATCH YOUR OPTIMISED LAYER 2 SIGNATURE
    f_matrix = build_forward_permutation_matrix(master_df, selected_ccy=selected_ccy)
    
    # 2. Dynamic Routing: Execute the specific mathematical model chosen by the user sidebar toggle
    if selected_scan_type == 'CONDOR':
        rank_df, series_storage = run_systematic_condor_scan(f_matrix)
    else:
        rank_df, series_storage = run_systematic_butterfly_scan(f_matrix)
        
    # Extract the highest-ranking statistical outlier from the sorted dataframe matrix
    if rank_df.empty: 
        return go.Figure(), html.Div("Empty DataFrame structural parsing exception state.", className="text-danger p-3")
    
    # PERFECT LOOKUP: Extract the top sorted string element cleanly using absolute index position
    best_structure_name = rank_df.loc[rank_df.index[0], 'Structure']
    best_series = series_storage[best_structure_name]

    # Generate the twin subplots: Time-Series Residual Steps (Left) + Frequency Distribution Histogram (Right)
    fig = make_subplots(rows=1, cols=2, column_widths=[0.6, 0.4])
    
    fig.add_trace(go.Scatter(
        x=best_series.index, y=best_series.values * 10000, 
        mode='lines+markers', line_shape='hv', 
        line=dict(color='#ffc107', width=2.0),
        marker=dict(size=5, symbol='square', color='#ffc107'),
        name='Residual (bps)',
        hovertemplate="Date: %{x}<br>Residual Dislocation: %{y:.2f} bps<extra></extra>"
    ), row=1, col=1)
    
    fig.add_trace(go.Histogram(
        x=best_series.values * 10000, nbinsx=10, 
        marker_color='#0d6efd', name='Frequency'
    ), row=1, col=2)
    
    # Dynamic calculation of the +/- 2.00 Z-Score boundaries in basis points for the visual anchor lines
    std_dev_bps = best_series.std() * 10000
    mean_bps = best_series.mean() * 10000
    upper_tail = mean_bps + (2.00 * std_dev_bps)
    lower_tail = mean_bps - (2.00 * std_dev_bps)
    
    # Add Upper and Lower Tail Risk Threshold Boundary Lines
    fig.add_shape(type="line", x0=best_series.index[0], x1=best_series.index[-1], y0=upper_tail, y1=upper_tail, line=dict(color="#dc3545", width=1.5, dash="dash"), row=1, col=1)
    fig.add_shape(type="line", x0=best_series.index[0], x1=best_series.index[-1], y0=lower_tail, y1=lower_tail, line=dict(color="#dc3545", width=1.5, dash="dash"), row=1, col=1)
    
    fig.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
        margin=dict(l=40, r=20, t=20, b=40)
    )
    
    fig.update_yaxes(title="Residual Dislocation (bps)", gridcolor='#2d2d2d', row=1, col=1)
    fig.update_xaxes(title="Historical Timeline Axis", gridcolor='#2d2d2d', row=1, col=1)
    
    # Formulate high-density front office searchable datagrid layout matrix table
    table = dash_table.DataTable(
        data=rank_df.to_dict('records'), 
        columns=[{"name": i, "id": i} for i in rank_df.columns], 
        sort_action="native", 
        page_size=10, 
        style_table={'overflowX': 'auto'}, 
        style_header={'backgroundColor': '#212529', 'color': '#ffc107', 'fontWeight': 'bold'}, 
        style_cell={'backgroundColor': '#1a1a1a', 'color': '#f8f9fa', 'textAlign': 'center', 'fontSize': '12px'},
        style_data_conditional=[{
            'if': {'filter_query': '{Z-Score (Outlier)} > 2.00 || {Z-Score (Outlier)} < -2.00'},
            'backgroundColor': '#3a2512', 'color': '#ffc107'
        }]
    )
    return fig, table

# Main system application runtime process start checkpoint hook
if __name__ == '__main__':
    app.run(debug=True)
