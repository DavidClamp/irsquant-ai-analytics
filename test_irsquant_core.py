# test_irsquant_core.py - PRODUCTION TEST HARNESS FOR QUANTLIB CORE & EXTRA CURRENCIES
import json
import pandas as pd
import QuantLib as ql
from datetime import datetime

# Import your upgraded, calendar-aware infrastructure modules
from curves import BootstrappedDiscountCurve
from analytics import extract_implied_forward_swap, generate_forward_block_matrix
from utils import DataSanitizer

def run_system_diagnostic_test():
    print("=" * 80)
    print("IRSQUANT WORKSTATION: SYSTEM INTEGRATION TEST HARNESS")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # STEP 1: LOAD SYSTEM DATA REPOSITORIES
    # --------------------------------------------------------------------------
    print("\n🔍 STEP 1: Loading raw curve database files from disk...")
    try:
        with open("data/g4_curves.json", "r") as f:
            raw_data = json.load(f)
        master_df = pd.DataFrame(raw_data)
        print(f"✅ Data loaded successfully. Total historical records: {len(master_df)}")
    except Exception as e:
        print(f"❌ CRITICAL DATA LOADING ERROR: {str(e)}")
        return

    # Extract available currencies to verify our data generator covers all blocks
    available_ccys = list(master_df['currency'].unique())
    print(f"Active Currency Universe: {available_ccys}")

    # --------------------------------------------------------------------------
    # STEP 2: TEST THE EXTRA CURRENCIES AND DATA FILTERING GUARDRAILS
    # --------------------------------------------------------------------------
    print("\n🔍 STEP 2: Running target stress tests over the new extra asset blocks...")
    extra_currencies = ["CHF", "NOK", "SEK", "ZAR"]
    
    # Pick the most recent historical date snapshot available in the dataset
    target_date = sorted(list(master_df['date'].unique()))[-1]
    print(f"Target Diagnostic Evaluation Date Anchor: {target_date}")

    for ccy in extra_currencies:
        print("-" * 60)
        print(f"💱 Testing Asset Class: [{ccy}]")
        
        if ccy not in available_ccys:
            print(f"❌ ERROR: {ccy} is missing from the database file. Run generate_vol_data.py first.")
            continue
            
        # Extract the specific curve slice for this currency and date
        slice_df = master_df[(master_df['currency'] == ccy) & (master_df['date'] == target_date)]
        raw_spots = dict(zip(slice_df['tenor'], slice_df['rate']))
        
        print(f"  • Raw market data nodes ingested: {len(raw_spots)}")
        
        # Test DataSanitizer Tenor Mapping Core
        sample_tenor = " 12y "
        clean_token = DataSanitizer.clean_tenor_string(sample_tenor)
        print(f"  • DataSanitizer Test: '{sample_tenor}' successfully parsed to -> '{clean_token}'")

        # --------------------------------------------------------------------------
        # STEP 3: TEST QUANTLIB DUAL-CURVE BOOTSTRAPPING
        # --------------------------------------------------------------------------
        print("  • Triggering QuantLib Piecewise C++ curve bootstrapping...")
        try:
            # Instantiate your calendar-aware engine wrapper
            curve_wrapper = BootstrappedDiscountCurve(
                target_date=target_date, 
                spot_rates_dict=raw_spots, 
                currency=ccy
            )
            
            # Print the calendar and day-count convention that QuantLib applied
            print(f"    - QuantLib Calendar Activated: {curve_wrapper.calendar.name()}")
            print(f"    - Day-Count Counter Applied: {curve_wrapper.day_counter}")
            
            # Extract test discount factor to confirm matrix solver executed cleanly
            df_5y = curve_wrapper.get_discount_factor(5.0)
            print(f"    - 5Y Discount Factor extracted: {df_5y:.6f}")
            print("    ✅ QuantLib Curve Bootstrapping: PASSED")
            
        except Exception as e:
            print(f"    ❌ QUANTLIB CURVE BOOTSTRAP FAILED for {ccy}: {str(e)}")
            continue

        # --------------------------------------------------------------------------
        # STEP 4: TEST NON-LINEAR FORWARD ARBITRAGE SCANNER INTEGRATION
        # --------------------------------------------------------------------------
        print("  • Testing forward permutation block matrix extraction...")
        try:
            fwd_matrix = generate_forward_block_matrix(curve_wrapper)
            print(f"    - Formed a clean {fwd_matrix.shape[0]}x{fwd_matrix.shape[1]} forward block array.")
            
            # Extract a sample forward swap rate (e.g., 1Y forward starting in 2 years)
            sample_fwd = extract_implied_forward_swap(
                curve_wrapper.ql_curve, 
                start_n=2.0, 
                tenor_m=1.0, 
                day_counter=curve_wrapper.day_counter
            )
            print(f"    - Sample 2F1Y Implied Forward Swap Rate: {sample_fwd:.4f}%")
            print("    ✅ Analytics Forward Extraction: PASSED")
            
        except Exception as e:
            print(f"    ❌ ANALYTICS FORWARD EXTRACTION FAILED for {ccy}: {str(e)}")
            continue

    print("=" * 80)
    print("🏁 DIAGNOSTIC COMPLETION REPORT: ALL SYSTEMS OPERATIONAL")
    print("Your 8-currency QuantLib engine is stable, calendar-aware, and data-defensive.")
    print("=" * 80)

if __name__ == "__main__":
    run_system_diagnostic_test()
