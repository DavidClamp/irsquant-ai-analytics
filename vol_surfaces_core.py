# vol_surfaces_core.py - DATA-DEFENSIVE VOLATILITY SURFACE STRIPPER
import json
import numpy as np
import plotly.graph_objects as go

class VolSurfaceEngine:
    """Dynamic quantitative engine that reads historical asset blocks, clearing zero-node drops."""
    
    @staticmethod
    def load_raw_matrices():
        """Reads consolidated interbank volatility structures safely from disk."""
        try:
            with open("data/g4_vol_surfaces.json", "r") as f:
                return json.load(f)
        except Exception:
            return {"swaption_sabr_grids": {}, "cap_flat_strips": {}}

    @classmethod
    def _clean_and_impute_mesh(cls, z_matrix):
        """
        Intercepts missing option nodes (volatility == 0.0) and replaces them
        using a spatial proximity interpolation to maintain smooth 3D surfaces.
        """
        z_matrix = np.array(z_matrix, dtype=float)
        rows, cols = z_matrix.shape
        
        # Absolute structural safety shield: If the entire matrix is corrupt, return an ATM baseline
        if np.all(z_matrix <= 0.0):
            return np.full((rows, cols), 20.0)
            
        # Iterate through the grid to clear out dropped nodes
        for r in range(rows):
            for c in range(cols):
                if z_matrix[r, c] <= 0.0:
                    # Find all valid, non-zero neighboring points in the mesh
                    valid_neighbors = []
                    for nr in range(rows):
                        for nc in range(cols):
                            if z_matrix[nr, nc] > 0.0:
                                # Calculate simple Manhattan distance
                                distance = abs(r - nr) + abs(c - nc)
                                valid_neighbors.append((distance, z_matrix[nr, nc]))
                    
                    # Sort by proximity and patch the hole with the nearest valid rate
                    valid_neighbors.sort(key=lambda x: x[0])
                    z_matrix[r, c] = valid_neighbors[0][1]
                    
        return z_matrix

    @classmethod
    def get_swaption_surface(cls, currency, target_date=None):
        """Extracts SABR grid nodes dynamically, neutralizing illiquid data gaps."""
        data = cls.load_raw_matrices()
        grid_map = data.get("swaption_sabr_grids", {})
        
        currency = currency.upper().strip()
        if currency not in grid_map:
            currency = list(grid_map.keys())[0] if grid_map else "USD"
            
        grid_data = grid_map.get(currency, {})
        if not grid_data:
            return go.Figure(), {"alpha": 0, "beta": 0, "rho": 0, "nu": 0}
            
        expiries = grid_data["expiry_nodes"]
        tenors = grid_data["underlying_tenors"]
        hist_dict = grid_data.get("historical_data", {})
        
        if not target_date or target_date not in hist_dict:
            target_date = sorted(list(hist_dict.keys()))[-1] if hist_dict else None
            
        if not target_date:
            return go.Figure(), {"alpha": 0, "beta": 0, "rho": 0, "nu": 0}
            
        day_slice = hist_dict[target_date]
        
        # RUN IMPUTATION DETECTOR OVER THE SURFACE MESH
        z_matrix = cls._clean_and_impute_mesh(day_slice["grid_matrix"])
        params = day_slice["parameters"]
        
        # Build High-Contrast 3D Plotly Surface
        fig = go.Figure(data=[go.Surface(
            x=tenors, y=expiries, z=z_matrix,
            colorscale='Viridis', colorbar=dict(title="Implied Vol (%)", thickness=15)
        )])
        
        fig.update_layout(
            title=dict(text=f"IRO Swaption 3D Volatility Grid ({currency} SABR Matrix - {target_date})", font=dict(color='#ffc107', size=14)),
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            scene=dict(xaxis=dict(title="Underlying Tenor"), yaxis=dict(title="Option Expiry"), zaxis=dict(title="Implied Vol (%)")),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        return fig, params

    @classmethod
    def get_cap_surface(cls, currency, target_date=None):
        """Extracts linear cap strips dynamically, neutralizing strike boundary drops."""
        data = cls.load_raw_matrices()
        cap_map = data.get("cap_flat_strips", {})
        
        currency = currency.upper().strip()
        if currency not in cap_map:
            currency = list(cap_map.keys())[0] if cap_map else "USD"
            
        cap_data = cap_map.get(currency, {})
        if not cap_data:
            return go.Figure()
            
        maturities = cap_data["maturities"]
        strikes = cap_data["strikes"]
        hist_dict = cap_data.get("historical_data", {})
        
        if not target_date or target_date not in hist_dict:
            target_date = sorted(list(hist_dict.keys()))[-1] if hist_dict else None
            
        if not target_date:
            return go.Figure()
            
        day_slice = hist_dict[target_date]
        
        # RUN IMPUTATION DETECTOR OVER THE STRIP MESH
        z_matrix = cls._clean_and_impute_mesh(day_slice["strip_matrix"])
        
        # Build High-Contrast 3D Surface
        fig = go.Figure(data=[go.Surface(
            x=strikes, y=maturities, z=z_matrix,
            colorscale='Cividis', colorbar=dict(title="Flat Vol (%)", thickness=15)
        )])
        
        fig.update_layout(
            title=dict(text=f"Cap/Floorlet Linear Volatility Surface Strip ({currency} - {target_date})", font=dict(color='#17a2b8', size=14)),
            template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            scene=dict(xaxis=dict(title="Absolute Strike"), yaxis=dict(title="Maturity Term"), zaxis=dict(title="Flat Vol (%)")),
            margin=dict(l=10, r=10, t=40, b=10)
        )
        return fig
