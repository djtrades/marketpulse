"""
Tactical Point of View (POV) & Trading Battleplan Engine
Synthesizes Gift Nifty cues, NSE Weekly Option Chain Open Interest, Global Momentum,
and Macro Indicators into a coherent morning tactical gameplan with if-then trade rules.
"""

from typing import Dict, Any

def generate_morning_pov(
    option_data: Dict[str, Any],
    global_data: Dict[str, Any],
    inst_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Synthesizes the morning point of view and actionable trading plan.
    """
    spot = option_data["spot_price"]
    gap_pts = global_data["gift_nifty"]["gap_points"]
    pcr = option_data["total_pcr"]
    max_pain = option_data["max_pain"]
    r2_call_wall = option_data["r2_major_call_wall"]
    r1_imm_res = option_data["r1_imm_res"]
    s2_put_wall = option_data["s2_major_put_wall"]
    s1_imm_supp = option_data["s1_imm_supp"]
    
    # 1. Scoring Algorithmic Bias (-100 to +100)
    score = 0
    # Gift Nifty Gap weight (30 pts)
    score += max(-30, min(30, int(gap_pts * 0.4)))
    
    # PCR weight (30 pts)
    if pcr >= 1.25: score += 25
    elif pcr >= 1.05: score += 15
    elif pcr <= 0.75: score -= 20
    elif pcr <= 0.90: score -= 10
    
    # Global Tech / Wall St weight (20 pts)
    nasdaq_pct = global_data["us_markets"]["nasdaq"]["pct_change"]
    score += max(-20, min(20, int(nasdaq_pct * 15)))
    
    # Institutional Flow weight (10 pts)
    if inst_data["combined_net_cr"] > 0: score += 10
    else: score -= 10
    
    # Macro tailwind weight (10 pts)
    brent_chg = global_data["macro"]["brent"]["pct_change"]
    if brent_chg < 0: score += 10  # Cooling oil is positive for India
    else: score -= 10

    # 2. Determine Stance & Confidence
    confidence = min(92, max(65, 50 + abs(score) // 2))
    
    if score >= 35:
        stance = "BULLISH (Buy-on-Dips Bias)"
        stance_color = "emerald"
    elif score >= 10:
        stance = "MILDLY BULLISH (Cautious Optimism)"
        stance_color = "emerald"
    elif score <= -35:
        stance = "BEARISH (Sell-on-Rallies)"
        stance_color = "rose"
    elif score <= -10:
        stance = "MILDLY BEARISH (Defensive / Sell High)"
        stance_color = "rose"
    else:
        stance = "NEUTRAL / RANGEBOUND (Theta Decay Market)"
        stance_color = "amber"

    # 3. Expected Opening & Trading Range
    expected_open_mid = round(spot + gap_pts)
    expected_open_low = expected_open_mid - 20
    expected_open_high = expected_open_mid + 20
    
    straddle = option_data["straddle_price"]
    expected_day_low = round(spot - straddle)
    expected_day_high = round(spot + straddle)
    
    # Pivot point calculation
    pivot_level = round((r1_imm_res + s1_imm_supp + spot) / 3.0)

    # 4. Scenario-Based Tactical Battleplan
    if gap_pts >= 30:
        scenario_1_title = f"SCENARIO 1: Gap-Up Open (> {expected_open_low})"
        scenario_1_desc = (
            f"Do not blindly chase long breakout trades at the opening bell. The {r2_call_wall} strike "
            f"houses heavy Call OI concentration ({option_data['r2_call_oi_lakhs']}L shares) acting as a ceiling. "
            f"Wait for the initial 15-minute price discovery. A healthy pullback towards {s1_imm_supp} - {pivot_level} "
            f"supported by Put writing offers favorable risk-reward long entries targeting {r1_imm_res}."
        )
    elif gap_pts <= -30:
        scenario_1_title = f"SCENARIO 1: Gap-Down Open (< {expected_open_high})"
        scenario_1_desc = (
            f"Expect initial panic selling towards the {s2_put_wall} Put Wall ({option_data['s2_put_oi_lakhs']}L shares). "
            f"Watch for absorption near {s2_put_wall}. If PCR is oversold ({pcr}), look for quick mean-reversion "
            f"pullbacks towards {pivot_level}. Avoid fresh shorting directly into major support."
        )
    else:
        scenario_1_title = "SCENARIO 1: Flat / Neutral Opening"
        scenario_1_desc = (
            f"Rangebound morning session expected between {s1_imm_supp} and {r1_imm_res}. "
            f"Ideal for non-directional option sellers (Short Straddles / Iron Condors) aiming to capitalize on early theta decay."
        )

    scenario_2_title = f"SCENARIO 2: Resistance Test at {r2_call_wall} (Call Wall)"
    scenario_2_desc = (
        f"If Nifty crosses {r1_imm_res} and sustains above {r2_call_wall} for over 30 minutes, "
        f"expect rapid short-covering panic from trapped call sellers, unleashing momentum towards {r2_call_wall + 100}. "
        f"Conversely, sharp price rejection at {r2_call_wall} triggers quick mean-reversion scalp shorts back to {pivot_level}."
    )

    scenario_3_title = f"SCENARIO 3: Bearish Invalidation Level at {s2_put_wall} (Put Wall)"
    scenario_3_desc = (
        f"The intraday bullish/neutral thesis is completely invalidated if Nifty breaks and closes below the {s2_put_wall} support floor. "
        f"A decisive breach will initiate aggressive long unwinding, exposing lower targets towards {s2_put_wall - 100}."
    )

    return {
        "stance": stance,
        "stance_color": stance_color,
        "confidence_pct": confidence,
        "score": score,
        "expected_open_range": f"{expected_open_low:,} – {expected_open_high:,}",
        "expected_day_range": f"{expected_day_low:,} – {expected_day_high:,}",
        "pivot_level": pivot_level,
        "r2_call_wall": r2_call_wall,
        "r1_imm_res": r1_imm_res,
        "s1_imm_supp": s1_imm_supp,
        "s2_put_wall": s2_put_wall,
        "max_pain": max_pain,
        "straddle_pts": straddle,
        "scenario_1_title": scenario_1_title,
        "scenario_1_desc": scenario_1_desc,
        "scenario_2_title": scenario_2_title,
        "scenario_2_desc": scenario_2_desc,
        "scenario_3_title": scenario_3_title,
        "scenario_3_desc": scenario_3_desc
    }
