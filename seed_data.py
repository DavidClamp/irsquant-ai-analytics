# seed_data.py - CORE DATASET SEED UTILITY
import json
import datetime
import os
import numpy as np

print("🔄 Building institutional multi-currency yield curve databases...")

np.random.seed(42)
start_date = datetime.date(2021, 9, 1)
end_date = datetime.date(2026, 8, 28)
currencies = ["USD", "EUR", "GBP", "JPY", "CHF", "NOK", "SEK", "ZAR"]
tenors = ["1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "30Y"]

base_rates = {
    "USD": 3.50, "EUR": 2.50, "GBP": 3.80, "JPY": 0.25,
    "CHF": 1.20, "NOK": 4.10, "SEK": 3.30, "ZAR": 7.60
}

hist_data = []
current_date = start_date
daily_rates = {ccy: base_rates[ccy] for ccy in currencies}

# 1. GENERATE 5 YEARS OF CHRONOLOGICAL TIMELINE VALUES
while current_date <= end_date:
    if current_date.weekday() < 5:  # Business days only
        date_str = current_date.strftime("%Y-%m-%d")
        for ccy in currencies:
            daily_rates[ccy] += np.random.normal(0, 0.012)
            daily_rates[ccy] = max(0.01, min(daily_rates[ccy], 12.0))
            
            for idx, tenor in enumerate(tenors):
                curve_spread = idx * 0.15 + np.random.normal(0, 0.005)
                tenor_rate = daily_rates[ccy] + curve_spread
                
                hist_data.append({
                    "date": date_str,
                    "currency": ccy,
                    "tenor": tenor,
                    "rate": round(tenor_rate, 4)
                })
    current_date += datetime.timedelta(days=1)

# 2. GENERATE TODAY'S LATEST INTERBANK ARRAYS
live_date_str = "2026-08-30"
live_data = []
for ccy in currencies:
    final_base = daily_rates[ccy] + np.random.normal(0, 0.02)
    for idx, tenor in enumerate(tenors):
        curve_spread = idx * 0.16 + np.random.normal(0, 0.005)
        live_data.append({
            "date": live_date_str,
            "currency": ccy,
            "tenor": tenor,
            "rate": round(final_base + curve_spread, 4)
        })

# Ensure the target storage folder exists
os.makedirs("data", exist_ok=True)

with open("data/g4_curves_hist.json", "w") as f:
    json.dump(hist_data, f, indent=2)

with open("data/g4_curves_live.json", "w") as f:
    json.dump(live_data, f, indent=2)

print(f"✔ SUCCESS: Shipped {len(hist_data)} historical rows and {len(live_data)} today's live execution entries down to disk.")
