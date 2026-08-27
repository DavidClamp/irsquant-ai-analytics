import sys
import os

print("🔄 STAGE 1: Validating Master Workspace System Anchors...")

try:
    import dash
    import dash_bootstrap_components as dbc
    from dash import html, dcc, Input, Output, State
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
    from utils.report_gen import DailyRiskReportGenerator
    print("✔ STAGE 2: All 6 layout view panel modules successfully integrated.")
except Exception as e:
    print(f"❌ CRITICAL STAGE 2 FAILURE: Layout mapping loop dropped: {str(e)}")
    print("💡 Fix Checklist: Check that you saved your files and layouts/__init__.py has matching references.")
    sys.exit(1)

print("\n🔄 STAGE 3: Launching Front-Office Core Web Server Node...")
try:
    app = dash.Dash(
        __name__, 
        external_stylesheets=[dbc.themes.CYBORG],
        suppress_callback_exceptions=True
    )
    app.title = "IRSQuant NextGen Terminal"
    
    # CRUCIAL FOR HEROKU: Expose underlying flask server for gunicorn
    server = app.server

    # MASTER LAYOUT GRID MOUNT
    app.layout = html.Div(
        style={'backgroundColor': '#060709', 'minHeight': '100vh', 'padding': '20px'},
        children=[
            # HEADER BANNER STRIP
            dbc.Row(
                className="border-bottom border-secondary pb-3 mb-4 align-items-center g-3",
                children=[
                    dbc.Col(md=5, children=[
                        html.H1("IRSQuant NextGen Analytics Terminal", className="text-success fw-bold m-0", style={'letterSpacing': '0.5px'}),
                        html.P("Standalone QuantLib C++ Asset Workstation | Proprietary RV Desk", className="text-muted small m-0")
                    ]),
                    dbc.Col(md=4, className="text-md-center", children=[
                        dbc.Button("Trigger EOD Report", id="global-report-btn", color="outline-warning", className="fw-bold px-4"),
                        html.Div(id="global-report-status", className="text-warning small monospace mt-1", style={'fontSize': '11px'})
                    ]),
                    dbc.Col(md=3, className="text-md-end d-flex align-items-center justify-content-end", children=[
                        html.Div(
                            style={'backgroundColor': '#0b0d12', 'border': '1px solid #00ff66', 'borderRadius': '6px', 'padding': '10px 16px', 'boxShadow': '0 0 10px rgba(0, 255, 102, 0.15)', 'minWidth': '210px'},
                            className="text-start",
                            children=[
                                html.Small("SYSTEM ENGINE STATUS:", className="text-muted d-block fw-bold mb-1", style={'fontSize': '9px', 'fontFamily': 'monospace'}),
                                html.Span("● QUANTLIB NATIVE ACTIVE", className="text-success fw-bold d-block", style={'fontSize': '12px', 'fontFamily': 'monospace'})
                            ]
                        )
                    ])
                ]
            ),
            
            # WORKSPACE DESK TABS MATRIX NAVIGATION
            dcc.Tabs(
                id="master-workspace-tabs",
                value="tab-diagnostics",
                children=[
                    dcc.Tab(label="Curve Diagnostics", value="tab-diagnostics", className="custom-tab", selected_className="custom-tab-selected"),
                    dcc.Tab(label="RV Butterfly Scanner", value="tab-scanner", className="custom-tab", selected_className="custom-tab-selected"),
                    dcc.Tab(label="3-Leg Fly Sizer", value="tab-fly-sizer", className="custom-tab", selected_className="custom-tab-selected"),
                    dcc.Tab(label="2-Leg Basis Desk", value="tab-basis-desk", className="custom-tab", selected_className="custom-tab-selected"),
                    dcc.Tab(label="Caplet Stripping", value="tab-caplets", className="custom-tab", selected_className="custom-tab-selected"),  
                    dcc.Tab(label="Option Vol Desks", value="tab-swaptions", className="custom-tab", selected_className="custom-tab-selected"),
                ],
                style={'height': '44px'}
            ),
            
            # ACTIVE PANEL HOLDER RECEPTACLE
            html.Div(id="master-workspace-view-content", className="pt-4")
        ]
    )

    # REGISTER REACTIVE SYSTEM ROUTING CALLBACK MATRICES
    register_diagnostics_callbacks(app)
    register_scanner_callbacks(app)
    register_cap_callbacks(app)
    register_fly_callbacks(app)      
    register_basis_callbacks(app)    
    register_global_volatility_pipelines(app)

    @app.callback(
        Output("master-workspace-view-content", "children"),
        Input("master-workspace-tabs", "value")
    )
    def route_workspace_view_panels(active_tab):
        if active_tab == "tab-diagnostics": return render_diagnostics_layout()
        elif active_tab == "tab-scanner": return render_scanner_layout()
        elif active_tab == "tab-fly-sizer": return render_fly_layout()       
        elif active_tab == "tab-basis-desk": return render_basis_layout()     
        elif active_tab == "tab-caplets": return render_cap_layout()
        elif active_tab == "tab-swaptions": return render_swaption_layout()
        return html.Div("View component missing context parameters.", className="text-danger monospace small")
    
    @app.callback(
        Output("global-report-status", "children"),
        Input("global-report-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def execute_ui_report_snapshot(n_clicks):
        if not n_clicks: 
            return dash.no_update
        
        try: 
            generator = DailyRiskReportGenerator()
            report_path = generator.generate_eod_snapshot()
            return f"✔ Compiled: reports/{os.path.basename(report_path)}"
        except Exception as e: 
            return f"❌ Snapshot crashed: {str(e)}"

# FIX: Added the missing except block for Stage 3 initialization
except Exception as e:
    print(f"❌ CRITICAL STAGE 3 FAILURE: Dash application setup failed: {str(e)}")
    sys.exit(1)


# --- SERVER RUN TIME ANCHOR ---
# Completely flush left (0 spaces) outside the initialization tracks
if __name__ == "__main__":
    try:
        print("🚀 Initializing Master IRSQuant Core Router Nodes...")
        print("🌍 Terminal Link Ready: Point your browser to http://127.0.0.1:8050")
        app.run(debug=True, port=8050)
    except Exception as e:
        print(f"❌ CRITICAL RUNTIME FAILURE: Server boot process dropped: {str(e)}")
        sys.exit(1)
