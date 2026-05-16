# Brief Schema Mapping: Data Sources to Brief Components

## Signal Flow: Raw Data → Brief Object

```
Data Layer (APIs)
    ↓
Transform Layer (Normalize, calculate derived metrics)
    ↓
Signal Layer (Classify regime, identify findings, set confidence)
    ↓
Brief Layer (Narrative + structure + caveats)
    ↓
Publication Layer (Email, app, web)
```

---

## Regime Classification Matrix

### Input Signals

| Signal | Data Source | Tier | Normal Range | Alert Threshold |
|--------|-------------|------|--------------|-----------------|
| **IG OAS** | FRED BAMLC0A0CM | S | 75-100 bps | <75 (compressed) / >120 (stressed) |
| **HY OAS** | FRED BAMLH0A0HYM2 | S | 250-300 bps | <230 (excess risk) / >350 (crisis) |
| **VIX** | CBOE (daily snapshot) | S | 12-20 | >25 (alert) / >30 (high) / >40 (extreme) |
| **10Y Yield** | Treasury API | S | 3.5-4.5% | Rising (inflation) / Falling (flight-to-safety) |
| **10-2 Spread** | Treasury (yield difference) | S | 0.5-2.5% | <0% (inverted, recession signal) |
| **VIX Term Structure** | CBOE (VX1 vs VX2 futures) | A | Contango normal | Backwardation (crisis) |
| **HY vs. IG Spread** | FRED (BAMLH0A0HYM2 - BAMLC0A0CM) | S | 150-200 bps | >250 bps (widening) |
| **Non-Commercial COT** | CFTC COT (disaggregated) | S | Baseline varies | Extreme long/short (>+2σ) |
| **VVIX** | FRED VVIXCLS | A | 70-90 | >110 (fear) / <60 (complacency) |
| **SPX Trend** | Alpha Vantage daily | A | Price trend | New 52w high/low |
| **USD Strength** | FX APIs (DXY proxy) | B | Index 100-105 | >105 (strong) / <95 (weak) |
| **BTC Dominance** | CoinGecko | B | 40-50% | >60% (risk-off) / <40% (risk-on) |
| **Job Openings (JOLTS)** | BLS (monthly) | S | 3.5-4.5M | >5M (tight labor) / <3M (slack) |
| **Unemployment** | BLS (monthly) | S | 3.5-4.5% | <3.5% (tight) / >5% (slack) |

### Regime Classification Logic

```
CALM (Growth, low volatility):
  ✓ IG OAS <90 bps
  ✓ HY OAS <280 bps
  ✓ VIX <18
  ✓ 10-2 spread positive (not inverted)
  ✓ VVIX <85
  ✓ Non-commercials net long (COT)
  → Confidence = % of signals present × 100
  → Typically 80-95% confidence

HOT (Risk-on, momentum, elevated volatility):
  ✓ IG OAS 90-115 bps
  ✓ HY OAS 280-330 bps
  ✓ VIX 18-28
  ✓ 10-2 spread positive
  ✓ VVIX 85-110
  ✓ Non-commercials crowded long (COT divergence)
  → Typical 75-90% confidence

STRESSED (Risk-off, crisis signals):
  ✓ IG OAS >120 bps OR widening >20 bps from yesterday
  ✓ HY OAS >330 bps
  ✓ VIX >28
  ✓ 10-2 spread <0.5% (flattening) or negative (inverted)
  ✓ VVIX >110
  ✓ Non-commercials shifting short (COT reversal)
  → Typical 85-99% confidence
```

---

## Finding-to-Source Mapping

### Finding Type 1: Credit Stress Signal

```json
{
  "finding_id": "credit-stress-001",
  "headline": "HY credit spreads widened 35 bps this week, signaling stress",
  "sources_required": [
    {
      "source_id": "FRED_BAMLH0A0HYM2",
      "source_name": "ICE BofA HY OAS",
      "tier": "S",
      "data_point": {
        "current": 285,
        "week_ago": 250,
        "change": 35,
        "unit": "bps"
      }
    }
  ],
  "confidence_calculation": {
    "base": 95, // Tier S source, excellent track record
    "adjustments": [
      { "factor": "single_source", "adjustment": -5 }, // Only 1 source, cross-check needed
      { "factor": "cftc_confirms", "adjustment": +5 } // If COT shows stress, add confidence
    ],
    "final_confidence": 95
  },
  "archive_context": {
    "last_time_happened": "April 15 (4 weeks ago)",
    "outcome_then": "Led to 8% SPX correction",
    "frequency": "3 times in past 12 months"
  }
}
```

**Data Sources Used:**
- FRED (HY OAS)
- Optional: CFTC COT (if stress confirmed by positioning)
- Archive (prior credit spreads)

**Confidence Drivers:**
- Tier S source = high confidence
- Single source = lower confidence (need cross-check)
- Historical precedent = higher confidence

---

### Finding Type 2: Positioning Divergence

```json
{
  "finding_id": "positioning-divergence-001",
  "headline": "Hedge funds net long ES at 6-month high while commercials reduce exposure",
  "sources_required": [
    {
      "source_id": "CFTC_COT_disaggregated",
      "source_name": "CFTC COT Disaggregated (ES futures)",
      "tier": "S",
      "data_point": {
        "non_commercial_net_long": 15200, // contracts
        "commercial_net_short": 8500,
        "divergence_signal": "EXTREME_LONG"
      }
    }
  ],
  "confidence_calculation": {
    "base": 92,
    "adjustments": [
      { "factor": "consensus_crowded", "adjustment": -8 } // High divergence = elevated reversal risk
    ],
    "final_confidence": 84
  },
  "trigger_watchlist": true,
  "watchlist_condition": "Non-commercial positioning reverses >15%, likely 2-3 day correction"
}
```

**Data Sources Used:**
- CFTC COT (disaggregated report, releases Friday 3:30 PM)
- Optional: Options gamma exposure (FlashAlpha) for real-time confirmation

**Confidence Drivers:**
- COT data = Tier S (official source)
- Divergence magnitude = confidence modifier (higher divergence = more risk)
- Timeliness = Friday release (1-week lag, noted in caveats)

---

### Finding Type 3: Volatility Regime Shift

```json
{
  "finding_id": "vol-regime-001",
  "headline": "VIX term structure inverted for 3rd consecutive day—dealer stress evident",
  "sources_required": [
    {
      "source_id": "CBOE_VIX",
      "source_name": "CBOE VIX (spot)",
      "tier": "S",
      "data_point": {
        "value": 28,
        "change_from_yesterday": 3
      }
    },
    {
      "source_id": "CBOE_VIX_TERM",
      "source_name": "VIX Futures Term Structure (VX1 vs VX2)",
      "tier": "A",
      "data_point": {
        "vx1": 31,
        "vx2": 28,
        "status": "backwardation"
      }
    }
  ],
  "confidence_calculation": {
    "base": 88,
    "adjustments": [
      { "factor": "term_structure_inverted", "adjustment": +5 },
      { "factor": "multi_day_pattern", "adjustment": +4 }
    ],
    "final_confidence": 97
  },
  "trigger_watchlist": true,
  "watchlist_condition": "If VIX breaks 32, dealers must rebalance → cascade vol spike likely"
}
```

**Data Sources Used:**
- CBOE VIX (daily snapshot)
- VIX term structure (VX1/VX2 futures prices)
- Optional: VVIX (vol of vol) for confirmation

**Confidence Drivers:**
- Real-time data = immediate signal
- Term structure shape = directional confidence
- Persistence (3 days) = stronger signal than 1-day spike

---

### Finding Type 4: Labor Market Slack

```json
{
  "finding_id": "labor-001",
  "headline": "Job openings fell to 3.8M, lowest in 2 years—recession risk rising",
  "sources_required": [
    {
      "source_id": "BLS_JOLTS",
      "source_name": "BLS JOLTS (Job Openings)",
      "tier": "S",
      "data_point": {
        "current": 3800000,
        "month_ago": 4100000,
        "change_pct": -7.3
      }
    }
  ],
  "confidence_calculation": {
    "base": 85,
    "adjustments": [
      { "factor": "data_lag_30days", "adjustment": -5 }, // Monthly data, 1-2 week lag
      { "factor": "leading_indicator", "adjustment": +10 } // JOLTS leads unemployment
    ],
    "final_confidence": 90
  },
  "caveat": "Data is from April, 3 weeks old. Will refresh in early May.",
  "context": "JOLTS typically leads unemployment change by 6-8 weeks"
}
```

**Data Sources Used:**
- BLS JOLTS (monthly)

**Confidence Drivers:**
- Official government source = Tier S
- Leading indicator status = high value despite lag
- Month-old data = acknowledged caveat

---

### Finding Type 5: Insider Activity

```json
{
  "finding_id": "insider-001",
  "headline": "Tech insider buying surged this week—contrarian signal?",
  "sources_required": [
    {
      "source_id": "SEC_FORM_4",
      "source_name": "SEC Form 4 Insider Filings",
      "tier": "A",
      "data_point": {
        "filings_this_week": 34,
        "net_buys": 22,
        "net_sells": 12,
        "buy_sell_ratio": 1.83
      }
    }
  ],
  "confidence_calculation": {
    "base": 72,
    "adjustments": [
      { "factor": "correlation_weak", "adjustment": -12 }, // Not all insider buying = bottom
      { "factor": "sample_size", "adjustment": -5 } // Only 34 filings, small sample
    ],
    "final_confidence": 55
  },
  "caveat": "Insider buying is contrarian but not reliable short-term. Use as context, not signal.",
  "trigger_watchlist": false
}
```

**Data Sources Used:**
- SEC EDGAR Form 4 (real-time)

**Confidence Drivers:**
- Real-time data = immediate awareness
- Weak historical correlation = lower confidence
- Low conviction finding (55%) = adds to context, not main signal

---

## Caveat-to-Source Mapping

### Caveat Type 1: Data Lag

```json
{
  "caveat_id": "lag-001",
  "text": "CFTC COT positioning data is 1 week old (released Friday for prior Tuesday close)",
  "affects_confidence": -5,
  "resolution": "Monitor options gamma exposure (real-time) + watch for COT divergence confirmation",
  "data_source": "CFTC_COT",
  "time_to_resolution": "Friday 3:30 PM ET (next COT release)"
}
```

### Caveat Type 2: Insufficient Data

```json
{
  "caveat_id": "insufficient-002",
  "text": "Insider Form 4 buying is elevated, but sample size is small (only 34 filings this week vs. 50 typical)",
  "affects_confidence": -8,
  "resolution": "Monitor if buying trend persists next 2 weeks before acting",
  "data_source": "SEC_FORM_4",
  "time_to_resolution": "5-7 days (1-2 trading weeks)"
}
```

### Caveat Type 3: Contradictory Signals

```json
{
  "caveat_id": "contradiction-001",
  "text": "Credit spreads are tight (risk-on signal) but non-commercials are reducing long positions (caution signal). Conflicting regime indicators.",
  "affects_confidence": -10,
  "resolution": "Which signal wins? Typically credit spreads lead equities by 3-6 weeks. Favor spreads.",
  "sources": ["FRED_BAMLH0A0HYM2", "CFTC_COT_disaggregated"],
  "time_to_resolution": "2-4 weeks (see which signal resolves first)"
}
```

---

## Watchlist-to-Source Mapping

### Watchlist Trigger 1: Credit Spread Spike

```json
{
  "watchlist_id": "watch-credit-001",
  "trigger_condition": "HY OAS widens >30 bps in 1 day OR >50 bps in 1 week",
  "data_sources": [
    {
      "source": "FRED_BAMLH0A0HYM2",
      "polling_frequency": "Daily, 6 PM ET",
      "calculation": "abs(today - yesterday) > 30 bps"
    }
  ],
  "action_on_trigger": {
    "email_subscribers": true,
    "brief_update": true,
    "watchlist_status": "TRIGGERED",
    "watchlist_message": "Credit stress signal activated. Monitor SPX for corrections."
  },
  "probability_estimate": "23%", // How often does this trigger, and when it does, how often is it actionable?
  "resolution_criteria": "HY OAS stabilizes above 260 bps for 2 consecutive days"
}
```

### Watchlist Trigger 2: COT Divergence Reversal

```json
{
  "watchlist_id": "watch-cot-001",
  "trigger_condition": "Non-commercial net long in ES reverses >10% week-over-week (especially if >+2σ previously)",
  "data_sources": [
    {
      "source": "CFTC_COT_disaggregated",
      "polling_frequency": "Every Friday 3:30 PM ET",
      "calculation": "week_to_week_change > -10%"
    }
  ],
  "action_on_trigger": {
    "email_subscribers": true,
    "brief_update": true,
    "watchlist_status": "TRIGGERED",
    "watchlist_message": "Hedge fund positioning reversed sharply. Likely 2-5% correction over next 1-2 weeks."
  },
  "probability_estimate": "18%",
  "resolution_criteria": "COT confirms follow-through for 2 consecutive weeks OR SPX corrects >3%"
}
```

### Watchlist Trigger 3: Yield Curve Inversion

```json
{
  "watchlist_id": "watch-curve-001",
  "trigger_condition": "10-2 spread becomes negative for first time in this cycle",
  "data_sources": [
    {
      "source": "TREASURY_YIELDS",
      "polling_frequency": "Daily, 3:30 PM ET",
      "calculation": "DGS10 - DGS2 < 0"
    }
  ],
  "action_on_trigger": {
    "email_subscribers": true,
    "brief_update": true,
    "watchlist_status": "TRIGGERED",
    "watchlist_message": "Curve inverted—recession signal. Historical lead time: 6-12 months to slowdown."
  },
  "probability_estimate": "~10% annually",
  "resolution_criteria": "Curve normalizes (unlikely) OR recession begins (6-12 months)"
}
```

---

## Source Tier Assignment Rules

### Tier S (Highest Reliability)

```
✓ Government source OR
✓ Standardized methodology (CBOE, ICE) OR
✓ >20 years track record in our briefs AND accuracy >85%

Sources: FRED, BLS, Treasury, CFTC, SEC, CBOE VIX, credit spreads
```

### Tier A (High Quality, Minor Limitations)

```
✓ Official exchange/regulator data, but with lag OR
✓ Derived from Tier S data but with methodological transformation OR
✓ 5+ years history in our briefs AND accuracy >80%

Sources: VIX term structure, EDGAR fundamentals, options gamma estimates
```

### Tier B (Good, Contextual)

```
✓ Private company proprietary computation OR
✓ Newer track record (2-5 years) AND accuracy >75% OR
✓ Requires cross-checking with other sources

Sources: Sentiment scores, fund flow estimates, crypto metrics
```

### Tier C (Informational Only)

```
✓ Nascent/experimental data OR
✓ Unreliable track record OR
✓ Must always be paired with Tier S/A confirmation

Sources: Social sentiment, niche alternative data
```

---

## Monthly Source Accuracy Review

Every month, calculate source reliability:

```
Source accuracy = # of times source was cited in finding AND finding aged well (no contradictions) / total # of findings citing source

E.g., FRED BAMLH0A0HYM2 cited in 12 findings in May. 11 aged well (brief held), 1 contradicted. Accuracy = 11/12 = 91.7%
```

**Action Thresholds:**
- Accuracy <75% → Demote to Tier B
- Accuracy <50% → Add caveat ("This source recently unreliable")
- Accuracy 95%+ → Promote to Tier S (if not already)

Update public source scoreboard monthly. This becomes a moat.
