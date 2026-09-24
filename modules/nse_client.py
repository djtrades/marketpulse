"""
NSE India Option Chain Client & Derivatives Analytics Engine
Fetches live weekly expiry option chain data from NSE API using curl_cffi stealth session.
Calculates PCR, Max Pain, ATM Straddle expected range, OI Walls, and strike distributions.
"""

import math
from typing import Dict, Any, List

def fetch_nifty_option_chain() -> Dict[str, Any]:
    """
    Fetches the live weekly option chain for Nifty 50 from NSE India.
    Returns parsed metrics including Spot, PCR, Max Pain, Key Walls, and Strike Ladder.
    """
    try:
        from curl_cffi import requests as cureq
        
        session = cureq.Session(impersonate="chrome120")
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        })
        
        # Handshake with NSE homepage to obtain session cookies
        session.get("https://www.nseindia.com", timeout=12)
        
        # 1. Fetch Contract Info for Nifty Expiry Dates
        contract_info_resp = session.get(
            "https://www.nseindia.com/api/option-chain-contract-info?symbol=NIFTY",
            timeout=10
        )
        if contract_info_resp.status_code != 200:
            raise RuntimeError(f"Contract info returned HTTP {contract_info_resp.status_code}")
            
        contract_info = contract_info_resp.json()
        expiry_dates = contract_info.get("expiryDates", [])
        if not expiry_dates:
            raise RuntimeError("No expiry dates found in NSE contract info")
            
        nearest_expiry = expiry_dates[0]
        
        # 2. Fetch Option Chain V3 for the nearest weekly expiry
        oc_url = f"https://www.nseindia.com/api/option-chain-v3?type=Indices&symbol=NIFTY&expiry={nearest_expiry}"
        oc_resp = session.get(oc_url, timeout=12)
        if oc_resp.status_code != 200:
            raise RuntimeError(f"Option chain v3 returned HTTP {oc_resp.status_code}")
            
        payload = oc_resp.json()
        records = payload.get("records", {})
        spot_price = float(records.get("underlyingValue", 0.0))
        timestamp = records.get("timestamp", "Today")
        raw_data = records.get("data", [])
        
        if not raw_data or spot_price <= 0:
            raise RuntimeError("Invalid underlying value or empty data array from NSE")
            
        return parse_option_chain_data(raw_data, spot_price, nearest_expiry, timestamp, is_simulated=False)

    except Exception as e:
        print(f"[WARN] NSE Live Fetch Failed ({e}). Falling back to cached / fallback simulation.")
        return generate_fallback_option_chain()


def parse_option_chain_data(raw_data: List[Dict], spot_price: float, expiry_date: str, timestamp: str, is_simulated: bool = False) -> Dict[str, Any]:
    """
    Parses raw NSE option chain data, computes derivatives indicators, Max Pain, and strike ladder.
    """
    atm_strike = round(spot_price / 50.0) * 50
    
    strikes = []
    tot_call_oi = 0
    tot_put_oi = 0
    tot_call_change_oi = 0
    tot_put_change_oi = 0
    
    ce_map = {}
    pe_map = {}
    
    for item in raw_data:
        sp = item.get("strikePrice")
        if not sp:
            continue
        strikes.append(sp)
        
        if "CE" in item:
            ce = item["CE"]
            coi = float(ce.get("openInterest", 0) or 0)
            cchg = float(ce.get("changeinOpenInterest", 0) or 0)
            tot_call_oi += coi
            tot_call_change_oi += cchg
            ce_map[sp] = ce
            
        if "PE" in item:
            pe = item["PE"]
            poi = float(pe.get("openInterest", 0) or 0)
            pchg = float(pe.get("changeinOpenInterest", 0) or 0)
            tot_put_oi += poi
            tot_put_change_oi += pchg
            pe_map[sp] = pe

    # 1. Total Put-Call Ratio
    total_pcr = round(tot_put_oi / tot_call_oi, 2) if tot_call_oi > 0 else 1.0

    # 2. ATM PCR (+/- 150 points around ATM)
    atm_strikes_range = [atm_strike - 150, atm_strike - 100, atm_strike - 50, atm_strike, atm_strike + 50, atm_strike + 100, atm_strike + 150]
    atm_put_oi = sum(pe_map.get(s, {}).get("openInterest", 0) for s in atm_strikes_range)
    atm_call_oi = sum(ce_map.get(s, {}).get("openInterest", 0) for s in atm_strikes_range)
    atm_pcr = round(atm_put_oi / atm_call_oi, 2) if atm_call_oi > 0 else total_pcr

    # 3. Max Pain Calculation
    unique_strikes = sorted(list(set(strikes)))
    min_loss = float("inf")
    max_pain_strike = atm_strike
    
    for test_strike in unique_strikes:
        total_payout = 0
        for s in unique_strikes:
            call_oi = ce_map.get(s, {}).get("openInterest", 0) or 0
            put_oi = pe_map.get(s, {}).get("openInterest", 0) or 0
            if test_strike > s:
                total_payout += call_oi * (test_strike - s)
            elif test_strike < s:
                total_payout += put_oi * (s - test_strike)
                
        if total_payout < min_loss:
            min_loss = total_payout
            max_pain_strike = test_strike

    # 4. Support and Resistance Walls (Highest & 2nd Highest OI)
    sorted_call_strikes = sorted(ce_map.keys(), key=lambda s: ce_map[s].get("openInterest", 0) or 0, reverse=True)
    sorted_put_strikes = sorted(pe_map.keys(), key=lambda s: pe_map[s].get("openInterest", 0) or 0, reverse=True)
    
    major_res_r2 = sorted_call_strikes[0] if sorted_call_strikes else (atm_strike + 100)
    imm_res_r1 = sorted_call_strikes[1] if len(sorted_call_strikes) > 1 else (atm_strike + 50)
    
    major_supp_s2 = sorted_put_strikes[0] if sorted_put_strikes else (atm_strike - 100)
    imm_supp_s1 = sorted_put_strikes[1] if len(sorted_put_strikes) > 1 else (atm_strike - 50)

    # 5. Max Additions (Fresh writing)
    max_call_add_strike = max(ce_map.keys(), key=lambda s: ce_map[s].get("changeinOpenInterest", 0) or 0)
    max_put_add_strike = max(pe_map.keys(), key=lambda s: pe_map[s].get("changeinOpenInterest", 0) or 0)
    
    max_call_add_val = ce_map[max_call_add_strike].get("changeinOpenInterest", 0)
    max_put_add_val = pe_map[max_put_add_strike].get("changeinOpenInterest", 0)

    # 6. ATM Straddle & Expected Trading Range
    atm_call_ltp = float(ce_map.get(atm_strike, {}).get("lastPrice", 0) or 0)
    atm_put_ltp = float(pe_map.get(atm_strike, {}).get("lastPrice", 0) or 0)
    straddle_price = round(atm_call_ltp + atm_put_ltp, 1)
    if straddle_price <= 10.0:  # Fallback if outside trading hours or zero
        straddle_price = round(spot_price * 0.009, 1) # ~0.9% daily straddle
        
    expected_low = round(spot_price - straddle_price)
    expected_high = round(spot_price + straddle_price)

    # 7. Visual Strike Ladder (Filter around ATM: -300 to +300 points)
    ladder_strikes = [s for s in unique_strikes if abs(s - atm_strike) <= 300]
    if len(ladder_strikes) < 7:
        ladder_strikes = [atm_strike + (i * 50) for i in range(-5, 6)]
        
    strike_ladder = []
    max_bar_oi = 1
    
    for s in ladder_strikes:
        c_oi = ce_map.get(s, {}).get("openInterest", 0) or 0
        p_oi = pe_map.get(s, {}).get("openInterest", 0) or 0
        if c_oi > max_bar_oi: max_bar_oi = c_oi
        if p_oi > max_bar_oi: max_bar_oi = p_oi

    for s in sorted(ladder_strikes, reverse=True):
        c_item = ce_map.get(s, {})
        p_item = pe_map.get(s, {})
        
        c_oi = c_item.get("openInterest", 0) or 0
        p_oi = p_item.get("openInterest", 0) or 0
        c_chg = c_item.get("changeinOpenInterest", 0) or 0
        p_chg = p_item.get("changeinOpenInterest", 0) or 0
        
        strike_ladder.append({
            "strike": s,
            "is_atm": (s == atm_strike),
            "call_oi_lakhs": round(c_oi / 100000.0, 1),
            "put_oi_lakhs": round(p_oi / 100000.0, 1),
            "call_chg_lakhs": round(c_chg / 100000.0, 1),
            "put_chg_lakhs": round(p_chg / 100000.0, 1),
            "call_bar_pct": min(100, int((c_oi / max_bar_oi) * 100)) if max_bar_oi > 0 else 10,
            "put_bar_pct": min(100, int((p_oi / max_bar_oi) * 100)) if max_bar_oi > 0 else 10,
            "call_ltp": c_item.get("lastPrice", 0),
            "put_ltp": p_item.get("lastPrice", 0),
        })

    # Sentiment interpretation of PCR
    if total_pcr >= 1.30:
        pcr_stance = "Bullish / Overbought Warning"
        pcr_badge_color = "emerald"
    elif total_pcr >= 1.05:
        pcr_stance = "Mildly Bullish (Put Writers in Charge)"
        pcr_badge_color = "emerald"
    elif total_pcr >= 0.85:
        pcr_stance = "Neutral / Rangebound"
        pcr_badge_color = "amber"
    else:
        pcr_stance = "Bearish / Oversold Bounce Zone"
        pcr_badge_color = "rose"

    # 8. Dynamic Expiry Day and Days to Expiry Calculation
    try:
        import datetime
        now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30))).date()
        exp_dt = datetime.datetime.strptime(expiry_date, "%d-%b-%Y").date()
        days_to_exp = (exp_dt - now_ist).days
        exp_weekday = exp_dt.strftime("%A")
        is_expiry_today = (days_to_exp == 0)
    except Exception:
        days_to_exp = 0
        exp_weekday = "Tuesday"
        is_expiry_today = False

    return {
        "status": "LIVE" if not is_simulated else "SIMULATED_FALLBACK",
        "spot_price": round(spot_price, 2),
        "atm_strike": atm_strike,
        "expiry_date": expiry_date,
        "expiry_weekday": exp_weekday,
        "days_to_expiry": max(0, days_to_exp),
        "is_expiry_today": is_expiry_today,
        "timestamp": timestamp,
        "total_pcr": total_pcr,
        "atm_pcr": atm_pcr,
        "pcr_stance": pcr_stance,
        "pcr_badge_color": pcr_badge_color,
        "max_pain": max_pain_strike,
        "r2_major_call_wall": major_res_r2,
        "r2_call_oi_lakhs": round(ce_map.get(major_res_r2, {}).get("openInterest", 0) / 100000.0, 1),
        "r1_imm_res": imm_res_r1,
        "s2_major_put_wall": major_supp_s2,
        "s2_put_oi_lakhs": round(pe_map.get(major_supp_s2, {}).get("openInterest", 0) / 100000.0, 1),
        "s1_imm_supp": imm_supp_s1,
        "max_call_add_strike": max_call_add_strike,
        "max_call_add_lakhs": round(max_call_add_val / 100000.0, 1),
        "max_put_add_strike": max_put_add_strike,
        "max_put_add_lakhs": round(max_put_add_val / 100000.0, 1),
        "straddle_price": straddle_price,
        "expected_range_low": expected_low,
        "expected_range_high": expected_high,
        "strike_ladder": strike_ladder
    }


def generate_fallback_option_chain() -> Dict[str, Any]:
    """
    Fallback data generator with realistic Nifty derivative levels when NSE API is blocked/offline.
    """
    spot = 24900.0
    atm = 24900
    expiry = "Current Weekly Expiry"
    
    strikes = [24600, 24700, 24800, 24850, 24900, 24950, 25000, 25050, 25100, 25200]
    raw_data = []
    
    for s in strikes:
        diff = s - atm
        ce_oi = int(max(15000, 80000 + (diff * 80) if diff > 0 else 40000 - (diff * 20)))
        pe_oi = int(max(15000, 95000 - (diff * 85) if diff < 0 else 35000 + (diff * 15)))
        raw_data.append({
            "strikePrice": s,
            "CE": {"openInterest": ce_oi, "changeinOpenInterest": int(ce_oi * 0.15), "lastPrice": max(5.0, 140 - diff * 0.6)},
            "PE": {"openInterest": pe_oi, "changeinOpenInterest": int(pe_oi * 0.22), "lastPrice": max(5.0, 120 + diff * 0.6)}
        })
        
    return parse_option_chain_data(raw_data, spot, expiry, "Market Snapshot (Offline Mode)", is_simulated=True)
