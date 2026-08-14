# app.py - BLOCK 1: MAIN HEADERS, DATA INGESTION & CORES REGISTER
import pandas as pd
import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
from plotly.subplots import make_subplots

# Ingest your sub-module analytics packages seamlessly
import analytics as an
from curves import BootstrappedDiscountCurve
from vol import Black76Engine
from execution import ExecutionOptimizer

# Ingest your decoupled front-end layout presentation pack blueprints
from layouts.diagnostics import layout_diagnostics
from layouts.scanner import layout_scanner
from layouts.volatility import layout_volatility
from layouts.execution import layout_execution

# Pull all presentation layout package blueprints cleanly out of your verified __init__.py index
#from layouts import layout_diagnostics, layout_scanner, layout_volatility, layout_execution
# ==========================================
# DATA INGESTION & DATA ARCHITECTURE REGIME
# ==========================================
master_df = pd.read_json('g4_curves.json')
master_df['date'] = pd.to_datetime(master_df['date'])
master_df['date_str'] = master_df['date'].dt.strftime('%Y-%m-%d')

currencies = sorted(master_df['currency'].unique())
all_dates = sorted(master_df['date_str'].unique())

# ==========================================
# INITIALISE APPLICATION APP SHELL FRAMEWORK
# ==========================================
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Term Structure Snapshots", href="/", className="nav-link text-warning fw-bold px-3")),
        dbc.NavItem(dcc.Link("Systematic RV Scanner", href="/page-scanner", className="nav-link text-warning fw-bold px-3")),
        dbc.NavItem(dcc.Link("Volatility Analytics", href="/page-volatility", className="nav-link text-warning fw-bold px-3")),
        dbc.NavItem(dcc.Link("Execution Optimizer Desk", href="/page-execution", className="nav-link text-warning fw-bold px-3"))
    ],
    brand="IRSQuant Active Analytics Platform",
    brand_href="/",
    brand_style={'color': '#ffc107', 'fontWeight': 'bold'},
    color="dark",
    dark=True,
    className="mb-4 border-bottom border-secondary"
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Container(id='page-content', fluid=True, className="pb-5")
], style={'backgroundColor': '#0b0c10', 'minHeight': '100vh'})
# app.py - BLOCK 2: INTERFACE CONTROLLER ROUTER & MONITOR CALLBACKS

# ==========================================
# URL INTERFACE CONTROLLER ROUTER MATRIX
# ==========================================
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/page-scanner':
        return layout_scanner(currencies)
    elif pathname == '/page-volatility':
        return layout_volatility(currencies, all_dates)
    elif pathname == '/page-execution':
        return layout_execution(currencies)
    return layout_diagnostics(currencies, all_dates)

# ==========================================
# PRESENTATION INTERFACE LAYER CALL-BACK LOOPS
# ==========================================

@app.callback(
    [Output('diag-term-structure-snapshot', 'figure'), Output('diag-matrix-heatmap', 'figure')],
    [Input('diag-ccy-dropdown', 'value'), Input('diag-date-dropdown', 'value')]
)
def render_snapshot_curves(selected_ccy, selected_date):
    if not selected_date: return go.Figure(), go.Figure()
    day_df = master_df[(master_df['currency'] == selected_ccy) & (master_df['date_str'] == str(selected_date))].copy()
    if day_df.empty: return go.Figure(), go.Figure()
    
    tenor_label_map = {0.25:'3M', 1.0:'1Y', 2.0:'2Y', 3.0:'3Y', 4.0:'4Y', 5.0:'5Y', 6.0:'6Y', 7.0:'7Y', 8.0:'8Y', 9.0:'9Y', 10.0:'10Y', 12.0:'12Y', 15.0:'15Y', 20.0:'20Y', 25.0:'25Y', 30.0:'30Y'}
    raw_spots = day_df.set_index('tenor')['rate'].to_dict()
    spot_rates_dict = {tenor_label_map[float(t)]: float(r) for t, r in raw_spots.items() if float(t) in tenor_label_map}
    
    curve = BootstrappedDiscountCurve(target_date=str(selected_date), spot_rates_dict=spot_rates_dict)
    
    fig_line = go.Figure()
    tenors = sorted(list(curve.spot_rates.keys()), key=lambda x: float(x.replace('M', ''))/12 if 'M' in x else float(x.replace('Y', '')))
    rates = [curve.spot_rates[t]*100 for t in tenors]
    
    fig_line.add_trace(go.Scatter(x=tenors, y=rates, mode='lines+markers', line_shape='hv', line=dict(color='#ffc107', width=3)))
    fig_line.update_layout(title=f"Discrete Step Forward Snapshots - {selected_ccy} ({selected_date})", template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    grid_df = an.generate_forward_block_matrix(curve)
    fig_heat = go.Figure(data=go.Heatmap(z=grid_df.values, x=grid_df.columns, y=grid_df.index, colorscale='Cividis'))
    fig_heat.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig_line, fig_heat

@app.callback(
    [Output('scan-anomaly-canvas', 'figure'), Output('scan-table-container', 'children')],
    [Input('run-scan-btn', 'n_clicks')],
    [State('scan-ccy-dropdown', 'value'), State('scan-type-toggle', 'value')]
)
def execute_interface_regression_sweep(n_clicks, selected_ccy, selected_scan_type):
    if n_clicks is None or n_clicks == 0:
        return go.Figure(), html.Div("Configure parameters above and click 'Execute Curve Matrix Sweep'.", className="text-muted p-3 text-center")
        
    f_matrix = an.build_forward_permutation_matrix(master_df, selected_ccy=selected_ccy)
    rank_df, series_storage = an.run_systematic_condor_scan(f_matrix) if selected_scan_type == 'CONDOR' else an.run_systematic_butterfly_scan(f_matrix)
    
    if rank_df.empty: return go.Figure(), html.Div("Empty DataFrame exception.", className="text-danger p-3")
    
    best_structure_name = rank_df['Structure'].iloc[0]
    best_series = series_storage[best_structure_name]
    
    fig = make_subplots(rows=1, cols=2, column_widths=[0.6, 0.4])
    fig.add_trace(go.Scatter(x=best_series.index, y=best_series.values*10000, mode='lines+markers', line_shape='hv', line=dict(color='#ffc107', width=2)), row=1, col=1)
    fig.add_trace(go.Histogram(x=best_series.values*10000, marker_color='#0d6efd'), row=1, col=2)
    fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
    fig.update_yaxes(title="Residual Dislocation (bps)", tickformat=".1f", row=1, col=1)
    fig.update_xaxes(title="Historical Timeline Axis", type='category', row=1, col=1)
    fig.update_xaxes(title="Frequency Count", tickformat="d", row=1, col=2)
    
    column_formatting = {'Structure':'Structure Permutation', 'Hedge Ratio (Short)':'Hedge Ratio (Short)', 'Hedge Ratio (Long)':'Hedge Ratio (Long)', 'R-Squared':'R-Squared (R²)', 'Current Residual (bps)':'Current Residual (bps)', '1Y Horizon Roll (bps)':'1Y Horizon Roll (bps)', 'Z-Score (Outlier)':'Z-Score Rank'}
    table = dash_table.DataTable(data=rank_df.to_dict('records'), columns=[{"name": column_formatting.get(i, i), "id": i} for i in rank_df.columns], sort_action="native", page_size=10, style_header={'backgroundColor': '#212529', 'color': '#ffc107', 'fontWeight': 'bold'}, style_cell={'backgroundColor': '#1a1a1a', 'color': '#f8f9fa', 'textAlign': 'center'})
    return fig, table
# app.py - BLOCK 3: NON-LINEAR OPTIONS & CAPITAL ALLOCATION CALLBACK DESK

@app.callback(
    [Output('vol-smile-canvas', 'figure'), Output('vol-grid-canvas', 'figure'), Output('vol-matrix-container', 'children')],
    [Input('vol-ccy-dropdown', 'value'), Input('vol-date-dropdown', 'value'), Input('vol-expiry-dropdown', 'value'), Input('vol-tenor-dropdown', 'value'), Input('vol-atm-input', 'value')]
)
def process_volatility_pricing_matrix(selected_ccy, selected_date, expiry_T, tenor_m, atm_vol):
    if not selected_date or atm_vol is None: return go.Figure(), go.Figure(), html.Div("Awaiting target parameters...", className="text-muted p-2")
    ccy_df = master_df[(master_df['currency'] == selected_ccy) & (master_df['date_str'] == str(selected_date))].copy()
    if ccy_df.empty: return go.Figure(), go.Figure(), html.Div("Data record empty.", className="text-danger p-2")
    
    tenor_label_map = {0.25:'3M', 1.0:'1Y', 2.0:'2Y', 3.0:'3Y', 4.0:'4Y', 5.0:'5Y', 6.0:'6Y', 7.0:'7Y', 8.0:'8Y', 9.0:'9Y', 10.0:'10Y', 12.0:'12Y', 15.0:'15Y', 20.0:'20Y', 25.0:'25Y', 30.0:'30Y'}
    raw_spots = ccy_df.set_index('tenor')['rate'].to_dict()
    spot_rates_dict = {tenor_label_map[float(t)]: float(r) for t, r in raw_spots.items() if float(t) in tenor_label_map}
    
    curve = BootstrappedDiscountCurve(target_date=str(selected_date), spot_rates_dict=spot_rates_dict)
    p_start, p_end = curve.get_discount_factor(expiry_T), curve.get_discount_factor(expiry_T + tenor_m)
    annuity = curve.get_annuity_factor(start_n=expiry_T, tenor_m=tenor_m, payment_freq=1.0)
    if annuity == 0.0: return go.Figure(), go.Figure(), html.Div("Annuity collapse.", className="text-danger p-2")
    
    forward_swap = ((p_start - p_end) / annuity) * 100.0
    strikes_dict, quad_vols, sabr_vols = Black76Engine.generate_sabr_vs_quadratic_smiles(forward_swap, float(atm_vol), float(expiry_T))
    
    table_records, smile_strikes, smile_quad_y, smile_sabr_y = [], [], [], []
    for label in ["-200bps", "-100bps", "-50bps", "ATM", "+50bps", "+100bps", "+200bps"]:
        K, v_sabr = strikes_dict[label], sabr_vols[label]
        smile_strikes.append(K * 100.0)
        smile_quad_y.append(quad_vols[label] * 100.0)
        smile_sabr_y.append(v_sabr * 100.0)
        call_prem = Black76Engine.calculate_swaption_price(forward_swap/100.0, K, annuity, v_sabr, expiry_T, option_type='CALL')
        put_prem = Black76Engine.calculate_swaption_price(forward_swap/100.0, K, annuity, v_sabr, expiry_T, option_type='PUT')
        table_records.append({'Strike Offset': label, 'Absolute Strike (%)': round(K * 100.0, 3), 'SABR Implied Vol (%)': round(v_sabr * 100.0, 2), 'Call Premium (bps)': round(call_prem * 10000.0, 1), 'Put Premium (bps)': round(put_prem * 10000.0, 1)})
    
    smile_fig = go.Figure()
    smile_fig.add_trace(go.Scatter(x=smile_strikes, y=smile_quad_y, mode='lines', line=dict(color='#ffc107', width=2, dash='dash'), name='Quadratic'))
    smile_fig.add_trace(go.Scatter(x=smile_strikes, y=smile_sabr_y, mode='lines+markers', line=dict(color='#0d6efd', width=3.5, shape='spline'), name='SABR'))
    smile_fig.update_layout(title=dict(text=f"SABR vs Parametric Skew (ATM = {forward_swap:.3f}%)", font=dict(size=12)), template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    vol_matrix_df = Black76Engine.generate_volatility_term_structure_grid(float(atm_vol))
    grid_fig = go.Figure(data=go.Heatmap(z=vol_matrix_df.values, x=vol_matrix_df.columns, y=vol_matrix_df.index, colorscale='Viridis'))
    grid_fig.update_layout(title=dict(text="Institutional 3D Volatility Surface Heatmap", font=dict(size=12)), template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    
    table_cols = [{"name": i, "id": i} for i in ['Strike Offset', 'Absolute Strike (%)', 'SABR Implied Vol (%)', 'Call Premium (bps)', 'Put Premium (bps)']]
    table_grid = dash_table.DataTable(data=table_records, columns=table_cols, style_header={'backgroundColor': '#212529', 'color': '#ffc107'}, style_cell={'backgroundColor': '#1a1a1a', 'color': '#f8f9fa'})
    return smile_fig, grid_fig, table_grid


# PART 7c: ASYNCHRONOUSLY STABILIZED FRONT-OFFICE EXECUTION DESK CALLBACK
@app.callback(
    [Output('exec-carry-history-canvas', 'figure'), Output('exec-notional-container', 'children')],
    [Input('run-exec-btn', 'n_clicks')],
    [State('exec-ccy-dropdown', 'value'), State('exec-struct-string', 'value'), 
     State('exec-risk-input', 'value'), State('exec-ratio-short', 'value'), State('exec-ratio-long', 'value')]
)
def process_trade_notional_optimization(n_clicks, selected_ccy, structure_string, risk_amount, r_short, r_long):
    # Asynchronous Shield Gate: Preserves virtual DOM layout components on startup
    if n_clicks is None or n_clicks == 0:
        return go.Figure(), html.Div("Configure trade risk parameters on the left panel and click 'Optimize Execution Notional'.", className="text-muted text-center p-3")
        
    if risk_amount is None or not structure_string or r_short is None or r_long is None:
        return go.Figure(), html.Div("Target variables or weight ratio entries missing.", className="text-warning text-center p-3")
        
    f_matrix = an.build_forward_permutation_matrix(master_df, selected_ccy=selected_ccy)
    
    try:
        short_leg, mid_leg, long_leg = "1F1Y", "2F1Y", "3F1Y"
        validated_risk = float(risk_amount)
        
        # Pull clean rounded clips out of upgraded execution engine
        res_dict = ExecutionOptimizer.calculate_duration_neutral_notionals(validated_risk, r_short, r_long, structure_type='FLY')
        fig_carry = ExecutionOptimizer.generate_historical_carry_chart(f_matrix, short_leg, mid_leg, long_leg, float(r_short), float(r_long))
        
        # Formulate highly explicit interbank buy/sell routing layouts
        output_display = html.Div([
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("🔴 " + res_dict['Short Wing Action'], className="badge bg-danger mb-2 d-block text-start fs-6"),
                        html.Strong("Size: "), html.Span(f"${res_dict['Short Wing Notional']:,}", className="text-warning float-end")
                    ], className="p-3 bg-opacity-10 bg-danger rounded border border-danger")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.Span("🟢 " + res_dict['Belly Action'], className="badge bg-success mb-2 d-block text-start fs-6"),
                        html.Strong("Size: "), html.Span(f"${res_dict['Belly Notional']:,}", className="text-warning float-end")
                    ], className="p-3 bg-opacity-10 bg-success rounded border border-success")
                ], width=4),
                dbc.Col([
                    html.Div([
                        html.Span("🔴 " + res_dict['Long Wing Action'], className="badge bg-danger mb-2 d-block text-start fs-6"),
                        html.Strong("Size: "), html.Span(f"${res_dict['Long Wing Notional']:,}", className="text-warning float-end")
                    ], className="p-3 bg-opacity-10 bg-danger rounded border border-danger")
                ], width=4)
            ], className="mb-3 g-3"),
            html.Hr(className="border-secondary"),
            html.Div([
                html.Strong("Total Combined Execution Volume: "),
                html.Span(f"${res_dict['Total Structure Notional']:,}", className="text-info fw-bold fs-5 float-end")
            ])
        ])
        return fig_carry, output_display
    except Exception as e:
        return go.Figure(), html.Div(f"Structural formatting mismatch error: {str(e)}", className="text-danger p-2")

if __name__ == '__main__':
    app.run(debug=True)
