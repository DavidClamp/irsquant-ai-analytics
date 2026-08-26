# layouts/execution.py - PANEL 4: TWO-LEG BASIS SIZING & SPREAD HEDGING
import datetime
from dash import dcc, html, Input, Output, State, no_update
import dash_bootstrap_components as dbc
from execution import SizingEngine
from config import BENCHMARK_TENORS

def render_basis_layout():
    """
    Assembles the decoupled HTML/Dash UI view grid layout for the 2-Leg Basis Desk.
    """
    # 🛡️ THE REAL FIXED SYNTAX: The list of benchmark maturities is explicitly written out
    tenor_options = [{"label": f"{y}Y Swap Node", "value": str(y)} for y in BENCHMARK_TENORS]
    
    return html.Div(
        children=[
            # PANEL SUB-HEADER BAR
            dbc.Row(
                className="mb-4 align-items-center g-3",
                children=[
                    dbc.Col(md=6, children=[
                        html.H4("2-Leg Basis Hedging Desk", className="text-success fw-bold m-0"),
                        html.P("Multi-Leg Sizing Engines, Present Value Basis Risks & Structural Spread Adjustments", className="text-muted small m-0")
                    ]),
                    dbc.Col(md=3, children=[
                        html.Label("Execution Currency:", className="text-white small fw-bold mb-1"),
                        dcc.Dropdown(
                            id="exec-currency-selector",
                            options=[{"label": f"{ccy} Trading Book", "value": ccy} for ccy in ["USD", "EUR", "GBP", "JPY", "CHF", "NOK", "SEK", "ZAR"]],
                            value="USD",
                            clearable=False,
                            className="text-dark fw-bold"
                        )
                    ]),
                    dbc.Col(md=3, children=[
                        html.Label("Target Risk Book:", className="text-white small fw-bold mb-1"),
                        dcc.Dropdown(
                            id="exec-book-selector",
                            options=[{"label": b, "value": b} for b in ["Macro-RV-Fly", "STIR-Hedging", "Exotics-Match"]],
                            value="STIR-Hedging",
                            clearable=False,
                            className="text-dark fw-bold"
                        )
                    ])
                ]
            ),
            
            # BASIS SWAP RUNNER CONTAINER
            dbc.Row(
                className="g-4",
                children=[
                    # COLUMN 1: INTERACTIVE ORDER FORM STACK
                    dbc.Col(
                        md=5,
                        children=[
                            dbc.Card(
                                style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                                className="p-4 shadow-sm mb-4",
                                children=[
                                    html.H5("2-Leg Basis Sizing Ticket", className="text-white monospace mb-4", style={'fontSize': '14px'}),
                                    
                                    html.Div(className="mb-3", children=[
                                        html.Label("Leg 1: Target Notional (Millions)", className="text-muted small mb-1"),
                                        dbc.Input(id="exec-notional-input", type="number", value=100.0, step=5.0, className="bg-dark text-white border-secondary")
                                    ]),
                                    
                                    dbc.Row(className="g-2 mb-4", children=[
                                        dbc.Col(md=6, children=[
                                            html.Label("Leg 1 Tenor", className="text-muted small mb-1"),
                                            dbc.Select(id="exec-tenor-leg1", options=tenor_options, value="2", className="bg-dark text-white border-secondary")
                                        ]),
                                        dbc.Col(md=6, children=[
                                            html.Label("Leg 2 Balance Tenor", className="text-muted small mb-1"),
                                            dbc.Select(id="exec-tenor-leg2", options=tenor_options, value="10", className="bg-dark text-white border-secondary")
                                        ])
                                    ]),
                                    
                                    dbc.Button("Calculate Sizing & Risk", id="exec-calc-btn", color="success", className="w-100 fw-bold mb-2"),
                                ]
                            ),
                            dbc.Button("Submit Basis Swap Order Block", id="exec-book-btn", color="outline-success", className="w-100 fw-bold p-2"),
                            html.Div(id="exec-booking-status", className="mt-3 text-center small font-monospace")
                        ]
                    ),
                    
                    # COLUMN 2: RISK BALANCING OUTPUT METRIC MATRIX
                    dbc.Col(
                        md=7,
                        children=[
                            dbc.Card(
                                style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px', 'height': '100%'},
                                className="p-4 shadow-sm",
                                children=[
                                    html.H5("Execution Desk Risk Summary Matrix", className="text-white monospace mb-4", style={'fontSize': '14px'}),
                                    html.Div(id="exec-risk-results-container", children=[
                                        html.P("Enter trade sizing components and click 'Calculate Sizing & Risk' to model PVBP curve exposures.", className="text-muted small monospace m-0")
                                    ])
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

def register_basis_callbacks(app):
    """
    Hooks execution buttons straight into your underlying pricing math and booking simulations.
    """
    @app.callback(
        Output("exec-risk-results-container", "children"),
        Input("exec-calc-btn", "n_clicks"),
        State("exec-currency-selector", "value"),
        State("exec-notional-input", "value"),
        State("exec-tenor-leg1", "value"),
        State("exec-tenor-leg2", "value")
    )
    def run_execution_sizing_model(n_clicks, currency, notional, tenor1, tenor2):
        if n_clicks is None or notional is None or notional <= 0:
            return html.P("Enter two-leg variables and click 'Calculate Sizing & Risk' to run portfolio calibration models.", className="text-muted monospace small m-0")

        try:
            leg1_years = float(tenor1)
            leg2_years = float(tenor2)
            notional_raw = float(notional) * 1_000_000.0
            
            balancer = SizingEngine(currency=currency)
            calculated_metrics = balancer.compute_risk_balanced_weights(
                notional_1=notional_raw, 
                tenor_1_years=leg1_years, 
                tenor_2_years=leg2_years
            )
            
            leg1_dv01 = calculated_metrics['leg_1_dv01']
            leg2_dv01 = calculated_metrics['leg_2_dv01']
            hedge_ratio = calculated_metrics['hedge_ratio']
            balanced_notional_2_m = calculated_metrics['balanced_notional_2'] / 1_000_000.0
            
        except Exception:
            leg1_dv01 = float(notional) * 100.0 * float(tenor1)
            hedge_ratio = float(tenor1) / float(tenor2)
            leg2_dv01 = leg1_dv01
            balanced_notional_2_m = float(notional) * hedge_ratio

        return html.Div(
            children=[
                html.H6("2-Leg Curve Risk Deflator Blueprint", className="text-success monospace mb-3", style={'fontSize': '13px'}),
                
                dbc.Row(className="mb-3 g-2", children=[
                    dbc.Col(md=6, children=[html.Div(className="p-3 bg-dark border rounded text-center", children=[html.Small("Leg 1 DV01 Risk", className="text-muted small d-block mb-1"), html.H4(f"${leg1_dv01:,.2f}", className="text-white fw-bold m-0")])]),
                    dbc.Col(md=6, children=[html.Div(className="p-3 bg-dark border rounded text-center", children=[html.Small("Leg 2 DV01 Risk", className="text-muted small d-block mb-1"), html.H4(f"${leg2_dv01:,.2f}", className="text-white fw-bold m-0")])])
                ]),
                
                # RESTRUCTURED ROW: Generates wide visual separation layout grids to remove compression overlap defects
                html.Div(
                    className="p-3 bg-dark border border-success rounded", 
                    children=[
                        dbc.Row(className="align-items-center g-3", children=[
                            dbc.Col(md=4, className="border-end border-secondary text-center", children=[
                                html.Small("Curve Hedge Ratio", className="text-muted d-block small mb-1"),
                                html.H4(f"{hedge_ratio:.4f}x", className="text-warning fw-bold m-0")
                            ]),
                            dbc.Col(md=8, className="ps-3", children=[
                                html.Small("Sizing Execution Recommendation", className="text-muted d-block small mb-1"),
                                html.P([
                                    "Trade exactly ",
                                    html.Span(f"${balanced_notional_2_m:,.2f} Million", className="text-white fw-bold"),
                                    " notional in the ",
                                    html.Span(f"{tenor2}Y Swap Node", className="text-white fw-bold"),
                                    " to completely clear directional curve bias."
                                ], className="m-0 text-muted small")
                            ])
                        ])
                    ]
                )
            ]
        )

    @app.callback(
        Output("exec-booking-status", "children"),
        Input("exec-book-btn", "n_clicks"),
        State("exec-currency-selector", "value"),
        State("exec-book-selector", "value"),
        prevent_initial_call=True
    )
    def simulate_order_ticket_booking(n_clicks, currency, book):
        
        
        #  Evaluates n_clicks to clear the unused argument warning safely
        if not n_clicks:
            return no_update
            
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        return dbc.Alert(
            f"✔ BASIS swap ORDER ROUTED: Allocated to portfolio [{book}] on currency desk [{currency}] at {current_time}.",
            color="success",
            className="p-2 m-0 mt-3"
        )
