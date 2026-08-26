# utils.py - STREAMLINED IRSQUANT ANALYTICS UTILITY LAYER
import re
import json
import QuantLib as ql
import pandas as pd
import numpy as np
from datetime import datetime

def get_cleaned_yield_curve(target_date, currency="USD"):
    """
    Fetches raw spot rates directly from the local JSON data repository
    and bootstraps a calendar-perfect QuantLib Piecewise Log-Linear Discount Curve.
    """
    ccy = str(currency).upper().strip()
    
    try:
        with open("data/g4_curves.json", "r") as f:
            raw_data = json.load(f)
        df_all = pd.DataFrame(raw_data)
        df = df_all[(df_all['currency'] == ccy) & (df_all['date'] == str(target_date))][["tenor", "rate"]]
    except Exception:
        return None

    if df.empty:
        return None

        
    # [The rest of your operational QuantLib helper loops continue identically below...]

    # --- ASSET REGISTRY SWITCHBOARD ---
    registry = {
        "USD": {"calendar": ql.UnitedStates(ql.UnitedStates.GovernmentBond), "day_count": ql.Actual360(), "index": ql.Sofr},
        "EUR": {"calendar": ql.TARGET(), "day_count": ql.Actual360(), "index": ql.Euribor3M},
        "GBP": {"calendar": ql.UnitedKingdom(ql.UnitedKingdom.Exchange), "day_count": ql.Actual365Fixed(), "index": ql.Sonia},
        "JPY": {"calendar": ql.Japan(), "day_count": ql.Actual360(), "index": ql.Tona},
        
        "CHF": {"calendar": ql.Switzerland(), "day_count": ql.Actual360(), "index": ql.Saron},
        "NOK": {"calendar": ql.Norway(), "day_count": ql.Actual360(), "index": lambda: ql.IborIndex("Nowa", ql.Period(3, ql.Months), 2, ql.CHFCurrency(), ql.Norway(), ql.ModifiedFollowing, False, ql.Actual360())},
        "SEK": {"calendar": ql.Sweden(), "day_count": ql.Actual360(), "index": lambda: ql.IborIndex("Stibor", ql.Period(3, ql.Months), 2, ql.EURCurrency(), ql.Sweden(), ql.ModifiedFollowing, False, ql.Actual360())},
        "ZAR": {"calendar": ql.SouthAfrica(), "day_count": ql.Actual365Fixed(), "index": lambda: ql.IborIndex("Jibar", ql.Period(3, ql.Months), 2, ql.ZARCurrency(), ql.SouthAfrica(), ql.ModifiedFollowing, False, ql.Actual365Fixed())}
    }
    
    meta = registry.get(ccy, registry["USD"])
    calendar = meta["calendar"]
    day_counter = meta["day_count"]
    base_index = meta["index"]() if not callable(meta["index"]) else meta["index"]()

    ql_date = ql.Date(int(target_date.split('-')[2]), int(target_date.split('-')[1]), int(target_date.split('-')[0]))
    ql.Settings.instance().evaluationDate = ql_date

    helpers = []
    settlement_days = 2
    
    for _, row in df.iterrows():
        raw_rate = float(row["rate"])
        if raw_rate <= 0.0:
            continue
            
        quote_handle = ql.QuoteHandle(ql.SimpleQuote(raw_rate))
        clean_tenor_str = DataSanitizer.clean_tenor_string(row["tenor"])
        
        if 'M' in clean_tenor_str:
            period = ql.Period(int(clean_tenor_str.replace('M', '')), ql.Months)
        else:
            period = ql.Period(int(clean_tenor_str.replace('Y', '')), ql.Years)
            
        if clean_tenor_str == "3M":
            helper = ql.DepositRateHelper(quote_handle, period, settlement_days, calendar, ql.ModifiedFollowing, False, day_counter)
        else:
            helper = ql.SwapRateHelper(quote_handle, period, calendar, ql.Annual, ql.Unadjusted, day_counter, base_index)
        helpers.append(helper)

    if not helpers:
        return None

    curve_settlement_date = calendar.advance(ql_date, ql.Period(settlement_days, ql.Days))
    return ql.PiecewiseLogLinearDiscount(curve_settlement_date, helpers, day_counter)

# [DataSanitizer]

class DataSanitizer:
    """
    Centralised utility engine for handling string sanitization, date normalization,
    and statistical coordinate conversions across the IRSQuant workstation.
    """
    
    @staticmethod
    def clean_tenor_string(raw_tenor):
        """
        Forces a raw tensor/tenor parameter into a single, clean uppercase string token.
        🛡️ Failsafe: Automatically flattens lists, tuples, or nested structures.
        """
        # If the input itself is a list or tuple, extract the first entry safely
        if isinstance(raw_tenor, (list, tuple)):
            if len(raw_tenor) > 0:
                raw_tenor = raw_tenor[0]
            else:
                return "1Y" # Global default fallback anchor string
                
        # Cast to a flat string and strip whitespaces/linebreaks
        sanitized = str(raw_tenor).strip().upper()
        
        # Strip any extraneous bracket wrappers left over from pandas cell serialization
        sanitized = sanitized.replace('[', '').replace(']', '').replace("'", "").replace('"', '')
        
        return sanitized

    @staticmethod
    def parse_tenor_to_years(tenor_str):
        # 🛡️ FAILSAFE: If a full list or sequence slips through, extract the first entry safely
        if isinstance(tenor_str, (list, tuple)):
            if len(tenor_str) > 0:
                tenor_str = tenor_str[0]
            else:
                return 1.0

        clean_token = DataSanitizer.clean_tenor_string(tenor_str)
        try:
            if "M" in clean_token:
                return float(clean_token.replace("M", "")) / 12.0
            elif "Y" in clean_token:
                return float(clean_token.replace("Y", ""))
            return float(clean_token)
        except ValueError:
            # Fall back to isolating purely numeric digits if text parsing is jammed
            try:
                clean_num = "".join(filter(str.isdigit, clean_token))
                return float(clean_num) if clean_num else 1.0
            except Exception:
                return 1.0


    @staticmethod
    def normalize_date_string(raw_date):
        from datetime import datetime
        if not raw_date:
            return datetime.today().strftime("%Y-%m-%d")
            
        # 1. Cast to a primitive string, remove outer spaces, and fix slash marks immediately
        raw_str = str(raw_date).strip().replace("/", "-")
        
        # 2. Split on spaces to strip out any trailing timestamp blocks safely, then take element 0
        clean_date = raw_str.split(" ")[0]
        
        try:
            # Validate format compliance
            datetime.strptime(clean_date, "%Y-%m-%d")
            return clean_date
        except ValueError:
            return datetime.today().strftime("%Y-%m-%d")


    @staticmethod
    def calculate_z_score(current_residual, historical_residuals):
        if len(historical_residuals) < 2:
            return 0.0
        mean = float(sum(historical_residuals)) / len(historical_residuals)
        variance = sum((x - mean) ** 2 for x in historical_residuals) / (len(historical_residuals) - 1)
        std_dev = variance ** 0.5
        if std_dev < 1e-6:
            return 0.0
        z_score = (current_residual - mean) / std_dev
        return round(float(z_score), 2)



def get_sofr_curve(target_date):
    """
    Bootstrap a Piecewise Log-Linear Discount Curve using ONLY
    the rates for the specific target_date.
    """
    # 1. Fetch ONLY the rates for the specific date and index
    rates_qs = HistoricalRate.objects.filter(
        date=target_date, index_name="SOFR"
    )

    if not rates_qs.exists():
        return None

    # Convert to DataFrame for easier QuantLib iteration
    df = pd.DataFrame(list(rates_qs.values("tenor", "rate")))

    # 2. Global QuantLib Settings: Define the evaluation date for bootstrapping
    ql_date = ql.Date(target_date.day, target_date.month, target_date.year)
    ql.Settings.instance().evaluationDate = ql_date

    # 3. Build Rate Helpers: Map market tenors (1Y, 5Y, etc.) to SOFR OIS conventions
    helpers = []
    for _, row in df.iterrows():
        helpers.append(
            ql.SwapRateHelper(
                ql.QuoteHandle(ql.SimpleQuote(row["rate"])),
                ql.Period(row["tenor"]),
                ql.UnitedStates(ql.UnitedStates.Settlement),
                ql.Annual,
                ql.Unadjusted,
                ql.Actual360(),
                ql.Sofr(),
            )
        )

    # 4. Bootstrap and return the mathematical YieldTermStructure
    return ql.PiecewiseLogLinearDiscount(
        0, ql.UnitedStates(ql.UnitedStates.Settlement), helpers, ql.Actual360()
    )


def calculate_trade_npv(trade_id, curve):
    """
    Calculate NPV with support for Forward Starting Swaps.
    """
    if not curve:
        return 0.0

    # 1. Retrieve trade parameters
    trade = Trade.objects.get(id=trade_id)
    notional = float(trade.notional)
    fixed_rate = trade.fixed_rate / 100.0
    tenor = ql.Period(trade.tenor_years, ql.Years)

    # 2. Determine Trade Direction
    side = (
        ql.VanillaSwap.Payer
        if trade.side == "PAY"
        else ql.VanillaSwap.Receiver
    )

    # 3. Instrument Setup
    calendar = ql.UnitedStates(ql.UnitedStates.Settlement)
    curve_handle = ql.RelinkableYieldTermStructureHandle(curve)
    index = ql.Sofr(curve_handle)

    # --- TIME LOGIC ---

    # A. Get the Curve's Reference Date (Spot Date)
    ref_date = curve.referenceDate()

    # B. Calculate Effective Date (Start Date)
    # Shift the start date by the forward delay (e.g., +1 Year)
    # Use Days for precision with floats (0.25 years approx 91 days)
    delay_days = int(trade.forward_start * 365)
    effective_date = calendar.advance(
        ref_date, delay_days, ql.Days, ql.ModifiedFollowing
    )

    # C. Calculate Maturity Date
    # Maturity is calculated from the EFFECTIVE date, not reference date.
    # i.e A 5Y swap starting in 1Y matures at T + 6Y.
    maturity_date = effective_date + tenor

    # 4. Generate Payment Schedules
    fixed_schedule = ql.Schedule(
        effective_date,
        maturity_date,
        ql.Period(ql.Annual),
        calendar,
        ql.ModifiedFollowing,
        ql.ModifiedFollowing,
        ql.DateGeneration.Forward,
        False,
    )

    floating_schedule = ql.Schedule(
        effective_date,
        maturity_date,
        ql.Period(ql.Annual),
        calendar,
        ql.ModifiedFollowing,
        ql.ModifiedFollowing,
        ql.DateGeneration.Forward,
        False,
    )

    # 5. Build and Price
    swap = ql.VanillaSwap(
        side,
        notional,
        fixed_schedule,
        fixed_rate,
        ql.Actual360(),
        floating_schedule,
        index,
        0.0,
        ql.Actual360(),
    )

    swap.setPricingEngine(ql.DiscountingSwapEngine(curve_handle))

    # 6. Persist
    npv = swap.NPV()
    trade.last_npv = npv
    trade.save()

    return npv


def get_histogram_data(index_name="SOFR", tenor="1Y", bins=15):
    """
    Groups historical rates into frequency bins.
    """
    # 1. Pull historical rates for the specific index/tenor
    rates = HistoricalRate.objects.filter(
        index_name=index_name, tenor=tenor
    ).values_list("rate", flat=True)

    if not rates or len(rates) < 2:
        return [], []

    # 2. Use Numpy to create the histogram (counts per bin and bin edges)
    counts, bin_edges = np.histogram(rates, bins=bins)

    # 3. Create labels using the midpoint of each bin (formatted as %)
    labels = []
    for i in range(len(counts)):
        midpoint = (bin_edges[i] + bin_edges[i + 1]) / 2
        labels.append(f"{midpoint*100:.2f}%")

    return labels, counts.tolist()


def get_forward_histogram_data(index_name="SOFR", bins=15):
    """
    Calculates the historical frequency of the 1y1y Forward Rate.
    Reduced bins=15 for cleaner visual presentation.
    """
    # 1. Fetch the raw ingredients (Spot 1Y and Spot 2Y)
    qs_1y = HistoricalRate.objects.filter(
        index_name=index_name, tenor="1Y"
    ).values("date", "rate")
    qs_2y = HistoricalRate.objects.filter(
        index_name=index_name, tenor="2Y"
    ).values("date", "rate")

    # 2. Align Data
    df1 = (
        pd.DataFrame(list(qs_1y))
        .set_index("date")
        .rename(columns={"rate": "z1"})
    )
    df2 = (
        pd.DataFrame(list(qs_2y))
        .set_index("date")
        .rename(columns={"rate": "z2"})
    )

    df = df1.join(df2, how="inner")

    if df.empty:
        return [], [], 0, "0.00"

    # 3. Calculate Forward Rate
    df["fwd"] = (((1 + df["z2"]) ** 2) / (1 + df["z1"])) - 1

    # 4. Histogram Binning (Consolidated)
    data_points = df["fwd"].values * 100
    # NumPy automatically handles the bin distribution
    counts, bin_edges = np.histogram(data_points, bins=bins)

    # 5. Format Labels (2 decimal places)
    labels = []
    for i in range(len(counts)):
        midpoint = (bin_edges[i] + bin_edges[i + 1]) / 2
        labels.append(f"{midpoint:.2f}%")

    # 6. Statistics
    sample_size = len(df)
    mean_val = f"{np.mean(data_points):.2f}"

    return labels, counts.tolist(), sample_size, mean_val


def get_forward_term_structure(curve, max_years=10):
    """
    Calculates the 'Forward Curve': A series of 1-Year rates
    starting 1, 2, 3... years into the future.

    Returns: labels ['1Y1Y', '2Y1Y'...], values [4.5, 4.7...]
    """
    if not curve:
        return [], []

    calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
    day_count = ql.Actual360()
    ref_date = curve.referenceDate()

    labels = []
    rates = []

    # Loop: Calculate the 1-Year rate starting at year i
    # 0y1y is Spot. We start at 1y1y (Year 1 to Year 2).
    for i in range(0, max_years):
        start_dist = i
        end_dist = i + 1

        # Advance dates
        d1 = calendar.advance(ref_date, ql.Period(start_dist, ql.Years))
        d2 = calendar.advance(ref_date, ql.Period(end_dist, ql.Years))

        # Calculate Forward Rate
        fwd = curve.forwardRate(
            d1, d2, day_count, ql.Compounded, ql.Annual
        ).rate()

        # Label: "0y1y" (Spot), "1y1y", "2y1y"
        labels.append(f"{i}y1y")
        rates.append(fwd * 100)  # Percent

    return labels, rates

