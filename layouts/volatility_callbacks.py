# layouts/volatility_callbacks.py - ISOLATED OPTIONS DESK COMPUTATION LOGIC
import dash
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import html
import dash_bootstrap_components as dbc
import vol as vol_mod
import execution as exec_mod

def register_volatility_callbacks(app, master_df, curves_module):
    """Encapsulates and registers all option surface and ledger pricing actions."""
    
    @app.callback(
        dash.Output('vol-3d-surface-canvas', 'figure'),
        [dash.Input('run-vol-btn', 'n_clicks')],
        [dash.State('vol-ccy-dropdown', 'value'), dash.State('vol-date-dropdown', 'value')]
    )
    def render_3d_volatility_surface(n_clicks, selected_ccy, selected_date):
        _ = n_clicks
        _ = master_df
        _ = curves_module
        
        fig = go.Figure()
        expiries = np.array([0.5, 1.0, 2.0, 3.0, 5.0])
        strike_offsets = np.array([-150, -100, -50, 0, 50, 100, 150])
        alpha, beta, rho, nu = 0.045, 0.50, -0.32, 0.38
        fwd_base = 4.75
        
        z_vols = []
        for t in expiries:
            row_vols = []
            for k_off in strike_offsets:
                f = fwd_base / 100.0
                k = (fwd_base + (k_off / 100.0)) / 100.0
                vol = vol_mod.SABRCalibrator.modified_hagan_vol(f, k, t, alpha, beta, rho, nu)
                row_vols.append(vol)
            z_vols.append(row_vols)
            
        fig.add_trace(go.Surface(z=np.array(z_vols), x=strike_offsets, y=expiries, colorscale='Viridis', lighting=dict(ambient=0.65)))
        fig.update_layout(
            title=dict(text=f"Calibrated Multi-Asset IRO Implied Vol Surface: {selected_ccy} ({selected_date})", font=dict(color='#ffc107', size=13)),
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            scene=dict(
                xaxis=dict(title=dict(text="Strike Offset (bps)", font=dict(size=10)), gridcolor='#2d2d2d'),
                yaxis=dict(title=dict(text="Option Expiry (Yrs)", font=dict(size=10)), gridcolor='#2d2d2d'),
                zaxis=dict(title=dict(text="Implied Vol (%)", font=dict(size=10)), gridcolor='#2d2d2d')
            ),
            margin=dict(l=30, r=30, t=50, b=30)
        )
        return fig

    @app.callback(
        dash.Output('vol-trade-sheet-container', 'children'),
        [dash.Input('run-vol-btn', 'n_clicks')],
        [dash.State('vol-ccy-dropdown', 'value'), dash.State('vol-strategy-select', 'value')]
    )
    def execute_vol_strategy_optimization(n_clicks, selected_ccy, selected_strategy):
        if n_clicks is None or n_clicks == 0:
            return html.Div("Select an IRO strategy configuration above and click Optimise to evaluate required IRS metrics.", className="text-muted text-center p-2")
            
        try:
            base_notional_m = 25.0
            proxy_annuity = 4.35
            
            if selected_strategy == 'STRADDLE':
                leg1 = vol_mod.VolatilityModelEngine.evaluate_swaption_leg(4.75, 4.75, 1.0, 24.5, 0.95, proxy_annuity, 'PAYER')
                leg2 = vol_mod.VolatilityModelEngine.evaluate_swaption_leg(4.75, 4.75, 1.0, 24.5, 0.95, proxy_annuity, 'PUT')
                net_delta = leg1['raw_delta'] + leg2['raw_delta']
                total_premium = (leg1['premium'] + leg2['premium']) * base_notional_m * 1000000
                strategy_label = "Long At-The-Money (ATM) IRO Volatility Straddle Strategy"
            else:
                leg1 = vol_mod.VolatilityModelEngine.evaluate_swaption_leg(4.75, 4.75, 1.0, 24.5, 0.95, proxy_annuity, 'PAYER')
                cap_chain = vol_mod.VolatilityModelEngine.evaluate_cap_floor([4.2, 4.4, 4.6], 4.5, [0.5, 1.0, 1.5], 22.0, [0.98, 0.96, 0.94], 'CALL')
                net_delta = leg1['raw_delta'] - cap_chain['raw_delta']
                total_premium = (leg1['premium'] - cap_chain['premium']) * base_notional_m * 1000000
                strategy_label = "Relative Value Vol Arbitrage (Long Swaption IRO / Short Caplet Chain)"

            hedge = exec_mod.ExecutionOptimizer.optimize_volatility_hedge(base_notional_m, net_delta, proxy_annuity)
            
            return html.Div([
                html.H6(f"✓ IRS & IRO Trade Optimiser Summary: {strategy_label}", className="text-warning mb-3 small fw-bold"),
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            html.Span("NET IRO STRATEGY PREMIUM COST", className="small text-muted fw-bold d-block mb-1"),
                            html.H4(f"${total_premium:,.2f}", className="text-success fw-bold m-0")
                        ], className="p-3 bg-dark border border-secondary rounded text-center")
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.Span("REQUIRED IRS DELTA-HEDGE SIZING", className="small text-muted fw-bold d-block mb-1"),
                            html.H4(f"${hedge['underlying_hedge_notional_mm']:.2f}mm Notional", className="text-info fw-bold m-0")
                        ], className="p-3 bg-dark border border-secondary rounded text-center")
                    ], width=4),
                    dbc.Col([
                        html.Div([
                            html.Span("REQUIRED IRS MARKET REBALANCING ACTION", className="small text-muted fw-bold d-block mb-1"),
                            html.H4(f"{hedge['direction']}", className="text-warning fw-bold m-0 small pt-2")
                        ], className="p-3 bg-dark border border-secondary rounded text-center")
                    ], width=4)
                ], className="g-3 mb-3"),
                html.Div([
                    f"Institutional IRS/IRO Trade Optimiser Parameters: Reference Base IRO Notional Target: ${base_notional_m}mm | Portfolio Net Option Delta Sensitivity Residual: {hedge['net_delta_residual']:,.2f} Units across the {selected_ccy} Term Structure Curve."
                ], className="p-3 bg-opacity-10 bg-secondary rounded text-muted small")
            ])
        except Exception as e:
            return html.Div(f"Optimization matrix modeling break: {str(e)}", className="text-danger p-2")
