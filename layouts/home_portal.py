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
            # PREMIUM WELCOME HEADER
            
            dbc.Row(
                className="mb-4 align-items-center border-bottom border-secondary pb-3",
                children=[
                    dbc.Col(md=8, children=[
                        html.H2("IRSQuant NextGen Trading Desk", className="text-info fw-bold mb-1", style={'fontFamily': 'monospace'}),
                        html.Div([
                            html.Span("IRD Analytics and Trading Tools Node", className="text-muted small me-3"),
                            
                            html.Span(
                                "Lead Practitioner: David", 
                                className="font-monospace px-2 py-0.5 rounded", 
                                style={
                                    'backgroundColor': '#1a202c', 
                                    'color': '#ffffff', 
                                    'fontSize': '11px', 
                                    'border': '1px solid #2d3748',
                                    'display': 'inline-block'
                                }
                            )
                        ], className="d-flex align-items-center mt-1")
                    ]),
                    dbc.Col(md=4, className="text-end", children=[
                        html.Span("SYSTEM ACTIVE", className="badge bg-success font-monospace px-2 py-2 small", style={'letterSpacing': '1px'})
                    ])
                ]
            ),

            
            # MISSION CONTROL INTRODUCTION & PIPELINE STATUS
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
                                    "structural relative-value carry profiles across G4 and Emerging Market books. Features an active, "
                                    "Regex-tokenised Natural Language Processing (NLP) AI Co-Pilot console that translates conversational English "
                                    "commands directly into fractional decimal portfolio weightings and historical trade simulation charts.",
                                    style={
                                        'color': '#ffffff', 
                                        'fontSize': '12px', 
                                        'fontFamily': 'monospace', 
                                        'lineHeight': '1.7', 
                                        'marginBottom': '20px'
                                    }
                                ),
                                
                                # PIPELINE ROADMAP BLOCK
                                 # PIPELINE ROADMAP BLOCK (REFACTORED FOR FI PORTFOLIO DEPLOYMENT)
                                html.Div(
                                    style={'borderTop': '1px dashed #2d3748', 'paddingTop': '20px'},
                                    children=[
                                        html.Div("WORKSPACE EXTENSION PIPELINE", style={'color': '#00d2ff', 'fontWeight': 'bold', 'fontFamily': 'monospace', 'fontSize': '11px', 'marginBottom': '12px'}),
                                        html.Div(
                                            className="p-3 border border-secondary rounded mb-2",
                                            style={'backgroundColor': '#07080a'},
                                            children=[
                                                html.Span("Future developments to be scheduled: ", className="text-muted small monospace"),
                                                html.Strong("Complex IRS/IRO Structured Analytics", className="text-warning font-monospace", style={'fontSize': '12px'})
                                            ]
                                        ),
                                        html.Div(
                                            className="p-3 border border-secondary rounded",
                                            style={'backgroundColor': '#07080a'},
                                            children=[
                                                html.Span("Future projects under scoping: ", className="text-muted small monospace"),
                                                html.Strong("Credit Derivatives Integration via Large-Scale Fixed-Income Databases", className="text-warning font-monospace", style={'fontSize': '12px'})
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
