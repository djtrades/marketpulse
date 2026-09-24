"""
HTML Dashboard Renderer
Generates a responsive, standalone HTML dashboard with Tailwind CSS,
interactive strike ladder OI charts, and shareable morning briefing copy generator.
"""

from typing import Dict, Any

def render_html_dashboard(data: Dict[str, Any]) -> str:
    """
    Renders the complete self-contained HTML file from structured scanner data.
    """
    option = data["option_chain"]
    glob = data["global_markets"]
    news_list = data["news"]
    inst = data["institutional"]
    pov = data["pov"]
    runtime = data["runtime"]

    # Generate Strike Ladder HTML rows
    strike_rows_html = ""
    for row in option["strike_ladder"]:
        is_atm = row["is_atm"]
        atm_class = "bg-amber-950/20 border border-amber-500/30" if is_atm else ""
        badge = " <span class='text-[10px] text-amber-400 font-bold ml-1'>ATM</span>" if is_atm else ""
        
        strike_rows_html += f"""
        <div class="grid grid-cols-12 items-center gap-2 py-1 px-1.5 rounded-lg {atm_class}">
          <!-- Call OI Bar & Val -->
          <div class="col-span-5 flex justify-end items-center gap-2">
            <span class="text-slate-400 text-[10px] font-mono">{row['call_oi_lakhs']}L</span>
            <div class="w-24 sm:w-36 bg-slate-800/80 h-3.5 rounded-l overflow-hidden flex justify-end">
              <div class="bg-rose-500 h-full" style="width: {row['call_bar_pct']}%;"></div>
            </div>
          </div>
          
          <!-- Strike Price -->
          <div class="col-span-2 text-center font-bold text-slate-200 bg-slate-900/90 py-0.5 rounded border border-slate-800 font-mono text-xs">
            {row['strike']}{badge}
          </div>
          
          <!-- Put OI Bar & Val -->
          <div class="col-span-5 flex items-center gap-2">
            <div class="w-24 sm:w-36 bg-slate-800/80 h-3.5 rounded-r overflow-hidden">
              <div class="bg-emerald-500 h-full" style="width: {row['put_bar_pct']}%;"></div>
            </div>
            <span class="text-slate-400 text-[10px] font-mono">{row['put_oi_lakhs']}L</span>
          </div>
        </div>
        """

    # Generate News HTML cards
    news_cards_html = ""
    for n in news_list:
        news_cards_html += f"""
        <div class="bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 flex flex-col md:flex-row md:items-start justify-between gap-3">
          <div class="space-y-1.5 flex-1">
            <div class="flex items-center gap-2">
              <span class="px-2 py-0.5 rounded text-[10px] font-bold border {n['badge_class']}">{n['sentiment_tag']}</span>
              <span class="text-[11px] text-slate-500 font-mono">{n['source']}</span>
            </div>
            <h3 class="text-xs md:text-sm font-bold text-white leading-snug">{n['title']}</h3>
            <p class="text-xs text-slate-400 leading-relaxed">{n['description']}</p>
          </div>
          <div class="md:w-72 bg-slate-900/90 p-2.5 rounded-lg border border-slate-800 text-xs shrink-0">
            <span class="text-[10px] font-bold uppercase text-indigo-400 tracking-wider">Direct Nifty Impact:</span>
            <p class="text-slate-300 text-xs mt-0.5 font-medium">{n['nifty_impact']}</p>
          </div>
        </div>
        """

    # Generate Sector Watchlist HTML
    sector_cards_html = ""
    for s in inst["sector_watchlist"]:
        sector_cards_html += f"""
        <div class="p-2.5 rounded-xl bg-slate-950/70 border border-slate-800">
          <div class="flex items-center justify-between mb-1">
            <span class="font-bold text-xs text-white">{s['name']}</span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold border {s['badge_class']}">{s['status']}</span>
          </div>
          <p class="text-[11px] text-slate-400">{s['reason']}</p>
        </div>
        """

    # Generate Quick Copy Text for WhatsApp/Telegram
    copy_text = (
        f"🌅 NIFTY MORNING PULSE ({runtime['date']})\\n"
        f"• Stance: {pov['stance']}\\n"
        f"• Expected Open: {pov['expected_open_range']} (Gift Nifty: {glob['gift_nifty']['gap_points']:+0.1f} pts)\\n"
        f"• Range: {pov['expected_day_range']} | Pivot: {pov['pivot_level']:,}\\n"
        f"• PCR: {option['total_pcr']} | Max Pain: {option['max_pain']:,}\\n"
        f"• Put OI Chg: {'+' if option['tot_put_chg_lakhs'] >= 0 else ''}{option['tot_put_chg_lakhs']}L | Call OI Chg: {'+' if option['tot_call_chg_lakhs'] >= 0 else ''}{option['tot_call_chg_lakhs']}L\\n"
        f"• FII Cash: {inst['fii_net_cr']} Cr | DII: +{inst['dii_net_cr']} Cr\\n"
        f"Check full dashboard: "
    )

    # Dynamic Expiry Badges
    exp_day = option.get('expiry_weekday', 'Tuesday')
    days_left = option.get('days_to_expiry', 0)
    if option.get('is_expiry_today'):
        top_expiry_badge = f'<span class="text-[10px] font-bold px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-mono animate-pulse">🔥 EXPIRY TODAY ({exp_day.upper()})</span>'
        sec2_badge = f'<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse">🔥 EXPIRY TODAY ({exp_day.upper()})</span>'
    else:
        top_expiry_badge = f'<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono">EXPIRY: {option["expiry_date"]} ({exp_day}, {days_left}d left)</span>'
        sec2_badge = f'<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">{exp_day.upper()} WEEKLY EXPIRY</span>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nifty Pre-Market Pulse & Expiry Radar ({runtime['date']})</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }}
    .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: rgba(0, 0, 0, 0.05); }}
    ::-webkit-scrollbar-thumb {{ background: rgba(100, 116, 139, 0.3); border-radius: 4px; }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 antialiased min-h-screen p-3 sm:p-5 selection:bg-indigo-500 selection:text-white">

  <div class="max-w-7xl mx-auto space-y-6">

    <!-- ==================== HEADER & TOP TICKER ==================== -->
    <header class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 sm:p-5 shadow-2xl backdrop-blur-md">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div class="flex items-center gap-2.5 flex-wrap">
            <div class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
            <h1 class="text-xl sm:text-2xl font-black tracking-tight text-white flex items-center gap-2">
              NIFTY PRE-MARKET PULSE
              <span class="text-xs font-semibold px-2 py-0.5 rounded bg-indigo-600/30 text-indigo-300 border border-indigo-500/30">08:00 AM IST</span>
            </h1>
            {top_expiry_badge}
          </div>
          <p class="text-xs sm:text-sm text-slate-400 mt-1">
            Global Overnight Snapshot • NSE Option Chain Derivatives Matrix • Tactical Intraday Gameplan
          </p>
        </div>

        <!-- Meta Strip & Quick Share Button -->
        <div class="flex flex-wrap items-center gap-2.5 text-xs">
          <div class="bg-slate-950/70 px-3 py-1.5 rounded-lg border border-slate-800 font-mono text-slate-300">
            <span class="text-slate-500">Nifty Spot:</span> <span class="text-white font-bold">{option['spot_price']:,}</span>
          </div>
          <div class="bg-slate-950/70 px-3 py-1.5 rounded-lg border border-slate-800 font-mono text-slate-300">
            <span class="text-slate-500">Refreshed:</span> <span class="text-emerald-400 font-bold">{runtime['timestamp']} IST</span>
          </div>
          <button onclick="copyBriefing()" class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-3 py-1.5 rounded-lg transition shadow-md flex items-center gap-1.5 cursor-pointer">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
            <span id="copyBtnText">Copy Morning Brief</span>
          </button>
        </div>
      </div>

      <!-- Quick Ticker Strip -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mt-4 pt-1">
        <!-- Gift Nifty -->
        <div class="bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80">
          <div class="text-[11px] font-semibold text-slate-400 flex items-center justify-between">
            <span>GIFT NIFTY</span>
            <span class="text-emerald-400 font-mono text-[10px]">CUE</span>
          </div>
          <div class="text-base font-bold text-white font-mono mt-0.5">{glob['gift_nifty']['estimated_price']:,}</div>
          <div class="text-[11px] font-mono text-{glob['gift_nifty']['gap_color']}-400 font-semibold">
            {glob['gift_nifty']['gap_points']:+0.1f} pts ({glob['gift_nifty']['gap_pct']:+0.2f}%)
          </div>
        </div>

        <!-- India VIX -->
        <div class="bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80">
          <div class="text-[11px] font-semibold text-slate-400 flex items-center justify-between">
            <span>INDIA VIX</span>
            <span class="text-slate-500 font-mono text-[10px]">VOLATILITY</span>
          </div>
          <div class="text-base font-bold text-slate-200 font-mono mt-0.5">{glob['macro']['vix']['price']}</div>
          <div class="text-[11px] font-mono text-{'emerald' if glob['macro']['vix']['pct_change'] <= 0 else 'rose'}-400">
            {glob['macro']['vix']['pct_change']:+0.2f}% (Normal)
          </div>
        </div>

        <!-- Brent Crude -->
        <div class="bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80">
          <div class="text-[11px] font-semibold text-slate-400 flex items-center justify-between">
            <span>BRENT CRUDE</span>
            <span class="text-slate-500 font-mono text-[10px]">COMMODITY</span>
          </div>
          <div class="text-base font-bold text-slate-200 font-mono mt-0.5">${glob['macro']['brent']['price']}/bbl</div>
          <div class="text-[11px] font-mono text-{'emerald' if glob['macro']['brent']['pct_change'] <= 0 else 'rose'}-400">
            {glob['macro']['brent']['pct_change']:+0.2f}%
          </div>
        </div>

        <!-- US 10Y Yield -->
        <div class="bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80">
          <div class="text-[11px] font-semibold text-slate-400 flex items-center justify-between">
            <span>US 10Y YIELD</span>
            <span class="text-slate-500 font-mono text-[10px]">BONDS</span>
          </div>
          <div class="text-base font-bold text-slate-200 font-mono mt-0.5">{glob['macro']['us10y']['price']}%</div>
          <div class="text-[11px] font-mono text-{'emerald' if glob['macro']['us10y']['pct_change'] <= 0 else 'rose'}-400">
            {glob['macro']['us10y']['pct_change']:+0.2f}%
          </div>
        </div>

        <!-- Dollar Index DXY -->
        <div class="bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80">
          <div class="text-[11px] font-semibold text-slate-400 flex items-center justify-between">
            <span>DOLLAR DXY</span>
            <span class="text-slate-500 font-mono text-[10px]">CURRENCY</span>
          </div>
          <div class="text-base font-bold text-slate-200 font-mono mt-0.5">{glob['macro']['dxy']['price']}</div>
          <div class="text-[11px] font-mono text-{'emerald' if glob['macro']['dxy']['pct_change'] <= 0 else 'rose'}-400">
            {glob['macro']['dxy']['pct_change']:+0.2f}%
          </div>
        </div>

        <!-- USD / INR -->
        <div class="bg-slate-950/70 p-2.5 rounded-xl border border-slate-800/80">
          <div class="text-[11px] font-semibold text-slate-400 flex items-center justify-between">
            <span>USD / INR</span>
            <span class="text-slate-500 font-mono text-[10px]">FOREX</span>
          </div>
          <div class="text-base font-bold text-slate-200 font-mono mt-0.5">₹{glob['macro']['usdinr']['price']}</div>
          <div class="text-[11px] font-mono text-slate-400">
            {glob['macro']['usdinr']['pct_change']:+0.2f}%
          </div>
        </div>
      </div>
    </header>

    <!-- ==================== MAIN POV & TACTICAL GAMEPLAN ==================== -->
    <section class="bg-gradient-to-br from-slate-900 via-slate-900/95 to-indigo-950/40 border border-indigo-500/30 rounded-2xl p-5 md:p-6 shadow-xl relative overflow-hidden">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div class="flex items-center gap-3">
          <span class="p-2.5 rounded-xl bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
          </span>
          <div>
            <h2 class="text-lg md:text-xl font-bold text-white tracking-tight">Today's Morning Point of View (POV) & Tactical Battleplan</h2>
            <p class="text-xs text-slate-400">Synthesized from overnight cues, FII/DII cash flows, and live weekly open interest writing</p>
          </div>
        </div>

        <!-- Stance Badge -->
        <div class="flex items-center gap-2.5 bg-{pov['stance_color']}-500/15 border border-{pov['stance_color']}-500/30 rounded-xl px-4 py-2">
          <div class="w-2.5 h-2.5 rounded-full bg-{pov['stance_color']}-400 animate-ping"></div>
          <div>
            <div class="text-[10px] uppercase font-bold text-{pov['stance_color']}-400/80 tracking-wider">Market Stance (Confidence {pov['confidence_pct']}%)</div>
            <div class="text-base font-extrabold text-{pov['stance_color']}-300">{pov['stance']}</div>
          </div>
        </div>
      </div>

      <!-- Key Forecast Metrics -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3.5 my-5">
        <div class="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400 font-medium">Expected Open Range</div>
          <div class="text-lg sm:text-xl font-extrabold text-white font-mono mt-1">{pov['expected_open_range']}</div>
          <div class="text-[11px] text-{glob['gift_nifty']['gap_color']}-400 font-semibold mt-0.5">{glob['gift_nifty']['gap_type']}</div>
        </div>

        <div class="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400 font-medium">Expected Day Range</div>
          <div class="text-lg sm:text-xl font-extrabold text-white font-mono mt-1">{pov['expected_day_range']}</div>
          <div class="text-[11px] text-slate-400 mt-0.5">Implied Straddle: ~{pov['straddle_pts']} pts</div>
        </div>

        <div class="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400 font-medium">Intraday Pivot Level</div>
          <div class="text-lg sm:text-xl font-extrabold text-indigo-300 font-mono mt-1">{pov['pivot_level']:,}</div>
          <div class="text-[11px] text-slate-400 mt-0.5">Equilibrium Center</div>
        </div>

        <div class="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400 font-medium">Expiry Max Pain</div>
          <div class="text-lg sm:text-xl font-extrabold text-amber-400 font-mono mt-1">{option['max_pain']:,}</div>
          <div class="text-[11px] text-slate-400 mt-0.5">Gravitational Expiry Center</div>
        </div>
      </div>

      <!-- Tactical If-Then Gameplan -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
        <div class="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3.5">
          <div class="flex items-center gap-2 font-bold text-amber-300 mb-1.5">
            <span class="w-1.5 h-3.5 bg-amber-400 rounded-sm"></span>
            {pov['scenario_1_title']}
          </div>
          <p class="text-slate-300 leading-relaxed text-xs">{pov['scenario_1_desc']}</p>
        </div>

        <div class="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3.5">
          <div class="flex items-center gap-2 font-bold text-emerald-300 mb-1.5">
            <span class="w-1.5 h-3.5 bg-emerald-400 rounded-sm"></span>
            {pov['scenario_2_title']}
          </div>
          <p class="text-slate-300 leading-relaxed text-xs">{pov['scenario_2_desc']}</p>
        </div>

        <div class="bg-slate-950/50 border border-slate-800/80 rounded-xl p-3.5">
          <div class="flex items-center gap-2 font-bold text-rose-300 mb-1.5">
            <span class="w-1.5 h-3.5 bg-rose-400 rounded-sm"></span>
            {pov['scenario_3_title']}
          </div>
          <p class="text-slate-300 leading-relaxed text-xs">{pov['scenario_3_desc']}</p>
        </div>
      </div>
    </section>

    <!-- ==================== NSE WEEKLY OPTION CHAIN ==================== -->
    <section class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 md:p-6 shadow-xl">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div>
          <div class="flex items-center gap-2">
            <h2 class="text-lg md:text-xl font-bold text-white">NSE Nifty Weekly Expiry Option Chain Analysis</h2>
            {sec2_badge}
          </div>
          <p class="text-xs text-slate-400 mt-0.5">Parsed from official NSE live book for active contract: {option['expiry_date']}</p>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-xs text-slate-400">ATM Strike:</span>
          <span class="font-mono font-bold text-white bg-slate-800 px-2.5 py-1 rounded-md border border-slate-700">{option['atm_strike']}</span>
        </div>
      </div>

      <!-- Derivatives Stats Strip (4 Core Metrics) -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3.5 my-5">
        <div class="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400 font-medium">Total PCR</div>
          <div class="text-xl font-bold text-{option['pcr_badge_color']}-400 font-mono mt-0.5">{option['total_pcr']}</div>
          <div class="text-[11px] text-slate-400">{option['pcr_stance']}</div>
        </div>

        <div class="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400 font-medium">Max Pain Strike</div>
          <div class="text-xl font-bold text-amber-400 font-mono mt-0.5">{option['max_pain']:,}</div>
          <div class="text-[11px] text-slate-400">Expiry Gravity Pin Center</div>
        </div>

        <div class="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400 font-medium">Total Put OI Change</div>
          <div class="text-xl font-bold text-emerald-400 font-mono mt-0.5">{'+' if option['tot_put_chg_lakhs'] >= 0 else ''}{option['tot_put_chg_lakhs']}L</div>
          <div class="text-[11px] text-slate-400">{'Put Writing (Support Addition)' if option['tot_put_chg_lakhs'] >= 0 else 'Put Unwinding (Liquidation)'}</div>
        </div>

        <div class="bg-slate-950/70 p-3.5 rounded-xl border border-slate-800">
          <div class="text-xs text-slate-400 font-medium">Total Call OI Change</div>
          <div class="text-xl font-bold text-rose-400 font-mono mt-0.5">{'+' if option['tot_call_chg_lakhs'] >= 0 else ''}{option['tot_call_chg_lakhs']}L</div>
          <div class="text-[11px] text-slate-400">{'Call Writing (Resistance Addition)' if option['tot_call_chg_lakhs'] >= 0 else 'Call Unwinding (Short Covering)'}</div>
        </div>
      </div>

      <!-- Strike Ladder Chart -->
      <div class="bg-slate-950/70 p-4 rounded-xl border border-slate-800 mt-4">
        <div class="flex items-center justify-between text-xs mb-3">
          <span class="font-bold text-slate-300 uppercase tracking-wider text-[11px]">Open Interest Distribution by Strike (Call vs Put Walls)</span>
          <div class="flex items-center gap-4 text-[11px]">
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-rose-500"></span> Call OI (Resistance)</span>
            <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-emerald-500"></span> Put OI (Support)</span>
          </div>
        </div>

        <div class="space-y-1">
          {strike_rows_html}
        </div>

        <div class="mt-4 pt-3 border-t border-slate-800 text-xs text-slate-400 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <span>💡 <strong>Derivatives Reading:</strong> Total Put OI change is {'+' if option['tot_put_chg_lakhs'] >= 0 else ''}{option['tot_put_chg_lakhs']}L vs Total Call OI change of {'+' if option['tot_call_chg_lakhs'] >= 0 else ''}{option['tot_call_chg_lakhs']}L across the active contract. Expiry Max Pain centered at {option['max_pain']:,}.</span>
          <span class="font-mono text-indigo-400 text-[11px]">Source: NSE India Live Derivatives Book</span>
        </div>
      </div>
    </section>

    <!-- ==================== TWO COLUMNS: GLOBAL MARKETS & INSTITUTIONAL ==================== -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

      <!-- GLOBAL MARKETS OVERNIGHT & MORNING CUES -->
      <section class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <div class="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
          <div class="flex items-center gap-2">
            <span class="text-lg">🌐</span>
            <h2 class="text-base font-bold text-white">Global Markets Overnight & Asian Cues</h2>
          </div>
          <span class="text-xs text-slate-400 font-mono">08:00 AM IST</span>
        </div>

        <div class="space-y-3">
          <!-- US Wall St -->
          <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
              <span>🇺🇸 US Wall Street (Overnight Close)</span>
              <span class="text-emerald-400 text-[10px]">{glob['us_markets']['summary']}</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-center font-mono">
              <div class="bg-slate-900 p-2 rounded-lg border border-slate-800">
                <div class="text-[11px] text-slate-400">Dow Jones</div>
                <div class="text-xs font-bold text-white mt-0.5">{glob['us_markets']['dow']['price']:,}</div>
                <div class="text-[10px] text-{'emerald' if glob['us_markets']['dow']['is_positive'] else 'rose'}-400">{glob['us_markets']['dow']['pct_change']:+0.2f}%</div>
              </div>
              <div class="bg-slate-900 p-2 rounded-lg border border-slate-800">
                <div class="text-[11px] text-slate-400">S&P 500</div>
                <div class="text-xs font-bold text-white mt-0.5">{glob['us_markets']['sp500']['price']:,}</div>
                <div class="text-[10px] text-{'emerald' if glob['us_markets']['sp500']['is_positive'] else 'rose'}-400">{glob['us_markets']['sp500']['pct_change']:+0.2f}%</div>
              </div>
              <div class="bg-slate-900 p-2 rounded-lg border border-slate-800">
                <div class="text-[11px] text-slate-400">Nasdaq 100</div>
                <div class="text-xs font-bold text-white mt-0.5">{glob['us_markets']['nasdaq']['price']:,}</div>
                <div class="text-[10px] text-{'emerald' if glob['us_markets']['nasdaq']['is_positive'] else 'rose'}-400">{glob['us_markets']['nasdaq']['pct_change']:+0.2f}%</div>
              </div>
            </div>
          </div>

          <!-- Asian Markets -->
          <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
              <span>🌏 Asian Markets (Live Morning Trade)</span>
              <span class="text-emerald-400 text-[10px]">{glob['asian_markets']['summary']}</span>
            </div>
            <div class="grid grid-cols-3 gap-2 text-center font-mono">
              <div class="bg-slate-900 p-2 rounded-lg border border-slate-800">
                <div class="text-[11px] text-slate-400">Nikkei 225</div>
                <div class="text-xs font-bold text-white mt-0.5">{glob['asian_markets']['nikkei']['price']:,}</div>
                <div class="text-[10px] text-{'emerald' if glob['asian_markets']['nikkei']['is_positive'] else 'rose'}-400">{glob['asian_markets']['nikkei']['pct_change']:+0.2f}%</div>
              </div>
              <div class="bg-slate-900 p-2 rounded-lg border border-slate-800">
                <div class="text-[11px] text-slate-400">Hang Seng</div>
                <div class="text-xs font-bold text-white mt-0.5">{glob['asian_markets']['hangseng']['price']:,}</div>
                <div class="text-[10px] text-{'emerald' if glob['asian_markets']['hangseng']['is_positive'] else 'rose'}-400">{glob['asian_markets']['hangseng']['pct_change']:+0.2f}%</div>
              </div>
              <div class="bg-slate-900 p-2 rounded-lg border border-slate-800">
                <div class="text-[11px] text-slate-400">Shanghai</div>
                <div class="text-xs font-bold text-white mt-0.5">{glob['asian_markets']['shanghai']['price']:,}</div>
                <div class="text-[10px] text-{'emerald' if glob['asian_markets']['shanghai']['is_positive'] else 'rose'}-400">{glob['asian_markets']['shanghai']['pct_change']:+0.2f}%</div>
              </div>
            </div>
          </div>

          <!-- Europe -->
          <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <div class="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
              <span>🇪🇺 European Markets (Previous Session)</span>
            </div>
            <div class="grid grid-cols-2 gap-2 text-center font-mono">
              <div class="bg-slate-900 p-2 rounded-lg border border-slate-800 flex justify-between items-center px-3">
                <span class="text-xs text-slate-300">Germany DAX</span>
                <span class="text-xs font-bold text-{'emerald' if glob['european_markets']['dax']['is_positive'] else 'rose'}-400">
                  {glob['european_markets']['dax']['pct_change']:+0.2f}%
                </span>
              </div>
              <div class="bg-slate-900 p-2 rounded-lg border border-slate-800 flex justify-between items-center px-3">
                <span class="text-xs text-slate-300">UK FTSE 100</span>
                <span class="text-xs font-bold text-{'emerald' if glob['european_markets']['ftse']['is_positive'] else 'rose'}-400">
                  {glob['european_markets']['ftse']['pct_change']:+0.2f}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- INSTITUTIONAL FLOWS & SECTOR RADAR -->
      <section class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
            <div class="flex items-center gap-2">
              <span class="text-lg">🏛️</span>
              <h2 class="text-base font-bold text-white">Institutional Flows (FII / DII) & Sectors</h2>
            </div>
            <span class="text-xs text-slate-400 font-mono">Session: {inst['date']}</span>
          </div>

          <!-- FII / DII Numbers -->
          <div class="grid grid-cols-3 gap-3 mb-4">
            <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
              <div class="text-[11px] text-slate-400">FII Cash Net</div>
              <div class="text-sm sm:text-base font-bold text-{'emerald' if inst['fii_net_cr'] >= 0 else 'rose'}-400 font-mono mt-0.5">
                {inst['fii_net_cr']:+0.1f} Cr
              </div>
              <div class="text-[10px] text-slate-400">{"Net Buyers" if inst['fii_net_cr'] >= 0 else "Net Sellers"}</div>
            </div>

            <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
              <div class="text-[11px] text-slate-400">DII Cash Net</div>
              <div class="text-sm sm:text-base font-bold text-{'emerald' if inst['dii_net_cr'] >= 0 else 'rose'}-400 font-mono mt-0.5">
                {inst['dii_net_cr']:+0.1f} Cr
              </div>
              <div class="text-[10px] text-slate-400">Domestic Absorption</div>
            </div>

            <div class="bg-slate-950/60 p-3 rounded-xl border border-slate-800 text-center">
              <div class="text-[11px] text-slate-400">Combined Net</div>
              <div class="text-sm sm:text-base font-bold text-{'emerald' if inst['combined_net_cr'] >= 0 else 'rose'}-400 font-mono mt-0.5">
                {inst['combined_net_cr']:+0.1f} Cr
              </div>
              <div class="text-[10px] text-slate-400">{"Positive Inflow" if inst['combined_net_cr'] >= 0 else "Net Outflow"}</div>
            </div>
          </div>

          <!-- FII Futures Ratio -->
          <div class="bg-slate-950/60 p-3.5 rounded-xl border border-slate-800 mb-4">
            <div class="flex justify-between items-center text-xs mb-1.5">
              <span class="text-slate-300 font-semibold">FII Index Futures Exposure:</span>
              <span class="font-mono font-bold text-slate-200">{inst['fii_long_pct']}% Long vs {inst['fii_short_pct']}% Short</span>
            </div>
            <div class="w-full bg-rose-500/80 h-3 rounded-full overflow-hidden flex">
              <div class="bg-emerald-500 h-full" style="width: {inst['fii_long_pct']}%;"></div>
            </div>
          </div>

          <!-- Sector Watchlist Grid -->
          <div class="grid grid-cols-2 gap-2 text-xs">
            {sector_cards_html}
          </div>
        </div>
      </section>
    </div>

    <!-- ==================== MARKET MOVING NEWS WITH IMPACT ==================== -->
    <section class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 md:p-6 shadow-xl">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4 mb-4">
        <div class="flex items-center gap-2">
          <span class="text-lg">📰</span>
          <h2 class="text-lg font-bold text-white">Market-Moving News Influencing Today's Session</h2>
        </div>
        <span class="text-xs text-slate-400">Live Indian & Global financial feeds</span>
      </div>

      <div class="space-y-3">
        {news_cards_html}
      </div>
    </section>

    <!-- ==================== FOOTER ==================== -->
    <footer class="border-t border-slate-800/80 pt-5 pb-8 text-center text-xs text-slate-500 space-y-1">
      <p>Nifty Pre-Market Pulse • Auto-generated for 08:00 AM IST Indian Market Preparation</p>
      <p class="text-[11px] text-slate-600">Educational and informational reference only. Not SEBI registered investment advice.</p>
    </footer>

  </div>

  <script>
    function copyBriefing() {{
      const text = "{copy_text}" + window.location.href;
      navigator.clipboard.writeText(text).then(() => {{
        const btn = document.getElementById('copyBtnText');
        const orig = btn.innerText;
        btn.innerText = 'Copied to Clipboard! ✓';
        setTimeout(() => {{ btn.innerText = orig; }}, 2500);
      }}).catch(err => {{
        alert('Could not auto-copy. Please copy from screen.');
      }});
    }}
  </script>
</body>
</html>
"""
    return html
