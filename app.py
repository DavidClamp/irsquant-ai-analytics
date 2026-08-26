# app.py - MASTER PRESENTATION ROUTER & COUPLING ENGINE
import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State

# Import layout presentation blueprints
from layouts.diagnostics import render_diagnostics_layout, register_diagnostics_callbacks
from layouts.scanner import render_scanner_layout, register_scanner_callbacks
from layouts.swaption_analytics import render_swaption_layout
from layouts.cap_analytics import render_cap_layout, register_cap_callbacks
from layouts.execution import render_execution_layout, register_execution_callbacks

# Import centralized options event pipelines and report generator utility
from layouts.volatility_callbacks import register_global_volatility_pipelines
from utils.report_gen import DailyRiskReportGenerator

# Initialize the standalone terminal server with dark high-contrast themes
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True
)
app.title = "IRSQuant NextGen Terminal"

# ==============================================================================
# 🏛️ GLOBAL MASTER APP HOUSING FRAMEWORK
# ==============================================================================
app.layout = html.Div(
    style={'backgroundColor': '#060709', 'minHeight': '100vh', 'padding': '20px'},
    children=[
        # CENTRAL TERMINAL HEADER STRIP WITH ACTION BUTTON
        dbc.Row(
            className="border-bottom border-secondary pb-3 mb-4 align-items-center g-3",
            children=[
                dbc.Col(md=5, children=[
                    html.H1("IRSQuant NextGen Analytics Terminal", className="text-success fw-bold m-0", style={'letterSpacing': '0.5px'}),
                    html.P("Standalone QuantLib C++ Asset Workstation | Proprietary RV Desk", className="text-muted small m-0")
                ]),
                dbc.Col(md=4, className="text-md-center", children=[
                    dbc.Button(
                        "Trigger EOD Report", 
                        id="global-report-btn", 
                        color="outline-warning", 
                        className="fw-bold px-4",
                        style={'letterSpacing': '0.5px'}
                    ),
                    html.Div(id="global-report-status", className="text-warning small monospace mt-1", style={'fontSize': '11px'})
                ]),
                dbc.Col(md=3, className="text-md-end", children=[
                    html.Div(className="p-2 bg-dark rounded border border-secondary d-inline-block text-start", children=[
                        html.Small("System Core Status:", className="text-muted d-block small", style={'fontSize': '10px'}),
                        html.Span("● QUANTLIB NATIVE ACTIVE", className="text-success fw-bold monospace small", style={'fontSize': '12px'})
                    ])
                ])
            ]
        ),
        
        # MASTER NAVIGATION WORKSPACE TABS
        dcc.Tabs(
            id="master-workspace-tabs",
            value="tab-diagnostics",
            children=[
                dcc.Tab(label="Curve Diagnostics", value="tab-diagnostics", className="custom-tab", selected_className="custom-tab-selected"),
                dcc.Tab(label="RV Butterfly Scanner", value="tab-scanner", className="custom-tab", selected_className="custom-tab-selected"),
                dcc.Tab(label="Swaption Vol Desks", value="tab-swaptions", className="custom-tab", selected_className="custom-tab-selected"),
                dcc.Tab(label="Caplet Stripping Curves", value="tab-caplets", className="custom-tab", selected_className="custom-tab-selected"),
                dcc.Tab(label="IRS Sizing Order Desk", value="tab-execution", className="custom-tab", selected_className="custom-tab-selected"),
            ],
            style={'height': '44px'}
        ),
        
        # VIEW LAYER RECEPTACLE CONTAINER
        html.Div(id="master-workspace-view-content", className="pt-4")
    ]
)

# ==============================================================================
# 🔄 MASTER DESK PACKAGING INTERFACES & REGISTRATION CALLBACKS
# ==============================================================================
register_diagnostics_callbacks(app)
register_scanner_callbacks(app)
register_cap_callbacks(app)
register_execution_callbacks(app)
register_global_volatility_pipelines(app)

@app.callback(
    Output("master-workspace-view-content", "children"),
    Input("master-workspace-tabs", "value")
)
def route_workspace_view_panels(active_tab):
    if active_tab == "tab-diagnostics":
        return render_diagnostics_layout()
    elif active_tab == "tab-scanner":
        return render_scanner_layout()
    elif active_tab == "tab-swaptions":
        return render_swaption_layout()
    elif active_tab == "tab-caplets":
        return render_cap_layout()
    elif active_tab == "tab-execution":
        return render_execution_layout()
    return html.Div("View component missing context parameters.", className="text-danger monospace small")

# GLOBAL UTILITY ACTION: INTERACTIVE SNAPSHOT COUPLING
@app.callback(
    Output("global-report-status", "children"),
    Input("global-report-btn", "n_clicks"),
    prevent_initial_call=True
)
def execute_ui_report_snapshot(n_clicks):
    try:
        generator = DailyRiskReportGenerator()
        report_path = generator.generate_eod_snapshot()
        filename = os.path.basename(report_path)
        return f"✔ Compiled: reports/{filename}"
    except Exception as e:
        return f"❌ Snapshot crashed: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, port=8050)
