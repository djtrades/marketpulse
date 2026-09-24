"""
Global Stock Markets, Macro Indicators & Gift Nifty Calculator
Fetches real-time / overnight market indices, commodities, and yields.
Calculates implied Gift Nifty opening cues.
"""

from typing import Dict, Any, List
import requests
import certifi

def fetch_symbol_quote(symbol: str) -> Dict[str, Any]:
    """
    Fetches regular market price, previous close, and percentage change from Yahoo Finance API.
    """
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        resp = requests.get(url, headers=headers, verify=certifi.where(), timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            meta = data["chart"]["result"][0]["meta"]
            price = meta.get("regularMarketPrice", 0.0)
            prev = meta.get("chartPreviousClose") or meta.get("previousClose") or price
            chg = price - prev
            pct = (chg / prev * 100.0) if prev else 0.0
            return {
                "symbol": symbol,
                "price": round(price, 2),
                "change": round(chg, 2),
                "pct_change": round(pct, 2),
                "is_positive": (pct >= 0)
            }
    except Exception as e:
        pass
    
    # Graceful fallback default
    return {
        "symbol": symbol,
        "price": 0.0,
        "change": 0.0,
        "pct_change": 0.0,
        "is_positive": True
    }


def fetch_global_market_snapshot(nifty_spot: float = 24900.0) -> Dict[str, Any]:
    """
    Collects full global market snapshot across US, Asia, Europe, Commodities, and FX.
    """
    # 1. US Markets
    dow = fetch_symbol_quote("^DJI")
    sp500 = fetch_symbol_quote("^GSPC")
    nasdaq = fetch_symbol_quote("^NDX")
    if nasdaq["price"] == 0:
        nasdaq = fetch_symbol_quote("^IXIC")

    # 2. Asian Markets (Live at 8:00 AM IST)
    nikkei = fetch_symbol_quote("^N225")
    hangseng = fetch_symbol_quote("^HSI")
    shanghai = fetch_symbol_quote("000001.SS")
    kospi = fetch_symbol_quote("^KS11")

    # 3. European Markets (Previous Close)
    dax = fetch_symbol_quote("^GDAXI")
    ftse = fetch_symbol_quote("^FTSE")

    # 4. Commodities & Macro
    brent = fetch_symbol_quote("BZ=F")
    us10y = fetch_symbol_quote("^TNX")
    dxy = fetch_symbol_quote("DX-Y.NYB")
    usdinr = fetch_symbol_quote("USDINR=X")
    vix = fetch_symbol_quote("^INDIAVIX")

    # 5. Gift Nifty / Implied Nifty Open Calculation
    # Weighted overnight impulse: 40% US Tech (Nasdaq), 30% Asian Momentum (Nikkei/Hang Seng), 30% S&P 500
    asia_avg_pct = (nikkei["pct_change"] + (hangseng["pct_change"] if hangseng["pct_change"] != 0 else 0.2)) / 2.0
    global_cue_pct = (0.35 * nasdaq["pct_change"]) + (0.30 * sp500["pct_change"]) + (0.35 * asia_avg_pct)
    
    # Dampen extreme anomalies for sanity
    global_cue_pct = max(-2.5, min(2.5, global_cue_pct))
    
    implied_gap_pts = round(nifty_spot * (global_cue_pct / 100.0), 1)
    gift_nifty_est = round(nifty_spot + implied_gap_pts, 1)

    if implied_gap_pts > 40:
        gap_type = "SIGNIFICANT GAP-UP"
        gap_color = "emerald"
    elif implied_gap_pts > 15:
        gap_type = "MILD GAP-UP"
        gap_color = "emerald"
    elif implied_gap_pts < -40:
        gap_type = "SIGNIFICANT GAP-DOWN"
        gap_color = "rose"
    elif implied_gap_pts < -15:
        gap_type = "MILD GAP-DOWN"
        gap_color = "rose"
    else:
        gap_type = "FLAT / NEUTRAL OPEN"
        gap_color = "amber"

    # Macro Sentiment Tagging for India
    brent_sentiment = "Favorable (Cooling)" if brent["pct_change"] <= 0 else "Caution (Rising Fuel Costs)"
    us10y_sentiment = "Positive for EM Inflows" if us10y["pct_change"] <= 0 else "Yield Pressure on Tech/EM"
    dxy_sentiment = "Supportive for INR" if dxy["pct_change"] <= 0 else "Dollar Strength Headwind"

    return {
        "gift_nifty": {
            "estimated_price": gift_nifty_est,
            "gap_points": implied_gap_pts,
            "gap_pct": round(global_cue_pct, 2),
            "gap_type": gap_type,
            "gap_color": gap_color
        },
        "us_markets": {
            "dow": dow,
            "sp500": sp500,
            "nasdaq": nasdaq,
            "summary": "Tech-led strength across Wall Street overnight." if nasdaq["pct_change"] > 0 else "Tech consolidation observed in US trading."
        },
        "asian_markets": {
            "nikkei": nikkei,
            "hangseng": hangseng,
            "shanghai": shanghai,
            "kospi": kospi,
            "summary": "Green momentum dominating morning Asian equity trade." if asia_avg_pct > 0 else "Mixed to defensive posture in Asian trade."
        },
        "european_markets": {
            "dax": dax,
            "ftse": ftse
        },
        "macro": {
            "brent": brent,
            "brent_sentiment": brent_sentiment,
            "us10y": us10y,
            "us10y_sentiment": us10y_sentiment,
            "dxy": dxy,
            "dxy_sentiment": dxy_sentiment,
            "usdinr": usdinr,
            "vix": vix
        }
    }
