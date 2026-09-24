"""
Global Stock Markets, Macro Indicators & Live Gift Nifty Fetcher
Fetches real-time / overnight market indices, commodities, and yields.
Directly fetches live Gift Nifty quotes from financial price feeds.
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


def build_gift_nifty_dict(price: float, gap_pts: float, gap_pct: float, is_live: bool = True) -> Dict[str, Any]:
    if gap_pts > 40:
        gap_type = "SIGNIFICANT GAP-UP"
        gap_color = "emerald"
    elif gap_pts > 15:
        gap_type = "MILD GAP-UP"
        gap_color = "emerald"
    elif gap_pts < -40:
        gap_type = "SIGNIFICANT GAP-DOWN"
        gap_color = "rose"
    elif gap_pts < -15:
        gap_type = "MILD GAP-DOWN"
        gap_color = "rose"
    else:
        gap_type = "FLAT / NEUTRAL OPEN"
        gap_color = "amber"

    return {
        "estimated_price": round(price, 1),
        "gap_points": round(gap_pts, 1),
        "gap_pct": round(gap_pct, 2),
        "gap_type": gap_type,
        "gap_color": gap_color,
        "is_live": is_live
    }


def fetch_live_gift_nifty(nifty_spot: float) -> Dict[str, Any]:
    """
    Fetches the real-time traded price of Gift Nifty from live financial endpoints.
    Tries TradingView (NSEIX:NIFTY1!), Moneycontrol, and ET Markets live feeds.
    """
    # Source 1: TradingView Futures Scanner for GIFT NIFTY (Symbol: NSEIX:NIFTY1!)
    try:
        url = "https://scanner.tradingview.com/futures/scan"
        payload = {
            "symbols": {
                "tickers": ["NSEIX:NIFTY1!"],
                "query": {"types": []}
            },
            "columns": ["close", "change", "open", "high", "low"]
        }
        tv_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
            "Content-Type": "application/json",
            "Referer": "https://www.tradingview.com/"
        }
        resp = requests.post(url, json=payload, headers=tv_headers, verify=certifi.where(), timeout=6)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if data and len(data) > 0:
                vals = data[0].get("d", [])
                if vals and len(vals) > 0 and vals[0] and float(vals[0]) > 10000:
                    live_price = float(vals[0])
                    gap_pts = round(live_price - nifty_spot, 1)
                    gap_pct = round((gap_pts / nifty_spot * 100.0), 2) if nifty_spot else 0.0
                    return build_gift_nifty_dict(live_price, gap_pts, gap_pct, is_live=True)
    except Exception:
        pass

    # Source 2: TradingView Global Scanner fallback
    try:
        url = "https://scanner.tradingview.com/global/scan"
        payload = {
            "symbols": {
                "tickers": ["NSEIX:NIFTY1!"],
                "query": {"types": []}
            },
            "columns": ["close", "change"]
        }
        resp = requests.post(url, json=payload, headers={"User-Agent": "Mozilla/5.0"}, verify=certifi.where(), timeout=6)
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if data and len(data) > 0:
                vals = data[0].get("d", [])
                if vals and len(vals) > 0 and vals[0] and float(vals[0]) > 10000:
                    live_price = float(vals[0])
                    gap_pts = round(live_price - nifty_spot, 1)
                    gap_pct = round((gap_pts / nifty_spot * 100.0), 2) if nifty_spot else 0.0
                    return build_gift_nifty_dict(live_price, gap_pts, gap_pct, is_live=True)
    except Exception:
        pass

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.moneycontrol.com/"
    }

    # Source 3: Moneycontrol Direct Pricefeed for GIFT NIFTY (Symbol: in;NSX)
    try:
        url = "https://priceapi.moneycontrol.com/pricefeed/notapplicable/inidicesindia/in%3BNSX"
        resp = requests.get(url, headers=headers, verify=certifi.where(), timeout=5)
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            p_val = data.get("pricecurrent")
            if p_val:
                live_price = float(str(p_val).replace(",", "").strip())
                if live_price > 10000:
                    gap_pts = round(live_price - nifty_spot, 1)
                    gap_pct = round((gap_pts / nifty_spot * 100.0), 2) if nifty_spot else 0.0
                    return build_gift_nifty_dict(live_price, gap_pts, gap_pct, is_live=True)
    except Exception:
        pass

    # Source 4: Moneycontrol Technical Analysis Global Markets API
    try:
        url = "https://priceapi.moneycontrol.com/technicalAnalysisIndia/api/marketOverview/getGlobalMarketList?classic=true"
        resp = requests.get(url, headers=headers, verify=certifi.where(), timeout=5)
        if resp.status_code == 200:
            for item in resp.json().get("data", []):
                name = item.get("name", "").upper()
                if "GIFT" in name or "SGX" in name:
                    p_val = item.get("last_price")
                    if p_val:
                        live_price = float(str(p_val).replace(",", "").strip())
                        if live_price > 10000:
                            gap_pts = round(live_price - nifty_spot, 1)
                            gap_pct = round((gap_pts / nifty_spot * 100.0), 2) if nifty_spot else 0.0
                            return build_gift_nifty_dict(live_price, gap_pts, gap_pct, is_live=True)
    except Exception:
        pass

    # Source 5: ET Markets Global Indices API
    try:
        url = "https://etmarketsapis.indiatimes.com/ET_Stats/globalmarket"
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, verify=certifi.where(), timeout=5)
        if resp.status_code == 200:
            for row in resp.json().get("searchresult", []):
                cname = row.get("companyName", "").upper()
                if "GIFT" in cname or "SGX" in cname:
                    p_val = row.get("lastTradedPrice")
                    if p_val:
                        live_price = float(str(p_val).replace(",", "").strip())
                        if live_price > 10000:
                            gap_pts = round(live_price - nifty_spot, 1)
                            gap_pct = round((gap_pts / nifty_spot * 100.0), 2) if nifty_spot else 0.0
                            return build_gift_nifty_dict(live_price, gap_pts, gap_pct, is_live=True)
    except Exception:
        pass

    return None


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

    # 5. Gift Nifty - Fetch Real Live Traded Price
    gift_dict = fetch_live_gift_nifty(nifty_spot)
    asia_avg_pct = (nikkei["pct_change"] + (hangseng["pct_change"] if hangseng["pct_change"] != 0 else 0.2)) / 2.0
    
    if not gift_dict:
        # Fallback to implied calculation only if live APIs are completely unreachable
        global_cue_pct = (0.35 * nasdaq["pct_change"]) + (0.30 * sp500["pct_change"]) + (0.35 * asia_avg_pct)
        global_cue_pct = max(-2.5, min(2.5, global_cue_pct))
        implied_gap_pts = round(nifty_spot * (global_cue_pct / 100.0), 1)
        gift_price = round(nifty_spot + implied_gap_pts, 1)
        gift_dict = build_gift_nifty_dict(gift_price, implied_gap_pts, global_cue_pct, is_live=False)

    # Macro Sentiment Tagging for India
    brent_sentiment = "Favorable (Cooling)" if brent["pct_change"] <= 0 else "Caution (Rising Fuel Costs)"
    us10y_sentiment = "Positive for EM Inflows" if us10y["pct_change"] <= 0 else "Yield Pressure on Tech/EM"
    dxy_sentiment = "Supportive for INR" if dxy["pct_change"] <= 0 else "Dollar Strength Headwind"

    return {
        "gift_nifty": gift_dict,
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
