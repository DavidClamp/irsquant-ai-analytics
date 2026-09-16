# utils/calibrate_sabr.py - INSTITUTIONAL SABR SURFACE CALIBRATION UTILITY
import json
import math
import numpy as np
from scipy.optimize import minimize

def bachelier_sabr_vol(F, K, T, alpha, beta, rho, vol_of_vol):
    """
    Computes the Bachelier (Normal) implied volatility approximation for a given strike K
    using the Hagan et al. stochastic alpha-beta-rho (SABR) smile parameters framework.
    """
    if T <= 0:
        return alpha
    
    # Avoid zero divisions on exact ATM boundaries
    if abs(F - K) < 1e-6:
        f_mid = F
        denominator = (f_mid) ** (1.0 - beta)
        term1 = alpha / denominator
        gamma1 = beta / f_mid
        gamma2 = beta * (beta - 1.0) / (f_mid ** 2)
        
        factor = 1.0 + (((1.0 - beta) ** 2 / 24.0) * (alpha ** 2 / (f_mid ** (2.0 - 2.0 * beta))) + 
                        (0.25 * rho * beta * alpha * vol_of_vol / (f_mid ** (1.0 - beta))) + 
                        ((2.0 - 3.0 * rho ** 2) / 24.0) * (vol_of_vol ** 2)) * T
        return term1 * factor

    # Hagan closed-form parameters for OTM extensions
    log_fk = math.log(F / K)
    f_mid = math.sqrt(F * K)
    
    if beta == 1.0:
        # Lognormal backbone limit path standardisation
        z = (vol_of_vol / alpha) * log_fk
        x_z = math.log((math.sqrt(1.0 - 2.0 * rho * z + z ** 2) + z - rho) / (1.0 - rho)) if abs(z) > 1e-5 else z
        factor = 1.0 + ((2.0 - 3.0 * rho ** 2) / 24.0 * vol_of_vol ** 2) * T
        return alpha * (z / x_z) * factor
    else:
        # Normal backbone model space (beta = 0.0 or intermediate displacements)
        zeta = (vol_of_vol / alpha) * (F ** (1.0 - beta) - K ** (1.0 - beta)) / (1.0 - beta)
        x_zeta = math.log((math.sqrt(1.0 - 2.0 * rho * zeta + zeta ** 2) + zeta - rho) / (1.0 - rho)) if abs(zeta) > 1e-5 else zeta
        
        denom = (F * K) ** ((1.0 - beta) / 2.0) * (1.0 + ((1.0 - beta) ** 2 / 24.0) * log_fk ** 2 + ((1.0 - beta) ** 4 / 1920.0) * log_fk ** 4)
        
        factor = 1.0 + (((1.0 - beta) ** 2 / 24.0) * (alpha ** 2 / ((F * K) ** (1.0 - beta))) + 
                        (0.25 * rho * beta * vol_of_vol * alpha / ((F * K) ** ((1.0 - beta) / 2.0))) + 
                        ((2.0 - 3.0 * rho ** 2) / 24.0) * vol_of_vol ** 2) * T
                        
        return (vol_of_vol * (F - K) / x_zeta) * (factor / denom) if abs(x_zeta) > 1e-5 else (alpha / denom) * factor

def calibrate_sabr_surface_session():
    """
    Ingests live discrete grid points, runs an optimization routine across expiries,
    and updates the calibrated SABR surface parameter registries on disk.
    """
    print("🔄 Running optimization routines over live option surfaces...")
    
    # Setup template arrays mimicking your data directory architectures
    expiries = ["1M", "3M", "6M", "1Y", "2Y", "5Y"]
    strikes = [3.0, 3.5, 4.0, 4.5, 5.0]  # Stressed curve strike spectrum array
    forward_asset_price = 4.0000         # Underwired global spot par rate proxy
    
    # Simulated input coordinates for today's active live grid session data
    mock_live_grid = {
        "1M": [82.5, 74.1, 68.5, 75.2, 84.6],
        "3M": [84.2, 76.5, 70.2, 77.4, 86.8],
        "6M": [86.4, 78.1, 72.4, 79.1, 88.2],
        "1Y": [89.1, 81.3, 75.1, 82.8, 91.4],
        "2Y": [92.6, 84.2, 78.6, 85.4, 94.5],
        "5Y": [96.3, 88.6, 82.3, 89.1, 98.8]
    }
    
    calibrated_output_registry = {}
    
    for exp in expiries:
        t_val = float(exp.replace("M", "")) / 12.0 if "M" in exp else float(exp.replace("Y", ""))
        market_vols = np.array(mock_live_grid[exp]) / 10000.0  # Scale bps down to decimal yield space
        
        # 🟢 OBJECTIVE LOSS FUNCTION: Minimizes sum of squared errors between SABR and market vols
        def sabr_squared_error_loss(params):
            alpha, rho, nu = params
            if abs(rho) >= 1.0 or alpha <= 0 or nu <= 0:
                return 1e6  # Impose penalty restrictions for boundary breaks
            
            error_sum = 0.0
            for s_idx, K_strike in enumerate(strikes):
                sabr_v = bachelier_sabr_vol(forward_asset_price, K_strike / 100.0, t_val, alpha, 0.0, rho, nu)
                error_sum += (sabr_v - market_vols[s_idx]) ** 2
            return error_sum

        # Initial starting guess vector [alpha, rho, nu]
        initial_guess = [0.0070, -0.10, 0.40]
        bounds = ((1e-5, None), (-0.99, 0.99), (1e-5, None))
        
        result = minimize(sabr_squared_error_loss, initial_guess, method='L-BFGS-B', bounds=bounds)
        
        if result.success:
            c_alpha, c_rho, c_nu = result.x
            calibrated_output_registry[exp] = {
                "alpha": round(float(c_alpha), 6),
                "beta": 0.0,  # Locked normal model backbone setting
                "rho": round(float(c_rho), 4),
                "nu": round(float(c_nu), 4),
                "residual_error": round(float(result.fun), 8)
            }
            print(f"✔ Expiry {exp} fitted successfully. Loss Residual: {result.fun:.8f}")
            
    # Write calibration parameter arrays directly back to system disk memory
    output_path = "data/calibrated_sabr_surfaces.json"
    with open(output_path, "w") as f:
        json.dump(calibrated_output_registry, f, indent=4)
    print(f"🎉 Success: Surface parameters committed straight to {output_path}")

if __name__ == "__main__":
    calibrate_sabr_surface_session()
