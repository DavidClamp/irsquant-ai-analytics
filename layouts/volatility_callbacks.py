# layouts/volatility_callbacks.py - UNIFIED 8-CURRENCY OPTIONS LIFECYCLE CALLBACK ENGINE
import json
import math
import numpy as np
from dash import html, Input, Output, State, ALL
import dash_bootstrap_components as dbc

# 🟢 ROOT DIRECTION SYNC: Points directly to your root-level quantitative math scripts
from vol import VolatilityModelEngine
from vol_surfaces_core import VolatilitySurfaceStripper
from config import GLOBAL_UNIVERSE

def register_global_volatility_pipelines(app):
    """
    Centralised front-office options callback hub routing interactive parameters 
    for both the Swaption Expiry Surface and Cap/Floor Caplet chain desks across 8 currencies.
    """
    
    # =========================================================================
    # 🟢 PIPELINE 1: DYNAMIC 8-CURRENCY SWAPTION SURFACE & GREEKS MATRIX SOLVER
    # =========================================================================
    @app.callback(
        Output("vol-surface-table-slot", "children"),
        [Input("vol-surface-currency-selector", "value"),
         Input("vol-parallel-shift-slider", "value"),
         Input("vol-asset-shock-slider", "value")]
    )
    def update_swaption_volatility_surface_grid(selected_ccy, vol_shift, asset_shock):
        expiries = ["1M", "3M", "6M", "1Y", "2Y", "5Y"]
        skews = ["10D Put", "25D Put", "ATM", "25D Call", "10D Call"]
        
        try:
            stripper_instance = VolatilitySurfaceStripper(file_path="data/g4_vol_surfaces.json")
        except Exception:
            stripper_instance = None

        live_data_map = {exp: [70.0]*5 for exp in expiries}
        
        for exp in expiries:
            t_str = exp.replace("M", "").replace("Y", "")
            t_factor = float(t_str) / 12.0 if "M" in exp else float(t_str)
            
            for s_idx, sk in enumerate(skews):
                if stripper_instance:
                    swap_tenor_proxy = 10.0 if "10D" in sk else 5.0 if "25D" in sk else 2.0
                    raw_extracted_vol = stripper_instance.get_clean_atm_volatility(
                        currency=selected_ccy,
                        target_date="2026-09-15",
                        option_expiry=t_factor,
                        swap_tenor=swap_tenor_proxy
                    )
                    live_data_map[exp][s_idx] = float(raw_extracted_vol * 100.0 if raw_extracted_vol <= 1.5 else raw_extracted_vol)
                else:
                    np.random.seed(hash(selected_ccy) % 111)
                    vol_multiplier = 1.25 if selected_ccy in ["ZAR", "NOK", "SEK"] else 1.0
                    base_vols = {"1M": 68.5, "3M": 70.2, "6M": 72.4, "1Y": 75.1, "2Y": 78.6, "5Y": 82.3}
                    skew_shifts = [14.0, 5.5, 0.0, 6.7, 16.1]
                    live_data_map[exp][s_idx] = (base_vols[exp] + skew_shifts[s_idx]) * vol_multiplier

        table_headers = html.Tr([
            html.Th("Expiry / Skew", style={'color': '#ffffff', 'backgroundColor': '#1a202c', 'textAlign': 'left', 'fontWeight': 'bold', 'borderBottom': '2px solid #4a5568', 'minWidth': '140px'}),
            *[html.Th(sk, style={'color': '#ffffff', 'backgroundColor': '#1a202c', 'fontWeight': 'bold', 'borderBottom': '2px solid #4a5568'}) for sk in skews]
        ])

        table_rows = []
        for exp in expiries:
            row_cells = [html.Td(html.Strong(f"{exp} Expiry"), className="text-start font-monospace", style={'backgroundColor': '#11151d', 'color': '#ffffff', 'fontSize': '12px', 'fontWeight': 'bold'})]
            t_str = exp.replace("M", "").replace("Y", "")
            t_factor = float(t_str) / 12.0 if "M" in exp else float(t_str)
            
            for s_idx, sk in enumerate(skews):
                raw_vol = live_data_map[exp][s_idx] + float(vol_shift)
                underlying_fwd = 4.0000 * (1.0 + (float(asset_shock) / 100.0))
                
                strike_offset = (s_idx - 2) * 0.25
                target_strike = underlying_fwd + strike_offset
                
                metrics = VolatilityModelEngine.evaluate_swaption_leg(
                    fwd_rate=underlying_fwd * 100.0,
                    strike=target_strike * 100.0,
                    expiry=t_factor,
                    vol_pct=raw_vol,
                    df=0.96,
                    a_0=1.0,
                    call_put='CALL' if "CALL" in sk.upper() else 'PUT'
                )
                
                delta_val = metrics['raw_delta']
                vega_val = metrics['vega'] * 100.0
                gamma_val = 0.3989 / (underlying_fwd * (raw_vol / 100.0) * math.sqrt(t_factor)) if t_factor > 0 else 0.01
                theta_val = - (underlying_fwd * (raw_vol / 100.0)) / (2 * math.sqrt(t_factor)) if t_factor > 0 else -0.05
                
                if raw_vol >= 85.0:
                    v_color = '#ff4d4d'
                    cell_style = {'backgroundColor': 'rgba(239, 68, 68, 0.07)'}
                elif raw_vol <= 72.0:
                    v_color = '#00d2ff'
                    cell_style = {'backgroundColor': 'rgba(0, 210, 255, 0.07)'}
                else:
                    v_color = '#ffffff'
                    cell_style = {}

                cell_content = html.Div([
                    html.Div(f"{raw_vol:.1f} Vol", style={'color': v_color, 'fontSize': '13px', 'fontWeight': 'bold', 'fontFamily': 'monospace'}),
                    html.Div([
                        html.Span(f"Δ:{delta_val:+.2f} ", style={'color': '#a0aec0'}),
                        html.Span(f"Γ:{gamma_val:.2f}", style={'color': '#ffc107'})
                    ], style={'fontSize': '10px', 'marginTop': '2px', 'fontFamily': 'monospace'}),
                    html.Div([
                        html.Span(f"Θ:{theta_val:.2f} ", style={'color': '#ff4d4d'}),
                        html.Span(f"V:{vega_val:.2f}", style={'color': '#10b981'})
                    ], style={'fontSize': '10px', 'fontFamily': 'monospace'})
                ])
                row_cells.append(html.Td(cell_content, style=cell_style))
                
            table_rows.append(html.Tr(row_cells))

        return dbc.Table(
            [html.Thead(table_headers), html.Tbody(table_rows)],
            bordered=True, hover=True, responsive=True,
            className="table-dark m-0 small border-secondary text-center font-monospace"
        )

    # =========================================================================
    # 🟢 PIPELINE 2: VECTORISED PORTFOLIO INTEREST RATE CAP & FLOOR CHAIN PRICER
    # =========================================================================
    @app.callback(
        Output("cap-analytics-table-slot", "children"),
        [Input("cap-desk-currency-selector", "value"),
         Input("cap-floor-structure-toggle", "value"),
         Input("cap-strike-slider", "value"),
         Input("cap-vol-stress-slider", "value")]
    )
    def update_cap_floor_analytics_matrix(selected_ccy, structure_type, target_strike, vol_shift):
        maturities = ["1Y", "2Y", "3Y", "4Y", "5Y", "7Y", "10Y"]
        
        np.random.seed(hash(selected_ccy) % 222)
        vol_multiplier = 1.30 if selected_ccy in ["ZAR", "NOK", "SEK"] else 1.0
        base_implied_vol = 74.5 * vol_multiplier + float(vol_shift)

        table_headers = html.Tr([
            html.Th("Structure Parameter", style={'color': '#ffffff', 'backgroundColor': '#1a202c', 'textAlign': 'left', 'fontWeight': 'bold', 'borderBottom': '2px solid #4a5568'}),
            *[html.Th(f"{m} Maturity", style={'color': '#ffffff', 'backgroundColor': '#1a202c', 'fontWeight': 'bold', 'borderBottom': '2px solid #4a5568'}) for m in maturities]
        ])

        premium_row_cells = [html.Td(html.Strong("Premium Value (bps)"), className="text-start text-white font-monospace", style={'backgroundColor': '#11151d', 'fontWeight': 'bold'})]
        delta_row_cells = [html.Td(html.Strong("Aggregated Delta Sensitivity"), className="text-start text-white font-monospace", style={'backgroundColor': '#11151d', 'fontWeight': 'bold'})]
        vol_row_cells = [html.Td(html.Strong("Implied Vol Base"), className="text-start text-white font-monospace", style={'backgroundColor': '#11151d', 'fontWeight': 'bold'})]

        for m in maturities:
            years = float(m.replace("Y", ""))
            payment_tenors = np.arange(0.5, years + 0.1, 0.5)
            synthetic_fwd_rate_array = np.linspace(3.95, 4.35, len(payment_tenors)) + np.random.normal(0, 0.05)
            synthetic_df_array = [math.exp(-0.042 * t) for t in payment_tenors]
            
            metrics = VolatilityModelEngine.evaluate_cap_floor(
                fwd_rate_array=synthetic_fwd_rate_array,
                strike=target_strike,
                tenors=payment_tenors,
                vol_pct=base_implied_vol,
                df_array=synthetic_df_array,
                call_put=structure_type
            )
            
            premium_bps = metrics['premium'] * 1000.0
            delta_bps = metrics['raw_delta'] * 100.0
            
            premium_row_cells.append(html.Td(f"{premium_bps:.1f} bp", style={'color': '#00d2ff', 'fontWeight': 'bold', 'fontFamily': 'monospace'}))
            delta_row_cells.append(html.Td(f"{delta_bps:+.2f} bp", style={'color': '#ffc107' if delta_bps > 0 else '#f43f5e', 'fontFamily': 'monospace'}))
            vol_row_cells.append(html.Td(f"{base_implied_vol:.1f} v", style={'color': '#ffffff', 'fontFamily': 'monospace', 'fontSize': '12px'}))

        table_rows = [
            html.Tr(premium_row_cells),
            html.Tr(delta_row_cells),
            html.Tr(vol_row_cells)
        ]

        return dbc.Table(
            [html.Thead(table_headers), html.Tbody(table_rows)],
            bordered=True, hover=True, responsive=True,
            className="table-dark m-0 small border-secondary text-center font-monospace"
        )
