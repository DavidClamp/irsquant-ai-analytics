# app.py
import numpy as np
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ==========================================
# 1. CORE DATA ENGINE: INITIALISATION & TRANSFORM
# ==========================================
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
    
    # Inject a distinct structural forward anomaly in USD long-end structures
    if ccy == 'USD':
        paths['3Y'][-100:] += 0.0140  # Direct curve twist injection
        
    for idx, dt in enumerate(dates):
        for t in tenors:
            simulated_rows.append({
                'date': dt, 'currency': ccy, 'tenor': t, 'rate': paths[t][idx]
            })

master_df = pd.DataFrame(simulated_rows)

def generate_1y_forward_matrix(df, selected_ccy):
    """
    Isolates spot data and converts to clean 1-Year Implied Forward contract spaces.
    Formula: F(t, t+1) = [ (1 + R_{t+1})^(t+1) / (1 + R_t)^t ] - 1
    """
    ccy_df = df[df['currency'] == selected_ccy].copy()
    pivot_df = ccy_df.pivot(index='date', columns='tenor', values='rate').dropna()
    
    f_df = pd.DataFrame(index=pivot_df.index)
    f_df['0YF1Y (1Y Spot)'] = pivot_df['1Y']
    f_df['1YF1Y (2Y Spot)'] = ((1 + pivot_df['2Y'])**2 / (1 + pivot_df['1Y'])**1) - 1
    f_df['2YF1Y (3Y Spot)'] = ((1 + pivot_df['3Y'])**3 / (1 + pivot_df['2Y'])**2) - 1
    f_df['3YF1Y (4Y Spot)'] = ((1 + pivot_df['4Y'])**4 / (1 + pivot_df['3Y'])**3) - 1
    f_df['4YF1Y (5Y Spot)'] = ((1 + pivot_df['5Y'])**5 / (1 + pivot_df['4Y'])**4) - 1
    
    return f_df

# ==========================================
# 2. PLATFORM INITIALISATION & GLOBAL LAYOUT
# ==========================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Forward Charts", href="/page-forwards", className="nav-link text-warning fw-bold px-3")),
        dbc.NavItem(dcc.Link("Systematic RV Scanner", href="/page-scanner", className="nav-link text-muted px-3")),
    ],
    brand="IRSQuant Analytical Platform",
    brand_href="/",
    color="dark",
    dark=True,
    className="border-bottom border-secondary mb-4 px-4"
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Container(id='page-content', fluid=True)
])

# ==========================================
# 3. STATIC PAGE VIEW COMPONENT BLOCKS
# ==========================================
layout_index = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("G4 Institutional Analytics Console", className="text-warning fw-bold mt-4 mb-2"),
            html.P("Welcome David. Select an analytical page from the navigation bar above to begin.", className="text-muted mb-4"),
            html.Hr(className="text-secondary"),
        ], width=12)
    ])
])

# Page 1: Upgraded Implied Forwards Dashboard (Side-by-Side Plots Layout)
layout_forwards = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("1-Year Constant Maturity Implied Forwards Analysis Workspace", className="text-warning fw-bold mb-2"),
            html.P("Dual-panel monitoring system tracking forward timeline paths alongside distribution density charts.", className="text-muted mb-4")
        ], width=12)
    ]),
    
    dbc.Row([
        # Control configuration sidebar panel
        dbc.Col([
            html.Div([
                html.H5("Configuration", className="text-warning mb-3"),
                html.Label("Select Currency Node:", className="text-light small fw-bold"),
                dcc.Dropdown(
                    id='fwd-ccy-dropdown',
                    options=[{'label': c, 'value': c} for c in currencies],
                    value='USD',
                    className="text-dark mb-4"
                ),
                html.Label("Select Implied Forward Leg:", className="text-light small fw-bold"),
                dcc.Dropdown(
                    id='fwd-leg-dropdown',
                    placeholder="Select leg...",
                    className="text-dark"
                )
            ], className="p-3 bg-dark border border-secondary rounded mb-4")
        ], width=3),
        
        # Twin Panels Visual Mapping Canvas (Timeline left, Histogram right)
        dbc.Col([
            dcc.Graph(id='fwd-twin-canvas', style={'height': '500px'})
        ], width=9)
    ])
])

layout_scanner = html.Div([
    dbc.Row([
        dbc.Col([
            html.H3("Systematic Multi-Forward Relative Value Scanner", className="text-warning fw-bold mb-2"),
            html.P("Workspace currently being rebuilt for systematic portfolio logic synchronization.", className="text-muted mb-4"),
            html.Div(className="border border-dashed border-secondary p-5 text-center text-muted rounded", children=[
                "Structural Scanner Module Deactivated for Slow Rebuild Protocol."
            ])
        ], width=12)
    ])
])

# ==========================================
# 4. PLATFORM CONTROL ROUTING SYSTEM (CALLBACKS)
# ==========================================
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/page-forwards':
        return layout_forwards
    elif pathname == '/page-scanner':
        return layout_scanner
    else:
        return layout_index

@app.callback(
    [Output('fwd-leg-dropdown', 'options'),
     Output('fwd-leg-dropdown', 'value')],
    Input('fwd-ccy-dropdown', 'value')
)
def populate_forward_legs(selected_ccy):
    sample_fwd_df = generate_1y_forward_matrix(master_df, selected_ccy)
    options = [{'label': col, 'value': col} for col in sample_fwd_df.columns]
    default_val = sample_fwd_df.columns[0]
    return options, default_val

# Upgraded Callback: Generates both the timeline tracking and distribution plots side-by-side
@app.callback(
    Output('fwd-twin-canvas', 'figure'),
    [Input('fwd-ccy-dropdown', 'value'),
     Input('fwd-leg-dropdown', 'value')]
)
def update_forward_twin_plots(selected_ccy, selected_leg):
    if not selected_leg:
        return go.Figure()
        
    fwd_df = generate_1y_forward_matrix(master_df, selected_ccy)
    leg_data = fwd_df[selected_leg]
    
    mean_val = leg_data.mean()
    std_val = leg_data.std()
    latest_val = leg_data.iloc[-1]
    
    # Construct a 1x2 Subplot matrix layout panel
    fig = make_subplots(
        rows=1, cols=2, 
        shared_yaxes=False,
        column_widths=[0.6, 0.4], # 60% space for Timeline, 40% for Histogram
        subplot_titles=('Historical Timeline Track', 'Historical Value Distribution Density')
    )
    
    # 1. Left Panel Trace: Continuous Historical Timeline Line Chart
    fig.add_trace(
        go.Scatter(
            x=leg_data.index, 
            y=leg_data.values * 100, # Base conversion to readable percentages
            mode='lines',
            name='Forward Rate',
            line=dict(color='#ffc107', width=1.5)
        ),
        row=1, col=1
    )
    # Overlay an institutional mean reference boundary line on the timeline
    fig.add_hline(y=mean_val * 100, line_width=1.5, line_color="#6c757d", line_dash="dash", row=1, col=1)
    
    # 2. Right Panel Trace: Value Distribution Histogram
    fig.add_trace(
        go.Histogram(
            x=leg_data.values * 100,
            nbinsx=35,
            name='Density Distribution',
            marker=dict(color='#0d6efd', line=dict(color='#1a1a1a', width=0.5)), # Corporate Blue accent
            opacity=0.75
        ),
        row=1, col=2
    )
    # Add vertical latest value indicator anchor onto the density map
    fig.add_vline(x=latest_val * 100, line_width=2.5, line_color="#dc3545", row=1, col=2)
    
    # Configuration formatting properties for the enterprise canvas template
    fig.update_layout(
        title=dict(text=f"{selected_ccy} {selected_leg} Core Analytics Console", font=dict(color='#ffc107', size=16)),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    fig.update_xaxes(title_text="Date Timeline", gridcolor='#2d2d2d', row=1, col=1)
    fig.update_yaxes(title_text="Forward Rate (%)", gridcolor='#2d2d2d', row=1, col=1)
    
    fig.update_xaxes(title_text="Rate Band (%)", gridcolor='#2d2d2d', row=1, col=2)
    fig.update_yaxes(title_text="Frequency Count", gridcolor='#2d2d2d', row=1, col=2)
    
    return fig

# ==========================================
# 5. PLATFORM EXECUTION BOUNDARY ENTRY
# ==========================================
if __name__ == '__main__':
    app.run(debug=True)
