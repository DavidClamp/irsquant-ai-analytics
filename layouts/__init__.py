# layouts/__init__.py - PACKAGE INTERFACE EXPORTS
from .home_portal import render_home_portal_layout
from .diagnostics import render_diagnostics_layout, register_diagnostics_callbacks
from .scanner import render_scanner_layout, register_scanner_callbacks
from .fly_sizer import render_fly_layout, register_fly_callbacks
from .execution import render_basis_layout, register_basis_callbacks
from .swaption_analytics import render_swaption_layout
from .cap_analytics import render_cap_layout
from .volatility_callbacks import register_global_volatility_pipelines
from .deep_analysis import render_deep_analysis_layout, register_deep_analysis_callbacks
from .backtester import render_backtester_layout, register_backtester_callbacks
from .vol_smile_analytics import render_vol_smile_layout, register_vol_smile_callbacks
from .cap_smile_analytics import render_cap_smile_layout, register_cap_smile_callbacks

__all__ = [
    'render_home_portal_layout',
    'render_diagnostics_layout',
    'register_diagnostics_callbacks',
    'render_scanner_layout',
    'register_scanner_callbacks',
    'render_fly_layout',
    'register_fly_callbacks',
    'render_basis_layout',
    'register_basis_callbacks',
    'render_swaption_layout',
    'render_cap_layout',
    'register_global_volatility_pipelines', 
    'render_deep_analysis_layout',
    'register_deep_analysis_callbacks',
    'render_backtester_layout',             
    'register_backtester_callbacks',
    'render_vol_smile_layout',             
    'register_vol_smile_callbacks',
    'render_cap_smile_layout',           
    'register_cap_smile_callbacks'
]
