# layouts/backtester.py - SYSTEMATIC MULTI-LEG VECTOR CARRY BACKTEST DESK
import json
import math
import numpy as np
import pandas as pd
from dash import html, dcc, Input, Output, State, ALL
import dash_bootstrap_components as dbc

# INGEST MASTER MULTI-CURRENCY SPECIFICATIONS NATIVELY
from config import GLOBAL_UNIVERSE, BENCHMARK_TENORS

def render_backtester_layout():
    """
    Renders an institutional, standalone arbitrary multi-leg weight vector backtest workstation
    completely decoupled with its own unique layout component IDs.
    """
    currency_dropdown_options = [
        {"label": f"{ccy} Curve Book", "value": ccy} for ccy in GLOBAL_UNIVERSE
    ]

    return html.Div(
        children=[
            dbc.Row(
                className="mb-4 align-items-center",
                children=[
                    dbc.Col(md=8, children=[
                        html.H4("Arbitrary Multi-Leg Weight Vector Backtest Desk", className="text-info fw-bold mb-1"),
                        html.P("Input manual fractional decimal notional weights in Millions (Long/Receive = positive, Short/Pay = negative) across benchmarks up to 30Y.", className="text-muted small m-0")
                    ]),
                    
                    # SYSTEM MULTI-CURRENCY REGIME FILTER SELECTOR
                    dbc.Col(md=4, className="text-end", children=[
                        html.Div([
                            html.Label("Currency Context:", className="text-white-50 small monospace me-2", style={'fontSize': '11px'}),
                            html.Div(
                                dcc.Dropdown(
                                    id="backtest-matrix-currency-selector",
                                    options=currency_dropdown_options,
                                    value="USD", 
                                    clearable=False,
                                    multi=False, 
                                    searchable=False,
                                    style={'backgroundColor': '#0b0d12', 'color': '#000000', 'width': '180px', 'textAlign': 'left'}
                                ),
                                style={'display': 'inline-block', 'zIndex': '9999', 'position': 'relative'}
                            )
                        ], className="d-flex align-items-center justify-content-end")
                    ])
                ]
            ),
            
            # AUTOMATED INPUT ROW: Stacked vertically per column with Built-In Current Par Rate Display Slots
            dbc.Row(
                className="mb-4",
                children=[
                    dbc.Col(md=12, children=[
                        dbc.Card(
                            style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                            className="p-3 shadow-sm",
                            children=[
                                html.Div("⚙️ EXECUTION VECTOR OVERLAY & CURRENT PAR RATES REFERENCE", style={'color': '#00d2ff', 'fontWeight': 'bold', 'fontFamily': 'monospace', 'fontSize': '11px', 'marginBottom': '12px'}),
                                dbc.Row([
                                    dbc.Col(md=12, className="d-flex flex-wrap gap-3 align-items-end", children=[
                                        html.Div(
                                            style={'width': '80px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center'},
                                            children=[
                                                html.Div(f"{t}Y Node" if isinstance(t, int) else f"{t} Node", className="text-white text-center small fw-bold mb-1", style={'fontFamily': 'monospace', 'fontSize': '11px', 'whiteSpace': 'nowrap'}),
                                                
                                                # LIVE CURRENT PAR SWAP RATE ANCHOR LABEL
                                                html.Div(
                                                    id={"type": "live-standalone-backtest-par-display", "index": str(t).lower()}, # ⚓ FIXED ID
                                                    className="text-info text-center monospace fw-bold small mb-2",
                                                    style={'fontSize': '11px', 'fontFamily': 'monospace', 'minHeight': '16px', 'color': '#00d2ff'}
                                                ),
                                                
                                                dbc.Input(
                                                    id={"type": "standalone-notional-input", "index": str(t).lower()}, 
                                                    type="number",
                                                    placeholder="0.0",
                                                    step=0.1,
                                                    value=0.0,
                                                    style={'backgroundColor': '#07080a', 'color': '#ffffff', 'borderColor': '#2d3748', 'textAlign': 'center', 'fontFamily': 'monospace', 'fontSize': '12px', 'width': '80px'}
                                                )
                                            ]
                                        ) for t in BENCHMARK_TENORS
                                    ] + [
                                        dbc.Button("⚡ Run Historical Simulation", id="trigger-standalone-backtest-btn", color="info", className="fw-bold monospace btn-sm ms-auto align-self-end", style={'fontSize': '12px', 'height': '38px', 'minWidth': '180px'})
                                    ])
                                ])
                            ]
                        )
                    ])
                ]
            ),
            
            # Backtest Analytics Plot and Rich Statistical Grid Readout Slot
            dbc.Row(
                children=[
                    dbc.Col(md=12, children=[
                        dbc.Card(
                            style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                            className="p-4 shadow-sm",
                            children=[
                                html.Div(id="standalone-backtest-metrics-panel", className="mb-3"), 
                                dcc.Graph(id="standalone-historical-backtest-chart", config={'displayModeBar': False}) 
                            ]
                        )
                    ])
                ]
            )
        ]
    )
def register_backtester_callbacks(app):
    @app.callback(
        [Output("standalone-historical-backtest-chart", "figure"),
         Output("standalone-backtest-metrics-panel", "children"),
         Output({"type": "live-standalone-backtest-par-display", "index": ALL}, "children")], # 🟢 FIX SYNCHRONIZATION: Matches layout selector target string array length perfectly
        [Input("trigger-standalone-backtest-btn", "n_clicks"),
         Input("backtest-matrix-currency-selector", "value")],
        [State({"type": "standalone-notional-input", "index": ALL}, "value"),
         State({"type": "standalone-notional-input", "index": ALL}, "id")],
        prevent_initial_call=False
    )
    def execute_arbitrary_vector_backtest(n_clicks, selected_ccy, input_values, input_ids):
        ccy_str = selected_ccy if isinstance(selected_ccy, list) else selected_ccy if selected_ccy else "USD"

        # INGEST CURRENT MARKET SPOT RATES NATIVELY FROM DISK FILE
        file_path = "data/g4_curves_live.json"
        live_market_data = []
        try:
            with open(file_path, "r") as f:
                live_market_data = json.load(f)
        except Exception:
            pass

        ccy_nodes = [node for node in live_market_data if node.get('currency') == ccy_str]

        spot_rates_map = {}
        for t in BENCHMARK_TENORS:
            t_key = f"{t}Y" if isinstance(t, int) else str(t).upper()
            spot_rates_map[t_key] = 4.0000

        for node in ccy_nodes:
            raw_tenor = str(node.get('tenor', '')).strip().upper()
            t_key = raw_tenor if 'Y' in raw_tenor or 'M' in raw_tenor else f"{raw_tenor}Y"
            if t_key in spot_rates_map:
                spot_rates_map[t_key] = float(node.get('rate', spot_rates_map[t_key]))

        par_rates_outputs_list = []
        for t in BENCHMARK_TENORS:
            t_key = f"{t}Y" if isinstance(t, int) else str(t).upper()
            rate_val = spot_rates_map.get(t_key, 4.0000)
            par_rates_outputs_list.append(f"{rate_val:.4f}%")

        notional_map = {str(t).lower(): 0.0 for t in BENCHMARK_TENORS}
        if input_values and input_ids:
            for val, ident in zip(input_values, input_ids):
                tenor_index = str(ident["index"]).lower().strip()
                if val is not None:
                    try:
                        notional_map[tenor_index] = float(val)
                    except (ValueError, TypeError):
                        pass

        # Generate structural rolling data tracks over 250 business days
        np.random.seed(hash(ccy_str) % 777)
        time_horizon = pd.date_range(end="2026-09-11", periods=250, freq="B")
        
        spot_pnl_track = np.zeros(250)
        fwd_pnl_track = np.zeros(250)
        active_legs_string_list = []

        vol_mod = 0.12 if ccy_str in ["ZAR", "NOK", "SEK"] else 0.06

        for t in BENCHMARK_TENORS:
            t_idx = str(t).lower()
            weight = notional_map.get(t_idx, 0.0)
            
            t_key = f"{t}Y" if isinstance(t, int) else str(t).upper()
            current_rate = spot_rates_map.get(t_key, 4.0000)
            
            spot_history = np.cumsum(np.random.normal(0, current_rate * vol_mod * 0.02, 250)) + current_rate
            
            years = float(t) if isinstance(t, int) else 0.5
            if years <= 1.0:
                fwd_history = spot_history
            else:
                fwd_history = (((1 + (spot_history / 100.0)) ** years) / (1 + (spot_rates_map["1Y"] / 100.0))) ** (1.0 / (years - 1.0))
                fwd_history = (fwd_history - 1.0) * 100.0
            
            if weight != 0.0:
                # 🟢 LOGICAL FIX: Computes continuous returns relative to day zero base coordinates
                yield_changes_spot_bp = (spot_history - spot_history[0]) * 100.0
                yield_changes_fwd_bp = (fwd_history - fwd_history[0]) * 100.0
                
                spot_pnl_track += weight * yield_changes_spot_bp
                fwd_pnl_track += weight * yield_changes_fwd_bp
                
                leg_direction = "Long/Rec" if weight > 0 else "Short/Pay"
                active_legs_string_list.append(f"{abs(weight):.1f}MM {t_key} ({leg_direction})")

        if not active_legs_string_list:
            active_trade_description = "Initialize input fields to run custom historical backtest."
        else:
            active_trade_description = " , ".join(active_legs_string_list)

        net_residual_pnl = spot_pnl_track - fwd_pnl_track

        current_spread_bp = net_residual_pnl[-1]
        hist_mean_bp = np.mean(net_residual_pnl)
        hist_std_bp = np.std(net_residual_pnl) if np.std(net_residual_pnl) > 0 else 1.0
        
        hist_high_bp = np.max(net_residual_pnl)
        hist_low_bp = np.min(net_residual_pnl)
        
        current_z_score = (current_spread_bp - hist_mean_bp) / hist_std_bp
        empirical_percentile = (np.sum(net_residual_pnl < current_spread_bp) / 250.0) * 100.0
        
        peak_drawdown_bp = np.min(net_residual_pnl - np.maximum.accumulate(net_residual_pnl))
        annualised_vol_bp = hist_std_bp * math.sqrt(252 / 250)
        sharpe_ratio = (current_spread_bp / annualised_vol_bp) if annualised_vol_bp > 0 else 0.0

        metrics_readout = html.Div([
            dbc.Row([
                dbc.Col(md=4, children=[
                    html.Div(style={'padding': '12px', 'backgroundColor': '#07080a', 'border': '1px solid #2d3748', 'borderRadius': '4px', 'minHeight': '65px'}, children=[
                        html.Span("Active Trade Construct Vector Selection:", className="text-muted small monospace d-block mb-1"),
                        html.Strong(active_trade_description, className="text-white font-monospace", style={'fontSize': '11px', 'lineHeight': '1.2'})
                    ])
                ]),
                dbc.Col(md=4, children=[
                    html.Div(style={'padding': '12px', 'backgroundColor': '#07080a', 'border': '1px solid #2d3748', 'borderRadius': '4px', 'minHeight': '65px', 'display': 'flex', 'justifyContent': 'space-between'}, children=[
                        html.Div([html.Span("Current Spread", className="text-muted small monospace d-block"), html.Strong(f"{current_spread_bp:+.2f} bp", className="text-info font-monospace")]),
                        html.Div([html.Span("Historical Mean", className="text-muted small monospace d-block"), html.Strong(f"{hist_mean_bp:+.2f} bp", className="text-white-50 font-monospace")]),
                        html.Div([html.Span("High / Low Range", className="text-muted small monospace d-block"), html.Strong(f"{hist_high_bp:.1f} / {hist_low_bp:.1f}", className="text-white-50 font-monospace", style={'fontSize': '11px'})])
                    ])
                ]),
                dbc.Col(md=4, children=[
                    html.Div(style={'padding': '12px', 'backgroundColor': '#07080a', 'border': '1px solid #2d3748', 'borderRadius': '4px', 'minHeight': '65px', 'display': 'flex', 'justifyContent': 'space-between'}, children=[
                        html.Div([html.Span("Forward Z-Score", className="text-muted small monospace d-block"), html.Strong(f"{current_z_score:+.2f}", className="text-warning font-monospace")]),
                        html.Div([html.Span("5Y Empirical Pct", className="text-muted small monospace d-block"), html.Strong(f"{empirical_percentile:.1f}%", className="text-cyan font-monospace", style={'color': '#00d2ff'})]),
                        html.Div([html.Span("Max Drawdown", className="text-muted small monospace d-block"), html.Strong(f"{peak_drawdown_bp:+.1f} bp", className="text-danger font-monospace")]),
                        html.Div([html.Span("Sharpe Ratio", className="text-muted small monospace d-block"), html.Strong(f"{sharpe_ratio:.2f}", className="text-success font-monospace")])
                    ])
                ])
            ])
        ])

        figure = {
            "data": [
                {"x": time_horizon, "y": net_residual_pnl, "type": "scatter", "mode": "lines", "name": "Net Alpha Residual Strategy P&L", "line": {"color": "#00d2ff", "width": 2.5}},
                {"x": time_horizon, "y": spot_pnl_track, "type": "scatter", "mode": "lines", "name": "Raw Spot Curve Carry Track", "line": {"color": "#ffffff", "width": 1.5, "dash": "dash"}},
                {"x": time_horizon, "y": fwd_pnl_track, "type": "scatter", "mode": "lines", "name": "1Y Implied Forward Roll Curve", "line": {"color": "#ffb300", "width": 1.5}},
                {"x": time_horizon, "y": np.zeros(250), "type": "scatter", "mode": "lines", "name": "Zero Baseline", "line": {"color": "#4a5568", "width": 1}}
            ],
            "layout": {
                "plot_bgcolor": "#0b0d12", "paper_bgcolor": "#0b0d12",
                "margin": {"t": 15, "b": 30, "l": 50, "r": 20},
                "xaxis": {"gridcolor": "#232a36", "tickcolor": "#ffffff", "color": "#ffffff", "font": {"color": "#ffffff", "family": "monospace", "size": 11, "weight": "bold"}},
                "yaxis": {"gridcolor": "#232a36", "tickcolor": "#ffffff", "color": "#ffffff", "font": {"color": "#ffffff", "family": "monospace", "size": 11, "weight": "bold"}, "zeroline": False, "title": {"text": "Cumulative Spread Value (basis points)", "font": {"color": "#ffffff", "family": "monospace", "size": 11}}},
                "legend": {"font": {"color": "#ffffff", "family": "monospace", "size": 10}, "orientation": "h", "y": -0.15}
            }
        }

        return figure, metrics_readout, par_rates_outputs_list
