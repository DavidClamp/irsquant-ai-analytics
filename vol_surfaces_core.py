# vol_surfaces_core.py - GENERICS-DRIVEN MULTI-ASSET VOLATILITY STRIPPER
import json
import numpy as np
import plotly.graph_objects as go

class VolSurfaceEngine:
    """Dynamic quantitative engine that reads asset blocks agnostically from file arrays."""
    
    @staticmethod
    def load_raw_matrices():
        """Reads consolidated interbank volatility structures safely from disk."""
        try:
            with open("data/g4_vol_surfaces.json", "r") as f:
                return json.load(f)
        except Exception:
            return {"swaption_sabr_grids": {}, "cap_flat_strips": {}}

    @classmethod
    def get_swaption_surface(cls, currency):
        """Extracts and maps SABR grid nodes dynamically for any requested currency key."""
        data = cls.load_raw_matrices()
        grid_map = data.get("swaption_sabr_grids", {})
        
        # Safe structural fallback lookup if currency passed doesn't exist yet
        if currency not in grid_map:
            # Dynamically grab the first available currency block as an automated anchor
            if grid_map:
                currency = list(grid_map.keys())[0]
            else:
                return go.Figure(), {"alpha": 0, "beta": 0, "rho": 0, "nu": 0}
                
        grid_data = grid_map[currency]
        expiries = grid_data["expiry_nodes"]
        tenors = grid_data["underlying_tenors"]
        z_matrix = np.array(grid_data["grid_matrix"])
        params = grid_data["parameters"]
        
        fig = go.Figure(data=[go.Surface(
            x=tenors, y=expiries, z=z_matrix,
            colorscale='Viridis',
            colorbar=dict(title="Implied Vol (%)", thickness=15)
        )])
        
        fig.update_layout(
            title=dict(text=f"IRO Swaption 3D Implied Volatility Grid ({currency} SABR Matrix)", font=dict(color='#ffc107', size=14)),
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            scene=dict(xaxis=dict(title="Underlying Tenor"), yaxis=dict(title="Option Expiry"), zaxis=dict(title="Implied Vol (%)")),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        return fig, params

    @classmethod
    def get_cap_surface(cls, currency):
        """Extracts and maps linear cap strips dynamically for any requested currency key."""
        data = cls.load_raw_matrices()
        cap_map = data.get("cap_flat_strips", {})
        
        if currency not in cap_map:
            if cap_map:
                currency = list(cap_map.keys())[0]
            else:
                return go.Figure()
                
        cap_data = cap_map[currency]
        maturities = cap_data["maturities"]
        strikes = cap_data["strikes"]
        z_matrix = np.array(cap_data["strip_matrix"])
        
        fig = go.Figure(data=[go.Surface(
            x=strikes, y=maturities, z=z_matrix,
            colorscale='Cividis',
            colorbar=dict(title="Flat Vol (%)", thickness=15)
        )])
        
        fig.update_layout(
            title=dict(text=f"Cap/Floorlet Linear Implied Volatility Surface Strip ({currency})", font=dict(color='#17a2b8', size=14)),
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            scene=dict(xaxis=dict(title="Absolute Strike"), yaxis=dict(title="Maturity Term"), zaxis=dict(title="Flat Vol (%)")),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        return fig
