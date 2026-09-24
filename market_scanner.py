#!/usr/bin/env python3
"""
Nifty Pre-Market Pulse - Master Orchestrator & Scanner
Runs daily around 07:50 - 08:00 AM IST.
Collects data, runs derivative analysis, compiles the morning POV, and generates index.html.
"""

import os
import sys
import datetime
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from modules.nse_client import fetch_nifty_option_chain
from modules.global_markets import fetch_global_market_snapshot
from modules.news_classifier import fetch_market_news
from modules.institutional import fetch_institutional_flows
from modules.pov_engine import generate_morning_pov
from modules.html_renderer import render_html_dashboard


def main():
    now_ist = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=5, minutes=30)))
    date_str = now_ist.strftime("%A, %d %b %Y")
    time_str = now_ist.strftime("%H:%M:%S")

    print(f"\n==================================================")
    print(f"  NIFTY PRE-MARKET SCANNER (8:00 AM IST RUNNER)   ")
    print(f"  Session Date: {date_str} | Time: {time_str} IST")
    print(f"==================================================\n")

    # 1. Fetch Option Chain & Derivatives Data
    print("⏳ [1/5] Fetching NSE Nifty Weekly Expiry Option Chain...")
    option_data = fetch_nifty_option_chain()
    print(f"   -> Spot: {option_data['spot_price']:,} | Expiry: {option_data['expiry_date']}")
    print(f"   -> PCR: {option_data['total_pcr']} | Max Pain: {option_data['max_pain']:,}")
    print(f"   -> Total Put OI Chg: {'+' if option_data['tot_put_chg_lakhs'] >= 0 else ''}{option_data['tot_put_chg_lakhs']}L | Call OI Chg: {'+' if option_data['tot_call_chg_lakhs'] >= 0 else ''}{option_data['tot_call_chg_lakhs']}L")

    # 2. Fetch Global Markets & Macro Cues
    print("\n⏳ [2/5] Fetching Global Markets & Macro Indicators...")
    global_data = fetch_global_market_snapshot(nifty_spot=option_data["spot_price"])
    gift = global_data["gift_nifty"]
    print(f"   -> Gift Nifty Implied Open: {gift['estimated_price']:,} ({gift['gap_points']:+0.1f} pts / {gift['gap_pct']:+0.2f}%)")
    print(f"   -> US Nasdaq: {global_data['us_markets']['nasdaq']['pct_change']:+0.2f}% | Nikkei: {global_data['asian_markets']['nikkei']['pct_change']:+0.2f}%")
    print(f"   -> Brent Crude: ${global_data['macro']['brent']['price']} | US 10Y: {global_data['macro']['us10y']['price']}%")

    # 3. Fetch Institutional Flows (FII / DII)
    print("\n⏳ [3/5] Fetching Institutional Cash & Derivative Flows...")
    inst_data = fetch_institutional_flows()
    print(f"   -> FII Cash: {inst_data['fii_net_cr']} Cr | DII Cash: +{inst_data['dii_net_cr']} Cr")
    print(f"   -> Combined Net: {inst_data['combined_net_cr']:+0.1f} Cr | FII Long Futures: {inst_data['fii_long_pct']}%")

    # 4. Fetch Market Moving News & Sector Catalysts
    print("\n⏳ [4/5] Aggregating & Classifying Market-Moving News...")
    news_items = fetch_market_news()
    print(f"   -> Curated {len(news_items)} market news headlines with direct Nifty impact.")

    # 5. Synthesize POV & Tactical Battleplan
    print("\n⏳ [5/5] Synthesizing Morning Point-of-View & Tactical Battleplan...")
    pov_data = generate_morning_pov(option_data, global_data, inst_data)
    print(f"   -> Stance: {pov_data['stance']} (Confidence: {pov_data['confidence_pct']}%)")
    print(f"   -> Pivot: {pov_data['pivot_level']:,} | Max Pain: {pov_data['max_pain']:,}")

    # Render HTML Dashboard
    payload = {
        "runtime": {
            "date": date_str,
            "timestamp": time_str
        },
        "option_chain": option_data,
        "global_markets": global_data,
        "institutional": inst_data,
        "news": news_items,
        "pov": pov_data
    }

    html_content = render_html_dashboard(payload)

    # Save to index.html and dist/index.html (for GitHub Pages deployment)
    output_path = BASE_DIR / "index.html"
    dist_dir = BASE_DIR / "dist"
    dist_dir.mkdir(exist_ok=True)
    dist_path = dist_dir / "index.html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    with open(dist_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ SUCCESS! Dashboard successfully generated:")
    print(f"   -> {output_path}")
    print(f"   -> {dist_path}")
    print(f"\n==================================================\n")


if __name__ == "__main__":
    main()
