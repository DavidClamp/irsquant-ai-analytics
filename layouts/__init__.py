# layouts/__init__.py - PACKAGE INTERFACE EXPORTS
from .diagnostics import render_diagnostics_layout, register_diagnostics_callbacks
from .scanner import render_scanner_layout, register_scanner_callbacks
from .execution import render_execution_layout, register_execution_callbacks
from .swaption_analytics import render_swaption_layout
from .cap_analytics import render_cap_layout, register_cap_callbacks

# Explicitly maps and registers your true layout engines as a clean suite
__all__ = [
    'render_diagnostics_layout',
    'register_diagnostics_callbacks',
    'render_scanner_layout',
    'register_scanner_callbacks',
    'render_execution_layout',
    'register_execution_callbacks',
    'render_swaption_layout',
    'render_cap_layout',
    'register_cap_callbacks'
]
