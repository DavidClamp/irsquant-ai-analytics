# layouts/__init__.py 
from .diagnostics import layout_diagnostics
from .scanner import layout_scanner
from .volatility import layout_volatility
from .execution import layout_execution

# Explicitly maps and registers your layouts as a cleanly packaged financial presentation suite
__all__ = ['layout_diagnostics', 'layout_scanner', 'layout_volatility', 'layout_execution']
