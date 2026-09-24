# 🌅 Nifty Pre-Market Pulse & NSE Expiry Radar (8:00 AM IST)

An automated, shareable pre-market intelligence dashboard designed for Indian market traders and investors. Every trading day at **07:50 AM IST**, an automated GitHub Action triggers, scans overnight global markets, parses the live NSE weekly option chain, calculates derivatives levels (PCR, Max Pain, Call/Put Walls), and publishes a responsive HTML dashboard accessible from any mobile or desktop browser.

---

## ⚡ What the Dashboard Delivers at 8:00 AM IST

1. **Synthesized Morning POV & Tactical Battleplan**:
   * Automated market stance (Bullish / Mildly Bullish / Neutral / Bearish) with confidence score.
   * Expected opening range & intraday trading range (calculated from ATM Straddle pricing).
   * Key Pivot levels: Major Resistance (R2 - Call Wall), Immediate Resistance (R1), Pivot, Immediate Support (S1), Major Support (S2 - Put Wall).
   * 3-Scenario If-Then Gameplan (how to trade opening gaps, test of resistance walls, and invalidation stops).

2. **Live NSE Weekly Expiry Option Chain Analysis**:
   * Scrapes live book from official NSE India API for the active weekly contract.
   * Total Put-Call Ratio (PCR) and ATM PCR ($\pm 150$ pts).
   * Max Pain Strike (the gravitational expiry pin center).
   * Call and Put OI distribution ladder with strike-by-strike open interest bars.
   * Max Call additions vs Max Put additions (identifies where big institutional option sellers are active).

3. **Global Markets Snapshot**:
   * US Wall Street overnight close: Dow Jones, S&P 500, Nasdaq 100.
   * Asian Markets live trade at 8:00 AM: Nikkei 225, Hang Seng, Shanghai Composite, Kospi.
   * European previous close: DAX, FTSE 100.
   * Gift Nifty estimated opening cue with points and percentage deviation.

4. **Macro & Intermarket Radar**:
   * Brent Crude Oil price & inflation sentiment tag.
   * US 10-Year Treasury Yield & emerging market foreign flow impact.
   * Dollar Index (DXY) & USD/INR exchange rate.
   * India VIX volatility gauge.

5. **Institutional Activity (FII / DII)**:
   * Previous session Cash market net buy/sell figures in ₹ Crores.
   * FII Index Futures Long vs Short exposure percentage.
   * Catalyst-driven sector watchlist (IT, Metals, Banks, Auto).

6. **Market-Moving News with "Direct Nifty Impact" Tags**:
   * Real-time headlines from Economic Times and Livemint.
   * Automated sentiment tagging and sector-specific takeaway.

7. **1-Click Share & Copy Button**:
   * Quickly copies a formatted text summary with your dashboard link to clipboard for instant sharing on WhatsApp, Telegram, or Twitter.

---

## 🚀 Step-by-Step: How to Host & Share (100% Free on GitHub Pages)

### Step 1: Create a New GitHub Repository
1. Log in to [GitHub](https://github.com) and click **"New repository"**.
2. Name it (e.g., `nifty-morning-pulse` or `market-pulse`).
3. Set visibility to **Public** (required for free GitHub Pages).
4. Leave "Add a README file" unchecked (we already have one).
5. Click **Create repository**.

### Step 2: Push This Code to Your GitHub Repository
Open Terminal on your Mac, navigate to this directory, and run:

```bash
cd /Users/dhawal/.gemini/antigravity/scratch/nifty-morning-pulse

# Initialize git
git init
git add .
git commit -m "Initial commit: Nifty 8:00 AM Pre-Market Pulse Dashboard"

# Link to your new GitHub repository (replace with your repo URL)
git branch -M main
git remote add origin https://github.com/djtrades/marketpulse.git
git push -u origin main
```

### Step 3: Enable GitHub Pages in 2 Clicks
1. On GitHub, go to your repository's **Settings** tab.
2. In the left sidebar, click **Pages** (under the "Code and automation" section).
3. Under **Build and deployment** > **Source**, select:
   * **GitHub Actions**
4. That's it! GitHub Actions will now handle all builds automatically.

### Step 4: Run Your First Build
1. Click the **Actions** tab at the top of your GitHub repository.
2. In the left sidebar, click **"Daily 8:00 AM IST Nifty Pre-Market Pulse"**.
3. Click the **"Run workflow"** button on the right, select branch `main`, and click the green button.
4. The workflow will run in ~30 seconds, fetch the latest market numbers, and deploy.
5. Your public dashboard will be live at:
   `https://djtrades.github.io/marketpulse/`

You can bookmark this URL on your phone or send it to anyone!

---

## ⏰ Automated Daily Schedule

The workflow `.github/workflows/daily_pulse.yml` is scheduled using GitHub cron:
```yaml
schedule:
  - cron: '20 2 * * 1-5' # 02:20 UTC = 07:50 AM IST (Monday to Friday)
```
By the time you wake up and check your phone at 08:00 AM IST, the dashboard will already be updated with fresh overnight data.

---

## 💻 Running Locally (Optional)

If you ever want to run or test it locally on your computer:

```bash
cd /Users/dhawal/.gemini/antigravity/scratch/nifty-morning-pulse

# Run scanner
python3 market_scanner.py

# Open the generated dashboard in your browser
open index.html
```

---

## 🛠️ How to Edit & Customize Later

All code is cleanly decoupled in the `modules/` folder so you can customize anything anytime:

| To Change... | File to Edit | What You Can Do |
| :--- | :--- | :--- |
| **Add Bank Nifty / Fin Nifty** | `modules/nse_client.py` | Change `symbol="NIFTY"` to `"BANKNIFTY"` or pass multiple indices. |
| **Tweak POV & Trade Bias Rules** | `modules/pov_engine.py` | Adjust the point weights for Gift Nifty, PCR thresholds, or scenario text. |
| **Add More News Sources** | `modules/news_classifier.py` | Add new RSS URLs into the `RSS_FEEDS` array. |
| **Change Colors / Styling** | `modules/html_renderer.py` | Customize Tailwind classes, fonts, or add new widgets. |
| **Change Morning Trigger Time** | `.github/workflows/daily_pulse.yml` | Adjust the cron expression (e.g., `0 2 * * 1-5` for 07:30 AM IST). |

---

## ⚖️ Disclaimer
*This dashboard is built for educational, analytical, and informational purposes only. Options trading involves substantial risk. Derivative metrics and point-of-view scenarios are algorithmic heuristics and should not be construed as SEBI registered investment advice.*
