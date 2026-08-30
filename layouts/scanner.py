# layouts/scanner.py - PART 1: UI LAYOUT ENGINE & COMPONENTS
import json
import datetime
import pandas as pd
import numpy as np
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from config import GLOBAL_UNIVERSE
from utils.ai_parser import parse_macro_intent

def render_scanner_layout():
    """
    Assembles the institutional front-office user interface for the cross-sectional
    Intra-Curve Butterfly Scanner desk.
    """
    return html.Div(
        children=[
            # PANEL SUB-HEADER NAVIGATION BAR
            dbc.Row(
                className="mb-4 align-items-center g-3",
                children=[
                    dbc.Col(md=4, children=[
                        html.H4("Relative-Value Butterfly Scanner", className="text-success fw-bold m-0"),
                        html.P("Intra-Curve Structural Deviation Analysis | Single-Currency Isolation Desk", className="text-muted small m-0")
                    ]),
                    dbc.Col(md=3, children=[
                        html.Label("Analysis Timeline Anchor Date:", className="text-white small fw-bold mb-1"),
                        dcc.Dropdown(
                            id="scanner-date-dropdown",
                            options=[{"label": "2026-08-30 (Live)", "value": "2026-08-30"}],
                            value="2026-08-30",
                            clearable=False,
                            className="text-dark fw-bold"
                        )
                    ]),
                    dbc.Col(md=3, children=[
                        html.Label("Manual Currency Filter:", className="text-white small fw-bold mb-1"),
                        dcc.Dropdown(
                            id="scanner-currency-dropdown",
                            options=[{"label": f"{ccy} Asset Deck", "value": ccy} for ccy in GLOBAL_UNIVERSE],
                            value="USD",
                            clearable=False,
                            className="text-dark fw-bold"
                        )
                    ]),
                    dbc.Col(md=2, children=[
                        dbc.Button("🟢 Trigger Matrix Sweep", id="scanner-sweep-btn", color="success", className="w-100 fw-bold pt-2 pb-2 mt-4")
                    ])
                ]
            ),
            
            # CORE AI INTEGRATION HUD PANEL
            dbc.Row(
                className="mb-4",
                children=[
                    dbc.Col(
                        md=12,
                        children=[
                            dbc.Card(
                                style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                                className="p-3 shadow-sm",
                                children=[
                                    html.Div("🤖 Natural Language Macro AI Co-Pilot Terminal", style={'color': '#00d2ff', 'fontWeight': 'bold', 'fontFamily': 'monospace', 'fontSize': '12px', 'marginBottom': '8px'}),
                                    dbc.InputGroup(
                                        children=[
                                            dbc.Input(id="scanner-ai-input", placeholder="Type macro prompt (e.g., 'Find cheap USD bellies')...", className="bg-dark text-white border-secondary"),
                                            dbc.Button("🔮 Parse Intent & Run AI Scan", id="scanner-ai-btn", color="purple", className="fw-bold px-4")
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # FRONT OFFICE LEADERBOARD GRID CONTAINER
            dbc.Row(
                children=[
                    dbc.Col(
                        md=12,
                        children=[
                            dbc.Card(
                                style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                                className="p-4 shadow-sm",
                                children=[
                                    html.H5("Intra-Curve Statistical Arbitrage Dislocation Leaderboard", className="text-white monospace mb-3", style={'fontSize': '14px'}),
                                    html.Div(id="scanner-matrix-table-slot", children=[
                                        html.P("Select currency asset deck parameters above and click 'Trigger Matrix Sweep' to map yield curve anomalies.", className="text-muted small font-monospace m-0")
                                    ])
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
# layouts/scanner.py - PART 2: QUANT MATRIX MATHEMATICS & CALLOUT SWITCHBOARD
def register_scanner_callbacks(app):
    """
    Ingests live single-currency curve data and computes relative-value butterfly spread
    metrics directly into a professional matrix grid table.
    """
    @app.callback(
        Output("scanner-matrix-table-slot", "children"),
        Input("scanner-sweep-btn", "n_clicks"),
        Input("scanner-ai-btn", "n_clicks"),
        State("scanner-currency-dropdown", "value"),
        State("scanner-ai-input", "value"),
        prevent_initial_call=True
    )
    def execute_single_currency_curve_scan(sweep_clicks, ai_clicks, selected_ccy, ai_prompt):
        _ = datetime.datetime.now()
        _ = np.nan
        
        target_currency = selected_ccy
        if ai_prompt and ai_clicks:
            ai_extracted_ccy = parse_macro_intent(ai_prompt)
            if ai_extracted_ccy in GLOBAL_UNIVERSE:
                target_currency = ai_extracted_ccy
        
        try:
            with open("data/g4_curves_live.json", "r") as f:
                raw_data = json.load(f)
            df_all = pd.DataFrame(raw_data)
            
            df_ccy = df_all[df_all['currency'] == str(target_currency).upper().strip()]
            if df_ccy.empty:
                raise ValueError(f"No records found inside live workspace register for: {target_currency}")
                
            rates_map = dict(zip(df_ccy['tenor'].str.strip().str.upper(), df_ccy['rate']))
            
            target_flies = [
                {"name": "1Y / 2Y / 3Y Short Fly", "s": "1Y", "b": "2Y", "l": "3Y"},
                {"name": "2Y / 3Y / 5Y Belly Fly", "s": "2Y", "b": "3Y", "l": "5Y"},
                {"name": "2Y / 5Y / 10Y Benchmark Fly", "s": "2Y", "b": "5Y", "l": "10Y"},
                {"name": "3Y / 5Y / 7Y Mid Curve Fly", "s": "3Y", "b": "5Y", "l": "7Y"},
                {"name": "5Y / 7Y / 10Y Core Fly", "s": "5Y", "b": "7Y", "l": "10Y"},
                {"name": "5Y / 10Y / 30Y Long Wing Fly", "s": "5Y", "b": "10Y", "l": "30Y"}
            ]
            
            scan_records = []
            for fly in target_flies:
                r_s = rates_map.get(fly["s"])
                r_b = rates_map.get(fly["b"])
                r_l = rates_map.get(fly["l"])
                
                if all(v is not None for v in [r_s, r_b, r_l]):
                    spread_bps = ((2.0 * float(r_b)) - float(r_s) - float(r_l)) * 100.0
                    local_sigma = 3.25
                    z_score = spread_bps / local_sigma
                    
                    if z_score > 1.25:
                        signal_tag = "🔴 Rich (Short Belly)"
                    elif z_score < -1.25:
                        signal_tag = "🔵 Cheap (Long Belly)"
                    else:
                        signal_tag = "⚪ Neutral"
                        
                    scan_records.append({
                        "Curve Asset Structure": fly["name"],
                        "Short Leg": f"{float(r_s):.3f}%",
                        "Belly Center": f"{float(r_b):.3f}%",
                        "Long Leg": f"{float(r_l):.3f}%",
                        "Spread (bps)": f"{spread_bps:+.2f} bp",
                        "Intra-Curve Z-Score": f"{z_score:+.2f} σ",
                        "Execution Signal": signal_tag
                    })
                    
            if not scan_records:
                raise ValueError("Maturity intersections are blank inside database matrix rows.")
                
            df_output = pd.DataFrame(scan_records)
            
            metrics_table = dbc.Table(
                bordered=True, hover=True, responsive=True, className="table-dark m-0 small border-secondary text-center font-monospace",
                children=[
                    html.Thead(html.Tr([
                        html.Th(html.Span("Curve Asset Structure", style={'color': '#ffffff'})),
                        html.Th(html.Span("Short Leg", style={'color': '#a0aec0'})),
                        html.Th(html.Span("Belly Center", style={'color': '#a0aec0'})),
                        html.Th(html.Span("Long Leg", style={'color': '#a0aec0'})),
                        html.Th(html.Span("Spread (bps)", style={'color': '#00d2ff'})),
                        html.Th(html.Span("Intra-Curve Z-Score", style={'color': '#e066ff'})),
                        html.Th(html.Span("Execution Signal", style={'color': '#00ff66'}))
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Strong(row["Curve Asset Structure"]), className="text-start text-white"),
                            html.Td(row["Short Leg"], className="text-white"),
                            html.Td(row["Belly Center"], className="text-white"),
                            html.Td(row["Long Leg"], className="text-white"),
                            html.Td(row["Spread (bps)"], className="text-info fw-bold"),
                            html.Td(row["Intra-Curve Z-Score"], className="fw-bold", style={'color': '#e066ff'}),
                            html.Td(row["Execution Signal"], className="fw-bold")
                        ]) for _, row in df_output.iterrows()
                    ])
                ]
            )
            return metrics_table
            
        except Exception as e:
            return dbc.Alert(f"⚠️ Curve scanner operational failure: {str(e)}", color="warning", className="m-0 small")
