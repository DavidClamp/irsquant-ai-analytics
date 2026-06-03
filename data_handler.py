# data_handler.py
import json

def load_mock_market_data():
    """
    BlueGamma Payload Loader: Parses custom dictionary layouts containing
    nested curve matrices, transforming them into flat records for Pandas.
    """
    file_path = 'usd_sofr_historical_data.json'
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            
            # Target your custom BlueGamma simulation dictionary structure directly
            if isinstance(data, dict):
                curve_data = data.get("curve", [])
                index_label = data.get("index", "USD-SOFR")
                val_date = data.get("valuation_date", "2026-04-09")
                
                flattened = []
                for row in curve_data:
                    flattened.append({
                        "date": val_date,
                        "index_name": index_label,
                        "tenor": row.get("tenor"),
                        "rate": float(row.get("rate", 0.0))
                    })
                return flattened
                
            # Fallback block if the payload is already flat
            elif isinstance(data, list):
                for row in data:
                    if 'index_name' not in row and 'index' in row:
                        row['index_name'] = row['index']
                return data
                
            return []
            
    except FileNotFoundError:
        print(f"CRITICAL DATA ERROR: Could not locate '{file_path}' in project root.")
        return []
