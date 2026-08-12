import os
import pandas as pd
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Namespace Core: Ingest the analytical framework as a clean package handle
import analytics as an

# 1. Ingest your continuous chronological data matrix file
master_df = pd.read_json('g4_curves.json')

# 2. Strict Type Coercion: Force formatting of data types to prevent serialization loops
master_df['date'] = pd.to_datetime(master_df['date'])
master_df['date_str'] = master_df['date'].dt.strftime('%Y-%m-%d')

# 3. Establish the global selection index parameter arrays
currencies = sorted(master_df['currency'].unique())
all_dates = sorted(master_df['date_str'].unique())

# 4. Instantiate the core web application container utilizing the Cyborg stylesheet
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server

# 5. Build out your front office corporate styling navbar shell structure
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Term Structure Snapshots", href="/", className="nav-link text-warning fw-bold px-3")),
        dbc.NavItem(dcc.Link("Systematic RV Scanner", href="/page-scanner", className="nav-link text-warning fw-bold px-3"))
    ],
    brand="IRSQuant Active Analytics Platform",
    brand_href="/",
    color="dark",
    dark=True,
    fluid=True,
    className="mb-4 border-bottom border-secondary shadow"
)


# ==========================================
# PART 5: FRONT OFFICE VIEW LAYOUT BLUEPRINTS
# ==========================================

def layout_diagnostics():
    return html.Div([
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
                    dcc.Dropdown(
                        id='diag-date-dropdown', 
                        options=[{'label': d, 'value': d} for d in all_dates], 
                        value=all_dates[-1] if all_dates else None,            
                        className="text-dark"
                    )
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


def layout_scanner():
    return html.Div([
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
                    
                    # Structure Type Selection Toggle Matrix Matrix
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


# ==========================================
# PART 6: PAGE 1 DIAGNOSTICS CALLBACK CORE
# ==========================================

@app.callback(
    Output('diag-twin-canvas', 'figure'),
    [Input('diag-ccy-dropdown', 'value'), Input('diag-date-dropdown', 'value')]
)
def render_term_structure_forward_steps(selected_ccy, selected_date):
    if not selected_date or selected_date == "Loading latest date matrix...":
        return go.Figure()
        
    x_starts, x_ends, y_rates = an.extract_forward_curve_snapshot(master_df, selected_ccy, selected_date)
    
    if not y_rates:
        return go.Figure()

    x_timeline = []
    y_stepped_rates = []
    for i in range(len(y_rates)):
        x_timeline.extend([x_starts[i], x_ends[i]])
        y_stepped_rates.extend([y_rates[i], y_rates[i]])
        
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_timeline, y=y_stepped_rates,
        mode='lines+markers', line_shape='hv', name='Forward Curve',
        line=dict(color='#ffc107', width=3.5),
        marker=dict(size=6, symbol='square', color='#ffc107'),
        hovertemplate="Horizon: %{x}Y<br>Forward Yield Rate: %{y:.2f}%<extra></extra>"
    ))

    fig.update_layout(
        title=dict(text=f"Institutional Forward Curve Term Structure Snapshot ({selected_ccy} | Dual Horizon | {selected_date})", font=dict(color='#ffc107', size=14)),
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
        margin=dict(l=55, r=40, t=65, b=55),
        xaxis=dict(title="Maturity Curve Horizon Timeline (Years out)", gridcolor='#2d2d2d', tickmode='linear', dtick=2.0, range=[0, 31.0]),
        yaxis=dict(title="Forward Implied Interest Yield Rate (%)", gridcolor='#2d2d2d', range=[0.0, 6.0])
    )
    return fig

@app.callback(
    Output('diag-matrix-heatmap', 'figure'),
    [Input('diag-ccy-dropdown', 'value'), Input('diag-date-dropdown', 'value')]
)
def render_forward_block_matrix_heatmap(selected_ccy, selected_date):
    if not selected_date or selected_date == "Loading latest date matrix...":
        return go.Figure()
        
    from curves import BootstrappedDiscountCurve
    
    # Global institutional tenor definition map used to protect data ingestion channels
    tenor_label_map = {
        0.25: '3M', 1.0: '1Y', 2.0: '2Y', 3.0: '3Y', 4.0: '4Y', 
        5.0: '5Y',  6.0: '6Y', 7.0: '7Y', 8.0: '8Y', 9.0: '9Y', 
        10.0: '10Y', 12.0: '12Y', 15.0: '15Y', 20.0: '20Y', 
        25.0: '25Y', 30.0: '30Y'
    }
    
    heatmap_ccy_df = master_df[(master_df['currency'] == selected_ccy) & (master_df['date_str'] == str(selected_date))].copy()
    
    if heatmap_ccy_df.empty:
        return go.Figure()
        
    raw_spots = heatmap_ccy_df.set_index('tenor')['rate'].to_dict()
    
    # CRUCIAL ACTIVATION: Transform raw float keys into valid institutional text labels
    heatmap_spots_dict = {tenor_label_map[t]: float(r) for t, r in raw_spots.items() if t in tenor_label_map}
    
    # Instantiate the curve object with explicit validated keyword parameters
    curve_obj = BootstrappedDiscountCurve(target_date=str(selected_date), spot_rates_dict=heatmap_spots_dict)
    
    grid_df = an.generate_forward_block_matrix(curve_obj)
    
    heatmap_fig = go.Figure(data=go.Heatmap(
        z=grid_df.values,
        x=grid_df.columns,
        y=grid_df.index,
        colorscale='Cividis',
        text=grid_df.values,
        texttemplate="%{text}%",
        textfont={"size": 11, "color": "white"},
        hovertemplate="Start Node: %{y}<br>Forward Length: %{x}<br>Yield Rate: %{z}%<extra></extra>"
    ))
    
    heatmap_fig.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=55, r=40, t=10, b=40),
        xaxis=dict(title="Forward Contract Horizon Length (Tenor m)"),
        yaxis=dict(title="Forward Start Delay Node (Expiry n)")
    )
    return heatmap_fig




# ==========================================
# PART 7: PAGE 2 SYSTEMATIC SCANNER CALLBACK
# ==========================================

@app.callback(
    [Output('scan-anomaly-canvas', 'figure'), Output('scan-table-container', 'children')],
    [Input('run-scan-btn', 'n_clicks'), Input('scan-ccy-dropdown', 'value'), Input('scan-type-toggle', 'value')]
)
def execute_interface_regression_sweep(_, selected_ccy, selected_scan_type):
    f_matrix = an.build_forward_permutation_matrix(master_df, selected_ccy=selected_ccy)
    
    if selected_scan_type == 'CONDOR':
        rank_df, series_storage = an.run_systematic_condor_scan(f_matrix)
    else:
        rank_df, series_storage = an.run_systematic_butterfly_scan(f_matrix)
        
    if rank_df.empty: 
        return go.Figure(), html.Div("Empty DataFrame structural parsing exception state.", className="text-danger p-3")
    
    best_structure_name = rank_df['Structure'].iloc[0]
    best_series = series_storage[best_structure_name]
    
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
    
    std_dev_bps = best_series.std() * 10000
    mean_bps = best_series.mean() * 10000
    upper_tail = mean_bps + (2.00 * std_dev_bps)
    lower_tail = mean_bps - (2.00 * std_dev_bps)
    
    fig.add_shape(type="line", x0=best_series.index[0], x1=best_series.index[-1], y0=upper_tail, y1=upper_tail, line=dict(color="#dc3545", width=1.5, dash="dash"), row=1, col=1)
    fig.add_shape(type="line", x0=best_series.index[0], x1=best_series.index[-1], y0=lower_tail, y1=lower_tail, line=dict(color="#dc3545", width=1.5, dash="dash"), row=1, col=1)
    
    fig.update_layout(
        template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False,
        margin=dict(l=40, r=20, t=20, b=40)
    )
    
    fig.update_yaxes(title="Residual Dislocation (bps)", gridcolor='#2d2d2d', row=1, col=1)
    fig.update_xaxes(title="Historical Timeline Axis", gridcolor='#2d2d2d', row=1, col=1)
    
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

# ==========================================
# PART 8: SYSTEM ROUTING & ARCHITECTURE CORE
# ==========================================

@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-scanner':
        return layout_scanner()
    return layout_diagnostics()

def serve_layout():
    return html.Div([
        dcc.Location(id='url', refresh=False),
        navbar,
        dbc.Container(id='page-content', fluid=True)
    ])

app.layout = serve_layout
app.config.suppress_callback_exceptions = True

if __name__ == '__main__':
    app.run(debug=True)
