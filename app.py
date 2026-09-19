# app.py - PART 1: MAIN CONFIGURATION, PACKAGES & USER INTERFACE LAYOUT
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from flask_compress import Compress

# 🟢 INSTITUTIONAL IMPORTS: Ingesting your modular multi-currency presentation layouts cleanly

from layouts import (
    render_home_portal_layout,
    render_diagnostics_layout,
    render_deep_analysis_layout,
    render_scanner_layout,
    render_fly_layout,
    render_basis_layout,
    render_cap_layout,
    render_swaption_layout,
    render_backtester_layout,
    render_vol_smile_layout,
    render_cap_smile_layout,
    register_diagnostics_callbacks,
    register_scanner_callbacks,
    register_fly_callbacks,
    register_basis_callbacks,
    register_deep_analysis_callbacks,
    register_backtester_callbacks,
    register_global_volatility_pipelines,
    register_vol_smile_callbacks,
    register_cap_smile_callbacks
) 

# Initialis core Dash workspace application shell container node natively

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    suppress_callback_exceptions=True,
    # Inject explicit institutional search indexing metadata tags natively
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "IRSQuant NextGen Analytics Terminal - Institutional Multi-Currency Interest Rate Derivatives Pricing Desk."}
    ]
)
server = app.server

Compress(server)


# =========================================================================
# 🏢 MASTER INTERFACE NAVIGATION BAR & LAYOUT STRUCTURE
# =========================================================================
app.layout = dbc.Container(
    fluid=True,
    style={'backgroundColor': '#07080a', 'minHeight': '100vh', 'color': '#ffffff', 'paddingTop': '15px'},
    children=[
        # Master Navigation Menu Tabs Header Wrapper
        dcc.Tabs(
            id="master-workspace-tabs",
            value="tab-home",  
            className="custom-tabs-container mb-4",
            children=[
                
                dcc.Tab(
                    label="Home", 
                    value="tab-home",
                    className="custom-tab-item",
                    selected_className="custom-tab-item--selected"
                ),
                dcc.Tab(
                    label="Curve Diagnostics", 
                    value="tab-diagnostics",
                    className="custom-tab-item",
                    selected_className="custom-tab-item--selected"
                ),
                dcc.Tab(
                    label="Swaption Vol Surface", 
                    value="tab-option-vol",
                    className="custom-tab-item",
                    selected_className="custom-tab-item--selected"
                ),
                dcc.Tab(
                    label="Caplet Stripping", 
                    value="tab-caplet-stripping",
                    className="custom-tab-item",
                    selected_className="custom-tab-item--selected"
                ),
                dcc.Tab(
                    label="Cap Smile", 
                    value="tab-cap-smile",
                    className="custom-tab-item",
                    selected_className="custom-tab-item--selected"
                ),
                dcc.Tab(
                    label="Vol Smile", 
                    value="tab-vol-smile",
                    className="custom-tab-item",
                    selected_className="custom-tab-item--selected"
                ),
                dcc.Tab(
                    label="RV Fly Sizer", 
                    value="tab-fly-sizer",
                    className="custom-tab-item",
                    selected_className="custom-tab-item--selected"
                ),
                dcc.Tab(
                    label="Cross-Tenor Matrix", 
                    value="tab-deep-matrix",
                    className="custom-tab-item",
                    selected_className="custom-tab-item--selected"
                ),
                dcc.Tab(
                    label="RV Basis Scanner", 
                    value="tab-scanner",
                    className="custom-tab-item",
                    selected_className="custom-tab-item--selected"
                ),
                dcc.Tab(
                    label="NLP Backtester", 
                    value="tab-backtest",
                    className="custom-tab-item",
                    selected_className="custom-tab-item--selected"
                )
            ]
        ),
        
        # THE ACTIVE VIEW RENDERING CANVAS SLOT
        html.Div(id="master-workspace-content-slot")
    ]
)

# app.py - PART 2: CENTRAL ROUTER CALLBACKS & MODERN SERVER BOOT

# =========================================================================
# 🔄 UNIFIED WORKSPACE LAYOUT SWITCHBOARD ROUTER CALLBACK
# =========================================================================
@app.callback(
    Output("master-workspace-content-slot", "children"),
    Input("master-workspace-tabs", "value")
)
def render_workspace_view_segment(active_tab):
    """
    Core switchboard callback that dynamically updates the rendering layout canvas
    based on the current active tab selection parameter token.
    """
    if active_tab == "tab-home" or active_tab is None:
        return render_home_portal_layout()
    elif active_tab == "tab-diagnostics":
        return render_diagnostics_layout()
    elif active_tab == "tab-deep-matrix":
        return render_deep_analysis_layout()
    elif active_tab == "tab-scanner":
        return render_scanner_layout()
    elif active_tab == "tab-fly-sizer":
        return render_fly_layout()
    elif active_tab == "tab-basis-desk":
        return render_basis_layout()
    elif active_tab == "tab-caplet-stripping":
        return render_cap_layout()
    elif active_tab == "tab-cap-smile":
        return render_cap_smile_layout()
    elif active_tab == "tab-option-vol":
        return render_swaption_layout()
    elif active_tab == "tab-vol-smile":
        return render_vol_smile_layout()
    elif active_tab == "tab-backtest":
        return render_backtester_layout()
            
    return html.Div("⚠️ Unknown Workspace View Segment Requested.", className="text-warning p-4")


# =========================================================================
# ⚙️ ARMED PORTFOLIO BACKGROUND CALLBACK SYSTEM UTILITIES
# =========================================================================
# Explicitly initialise active trading desk threads only.
register_diagnostics_callbacks(app)
register_scanner_callbacks(app)
register_fly_callbacks(app)
register_deep_analysis_callbacks(app)
register_backtester_callbacks(app)
register_global_volatility_pipelines(app) 
register_vol_smile_callbacks(app) 
register_basis_callbacks(app)
register_cap_smile_callbacks(app)

# 🟢 FIXED: Any loose, stray duplicate lines below here are fully erased

if __name__ == "__main__":
    # Boot the terminal app directly into the active local foreground loop window
    app.run(debug=True, port=8050)

