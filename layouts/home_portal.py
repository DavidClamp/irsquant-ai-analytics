# layouts/home_portal.py - QUANT WORKSTATION MASTER ROUTER PORTAL LANDING PAGE
from dash import dcc, html
import dash_bootstrap_components as dbc

def render_home_portal_layout():
    """
    Renders an institutional cockpit landing portal, acting as the structural 
    gateway across your 8-currency multi-asset analytics terminal.
    """
    return html.Div(
        className="p-3",
        children=[
            
            dbc.Row(
                className="mb-4 align-items-center border-bottom border-secondary pb-3",
                children=[
                    dbc.Col(md=8, children=[
                        html.H2("IRSQuant NextGen Execution Desk", className="text-info fw-bold mb-1", style={'fontFamily': 'monospace'}),
                        html.P("Interest Rate Derivatives Pricing, Curve Diagnostics & Volatility Analytics Terminal Node", className="text-muted m-0 small")
                    ]),
                    dbc.Col(md=4, className="text-end", children=[
                        html.Span("SYSTEM ACTIVE", className="badge bg-success font-monospace px-2 py-2 small", style={'letterSpacing': '1px'})
                    ])
                ]
            ),
            
            #  INTRODUCTION & PIPELINE STATUS
            dbc.Row(
                className="mb-4",
                children=[
                    dbc.Col(md=12, children=[
                        dbc.Card(
                            style={'backgroundColor': '#0b0d12', 'border': '1px solid #1a1f2c', 'borderRadius': '6px'},
                            className="p-4 shadow-sm",
                            children=[
                                html.H5("Work in Progress", className="text-white monospace mb-3", style={'fontSize': '14px'}),
                                html.P(
                                    "This workstation is a standalone discretionary derivatives trading analytics and risk recycling tool with "
                                    "quantitative engineering infrastructure. Use the master header navigation menu above "
                                    "to monitor non-linear option risk horizons, map cross-tenor basis skews, and isolate "
                                    "structural relative-value carry profiles across G4 and Emerging Market books.",
                                    className="text-muted font-monospace small mb-4", style={'lineHeight': '1.6'}
                                ),

                                # PIPELINE ROADMAP BLOCK
                                html.Div(
                                    style={'borderTop': '1px dashed #2d3748', 'paddingTop': '20px'},
                                    children=[
                                        html.Div("WORKSPACE EXTENSION PIPELINE", style={'color': '#00d2ff', 'fontWeight': 'bold', 'fontFamily': 'monospace', 'fontSize': '11px', 'marginBottom': '12px'}),
                                        html.Div(
                                            className="p-3 border border-secondary rounded",
                                            style={'backgroundColor': '#07080a'},
                                            children=[
                                                html.Span("Advanced EM Cross-Currency Swap (CCS) Pricing Engine: ", className="text-muted small monospace"),
                                                html.Strong("To be completed", className="text-warning font-monospace", style={'fontSize': '12px'})
                                            ]
                                        )
                                    ]
                                )
                            ]
                        )
                    ])
                ]
            )
        ]
    )
