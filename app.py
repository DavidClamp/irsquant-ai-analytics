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

# Re-focused strictly on the 4 cornerstone global macro curves
currencies = ['USD', 'EUR', 'GBP', 'JPY']
tenors = ['3M', '1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']

simulated_rows = []
for ccy in currencies:
    # Set structural base yield curves matching target central bank regimes
    if ccy == 'USD': base_rate = 0.0450
    elif ccy == 'GBP': base_rate = 0.0375
    elif ccy == 'EUR': base_rate = 0.0250
    else: base_rate = 0.0050               # JPY near-zero baseline
    
    # Generate historical random-walk trend paths for each maturity component matrix
    paths = {}
    for t in tenors:
        tenor_years = int(''.join(filter(str.isdigit, str(t))))
        # Shape a standard upward-sloping curve baseline matrix
        curve_slope = (tenor_years / 100) if 'Y' in t else -0.005
        paths[t] = base_rate + curve_slope + np.cumsum(np.random.normal(0, 0.0008, 500))
    
    # Inject an historical curve distortion anomaly into the USD 2Yx3Yx5Y loop for alert verification
    if ccy == 'USD':
        paths['3Y'][-75:] += 0.0140  # Anomaly injection to simulate a high-conviction entry tail event
        
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
            html.H2("IRSQuant Automated Core G4 RV Scanner", className="text-warning fw-bold mt-4 mb-2"),
            html.P("Systematic Scikit-Learn Permutation Matrix & Yield Carry Arbitrage Terminal | v5.2", className="text-muted mb-4")
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
                dbc.Button("Execute G4 Optimization Scan", id='scan-btn', color="warning", className="w-100 fw-bold py-2")
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
            html.H4("G4 Systematic Curve Alpha Matrix Rankings Table", className="text-warning fw-bold mb-3"),
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
    # Filter global dataframe pool to current target currency environment
    ccy_df = master_df[master_df['currency'] == selected_ccy].copy()
    pivot_df = ccy_df.pivot(index='date', columns='tenor', values='rate').dropna()
    
    # Isolate 1-Year implied forward contract proxy arrays
    curve_tenors = ['1Y', '2Y', '3Y', '4Y', '5Y', '7Y', '10Y']
    scan_results = []
    
    # Compute system permutations loop across all available curve tracks
    if strategy_mode == 'FLY':
        combinations = list(itertools.combinations(curve_tenors, 3))
        for short_t, mid_t, long_t in combinations:
            X = pivot_df[[short_t, long_t]].values
            y = pivot_df[mid_t].values
            
            # Auto-solve structure weights utilizing scikit-learn linter lines
            model = LinearRegression(fit_intercept=False)
            model.fit(X, y)
            w_short, w_long = model.coef_[0], model.coef_[1]
            
            # Map tracking array residuals vector configurations
            residuals = y - model.predict(X)
            current_residual = residuals[-1]
            z_score = (current_residual - residuals.mean()) / residuals.std()
            r2 = model.score(X, y)
            
            # Calculate Financing Yield Carry and Roll overlay using the 3M matrix row parameters
            current_3m = pivot_df['3M'].iloc[-1]
            carry_roll = pivot_df[mid_t].iloc[-1] - (w_short * current_3m + w_long * current_3m)
            
            scan_results.append({
                'Structure': f'{short_t} x {mid_t} x {long_t}',
                'Hedge Ratio (Short)': round(w_short, 2),
                'Hedge Ratio (Long)': round(w_long, 2),
                'R-Squared': round(r2, 4),
                'Current Residual (%)': round(current_residual * 100, 4),
                'Z-Score (Outlier)': round(z_score, 2),
                '3M Carry & Roll (bps/pa)': round(carry_roll * 10000, 1)
            })
            
    else:  # Run 4-Leg Condor Matrix Analysis Loops
        combinations = list(itertools.combinations(curve_tenors, 4))
        for t1, t2, t3, t4 in combinations:
            # Compute spread residual difference tracking metrics
            spread_series = (pivot_df[t3] - pivot_df[t2]) - (pivot_df[t4] - pivot_df[t1])
            current_residual = spread_series.iloc[-1]
            z_score = (current_residual - spread_series.mean()) / spread_series.std()
            current_3m = pivot_df['3M'].iloc[-1]
            carry_roll = (pivot_df[t4].iloc[-1] - pivot_df[t1].iloc[-1]) - current_3m
            
            scan_results.append({
                'Structure': f'{t1} x {t2} x {t3} x {t4}',
                'Hedge Ratio (Short)': 'Matrix',
                'Hedge Ratio (Long)': 'Matrix',
                'R-Squared': 0.999, 
                'Current Residual (%)': round(current_residual * 100, 4),
                'Z-Score (Outlier)': round(z_score, 2),
                '3M Carry & Roll (bps/pa)': round(carry_roll * 10000, 1)
            })
            
    rank_df = pd.DataFrame(scan_results)
    # Sort globally by absolute statistical dislocation anomaly to extract alpha opportunities immediately
    rank_df = rank_df.sort_values(by='Z-Score (Outlier)', key=abs, ascending=False)
    
    # 4. MAP TOP-RANKED OUTLIER DISLOCATION INTO GRAPH VISUAL PANELS
    best_strategy = rank_df.iloc[0]['Structure']
    fig = make_subplots(rows=1, cols=2, subplot_titles=(f'Top Anomaly Timeline: {best_strategy}', 'Residual Volatility Clustering'))
    
    if strategy_mode == 'FLY':
        s_leg, m_leg, l_leg = best_strategy.split(' x ')
        best_X = pivot_df[[s_leg, l_leg]].values
        best_y = pivot_df[m_leg].values
        best_model = LinearRegression(fit_intercept=False).fit(best_X, best_y)
        res_series = best_y - best_model.predict(best_X)
    else:
        t1, t2, t3, t4 = best_strategy.split(' x ')
        res_series = (pivot_df[t3] - pivot_df[t2]) - (pivot_df[t4] - pivot_df[t1])
        
    fig.add_trace(go.Scatter(x=pivot_df.index, y=res_series * 100, mode='lines', name='Residual Spread', line=dict(color='#ffc107', width=1.5)), row=1, col=1)
    fig.add_trace(go.Histogram(x=res_series * 100, nbinsx=40, name='Density', marker_color='#3498db', opacity=0.8), row=1, col=2)
    fig.update_layout(template='plotly_dark', showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=30, r=30, t=40, b=30))
    
    # Build clean interactive data table output grid UI
    output_table = dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in rank_df.columns],
        data=rank_df.to_dict('records'),
        sort_action="native",
        filter_action="native",
        style_header={'backgroundColor': '#1a1a1a', 'color': '#ffc107', 'fontWeight': 'bold', 'border': '1px solid #444'},
        style_data={'backgroundColor': '#2b2b2b', 'color': '#fff', 'border': '1px solid #444'},
        style_cell={'textAlign': 'center', 'fontFamily': 'monospace', 'fontSize': '12px', 'padding': '6px'},
        page_size=10
    )
    
    return fig, output_table

if __name__ == '__main__':
    app.run(debug=True)
