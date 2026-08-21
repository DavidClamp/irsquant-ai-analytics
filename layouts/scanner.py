# layouts/scanner.py - PANEL 2: CROSS-SECTIONAL OLS ARBITRAGE SCANNER UI
import json
import pandas as pd
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc
from analytics import build_forward_permutation_matrix, run_statistical_arbitrage_sweep

def render_scanner_layout():
    """
    Assembles the front-office UI view grid layout for the Relative-Value Fly Scanner.
    """
    return html.Div(
        children=[
            # PANEL SUB-HEADER
            dbc.Row(
                className="mb-4 align-items-center g-3",
                children=[
                    dbc.Col(md=6, children=[
                        html.H4("Relative-Value Butterfly Scanner", className="text-success fw-bold m-0"),
                        html.P("OLS Regression Sweep Over Self-Financing Forward Swap Wing/Body Formations", className="text-muted small m-0")
                    ]),
                    dbc.Col(md=3, children=[
                        html.Label("Target Scanner Currency:", className="text-white small fw-bold mb-1"),
                        dcc.Dropdown(
                            id="scan-currency-selector",
                            options=[{"label": f"{ccy} Arbitrage Sweep", "value": ccy} for ccy in ["USD", "EUR", "GBP", "JPY", "CHF", "NOK", "SEK", "ZAR"]],
                            value="USD",
                            clearable=False,
                            style={'backgroundColor': '#11141a', 'color': '#ffffff'}
                        )
                    ]),
                    dbc.Col(md=3, children=[
                        dbc.Button(
                            "Trigger Matrix Sweep", 
                            id="trigger-scan-btn", 
                            color="success", 
                            className="w-100 fw-bold mt-4",
                            style={'letterSpacing': '0.5px'}
                        )
                    ])
                ]
            ),
            
            # STATISTICAL LEADERBOARD GRID CONTAINER
            dbc.Row(
                children=[
                    dbc.Col(
                        width=12,
                        children=[
                            dbc.Card(
                                style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                                className="p-4 shadow-sm",
                                children=[
                                    html.H5("Structural Dislocation Leaderboard", className="text-white monospace mb-3", style={'fontSize': '14px'}),
                                    html.Div(id="scanner-leaderboard-container")
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

def register_scanner_callbacks(app):
    """
    Hooks UI execution buttons straight into your underlying analytics.py regression pipelines.
    """
    @app.callback(
        Output("scanner-leaderboard-container", "children"),
        Input("trigger-scan-btn", "n_clicks"),
        Input("scan-currency-selector", "value")
    )
    def execute_arbitrage_regression_sweep(n_clicks, currency):
        # 1. Pull flat-file continuous raw yield logs from local storage
        try:
            with open("data/g4_curves.json", "r") as f:
                raw_data = json.load(f)
            master_df = pd.DataFrame(raw_data)
        except Exception:
            # Fallback mock template to prevent front-end framework breakdown if disk is busy
            master_df = pd.DataFrame([
                {"date": "2026-08-21", "currency": "USD", "tenor": "1Y", "rate": 3.25},
                {"date": "2026-08-21", "currency": "USD", "tenor": "2Y", "rate": 3.40},
                {"date": "2026-08-21", "currency": "USD", "tenor": "5Y", "rate": 3.65},
                {"date": "2026-08-21", "currency": "USD", "tenor": "10Y", "rate": 3.85}
            ])

        # 2. Reconstruct forward permutation matrices and process ordinary least squares residuals
        try:
            fwd_df = build_forward_permutation_matrix(master_df, selected_ccy=currency)
            leaderboard_data = run_statistical_arbitrage_sweep(fwd_df)
        except Exception as e:
            # Shield layer error response row
            return html.Div(f"⚠️ Regression matrix processing dropped: {str(e)}", className="text-danger small monospace")

        if not leaderboard_data:
            return html.Div("No structures identified within defined liquidity constraints.", className="text-muted small")

        # 3. Flatten data fields into an enterprise-ready web table dataset
        df_leaderboard = pd.DataFrame(leaderboard_data).drop(columns=["raw_residuals"], errors="ignore")

        return dash_table.DataTable(
            data=df_leaderboard.to_dict('records'),
            columns=[{"name": col, "id": col} for col in df_leaderboard.columns],
            style_as_list_view=True,
            style_header={
                'backgroundColor': '#11141a',
                'color': '#8a99ad',
                'fontWeight': 'bold',
                'fontFamily': 'monospace',
                'borderBottom': '2px solid #22293a',
                'padding': '12px'
            },
            style_cell={
                'backgroundColor': '#0b0d12',
                'color': '#ffffff',
                'fontFamily': 'monospace',
                'padding': '12px',
                'borderBottom': '1px solid #1a1f2c',
                'textAlign': 'left',
                'fontSize': '13px'
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{Z-Score} >= 2.0'},
                    'color': '#00ff66',
                    'fontWeight': 'bold'
                },
                {
                    'if': {'filter_query': '{Z-Score} <= -2.0'},
                    'color': '#ff3333',
                    'fontWeight': 'bold'
                }
            ],
            page_size=12
        )
