# curves.py - LAYER 1 CORE: PIECEWISE CONTINUOUS LOG-LINEAR YIELD BOOTSTRAPPER
import json
import numpy as np
import pandas as pd
import QuantLib as ql
from utils import DataSanitizer

class BootstrappedDiscountCurve:
    """
    Ingests raw point-source spot rates, sanitizes non-standard tenor tokens, 
    and wraps native QuantLib C++ loaders to build a continuous piecewise log-linear yield structure.
    """
    def __init__(self, target_date, spot_rates_dict, currency="USD"):
        self.target_date_str = DataSanitizer.normalize_date_string(target_date)
        self.currency = str(currency).upper().strip()
        
        # 1. Map global institutional asset conventions and specific settlement calendars
        self.registry = {
            "USD": {"calendar": ql.UnitedStates(ql.UnitedStates.GovernmentBond), "day_count": ql.Actual360(), "index": ql.Sofr},
            "EUR": {"calendar": ql.TARGET(), "day_count": ql.Actual360(), "index": ql.Euribor3M},
            "GBP": {"calendar": ql.UnitedKingdom(ql.UnitedKingdom.Exchange), "day_count": ql.Actual365Fixed(), "index": ql.Sonia},
            "JPY": {"calendar": ql.Japan(), "day_count": ql.Actual360(), "index": ql.Tona},
            "CHF": {"calendar": ql.Switzerland(), "day_count": ql.Actual360(), "index": ql.Saron},
            "NOK": {"calendar": ql.Norway(), "day_count": ql.Actual360(), "index": lambda: ql.IborIndex("Nowa", ql.Period(3, ql.Months), 2, ql.CHFCurrency(), ql.Norway(), ql.ModifiedFollowing, False, ql.Actual360())},
            "SEK": {"calendar": ql.Sweden(), "day_count": ql.Actual360(), "index": lambda: ql.IborIndex("Stibor", ql.Period(3, ql.Months), 2, ql.EURCurrency(), ql.Sweden(), ql.ModifiedFollowing, False, ql.Actual360())},
            "ZAR": {"calendar": ql.SouthAfrica(), "day_count": ql.Actual365Fixed(), "index": lambda: ql.IborIndex("Jibar", ql.Period(3, ql.Months), 2, ql.ZARCurrency(), ql.SouthAfrica(), ql.ModifiedFollowing, False, ql.Actual365Fixed())}
        }
        
        meta = self.registry.get(self.currency, self.registry["USD"])
        self.calendar = meta["calendar"]
        self.day_counter = meta["day_count"]
        self.base_index = meta["index"]() if not callable(meta["index"]) else meta["index"]()
        
        # 2. Set evaluation date anchor in the native C++ singleton engine
        y, m, d = map(int, self.target_date_str.split('-'))
        self.ql_eval_date = ql.Date(d, m, y)
        ql.Settings.instance().evaluationDate = self.ql_eval_date
        
        # 3. Boot the piecewise continuous term assembler
        self.ql_curve = self._bootstrap_curve(spot_rates_dict)

    def _bootstrap_curve(self, spot_rates_dict):
        settlement_days = 2
        rate_helpers = []
        
        for raw_tenor, rate_val in spot_rates_dict.items():
            clean_rate = float(rate_val)
            if clean_rate <= 0.0:
                continue  # Filter missing gaps/liquidity drops to protect matrix solver
                
            quote_handle = ql.QuoteHandle(ql.SimpleQuote(clean_rate / 100.0 if clean_rate > 1.0 else clean_rate))
            clean_tenor_str = DataSanitizer.clean_tenor_string(raw_tenor)
            
            # Map clean token string variables to explicit C++ Period dimensions
            if 'M' in clean_tenor_str:
                period = ql.Period(int(clean_tenor_str.replace('M', '')), ql.Months)
            else:
                period = ql.Period(int(clean_tenor_str.replace('Y', '')), ql.Years)
                
            # Direct nodes to relevant interbank short-term or term structural helpers
            if clean_tenor_str == "3M" and self.currency not in ["GBP", "ZAR"]:
                helper = ql.DepositRateHelper(quote_handle, period, settlement_days, self.calendar, 
                                             ql.ModifiedFollowing, False, self.day_counter)
            else:
                helper = ql.SwapRateHelper(quote_handle, period, self.calendar, ql.Annual, 
                                          ql.Unadjusted, self.day_counter, self.base_index)
            rate_helpers.append(helper)
            
        if not rate_helpers:
            raise ValueError(f"Bootstrapping failed: Data vectors for {self.currency} on {self.target_date_str} are completely null.")
            
        curve_settlement_date = self.calendar.advance(self.ql_eval_date, ql.Period(settlement_days, ql.Days))
        
        # Enforce strict log-linear continuous interpolation over discount factors
        return ql.PiecewiseLogLinearDiscount(curve_settlement_date, rate_helpers, self.day_counter)

    def get_discount_factor(self, maturity_years):
        """
        Calculates a continuous discount factor target using raw year float coordinates.
        """
        target_date = self.ql_eval_date + ql.Period(int(float(maturity_years) * 365.25), ql.Days)
        return self.ql_curve.discount(target_date)

    def get_zero_rate(self, maturity_years):
        """
        Extracts continuous zero-coupon rates for yield curve plotting panels.
        """
        return self.ql_curve.zeroRate(float(maturity_years), ql.Continuous, ql.Annual).rate() * 100.0
