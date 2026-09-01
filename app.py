# app.py - CENTRAL TRADING TERMINAL DECK INTERFACE ORCHESTRATOR (PART 1)
import sys
import os

print("🔄 STAGE 1: Validating Master Workspace System Anchors...")
try:
    import dash
    import dash_bootstrap_components as dbc
    from dash import html, dcc, Input, Output, State, no_update
    import pandas as pd
    import numpy as np
    print("✔ STAGE 1: Core visual UI framework packages successfully mapped.")
except Exception as e:
    print(f"❌ CRITICAL STAGE 1 FAILURE: Dependency tracking drop: {str(e)}")
    sys.exit(1)

print("\n🔄 STAGE 2: Mapping Decoupled Presentation Views...")
try:
    from layouts.diagnostics import render_diagnostics_layout, register_diagnostics_callbacks
    from layouts.scanner import render_scanner_layout, register_scanner_callbacks
    from layouts.fly_sizer import render_fly_layout, register_fly_callbacks
    from layouts.execution import render_basis_layout, register_basis_callbacks
    from layouts.swaption_analytics import render_swaption_layout
    from layouts.cap_analytics import render_cap_layout, register_cap_callbacks
    from layouts.volatility_callbacks import register_global_volatility_pipelines
    from layouts.backtester import render_backtester_layout, register_backtester_callbacks
    from utils.report_gen import DailyRiskReportGenerator
    print("✔ STAGE 2: All 7 layout view panel modules successfully integrated.")
except Exception as e:
    print(f"❌ CRITICAL STAGE 2 FAILURE: Layout mapping loop dropped: {str(e)}")
    print("💡 Fix Checklist: Check that you saved your files and layouts/__init__.py has matching references.")
    sys.exit(1)

print("\n🔄 STAGE 3: Launching Front-Office Core Web Server Node...")
try:
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.CYBORG],
        # 🛡️ SUPPRESS EXCEPTIONS FORCED: Blocks cross-tab nonexistent ID validations on initial page load
        suppress_callback_exceptions=True
    )
    app.title = "IRSQuant NextGen Terminal"
    server = app.server
    # 🏛️ MASTER HUD DESIGN: Structures your front-office presentation panels
    app.layout = dbc.Container(
        fluid=True,
        className="p-3 bg-dark min-vh-100 text-white font-monospace",
        children=[
            # GLOBAL PLATFORM SUB-HEADER NAV BAR
            dbc.Row(
                className="bg-black border-bottom border-secondary mb-4 p-3 align-items-center rounded shadow-sm",
                children=[
                    dbc.Col(md=8, children=[
                        html.H1("IRSQuant NextGen Analytics Terminal",
                                className="text-success fw-bold m-0 font-monospace", style={'letterSpacing': '-0.5px'}),
                        html.P("Standalone QuantLib C++ Asset Workstation | Proprietary RV Desk",
                               className="text-muted small m-0")
                    ]),
                    dbc.Col(md=4, className="text-end d-flex justify-content-end gap-2", children=[
                        dbc.Button("Trigger EOD Report", id="eod-report-btn", color="warning",
                                   size="sm", className="fw-bold px-3 shadow"),
                        html.Span("SYSTEM ENGINE STATUS: ACTIVE",
                                  className="badge bg-success font-monospace p-2 shadow-sm d-flex align-items-center")
                    ])
                ]
            ),

            # CORE NAVIGATION WORKSPACE NAVIGATOR SWITCHBOARD
            dcc.Tabs(
                id="master-workspace-tabs",
                value="tab-diagnostics",
                className="mb-4 custom-tabs-container border-0",
                children=[
                    dcc.Tab(label="Curve Diagnostics", value="tab-diagnostics", className="custom-tab text-white bg-dark border-0",
                            selected_className="custom-tab--selected bg-black border-bottom border-success text-success fw-bold"),
                    dcc.Tab(label="RV Butterfly Scanner", value="tab-scanner", className="custom-tab text-white bg-dark border-0",
                            selected_className="custom-tab--selected bg-black border-bottom border-success text-success fw-bold"),
                    dcc.Tab(label="3-Leg Fly Sizer", value="tab-fly-sizer", className="custom-tab text-white bg-dark border-0",
                            selected_className="custom-tab--selected bg-black border-bottom border-success text-success fw-bold"),
                    dcc.Tab(label="2-Leg Basis Desk", value="tab-basis-desk", className="custom-tab text-white bg-dark border-0",
                            selected_className="custom-tab--selected bg-black border-bottom border-success text-success fw-bold"),
                    dcc.Tab(label="Caplet Stripping", value="tab-caplet-stripping", className="custom-tab text-white bg-dark border-0",
                            selected_className="custom-tab--selected bg-black border-bottom border-success text-success fw-bold"),
                    dcc.Tab(label="Option Vol Desks", value="tab-option-vol", className="custom-tab text-white bg-dark border-0",
                            selected_className="custom-tab--selected bg-black border-bottom border-success text-success fw-bold"),
                    dcc.Tab(label="Historical Backtest", value="tab-backtest", className="custom-tab text-white bg-dark border-0",
                            selected_className="custom-tab--selected bg-black border-bottom border-success text-success fw-bold"),
                ]
            ),

            # MASTER CONTENT PRESENTATION CORRIDOR
            html.Div(id="master-workspace-content-slot"),

            # HIDDEN NOTIFICATION REPORT LAYER
            html.Div(id="eod-report-status-hidden", style={"display": "none"})
        ]
    )
    # 🛠️ WORKSPACE SWITCHBOARD ROUTING LOGIC

    @app.callback(
        Output("master-workspace-content-slot", "children"),
        Input("master-workspace-tabs", "value")
    )
    def render_workspace_view_segment(active_tab):
        if active_tab == "tab-diagnostics":
            return render_diagnostics_layout()
        elif active_tab == "tab-scanner":
            return render_scanner_layout()
        elif active_tab == "tab-fly-sizer":
            return render_fly_layout()
        elif active_tab == "tab-basis-desk":
            return render_basis_layout()
        elif active_tab == "tab-caplet-stripping":
            return render_cap_layout()
        elif active_tab == "tab-option-vol":
            return render_swaption_layout()
        elif active_tab == "tab-backtest":
            return render_backtester_layout()
        return html.Div("⚠️ Unknown Workspace View Segment Requested.", className="text-warning p-4")

    @app.callback(
        Output("eod-report-status-hidden", "children"),
        Input("eod-report-btn", "n_clicks"),
        prevent_initial_call=True
    )
    def trigger_eod_risk_snapshot_export(n_clicks):
        if n_clicks:
            try:
                generator = DailyRiskReportGenerator()
                generator.export_terminal_snapshot_to_disk()
            except Exception:
                pass
        return no_update

    # 🛠️ REGISTER CENTRAL PERFORMANCE ROUTINES PIPELINES
    register_diagnostics_callbacks(app)
    register_scanner_callbacks(app)
    register_fly_callbacks(app)
    register_basis_callbacks(app)
    register_cap_callbacks(app)
    register_global_volatility_pipelines(app)
    register_backtester_callbacks(app)

    print("✔ STAGE 3: Web Server Node initialization completed successfully.")

except Exception as main_err:
    print(f"❌ CRITICAL STAGE 3 FAILURE: Web Node boot process halted: {str(main_err)}")
    sys.exit(1)

if __name__ == "__main__":
    # 🟢 FIXED: Swapped out obsolete 'run_server' for the modern 'run' method call
    app.run(debug=True, port=8050)
