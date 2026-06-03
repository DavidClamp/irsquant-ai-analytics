# debug_data.py
from data_handler import load_mock_market_data
import pandas as pd

raw_data = load_mock_market_data()
print("--- DATA INSPECTION LOGS ---")
print("Data Type:", type(raw_data))
print("Data Length:", len(raw_data) if raw_data else 0)

if raw_data and len(raw_data) > 0:
    df = pd.DataFrame(raw_data)
    print("\nDetected Columns in Pandas:", df.columns.tolist())
    print("\nSample Rows:\n", df.head(3))
