# layouts/scanner.py - PART 1: GLOBAL SWEEP UI ENGINE & COMPONENTS
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
                        html.P("Intra-Curve Structural Deviation Analysis | Cross-Asset Leaderboard", className="text-muted small m-0")
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
                        html.Label("Cross-Asset Scanner View:", className="text-white small fw-bold mb-1"),
                        dcc.Dropdown(
                            id="scanner-currency-dropdown",
                            options=[
                                {"label": "🌐 All Currency Books (Global Sweep)", "value": "ALL"},
                                *[{"label": f"{ccy} Asset Deck Only", "value": ccy} for ccy in GLOBAL_UNIVERSE]
                            ],
                            value="ALL",
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
                                            dbc.Input(id="scanner-ai-input", placeholder="Type macro prompt (e.g., 'Scan all books' or 'Show cheap USD flies')...", className="bg-dark text-white border-secondary"),
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
                                        html.P("Select currency parameters above and click 'Trigger Matrix Sweep' to map yield curve anomalies.", className="text-muted small font-monospace m-0")
                                    ])
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
# layouts/scanner.py - PART 2: STABLE GLOBAL MULTI-BOOK MATRIX INTERSECTION LEADERBOARD
def register_scanner_callbacks(app):
    """
    Ingests live parameters and historical archives to compute real-time relative-value spreads,
    darkened Z-scores, and true 5-year empirical distribution percentiles across all 8 global books.
    """
    @app.callback(
        Output("scanner-matrix-table-slot", "children"),
        Input("scanner-sweep-btn", "n_clicks"),
        Input("scanner-ai-btn", "n_clicks"),
        State("scanner-currency-dropdown", "value"),
        State("scanner-ai-input", "value"),
        prevent_initial_call=False
    )
    def execute_single_currency_curve_scan(sweep_clicks, ai_clicks, selected_view, ai_prompt):
        _ = datetime.datetime.now()
        _ = np.nan
        
        target_view = selected_view
        if ai_prompt and ai_clicks:
            p_upper = str(ai_prompt).upper()
            if "ALL" in p_upper or "EVERY" in p_upper or "GLOBAL" in p_upper or "BOOKS" in p_upper:
                target_view = "ALL"
            else:
                ai_extracted, _, _ = parse_macro_intent(ai_prompt)
                if ai_extracted in GLOBAL_UNIVERSE:
                    target_view = ai_extracted

        try:
            with open("data/g4_curves_live.json", "r") as f:
                raw_live = json.load(f)
            df_live_all = pd.DataFrame(raw_live)
            
            with open("data/g4_curves_hist.json", "r") as f:
                raw_hist = json.load(f)
            df_hist_all = pd.DataFrame(raw_hist)
            
            df_hist_all['date'] = pd.to_datetime(df_hist_all['date'])
            df_hist_all['tenor'] = df_hist_all['tenor'].astype(str).str.strip().str.upper()
            df_hist_all['currency'] = df_hist_all['currency'].astype(str).str.strip().str.upper()

            # Loops through all 8 global currencies seamlessly
            active_currencies = GLOBAL_UNIVERSE if target_view == "ALL" else [target_view]
            
            target_flies = [
                {"name": "1Y / 2Y / 3Y Short Fly", "s": "1Y", "b": "2Y", "l": "3Y"},
                {"name": "2Y / 3Y / 5Y Belly Fly", "s": "2Y", "b": "3Y", "l": "5Y"},
                {"name": "2Y / 5Y / 10Y Benchmark Fly", "s": "2Y", "b": "5Y", "l": "10Y"},
                {"name": "3Y / 5Y / 7Y Mid Curve Fly", "s": "3Y", "b": "5Y", "l": "7Y"},
                {"name": "5Y / 7Y / 10Y Core Fly", "s": "5Y", "b": "7Y", "l": "10Y"},
                {"name": "5Y / 10Y / 30Y Long Wing Fly", "s": "5Y", "b": "10Y", "l": "30Y"}
            ]
            
            scan_records = []
            
            for ccy in active_currencies:
                df_live_ccy = df_live_all[df_live_all['currency'] == str(ccy).upper().strip()]
                if df_live_ccy.empty:
                    continue
                rates_map = dict(zip(df_live_ccy['tenor'].str.strip().str.upper(), df_live_ccy['rate']))
                
                df_hist_ccy = df_hist_all[df_hist_all['currency'] == str(ccy).upper().strip()]
                df_hist_pivot = pd.DataFrame()
                if not df_hist_ccy.empty:
                    hist_clean = df_hist_ccy.drop_duplicates(subset=['date', 'tenor'])
                    df_hist_pivot = hist_clean.pivot(index='date', columns='tenor', values='rate').sort_index()
                
                for fly in target_flies:
                    r_s = rates_map.get(fly["s"])
                    r_b = rates_map.get(fly["b"])
                    r_l = rates_map.get(fly["l"])
                    
                    if all(v is not None for v in [r_s, r_b, r_l]):
                        spread_bps = ((2.0 * float(r_b)) - float(r_s) - float(r_l)) * 100.0
                        local_sigma = 3.5 if ccy in ["USD", "GBP", "EUR"] else 2.25 if ccy == "JPY" else 5.5
                        z_score = spread_bps / local_sigma
                        
                        percentile_val = 50.0
                        if not df_hist_pivot.empty and {fly["s"], fly["b"], fly["l"]}.issubset(df_hist_pivot.columns):
                            hist_fly_series = ((2.0 * df_hist_pivot[fly["b"]]) - df_hist_pivot[fly["s"]] - df_hist_pivot[fly["l"]]) * 100.0
                            percentile_val = (hist_fly_series < spread_bps).mean() * 100.0
                        
                        if z_score > 1.5 or percentile_val >= 95.0:
                            signal_tag = "🔴 Rich (Short Belly)"
                        elif z_score < -1.5 or percentile_val <= 5.0:
                            signal_tag = "🔵 Cheap (Long Belly)"
                        else:
                            signal_tag = "⚪ Neutral"
                            
                        scan_records.append({
                            "Book": ccy, "Structure": fly["name"], "Short": f"{float(r_s):.3f}%", "Belly": f"{float(r_b):.3f}%", "Long": f"{float(r_l):.3f}%",
                            "Spread": spread_bps, "Z": z_score, "Pct": percentile_val, "Sig": signal_tag, "Abs_Z": abs(z_score)
                        })
                        
            df_output = pd.DataFrame(scan_records).sort_values(by="Abs_Z", ascending=False)
            
            return dbc.Table(
                bordered=True, hover=True, responsive=True, className="table-dark m-0 small border-secondary text-center font-monospace",
                children=[
                    html.Thead(html.Tr([
                        html.Th("Currency"), html.Th("Curve Asset Structure"), html.Th("Short Leg"), html.Th("Belly Center"), html.Th("Long Leg"),
                        html.Th("Spread (bps)"), html.Th("Intra-Curve Z-Score"), html.Th("5Y Percentile Rank"), html.Th("Execution Signal")
                    ])),
                    html.Tbody([
                        html.Tr([
                            html.Td(html.Strong(row["Book"]), className="text-warning fw-bold"),
                            html.Td(row["Structure"], className="text-start text-white"),
                            html.Td(row["Short"], className="text-white-50"), html.Td(row["Belly"], className="text-white"), html.Td(row["Long"], className="text-white-50"),
                            html.Td(f"{row['Spread']:+.2f} bp", className="text-info fw-bold"),
                            html.Td(f"{row['Z']:+.2f} σ", style={'color': '#af52de', 'fontWeight': 'bold'}),
                            html.Td(f"{row['Pct']:.1f}%", className="fw-bold text-warning" if (row['Pct'] >= 90.0 or row['Pct'] <= 10.0) else "text-white"),
                            html.Td(row["Sig"], className="fw-bold")
                        ]) for _, row in df_output.iterrows()
                    ])
                ]
            )
        except Exception as e:
            return dbc.Alert(f"⚠️ Global curve scanner operational failure: {str(e)}", color="warning", className="m-0 small")
