"""
HTML Dashboard Renderer - Elite 5 Options Morning Radar
Renders an institutional-grade, responsive HTML dashboard focused on
the 5 non-negotiable options metrics, institutional ΔOI force, corridor ladder,
and tactical execution playbook.
"""

from typing import Dict, Any

def render_html_dashboard(data: Dict[str, Any]) -> str:
    """
    Renders the complete self-contained HTML file from structured scanner data.
    """
    option = data["option_chain"]
    runtime = data["runtime"]

    # 1. Calculations for the Elite 5
    spot = option["spot_price"]
    atm = option["atm_strike"]
    straddle = option.get("straddle_price", 150.0)
    straddle_pct = round((straddle / spot * 100.0), 2) if spot else 0.65

    exp_low = option.get("expected_range_low", round(spot - straddle))
    exp_high = option.get("expected_range_high", round(spot + straddle))

    max_call_strike = option.get("max_call_add_strike", atm + 150)
    max_call_lakhs = option.get("max_call_add_lakhs", 1.5)
    max_put_strike = option.get("max_put_add_strike", atm - 150)
    max_put_lakhs = option.get("max_put_add_lakhs", 1.4)

    max_pain = option.get("max_pain", atm)
    pain_diff = max_pain - spot
    pain_dir = "▲ Upward Pull" if pain_diff > 0 else ("▼ Downward Pull" if pain_diff < 0 else "• Pinned to Spot")
    pain_diff_text = f"{abs(round(pain_diff))} pts {'Above' if pain_diff > 0 else 'Below'} Spot"

    # Net Force Calculation
    tot_put_chg = option.get("tot_put_chg_lakhs", 0.0)
    tot_call_chg = option.get("tot_call_chg_lakhs", 0.0)
    total_abs = max(0.1, abs(tot_put_chg) + abs(tot_call_chg))
    put_pct = min(90, max(10, int((abs(tot_put_chg) / total_abs) * 100))) if total_abs > 0 else 50
    call_pct = 100 - put_pct
    net_force = round(tot_put_chg - tot_call_chg, 1)
    net_force_tag = "BULLISH WRITING BIAS" if net_force >= 0 else "BEARISH WRITING BIAS"
    net_force_color = "emerald" if net_force >= 0 else "rose"
    net_force_text = f"+{net_force}L Puts Added" if net_force >= 0 else f"{abs(net_force)}L Calls Added"

    # Dynamic Expiry Badges
    exp_day = option.get('expiry_weekday', 'Tuesday')
    days_left = option.get('days_to_expiry', 0)
    if option.get('is_expiry_today'):
        top_expiry_badge = f'<span class="text-[10px] font-bold px-2.5 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 font-mono animate-pulse">🔥 EXPIRY TODAY ({exp_day.upper()})</span>'
    else:
        top_expiry_badge = f'<span class="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 font-mono">EXPIRY: {option.get("expiry_date", "")} ({exp_day}, {days_left}d left)</span>'

    # Strike Ladder HTML Rows
    strike_rows_html = ""
    for row in option.get("strike_ladder", []):
        s = row["strike"]
        is_atm = row["is_atm"]
        is_ceil = (s == max_call_strike)
        is_floor = (s == max_put_strike)
        is_pain = (s == max_pain)

        if is_atm:
            row_style = "bg-amber-950/30 border border-amber-500/40 shadow-inner"
            badge = " <span class='text-[9px] font-black text-amber-300 bg-amber-900/60 px-1 py-0.2 rounded border border-amber-500/50 ml-1'>ATM</span>"
        elif is_ceil:
            row_style = "bg-rose-950/25 border border-rose-500/40"
            badge = " <span class='text-[9px] font-black text-rose-300 bg-rose-900/60 px-1 py-0.2 rounded border border-rose-500/50 ml-1'>CEIL</span>"
        elif is_floor:
            row_style = "bg-emerald-950/25 border border-emerald-500/40"
            badge = " <span class='text-[9px] font-black text-emerald-300 bg-emerald-900/60 px-1 py-0.2 rounded border border-emerald-500/50 ml-1'>FLOOR</span>"
        elif is_pain:
            row_style = "bg-purple-950/20 border border-purple-500/30"
            badge = " <span class='text-[9px] font-bold text-purple-300 bg-purple-900/60 px-1 py-0.2 rounded border border-purple-500/50 ml-1'>PAIN</span>"
        else:
            row_style = "hover:bg-slate-800/40 transition"
            badge = ""

        c_chg_sign = "+" if row['call_chg_lakhs'] >= 0 else ""
        p_chg_sign = "+" if row['put_chg_lakhs'] >= 0 else ""

        strike_rows_html += f"""
        <div class="grid grid-cols-12 items-center gap-2 py-1 px-2 rounded-lg {row_style}">
          <!-- Call OI Bar & Val -->
          <div class="col-span-5 flex justify-end items-center gap-2">
            <span class="text-[10px] text-rose-400/80 font-mono">{c_chg_sign}{row['call_chg_lakhs']}L</span>
            <span class="text-slate-300 font-bold text-xs font-mono">{row['call_oi_lakhs']}L</span>
            <div class="w-24 sm:w-36 bg-slate-800/80 h-3 rounded-l overflow-hidden flex justify-end">
              <div class="bg-rose-500 h-full" style="width: {row['call_bar_pct']}%;"></div>
            </div>
          </div>
          
          <!-- Strike Price -->
          <div class="col-span-2 text-center font-bold text-slate-200 bg-slate-950 py-0.5 rounded border border-slate-800 font-mono text-xs">
            {s}{badge}
          </div>
          
          <!-- Put OI Bar & Val -->
          <div class="col-span-5 flex items-center gap-2">
            <div class="w-24 sm:w-36 bg-slate-800/80 h-3 rounded-r overflow-hidden">
              <div class="bg-emerald-500 h-full" style="width: {row['put_bar_pct']}%;"></div>
            </div>
            <span class="text-slate-300 font-bold text-xs font-mono">{row['put_oi_lakhs']}L</span>
            <span class="text-[10px] text-emerald-400/80 font-mono">{p_chg_sign}{row['put_chg_lakhs']}L</span>
          </div>
        </div>
        """

    # Generate Quick Copy Text for WhatsApp/Telegram
    copy_text = (
        f"🎯 NIFTY 50 • ELITE 5 OPTIONS RADAR ({runtime['date']})\\n"
        f"1. THE BOUNDARY: {exp_low:,} – {exp_high:,} (ATM {atm} Straddle: {straddle} pts / ~{straddle_pct}%)\\n"
        f"2. CALL FORTRESS: {max_call_strike:,} CE (+{max_call_lakhs}L Added | Active Ceiling)\\n"
        f"3. PUT FORTRESS: {max_put_strike:,} PE (+{max_put_lakhs}L Added | Active Floor)\\n"
        f"4. THE SENTIMENT: Total PCR {option['total_pcr']} ({option['pcr_stance']})\\n"
        f"5. THE MAGNET: Max Pain {max_pain:,} ({pain_diff_text} | {pain_dir})\\n"
        f"• Net Force: {net_force_text} ({net_force_tag})\\n"
        f"Check full dashboard: https://djtrades.github.io/marketpulse/"
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Nifty 50 • Elite 5 Options Radar ({runtime['date']})</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
  <style>
    body {{ font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif; }}
    .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
    ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
    ::-webkit-scrollbar-track {{ background: rgba(0, 0, 0, 0.05); }}
    ::-webkit-scrollbar-thumb {{ background: rgba(100, 116, 139, 0.3); border-radius: 4px; }}
  </style>
</head>
<body class="bg-slate-950 text-slate-100 antialiased min-h-screen p-3 sm:p-6 selection:bg-indigo-500 selection:text-white">

  <div class="max-w-7xl mx-auto space-y-6">

    <!-- ==================== HEADER BAR ==================== -->
    <header class="bg-slate-900/95 border border-slate-800 rounded-2xl p-4 sm:p-6 shadow-2xl backdrop-blur-md">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div class="flex items-center gap-2.5 flex-wrap">
            <span class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
            <h1 class="text-xl sm:text-2xl font-black tracking-tight text-white flex items-center gap-2">
              NIFTY OPTIONS RADAR
              <span class="text-xs font-bold px-2 py-0.5 rounded bg-indigo-600/30 text-indigo-300 border border-indigo-500/30">ELITE 5 CORE</span>
            </h1>
            {top_expiry_badge}
          </div>
          <p class="text-xs sm:text-sm text-slate-400 mt-1">
            Pure Derivatives Microstructure • 5 Non-Negotiable Greeks & OI Signals for 09:15 AM
          </p>
        </div>

        <!-- Meta Strip & Share Button -->
        <div class="flex flex-wrap items-center gap-2.5 text-xs">
          <div class="bg-slate-950/70 px-3 py-1.5 rounded-lg border border-slate-800 font-mono text-slate-300">
            <span class="text-slate-500">Spot:</span> <span class="text-white font-bold">{spot:,}</span>
          </div>
          <div class="bg-slate-950/70 px-3 py-1.5 rounded-lg border border-slate-800 font-mono text-slate-300">
            <span class="text-slate-500">ATM:</span> <span class="text-amber-400 font-bold">{atm:,}</span>
          </div>
          <div class="bg-slate-950/70 px-3 py-1.5 rounded-lg border border-slate-800 font-mono text-slate-300">
            <span class="text-slate-500">Refreshed:</span> <span class="text-emerald-400 font-bold">{runtime['timestamp']} IST</span>
          </div>
          <button onclick="copyBriefing()" class="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold px-3 py-1.5 rounded-lg transition shadow-md flex items-center gap-1.5 cursor-pointer">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"/></svg>
            <span id="copyBtnText">Copy Options Brief</span>
          </button>
        </div>
      </div>

      <!-- Quick Guidance Banner -->
      <div class="mt-4 flex items-center justify-between text-xs text-slate-400 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800/60">
        <span class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
          <span><strong>The 30-Second Rule:</strong> Review the 5 Core Pillars below to establish Range, Walls, Sentiment, Gravity, and Net Flow.</span>
        </span>
        <span class="text-slate-500 font-mono text-[11px] hidden sm:inline">{runtime['date']}</span>
      </div>
    </header>

    <!-- ==================== THE ELITE 5 CORE HERO GRID ==================== -->
    <section class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">

      <!-- PILLAR 1: ATM STRADDLE (THE BOUNDARY) -->
      <div class="bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 border border-indigo-500/40 rounded-2xl p-4 shadow-xl flex flex-col justify-between relative overflow-hidden group hover:border-indigo-400 transition">
        <div class="absolute top-0 right-0 w-24 h-24 bg-indigo-500/10 rounded-full blur-2xl pointer-events-none"></div>
        <div>
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-extrabold uppercase tracking-wider text-indigo-400 bg-indigo-500/15 px-2 py-0.5 rounded border border-indigo-500/30">
              #1 THE BOUNDARY
            </span>
            <span class="text-[10px] font-mono text-slate-400 font-medium">ATM Straddle</span>
          </div>

          <div class="mt-3">
            <div class="text-xl sm:text-2xl font-black text-white font-mono tracking-tight">
              {exp_low:,} – {exp_high:,}
            </div>
            <div class="text-xs font-semibold text-indigo-300 mt-1 flex items-center gap-1.5">
              <span>±{straddle} pts</span>
              <span class="text-slate-500">•</span>
              <span>~{straddle_pct}% Implied Move</span>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 leading-relaxed">
          <span class="text-slate-300 font-medium">Statistical Sandbox:</span> Market makers price today's range within this band. High statistical edge for option selling outside.
        </div>
      </div>

      <!-- PILLAR 2: MAX CALL ΔOI (THE CEILING) -->
      <div class="bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 border border-rose-500/40 rounded-2xl p-4 shadow-xl flex flex-col justify-between relative overflow-hidden group hover:border-rose-400 transition">
        <div class="absolute top-0 right-0 w-24 h-24 bg-rose-500/10 rounded-full blur-2xl pointer-events-none"></div>
        <div>
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-extrabold uppercase tracking-wider text-rose-400 bg-rose-500/15 px-2 py-0.5 rounded border border-rose-500/30">
              #2 CALL FORTRESS
            </span>
            <span class="text-[10px] font-mono text-slate-400 font-medium">Active Ceiling</span>
          </div>

          <div class="mt-3">
            <div class="text-xl sm:text-2xl font-black text-rose-400 font-mono tracking-tight">
              {max_call_strike:,} CE
            </div>
            <div class="text-xs font-semibold text-rose-300 mt-1 flex items-center gap-1.5">
              <span>+{max_call_lakhs}L Added</span>
              <span class="text-slate-500">•</span>
              <span class="text-slate-400">Active Supply</span>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 leading-relaxed">
          <span class="text-slate-300 font-medium">Resistance Wall:</span> Highest fresh Call writing yesterday. Rallies toward this strike face heavy institutional selling.
        </div>
      </div>

      <!-- PILLAR 3: MAX PUT ΔOI (THE FLOOR) -->
      <div class="bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 border border-emerald-500/40 rounded-2xl p-4 shadow-xl flex flex-col justify-between relative overflow-hidden group hover:border-emerald-400 transition">
        <div class="absolute top-0 right-0 w-24 h-24 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none"></div>
        <div>
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-extrabold uppercase tracking-wider text-emerald-400 bg-emerald-500/15 px-2 py-0.5 rounded border border-emerald-500/30">
              #3 PUT FORTRESS
            </span>
            <span class="text-[10px] font-mono text-slate-400 font-medium">Active Floor</span>
          </div>

          <div class="mt-3">
            <div class="text-xl sm:text-2xl font-black text-emerald-400 font-mono tracking-tight">
              {max_put_strike:,} PE
            </div>
            <div class="text-xs font-semibold text-emerald-300 mt-1 flex items-center gap-1.5">
              <span>+{max_put_lakhs}L Added</span>
              <span class="text-slate-500">•</span>
              <span class="text-slate-400">Active Defense</span>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 leading-relaxed">
          <span class="text-slate-300 font-medium">Support Wall:</span> Highest fresh Put writing. Bulls defend this strike aggressively; a breakdown triggers sharp long liquidation.
        </div>
      </div>

      <!-- PILLAR 4: TOTAL PCR (THE SENTIMENT) -->
      <div class="bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 border border-amber-500/40 rounded-2xl p-4 shadow-xl flex flex-col justify-between relative overflow-hidden group hover:border-amber-400 transition">
        <div class="absolute top-0 right-0 w-24 h-24 bg-amber-500/10 rounded-full blur-2xl pointer-events-none"></div>
        <div>
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-extrabold uppercase tracking-wider text-amber-400 bg-amber-500/15 px-2 py-0.5 rounded border border-amber-500/30">
              #4 THE SENTIMENT
            </span>
            <span class="text-[10px] font-mono text-slate-400 font-medium">Total PCR</span>
          </div>

          <div class="mt-3">
            <div class="text-xl sm:text-2xl font-black text-{option['pcr_badge_color']}-400 font-mono tracking-tight flex items-baseline gap-2">
              <span>{option['total_pcr']}</span>
              <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-{option['pcr_badge_color']}-500/20 text-{option['pcr_badge_color']}-300 uppercase">
                {'OVERSOLD' if option['total_pcr'] < 0.75 else ('OVERBOUGHT' if option['total_pcr'] > 1.30 else 'NEUTRAL')}
              </span>
            </div>
            <div class="text-xs font-semibold text-slate-300 mt-1">
              {option['pcr_stance']}
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 leading-relaxed">
          <span class="text-slate-300 font-medium">Contrarian Meter:</span> Indicates market positioning extremes. Puts crowded below 0.70; Calls crowded above 1.30.
        </div>
      </div>

      <!-- PILLAR 5: MAX PAIN (THE MAGNET) -->
      <div class="bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-950 border border-purple-500/40 rounded-2xl p-4 shadow-xl flex flex-col justify-between relative overflow-hidden group hover:border-purple-400 transition">
        <div class="absolute top-0 right-0 w-24 h-24 bg-purple-500/10 rounded-full blur-2xl pointer-events-none"></div>
        <div>
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-extrabold uppercase tracking-wider text-purple-400 bg-purple-500/15 px-2 py-0.5 rounded border border-purple-500/30">
              #5 THE MAGNET
            </span>
            <span class="text-[10px] font-mono text-slate-400 font-medium">Max Pain</span>
          </div>

          <div class="mt-3">
            <div class="text-xl sm:text-2xl font-black text-purple-300 font-mono tracking-tight">
              {max_pain:,}
            </div>
            <div class="text-xs font-semibold text-purple-300 mt-1 flex items-center gap-1.5">
              <span>{pain_diff_text}</span>
              <span class="text-slate-500">•</span>
              <span class="text-emerald-400 font-bold">{pain_dir}</span>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 leading-relaxed">
          <span class="text-slate-300 font-medium">Gravitational Drift:</span> Strike where collective option buyers lose maximum money. Gravitational pull intensifies near expiry.
        </div>
      </div>

    </section>

    <!-- ==================== SECTION 2: NET INSTITUTIONAL FORCE (ΔOI BALANCE) ==================== -->
    <section class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3 mb-4">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <span>Net Institutional Force: ΔOI Ammunition Meter</span>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-{net_force_color}-500/15 text-{net_force_color}-300 border border-{net_force_color}-500/30">
              {net_force_tag}
            </span>
          </h2>
          <p class="text-xs text-slate-400">Total contracts added across all Put strikes vs Call strikes in active weekly cycle</p>
        </div>
        <div class="text-xs font-mono bg-slate-950 px-3 py-1 rounded-lg border border-slate-800 text-slate-300">
          Net Advantage: <span class="text-{net_force_color}-400 font-bold">{net_force_text}</span>
        </div>
      </div>

      <!-- Meter Visual -->
      <div class="space-y-2">
        <div class="flex items-center justify-between text-xs font-mono">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-sm bg-emerald-500"></span>
            <span class="text-slate-300">Put Writing (Support Added):</span>
            <span class="text-emerald-400 font-bold">+{tot_put_chg}L ({put_pct}%)</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-rose-400 font-bold">+{tot_call_chg}L ({call_pct}%)</span>
            <span class="text-slate-300">:Call Writing (Resistance Added)</span>
            <span class="w-3 h-3 rounded-sm bg-rose-500"></span>
          </div>
        </div>

        <!-- Split Progress Bar -->
        <div class="w-full bg-slate-800 h-3.5 rounded-full overflow-hidden flex p-0.5">
          <div class="bg-emerald-500 h-full rounded-l-full transition-all duration-500" style="width: {put_pct}%;"></div>
          <div class="bg-rose-500 h-full rounded-r-full transition-all duration-500" style="width: {call_pct}%;"></div>
        </div>

        <p class="text-[11px] text-slate-400 text-center pt-1">
          Institutional writers injected <strong>{abs(net_force)}L more {'put' if net_force >= 0 else 'call'} contracts</strong> yesterday. {'Downside moves are backed by institutional writing support.' if net_force >= 0 else 'Upside moves face aggressive overhead writing resistance.'}
        </p>
      </div>
    </section>

    <!-- ==================== SECTION 3: CORRIDOR STRIKE LADDER ==================== -->
    <section class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-xl">
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3 mb-4">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            Active Corridor Open Interest Distribution (± 300 pts)
          </h2>
          <p class="text-xs text-slate-400">Total OI (Bar width) & Fresh Daily ΔOI Additions by Strike</p>
        </div>
        <div class="flex items-center gap-4 text-xs font-mono">
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-rose-500"></span> Call OI (Ceiling)</span>
          <span class="flex items-center gap-1.5"><span class="w-3 h-3 rounded-sm bg-emerald-500"></span> Put OI (Floor)</span>
        </div>
      </div>

      <!-- Strike Ladder Rows -->
      <div class="space-y-1.5">
        {strike_rows_html}
      </div>
    </section>

    <!-- ==================== SECTION 4: 30-SECOND TACTICAL ACTION MATRIX ==================== -->
    <section class="bg-gradient-to-br from-slate-900 via-slate-900/95 to-indigo-950/40 border border-indigo-500/30 rounded-2xl p-5 shadow-xl">
      <div class="border-b border-slate-800 pb-3 mb-4">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <span>The 30-Second Tactical Action Matrix (If-Then Execution Rules)</span>
          <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">DISCIPLINE PLAYBOOK</span>
        </h2>
        <p class="text-xs text-slate-400">Rules-based execution triggers derived strictly from the Elite 5 options metrics</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">

        <!-- PLAY 1 -->
        <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-xl space-y-2">
          <div class="flex items-center gap-2 font-bold text-indigo-300">
            <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
            <span>RULE 1: Straddle Sandbox Play</span>
          </div>
          <div class="text-[11px] font-mono text-slate-400">
            Zone: <strong class="text-white">{exp_low:,} – {exp_high:,}</strong>
          </div>
          <p class="text-slate-300 leading-relaxed">
            If Nifty opens inside this band, statistical edge belongs to non-directional theta decay. Look to sell OTM Iron Condors or Strangles outside the boundary with strict straddle-based stop losses.
          </p>
        </div>

        <!-- PLAY 2 -->
        <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-xl space-y-2">
          <div class="flex items-center gap-2 font-bold text-rose-300">
            <span class="w-2 h-2 rounded-full bg-rose-400"></span>
            <span>RULE 2: Ceiling Rejection / Squeeze</span>
          </div>
          <div class="text-[11px] font-mono text-slate-400">
            Level: <strong class="text-rose-400">{max_call_strike:,} CE (+{max_call_lakhs}L)</strong>
          </div>
          <p class="text-slate-300 leading-relaxed">
            If price rallies toward {max_call_strike:,} and stalls, look for Bear Call Spreads. If price holds decisively above {max_call_strike:,} for &gt;30 mins with Call unwinding, expect an aggressive short-covering squeeze.
          </p>
        </div>

        <!-- PLAY 3 -->
        <div class="bg-slate-950/60 border border-slate-800 p-4 rounded-xl space-y-2">
          <div class="flex items-center gap-2 font-bold text-emerald-300">
            <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>RULE 3: Floor Defense / Invalidation</span>
          </div>
          <div class="text-[11px] font-mono text-slate-400">
            Level: <strong class="text-emerald-400">{max_put_strike:,} PE (+{max_put_lakhs}L)</strong>
          </div>
          <p class="text-slate-300 leading-relaxed">
            Dip-buying edge sits near {max_put_strike:,} with Put Credit Spreads. If Nifty closes a 15-minute candle below {max_put_strike:,}, immediately invalidate all bullish bias; expect an accelerated long liquidation cascade.
          </p>
        </div>

      </div>
    </section>


    <!-- FOOTER -->
    <footer class="text-center text-xs text-slate-500 py-3">
      Nifty 50 Options Radar • Automated Daily Runner at 4:00 PM IST • NSE Live Derivatives Engine
    </footer>

  </div>

  <!-- SCRIPT FOR BRIEFING COPY -->
  <script>
    function copyBriefing() {{
      const text = `{copy_text}`;
      navigator.clipboard.writeText(text).then(() => {{
        const btn = document.getElementById('copyBtnText');
        const original = btn.innerText;
        btn.innerText = 'Copied to Clipboard!';
        setTimeout(() => btn.innerText = original, 2000);
      }});
    }}
  </script>
</body>
</html>
"""
    return html
