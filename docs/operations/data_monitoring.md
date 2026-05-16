# Data Monitoring & Operational Procedures

## Data Freshness Dashboard

Real-time status board (editor-facing). Updates every 1 hour.

```
CRITICAL STATUS
═══════════════════════════════════════════════════════════════════

Data Freshness (All Tier S sources required for brief publication)
├─ FRED (macro + spreads): ✓ Updated 3h ago (within 24h SLA)
├─ CBOE VIX: ✓ Updated 24m ago (within same-day SLA)
├─ Treasury yields: ✓ Updated 2h ago (within same-day SLA)
├─ CFTC COT: ⏳ Pending (Friday 3:30 PM ET, will arrive in ~6h)
├─ BLS labor: ✓ Last update May 10 (monthly, on schedule)
├─ SEC EDGAR 8-K: ✓ 2 new filings in last hour
│  ├─ XYZ Corp bankruptcy filing
│  └─ ABC Inc. debt raise announcement
└─ Alpha Vantage: ✓ SPX closed $500 (updated 4h ago)

Tier A Sources (Optional, enhances brief)
├─ VVIX: ✓ Updated 24m ago
├─ Options flow (FlashAlpha): ✓ Updated daily (waiting for today's close)
└─ Finnhub news: ✓ Real-time (147 articles since 8 AM)

QUALITY ALERTS
═══════════════════════════════════════════════════════════════════
⚠ Treasury Bid-Ask Spread Alert: 10Y yield has 1.4bp spread (elevated, note in brief)
⚠ CoinGecko Latency: 4.2 minutes (within SLA but elevated)
✓ All Tier S sources available—brief can publish

READY FOR PUBLICATION
```

---

## Monitoring Rules Engine

### Rule 1: Critical Data Missing

```
IF any Tier S source missing >2 hours:
  THEN:
    1. Alert editor: "CRITICAL: [source_name] data not available"
    2. Suggest pause brief publication (if <30 min to deadline, OK to proceed with caveat)
    3. Log event in data quality history
    
EXAMPLE:
  "FRED API returns 500 error for HY OAS request"
  → Alert fired at 10:05 AM
  → Retry every 5 min until recovered
  → If not recovered by 11:00 AM, ask editor: "Proceed without credit spreads finding?"
```

### Rule 2: Stale Data Detection

```
IF data age exceeds SLA:
  THEN:
    1. Flag in dashboard with ⚠ symbol
    2. If Tier S: might delay brief (depends on severity)
    3. If Tier A: note in caveat ("Options flow data pending")
    
SLA Thresholds:
  FRED: 24 hours (refresh daily)
  VIX: 4 hours (should be same-day)
  Treasury: 6 hours (should be same-day)
  CFTC COT: Friday 3:30 PM + 2 hours (weekly, so wider window)
  BLS: 14 days (monthly data, lag is normal)
```

### Rule 3: Data Quality Degradation

```
IF data quality score drops <90%:
  THEN:
    1. Flag brief as "INCOMPLETE" (require editor ack to publish)
    2. Highlight which sources are problematic
    3. Suggest alternative data sources to include
    
Quality Score = % of Tier S sources reporting + % of data points valid
EXAMPLE:
  5 Tier S sources required
  4 reporting OK, 1 reporting stale data
  Quality = 4/5 = 80% → ALERT
```

### Rule 4: Watchlist Trigger Detection

```
IF any watchlist condition evaluates TRUE:
  THEN:
    1. Immediately notify subscribers (email + in-app)
    2. Update watchlist status to "TRIGGERED"
    3. Log trigger event + data point that triggered it
    4. Offer editor option to update brief with breaking context
    
Example trigger:
  "HY OAS spiked from 235 to 268 bps (33 bps in 1 day)"
  → Watchlist #1 triggered: "Widening >30 bps"
  → Email: "WATCHLIST ALERT: Credit stress signal—HY OAS spiked 33 bps today"
  → Subscriber can click to see updated brief with context
```

### Rule 5: Anomaly Detection

```
IF data point moves >2 standard deviations in 1 day:
  THEN:
    1. Flag for editor review (might be data error, might be real event)
    2. Cross-check with other sources (e.g., if VIX spikes, check VVIX)
    3. If confirmed: add to brief findings
    4. If error: flag as data quality issue
    
Example:
  "VIX jumps from 18 to 34 (+17 in 1 day)"
  → Is VVIX also elevated? (confirms stress)
  → Are credit spreads widening? (confirms stress)
  → If all confirmed: major finding in brief
  → If VIX alone spiking: might be options expiry artifact (note caveat)
```

---

## Source Reliability Scoring

### Monthly Accuracy Calculation

```
For each source in month:
  1. Count how many findings cited this source
  2. Review each finding: did it age well? (is position still valid today?)
  3. If finding contradicted later: mark as "wrong"
  4. If finding proven right or still pending: mark as "valid"
  5. Calculate: accuracy = valid findings / total findings
  
EXAMPLE (May):
  FRED HY OAS cited in 12 findings:
    ├─ Finding 1: "Spreads compressed" → Aged well ✓
    ├─ Finding 2: "Credit strength" → Aged well ✓
    ├─ Finding 3: "Widening likely" → Later contradicted (spreads fell further) ✗
    ├─ Finding 4-12: (9 findings, all aged well) ✓
    
  Accuracy = 11/12 = 91.7%
  Confidence band: ±5% (based on sample size 12)
  Track record: "11 correct out of 12 predictions in May"
```

### Cry-Wolf Rate (False Alarms)

```
For each source, track how often it triggers watchlist incorrectly:

EXAMPLE:
  FlashAlpha "GEX goes negative" used in 8 watchlist triggers in May
  Of those 8: 6 led to vol spike within 2 days, 2 did not
  Cry-wolf rate = 2/8 = 25%
  
Interpretation: When FlashAlpha says "dealer stress", 75% of time it's right.
When cry-wolf rate >30%: demote to Tier B or add caveat ("Often false alarms")
```

### Historical Track Record

```
For each source, maintain running stats:

CFTC COT (since 2015, ~250 briefs using this source):
  ├─ Total findings citing COT: 247
  ├─ Correct/valid: 206 (83.4%)
  ├─ Wrong/contradicted: 25 (10.1%)
  ├─ Pending (too recent to judge): 16 (6.5%)
  ├─ Cry-wolf rate: 12% (divergence often signals reversals, but not always immediate)
  ├─ Lead time: Average 1.8 weeks for COT divergence reversal to show in prices
  └─ Confidence: 83.4% accuracy → Tier S

FRED HY OAS (since 2015, ~300 briefs):
  ├─ Total findings: 298
  ├─ Correct/valid: 289 (97.0%)
  ├─ Wrong: 5 (1.7%)
  ├─ Pending: 4 (1.3%)
  ├─ Cry-wolf rate: 4% (very reliable)
  ├─ Lead time: Average 2-3 weeks before equity correction
  └─ Confidence: 97% accuracy → Tier S (highest tier)

Alpha Vantage sentiment (since 2022, ~80 briefs):
  ├─ Total findings: 78
  ├─ Correct/valid: 58 (74.4%)
  ├─ Wrong: 14 (17.9%)
  ├─ Pending: 6 (7.7%)
  ├─ Cry-wolf rate: 38% (noisy, often contradicted)
  ├─ Lead time: Unreliable (sentiment can whipsaw)
  └─ Confidence: 74% accuracy → Tier B (context only)
```

---

## Alerting Strategy

### Alert Types & Channels

| Alert Type | Condition | Channel | Recipient | Urgency |
|---|---|---|---|---|
| **Data Critical** | Tier S source missing >2h | Slack + Email | Editor | CRITICAL |
| **Data Stale** | Source exceeds SLA | Slack | Editor | HIGH |
| **Quality Degraded** | Quality score <90% | Email | Editor | MEDIUM |
| **Watchlist Triggered** | Condition evaluates true | Email + In-app + Slack | All subscribers + Editor | HIGH |
| **Anomaly Detected** | Data moves >2σ | Slack | Editor | MEDIUM |
| **Source Accuracy Down** | Monthly accuracy drops <80% | Email | Editor | MEDIUM |
| **8-K Filing (Material)** | Bankruptcy, debt, insider | Email | Editor | MEDIUM |
| **Archive Query** | Trader searches "recession" | Email (weekly) | Editor | LOW |

### Slack Notification Examples

```
🔴 CRITICAL: FRED API Unavailable
   HY OAS data missing >2 hours. Brief publication blocked.
   Retrying every 5 min. Estimate: resolved by 11:30 AM.
   [Retry Now] [Proceed Without] [Delay Publication]

🟡 Watchlist Triggered: Credit Spike
   HY OAS widened from 235 to 268 bps (33 bps in 1 day).
   Trigger probability: 23%. Email sent to subscribers.
   [View Brief Context] [Update Watchlist]

🟢 Good News: Source Accuracy Up
   FRED HY OAS hit 98% accuracy (highest on record).
   Confidence in credit findings: VERY HIGH.
```

### Email Alert Examples

```
TO: subscribers@living-briefs.com

Subject: WATCHLIST ALERT: Credit Stress Signal

Your watchlist item triggered today:
  "HY spreads widen >30 bps in 1 day"
  
What happened:
  High-yield credit spreads (HY OAS) spiked from 235 to 268 bps today
  (33 basis points in a single day).
  
Why it matters:
  This is the steepest 1-day widening in 6 weeks. Historical precedent:
  Last time this happened (April 15), led to 8% SPX correction in following week.
  
What to do:
  1. Review today's brief for credit stress findings
  2. Audit your portfolio for high-beta exposure
  3. Consider tightening stops or hedging
  4. Monitor tomorrow's credit market opening
  
Next steps:
  Watchlist will update when HY OAS stabilizes (>260 bps for 2 consecutive days)
  or SPX falls >3% (whichever comes first).
  
Questions? Ask the Brief: "What should I worry about now?"

https://living-briefs.com/brief/2026-05-12
```

---

## Data Quality Incident Response

### Incident: Data Source Down

```
11:00 AM: FRED API returns 503 (Service Unavailable)
          Affects: HY OAS, IG OAS, VIX, yields

Action:
  1. Immediately alert editor: "FRED down, retrying every 5 min"
  2. Check FRED status page (https://fred.stlouisfed.org/status)
  3. Check Slack/Twitter for outage reports (is it global?)
  4. If >30 min down: try fallback sources
     └─ IG OAS: Use ICE website direct
     └─ HY OAS: Use Bloomberg (if available)
  5. If outage continues >1h: decide
     └─ Delay brief publication until resolved (safest)
     └─ Or publish brief with caveat: "Credit data not available, using alternative sources"

Recovery:
  Once FRED returns: verify data is correct (check timestamps)
  Log incident: "FRED outage 11:00-11:45 AM, duration 45 min"
  Monitor for similar incidents (patterns = signal)
```

### Incident: Data Quality Error

```
4:30 PM: CFTC COT data looks wrong (non-commercial COT at absurd level, 10x normal)

Investigation:
  1. Cross-check against prior week: is it a massive position shift?
  2. Check CFTC website directly (is the error in our parser or CFTC data?)
  3. Check news: did something massive happen in futures markets? (e.g., major fund blow-up)
  4. Reach out to CFTC if necessary (unlikely but possible)
  
Resolution:
  If error is ours: fix parser, re-pull data
  If error is CFTC: use prior week's data, note caveat in brief
  If real data: include in brief but flag as unusual (use this for finding)
  
Log: "COT data quality issue, false alarm, used prior week instead"
```

### Incident: Source Track Record Degrades

```
June 1: End-of-month accuracy review shows Alpha Vantage sentiment dropped to 62% (was 74%)

Investigation:
  1. Did market regime change? (might explain why sentiment underperforms)
  2. Are we using sentiment correctly? (are we cherry-picking signals?)
  3. Compare to other sentiment providers (is problem universal or just Alpha Vantage?)
  
Decision:
  Demote Alpha Vantage sentiment from Tier B to Tier C (informational only)
  Use caveat: "Sentiment data has had poor accuracy recently (62% hit rate in May)"
  Plan: Test alternative sentiment providers (Finnhub, FinBERT)
  
Update public scoreboard: Show Alpha Vantage accuracy history (builds trust)
```

---

## Operational Checklists

### Daily Brief Publication Checklist (8 AM)

```
□ FRED data available (macro + credit spreads)
□ CBOE VIX snapshot fetched
□ Treasury yields pulled
□ SPX price updated
□ BLS data current (if month-end)
□ SEC EDGAR 8-Ks reviewed for material filings
□ Data quality score >90%
□ All Tier S sources reporting
□ No stale data >SLA
□ Editor reviewed brief draft
□ Caveats up-to-date
□ Watchlist conditions re-evaluated
□ Brief published
□ Subscribers notified (email + app)
□ Archive entry created
```

### Weekly COT Review (Friday 3:30 PM)

```
□ CFTC COT data released
□ Downloaded disaggregated report
□ Parsed large trader positioning (ES, NQ, currencies, commodities)
□ Compared to prior week + 1-month average
□ Calculated hedge fund divergence
□ If divergence >2σ: add to Saturday brief update
□ Updated public COT scoreboard
□ Logged for track record purposes
```

### Monthly Source Accuracy Review (First of month)

```
□ Calculated accuracy for all Tier S sources
□ Calculated cry-wolf rates
□ Identified any sources dropping <80% accuracy
□ Updated source tier assignments (promote/demote as needed)
□ Published updated source scoreboard
□ Identified underperforming sources (need replacement)
□ Identified overperforming sources (highlight to readers)
□ Logged findings in data quality history
□ Plan next month's integration priorities
```

### Quarterly Data Stack Review (Every 3 months)

```
□ Review cost breakdown (Tier 1 + Tier 2 costs)
□ Evaluate API reliability (uptime %, incident count)
□ Audit data quality metrics (average accuracy across all sources)
□ Identify any new data sources worth integrating
□ Benchmark against competitors (if any)
□ Plan for Q2 (what new data sources do we need?)
□ Update SOURCES_AND_DATA.md with latest findings
```

---

## Cost Optimization

### Current Stack Cost

| Component | Cost | Value |
|---|---|---|
| FRED | $0 | Essential (macro foundation) |
| CFTC | $0 | Essential (positioning data) |
| Treasury | $0 | Essential (yields) |
| BLS | $0 | Essential (labor) |
| SEC EDGAR | $0 | Essential (8-K alerts) |
| CBOE VIX | $0 | Essential (regime indicator) |
| Alpha Vantage | $0 (free tier) | Good (equity prices) |
| CoinGecko | $0 (free tier) | Useful (crypto signal) |
| **Tier 1 Total** | **$0** | |
| FlashAlpha | $79/mo | High ROI (options flow is predictive) |
| Finnhub | $99/mo | Medium ROI (news useful, sentiment noisy) |
| EODHD | $19/mo | Low ROI (sentiment redundant if Finnhub) |
| **Tier 2 Total** | **$197/mo** | |
| **Server/DB/Monitoring** | **$120-200/mo** | |
| **Total MVP Stack** | **$320-400/mo** | |

### Cost Reduction Strategies

**If budget tight (<$300/mo):**
- Keep Tier 1 ($0)
- Drop EODHD ($19, use Finnhub sentiment instead)
- Drop FlashAlpha ($79, use free options flow data from market data APIs)
- Keep Finnhub ($99)
- Result: ~$100/mo premium tier, $200-300 total

**If targeting profitability:**
- MVP: $0 data + $150 server = $150/mo total (sustainable on 50 paid users @ $5/mo)
- v1: Add FlashAlpha + Finnhub ($178 data + $150 server) = $330/mo (sustainable on 300 paid users @ $2/mo or 50 @ $8/mo)
- Scale: Add Databento ($199) for order flow = $530/mo data (unsustainable until 500+ users)

---

## KPIs & Reporting

### Monthly Data Quality Report

```
Living Briefs Data Quality — May 2026

Availability:
  FRED: 100% (8/8 data pulls successful)
  CBOE VIX: 100% (21/21 daily snapshots)
  Treasury: 100% (21/21 daily pulls)
  CFTC COT: 100% (1/1 Friday release captured)
  BLS: 100% (on schedule)
  SEC EDGAR: 99% (1 missed 8-K, caught by manual review)
  Alpha Vantage: 100% (21/21 daily)
  
Freshness:
  Average data age when published: 12 hours
  Data exceeding SLA: 0 times
  
Quality:
  Average accuracy across sources: 84.6%
  Sources improving: FRED (94%), CBOE (96%)
  Sources declining: Alpha Vantage (62%), Finnhub sentiment (70%)
  
Incidents:
  Total: 2
    1. FRED momentary 503 error (recovered <5 min)
    2. CoinGecko API latency spike (noted in caveat)
  
Reliability Score: 98.5% (excellent)
```

Use this to demonstrate data integrity to users + identify improvement areas.
