# app.py
import os
import json
import itertools
import pandas as pd
import numpy as np
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression

# 1. SYSTEMATIC CORE G4 GLOBAL MATRIX DATA GENERATION
np.random.seed(101)
dates = pd.date_range(end="2026-06-03", periods=500, freq='B')

currencies = ['USD', 'EUR', 'GBP', 'JPY']
tenors = ['3M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

simulated_rows = []
for ccy in currencies:
    if ccy == 'USD': base_rate = 0.0450
    elif ccy == 'GBP': base_rate = 0.0375
    elif ccy == 'EUR': base_rate = 0.0250
    else: base_rate = 0.0050               # JPY near-zero baseline
    
    paths = {}
    for t in tenors:
        tenor_years = 0.25 if '3M' in t else float(''.join(filter(str.isdigit, str(t))))
        curve_slope = (tenor_years / 100) if 'Y' in t else -0.005
        paths[t] = base_rate + curve_slope + np.cumsum(np.random.normal(0, 0.0008, 500))
    
    # Inject an historical curve distortion anomaly into the USD loops
    if ccy == 'USD':
        paths['5Y'][-75:] += 0.0120  
        paths['7Y'][-75:] -= 0.0080
        
    for idx, dt in enumerate(dates):
        for t in tenors:
            simulated_rows.append({
                'date': dt, 'currency': ccy, 'tenor': t, 'rate': paths[t][idx]
            })

master_df = pd.DataFrame(simulated_rows)

# 2. INITIALISE HIGH-PERFORMANCE INTERACTIVE DASHBOARD PLATFORM
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("IRSQuant Automated Multi-Forward RV Scanner", className="text-warning fw-bold mt-4 mb-2"),
            html.P("Systematic Permutation Matrix & Yield Carry Arbitrage Terminal | v6.0", className="text-muted mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        # Configuration Controls Panel Sidebar
        dbc.Col([
            html.Div([
                html.H5("Scan Parameters", className="text-warning mb-3"),
                html.Label("Select Core Currency Target:", className="text-light small fw-bold"),
                dcc.Dropdown(
                    id='ccy-dropdown',
                    options=[{'label': c, 'value': c} for c in currencies],
                    value='USD',
                    className="text-dark mb-4"
                ),
                html.Label("Strategy Matrix Filters:", className="text-light small fw-bold"),
                dcc.RadioItems(
                    id='strategy-type',
                    options=[
                        {'label': ' Run Butterflies (3-Leg loops)', 'value': 'FLY'},
                        {'label': ' Run Condors (4-Leg loops)', 'value': 'CONDOR'}
                    ],
                    value='FLY',
                    labelStyle={'display': 'block', 'className': 'text-muted small mb-2'}
                ),
                html.Hr(className="text-secondary"),
                dbc.Button("Execute Multi-Forward Optimization Scan", id='scan-btn', color="warning", className="w-100 fw-bold py-2")
            ], className="p-3 bg-dark border border-secondary rounded mb-4")
        ], width=3),
        
        # Twin Panels Visual Mapping Canvas
        dbc.Col([
            dcc.Graph(id='rv-analytics-canvas', style={'height': '450px'}, className="mb-4")
        ], width=9)
    ]),
    
    # High-Density Grid Matrix Rankings Output Interface Row
    dbc.Row([
        dbc.Col([
            html.H4("Systematic Curve Alpha Matrix Rankings Table", className="text-warning fw-bold mb-3"),
            html.Div(id='table-container', className="bg-dark p-2 border border-secondary rounded")
        ], width=12)
    ])
], fluid=True)

# 3. DYNAMIC COMBINATORIAL SCANNER ENGINE INTERFACE CALLBACK
@app.callback(
    [Output('rv-analytics-canvas', 'figure'),
     Output('table-container', 'children')],
    [Input('scan-btn', 'n_clicks'),
     Input('ccy-dropdown', 'value'),
     Input('strategy-type', 'value')]
)
def execute_systematic_curve_scan(n_clicks, selected_ccy, strategy_mode):
    ccy_df = master_df[master_df['currency'] == selected_ccy].copy()
    pivot_df = ccy_df.pivot(index='date', columns='tenor', values='rate').dropna()
    
    # Map tenors to explicit float year representations to safely drive matrix transformations
    tenor_map = {'3M': 0.25, '1Y': 1.0, '2Y': 2.0, '3Y': 3.0, '4Y': 4.0, '5Y': 5.0, '7Y': 7.0, '10Y': 10.0}
    spot_tenors = list(tenor_map.keys())
    
    # Build complete cross-sectional matrix of all possible valid Forward Start (n) x Forward Tenor (m) pairs
    forward_series_dict = {}
    for n_str, m_str in itertools.permutations(spot_tenors, 2):
        n = tenor_map[n_str]
        m = tenor_map[m_str]
        combined_years = n + m
        
        nm_str = next((k for k, v in tenor_map.items() if abs(v - combined_years) < 0.01), None)
        if nm_str:
            # Generalized Continuous Compounding Forward Equation Execution Matrix Build
            f_name = f"{n_str}F{m_str}"
            forward_series_dict[f_name] = ((1 + pivot_df[nm_str])**combined_years / (1 + pivot_df[n_str])**n)**(1/m) - 1

    f_matrix_df = pd.DataFrame(forward_series_dict, index=pivot_df.index)
    all_forward_tokens = list(f_matrix_df.columns)
    scan_results = []
    series_storage = {}
    
    if strategy_mode == 'FLY':
        # Generate and evaluate 3-point forward matrix loops
        combinations = list(itertools.combinations(all_forward_tokens, 3))
        for short_f, mid_f, long_f in combinations:
            X = f_matrix_df[[short_f, long_f]].values
            y = f_matrix_df[mid_f].values
            
            # Enforce zero-intercept constraint to eliminate absolute macro drift assumptions
            model = LinearRegression(fit_intercept=False)
            model.fit(X, y)
            
            residuals = y - model.predict(X)
            current_residual = residuals[-1]
            z_score = (current_residual - residuals.mean()) / residuals.std()
            r2 = model.score(X, y)
            
            struct_name = f"FLY: {mid_f} vs [{short_f} & {long_f}]"
            series_storage[struct_name] = pd.Series(residuals, index=pivot_df.index)
            
            scan_results.append({
                'Structure': struct_name,
                'Hedge Ratios': f"Wings: {round(model.coef_[0], 2)} / {round(model.coef_[1], 2)}",
                'R-Squared': round(r2, 4),
                'Current Residual (%)': round(current_residual * 100, 4),
                'Z-Score (Outlier)': round(z_score, 2)
            })
            
    else:  
        # Generate and evaluate 4-point forward matrix loops using Up-Down-Down-Up formatting
        combinations = list(itertools.combinations(all_forward_tokens, 4))
        for f1, f2, f3, f4 in combinations:
            # Native FI Condor Math: (f4 - f3) - (f2 - f1) => Up, Down, Down, Up
            spread_series = (f_matrix_df[f4] - f_matrix_df[f3]) - (f_matrix_df[f2] - f_matrix_df[f1])
            current_residual = spread_series.iloc[-1]
            z_score = (current_residual - spread_series.mean()) / spread_series.std()
            
            struct_name = f"CONDOR: ({f4}-{f3}) vs ({f2}-{f1})"
            series_storage[struct_name] = spread_series
            
            scan_results.append({
                'Structure': struct_name,
                'Hedge Ratios': "System Matrix [1:-1:-1:1]",
                'R-Squared': 1.0,
                'Current Residual (%)': round(current_residual * 100, 4),
                'Z-Score (Outlier)': round(z_score, 2)
            })
            
    rank_df = pd.DataFrame(scan_results)
    rank_df = rank_df.sort_values(by='Z-Score (Outlier)', key=abs, ascending=False)
    
    # 4. MAP TOP-RANKED ANOMALY INTO MULTI-PLOT INTERACTIVE CANVAS
    best_strategy = rank_df.iloc[0]['Structure']
    best_series = series_storage[best_strategy]
    
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Top Alpha Dislocation Timeline', 'Residual Noise Density Distribution'))
    
    # Plot 1: Timeline Analysis Trace
    fig.add_trace(
        go.Scatter(x=best_series.index, y=best_series.values * 100, mode='lines', name='Spread Residual', line=dict(color='#ffc107', width=2)),
        row=1, col=1
    )
    # Map ±2 Standard Deviation institutional risk lines
    mean_val = best_series.mean() * 100
    std_val = best_series.std() * 100
    fig.add_hline(y=mean_val + (2 * std_val), line_dash="dash", line_color="#dc3545", row=1, col=1)
    fig.add_hline(y=mean_val - (2 * std_val), line_dash="dash", line_color="#dc3545", row=1, col=1)
    
    # Plot 2: Volatility Distribution Histogram Trace
    fig.add_trace(
        go.Histogram(x=best_series.values * 100, nbinsx=40, name='Density', marker_color='#6c757d', opacity=0.75),
        row=1, col=2
    )
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    # 5. DATA GRID GRID OUTPUT BUILD
    table = dash_table.DataTable(
        data=rank_df.to_dict('records'),
        columns=[{"name": i, "id": i} for i in rank_df.columns],
        sort_action="native",
        filter_action="native",
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': '#212529', 'color': '#ffc107', 'fontWeight': 'bold', 'border': '1px solid #454d55'},
        style_cell={'backgroundColor': '#1a1a1a', 'color': '#f8f9fa', 'border': '1px solid #2d2d2d', 'fontFamily': 'sans-serif', 'fontSize': '12px', 'textAlign': 'center', 'padding': '8px'},
        style_data_conditional=[{
            'if': {'filter_query': '{Z-Score (Outlier)} > 2.00 || {Z-Score (Outlier)} < -2.00'},
            'backgroundColor': '#3a2512',
            'color': '#ffc107'
        }]
    )
    
    return fig, table

if __name__ == '__main__':
    app.run(debug=True)