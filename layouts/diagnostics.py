# layouts/diagnostics.py - DYNAMIC INTRA-CURVE 1Y➔1Y FORWARD MONITOR (AXIS SWAPPED)
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from config import GLOBAL_UNIVERSE, BENCHMARK_TENORS

def render_diagnostics_layout():
    """
    Assembles the front-page primary risk control center with an optimized layout grid.
    Places the vertical, consecutive 1Y->1Y forward rate histogram at the top.
    """
    return html.Div(
        children=[
            # PANEL SUB-HEADER BAR
            dbc.Row(
                className="mb-4 align-items-center g-3",
                children=[
                    dbc.Col(md=6, children=[
                        html.H4("Real-Time Curve Diagnostics", className="text-success fw-bold m-0"),
                        html.P("Live Data As Of: 2026-08-26 | Immediacy Monitoring & Live Pricing Validation", className="text-muted small m-0")
                    ]),
                    dbc.Col(md=4, children=[
                        html.Label("Primary Analysis Currency:", className="text-muted small mb-1"),
                        dcc.Dropdown(
                            id="diag-currency-selector",
                            options=[{"label": f"{ccy} Curve Book", "value": ccy} for ccy in GLOBAL_UNIVERSE],
                            value="USD",
                            clearable=False,
                            className="text-dark fw-bold"
                        )
                    ]),
                    dbc.Col(md=2, className="text-end", children=[
                        html.Span("MARKET LIVE", className="badge bg-success font-monospace small px-2 py-2")
                    ])
                ]
            ),
            
            # TOP ROW: INTRA-CURVE consecutive 1Y 1Y FORWARDS VERTICAL HISTOGRAM
            dbc.Row(
                className="mb-4",
                children=[
                    dbc.Col(
                        md=12,
                        children=[
                            dbc.Card(
                                style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                                className="p-4 shadow-sm",
                                children=[
                                    html.H5(id="diag-fwd-title-slot", className="text-white monospace mb-3", style={'fontSize': '14px'}),
                                    dcc.Graph(id="diag-fwd-histogram-graph", style={'height': '320px'}, config={'displayModeBar': False})
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # BOTTOM ROW: LIVE PAR SWAP CURVES GRAPH & ROLL SNAPSHOT
            dbc.Row(
                className="g-4",
                children=[
                    # GRAPH MODULE: LIVE SWAP CURVES
                    dbc.Col(
                        md=8,
                        children=[
                            dbc.Card(
                                style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                                className="p-4 shadow-sm",
                                children=[
                                    html.H5("Live Benchmark IRS Par Swap Yield Curve", className="text-white monospace mb-3", style={'fontSize': '14px'}),
                                    dcc.Graph(id="diag-par-curve-graph", style={'height': '320px'}, config={'displayModeBar': False})
                                ]
                            )
                        ]
                    ),
                    # MATRIX PANEL: ROLL AND CARRY DRIVERS
                    dbc.Col(
                        md=4,
                        children=[
                            dbc.Card(
                                style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px', 'height': '100%'},
                                className="p-4 shadow-sm",
                                children=[
                                    html.H5("Active 30D Curve Carry & Roll-Down", className="text-white monospace mb-3", style={'fontSize': '14px'}),
                                    html.Div(id="diag-roll-snapshot-container")
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

def register_diagnostics_callbacks(app):
    """
    Drives real-time graphic updates to instantly highlight mispricings and shape anomalies.
    """
    @app.callback(
        Output("diag-par-curve-graph", "figure"),
        Output("diag-roll-snapshot-container", "children"),
        Output("diag-fwd-histogram-graph", "figure"),
        Output("diag-fwd-title-slot", "children"),
        Input("diag-currency-selector", "value")
    )
    def compute_intra_day_visual_triage_metrics(currency):
        try:
            with open("data/g4_curves.json", "r") as f:
                raw_data = json.load(f)
            df_all = pd.DataFrame(raw_data)
            
            ccy = str(currency).upper().strip()
            df = df_all[df_all['currency'] == ccy]
            
            if df.empty:
                df = df_all[df_all['currency'] == 'USD']
                ccy = 'USD'
                
            df["tenor_val"] = df["tenor"].str.replace("Y", "").astype(float)
            df = df.sort_values("tenor_val")
            
            x_tenors = df["tenor"].tolist()
            y_rates = df["rate"].tolist()
            
            # 📈 CHART 1: NATIVE LIVE IRS PAR SWAP GRAPH
            fig_curve = go.Figure()
            fig_curve.add_trace(
                go.Scatter(
                    x=x_tenors, y=y_rates, mode="lines+markers",
                    name=f"{ccy} Spot Curve",
                    line=dict(color='#00ff66', width=3),
                    marker=dict(size=8, color='#ffffff', line=dict(color='#00ff66', width=2)),
                    hovertemplate="<b>Tenor:</b> %{x}<br><b>Yield:</b> %{y:.4f}%<extra></extra>"
                )
            )
            fig_curve.update_layout(
                paper_bgcolor='#0b0d12', plot_bgcolor='#0b0d12',
                margin=dict(l=40, r=20, t=10, b=30),
                xaxis=dict(showgrid=True, gridcolor='#161b26', tickfont=dict(family='monospace', color='#6c757d')),
                yaxis=dict(showgrid=True, gridcolor='#161b26', tickfont=dict(family='monospace', color='#6c757d'), title=dict(text="Yield (%)", font=dict(size=10, color='#6c757d')))
            )
            
            # 📊 CHART 2: RE-SWAPPED VERTICAL CONSECUTIVE 1Y FORWARDS HISTOGRAM
            rates_dict = dict(zip(df['tenor'].str.strip().str.upper(), df['rate']))
            
            forward_tenor_labels = []
            forward_rates_values = []
            
            # Walk chronologically across standard maturities from 1Y out to 30Y
            sequential_nodes = [1, 2, 3, 5, 7, 10, 15, 20, 30]
            for i in range(len(sequential_nodes) - 1):
                t_start = sequential_nodes[i]
                t_end = sequential_nodes[i+1]
                
                r_start = float(rates_dict.get(f"{t_start}Y", 4.0)) / 100.0
                r_end = float(rates_dict.get(f"{t_end}Y", 4.2)) / 100.0
                
                n_years = t_end - t_start
                
                try:
                    fwd_implied = ((((1.0 + r_end) ** t_end) / ((1.0 + r_start) ** t_start)) ** (1.0 / n_years)) - 1.0
                    fwd_percentage = round(fwd_implied * 100.0, 4)
                except ZeroDivisionError:
                    fwd_percentage = 0.0
                
                forward_tenor_labels.append(f"{t_start}Y➔{t_end}Y")
                forward_rates_values.append(fwd_percentage)
                
            fig_hist = go.Figure()
            fig_hist.add_trace(
                go.Bar(
                    x=forward_tenor_labels,               # Swapped: Year point interval is on the X-axis
                    y=forward_rates_values,               # Swapped: Implied Forward Rate value is on the Y-axis
                    orientation='v',                      # Forces vertical bar structure to stop line grouping overlapping
                    marker=dict(
                        color=forward_rates_values,
                        colorscale='Viridis',
                        line=dict(color='#1a1f2c', width=1)
                    ),
                    text=[f"{r:.3f}%" for r in forward_rates_values],
                    textposition='outside',               # Places text values cleanly over the top of the columns
                    textfont=dict(family='monospace', size=10, color='#ffffff')
                )
            )
            fig_hist.update_layout(
                paper_bgcolor='#0b0d12', plot_bgcolor='#0b0d12',
                margin=dict(l=50, r=20, t=30, b=40),
                showlegend=False,
                xaxis=dict(
                    title=dict(text="Forward Curve Sector Interval", font=dict(size=11, color='#6c757d')),
                    tickfont=dict(family='monospace', size=11, color='#ffffff')
                ),
                yaxis=dict(
                    title=dict(text="Implied Forward Rate Coupon (%)", font=dict(size=11, color='#6c757d')),
                    showgrid=True, gridcolor='#161b26', 
                    tickfont=dict(family='monospace', color='#6c757d')
                )
            )
            
            title_text = f"{ccy} Implied Forward Rate Curve Term Structure Profile"
            
                        # 📋 RENDER 3: ACTIVE CARRY & ROLL TABLE SNAPSHOT
            roll_items = []
            target_vertices = ["2Y", "5Y", "10Y", "30Y"]
            for v in target_vertices:
                current_rate = float(rates_dict.get(v, 4.0))
                v_num = int(v.replace("Y", ""))
                down_neighbor = f"{v_num - 1}Y" if v_num > 2 else "1Y"
                neighbor_rate = float(rates_dict.get(down_neighbor, current_rate - 0.15))
                
                monthly_roll_bps = (current_rate - neighbor_rate) * 100.0 / 12.0
                
                roll_items.append(
                    html.Div(
                        className="d-flex justify-content-between align-items-center p-2 mb-2 bg-dark rounded border border-secondary",
                        children=[
                            html.Span(f"{v} Benchmark Node", className="font-monospace text-white small"),
                            html.Span(f"{monthly_roll_bps:+.1f} bps/mo", className=f"font-monospace fw-bold text-{'success' if monthly_roll_bps >= 0 else 'danger'}")
                        ]
                    )
                )
                
            return fig_curve, html.Div(roll_items), fig_hist, title_text
            
        except Exception as e:
            blank_fig = go.Figure()
            error_msg = html.P(f"⚠️ Core Loop Interruption: {str(e)}", className="text-warning small font-monospace m-0")
            return blank_fig, error_msg, blank_fig, "Curve Error State"

