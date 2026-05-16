# Data Ingestion & Processing Architecture

## System Overview

```
[Data Sources] → [Ingestion Layer] → [Transformation] → [Brief Object] → [UI Rendering]
     (APIs)         (Batch/Real-time)   (Schema, Tier)      (JSON)        (Client)
```

---

## Data Pipeline

### Daily Batch (8 AM ET)

Runs before brief publication. Fetches yesterday's data + latest positioning.

```
08:00 AM: Trigger batch job
  ├─ FRED (macro): GET latest CPI, yields, spreads
  ├─ CBOE VIX: Fetch yesterday's close (daily snapshot)
  ├─ Treasury: Pull 10Y-2Y spread
  ├─ BLS (monthly): If month-end, fetch latest employment
  ├─ Alpha Vantage: Get SPX close + sentiment
  └─ CoinGecko: Fetch BTC/dominance

  Parallel queries (no blocking). Target: <5 sec total latency.

08:05 AM: Transform data
  ├─ Normalize all inputs to brief schema
  ├─ Calculate derived signals:
  │  ├─ Regime classification (calm/hot/stressed based on spreads+vol)
  │  ├─ Trend direction (yields up/down, spreads wide/tight)
  │  └─ Positioning consensus (from COT if Friday)
  └─ Assign source tiers (all FRED data = Tier S, etc.)

08:10 AM: Editor review window
  ├─ Brief preview generated (auto-filled with data)
  ├─ Editor reviews, adds narrative, updates caveats
  └─ Publishes brief (goes live)

08:15 AM: Brief live
  ├─ Email sent to subscribers
  ├─ App notifications fired
  └─ Watchlist alerts checked
```

### Weekly Batch (Friday 3:30 PM ET)

CFTC COT data releases at 3:30 PM Friday. Trigger immediate update.

```
15:30 PM: COT released by CFTC
  ├─ Fetch CFTC COT (disaggregated report)
  ├─ Transform: Extract ES, NQ, currency, commodity positioning
  ├─ Calculate: Hedge fund net long/short vs. commercials
  ├─ Compare: To prior week + 1-month average
  └─ Generate alert: "Large traders shifted [X]% short this week"

16:00 PM: Optional brief update
  ├─ If COT divergence detected (major positioning shift):
  │  └─ Email subscribers: "Friday positioning update"
  └─ Add to watchlist (if criteria triggered)
```

### Real-Time (Event-Driven)

Triggered by material events or data freshness milestones.

```
When 8-K filed (SEC EDGAR):
  ├─ Fetch 8-K details (URL, headline, filer)
  ├─ Categorize: bankruptcy/debt/M&A/insider-trading/etc.
  └─ Alert: "Material event: [Company] filed [Type] 8-K"

When VIX > 30:
  ├─ Fetch current VIX, VVIX, SKEW
  ├─ Check TradingView or CBOE site for latest
  └─ Alert: "VIX spike alert: [Value]"

When credit spreads spike (>25 bps in 1 day):
  ├─ Fetch IG OAS, HY OAS from FRED
  ├─ Calculate: Widening % vs. 20-day avg
  └─ Watchlist trigger: "Credit stress signal"
```

---

## Data Storage & Schema

### Brief Object (PostgreSQL)

```sql
briefs (
  id UUID PRIMARY KEY,
  date DATE NOT NULL,
  published_at TIMESTAMP,
  regime TEXT, -- 'calm' | 'hot' | 'stressed'
  regime_confidence INT, -- 0-100%
  thesis TEXT,
  brief_json JSONB, -- Full brief object (findings, sources, caveats, watchlist)
  
  INDEX (date DESC),
  INDEX (published_at DESC)
);

findings (
  id UUID PRIMARY KEY,
  brief_id UUID REFERENCES briefs(id),
  headline TEXT,
  confidence INT, -- 0-100%
  source_ids UUID[], -- Which sources cited
  watchlist_impact BOOLEAN,
  
  INDEX (brief_id)
);

sources (
  id UUID PRIMARY KEY,
  name TEXT UNIQUE, -- 'FRED_BAMLH0A0HYM2', 'CFTC_COT', 'CBOE_VIX'
  tier TEXT, -- 'S' | 'A' | 'B' | 'C'
  accuracy_30d DECIMAL, -- 0-1
  cry_wolf_rate DECIMAL, -- false alarm %
  track_record_count INT,
  last_updated TIMESTAMP,
  
  NO INDEX (small table, <50 sources)
);

source_accuracy_history (
  source_id UUID,
  date DATE,
  accuracy DECIMAL,
  briefs_using_this_source INT,
  
  INDEX (source_id, date DESC)
);

watchlist_items (
  id UUID PRIMARY KEY,
  brief_id UUID,
  trigger_condition TEXT, -- 'HY spreads > 350 bps'
  status TEXT, -- 'pending' | 'triggered' | 'resolved'
  resolution_date DATE,
  
  INDEX (brief_id, status)
);

data_freshness_log (
  source_name TEXT,
  date DATE,
  last_value DECIMAL,
  prior_value DECIMAL,
  change_pct DECIMAL,
  freshness_lag_hours INT, -- how old is this data?
  
  INDEX (source_name, date DESC)
);
```

### Brief JSON Structure

```json
{
  "id": "brief-2026-05-12",
  "date": "2026-05-12",
  "regime": {
    "label": "hot",
    "confidence": 84,
    "signals": [
      {"metric": "IG OAS", "value": 85, "normal_range": "75-100", "status": "normal"},
      {"metric": "HY OAS", "value": 235, "normal_range": "250-300", "status": "compressed"},
      {"metric": "VIX", "value": 24, "normal_range": "12-20", "status": "elevated"}
    ]
  },
  "thesis": "Growth regime, elevated valuations, crowded positioning",
  "findings": [
    {
      "id": "finding-1",
      "headline": "HY spreads compressed to 235 bps, risk-on appetite",
      "confidence": 92,
      "sources": ["FRED_BAMLH0A0HYM2"],
      "source_tiers": ["S"],
      "data_point": {
        "metric": "HY Master II OAS",
        "value": 235,
        "unit": "bps",
        "date": "2026-05-11",
        "change_from_week_ago": -18,
        "change_pct": -7.1
      },
      "context": "...explanation...",
      "archive_memory": "Last at this level: April 18. Preceded 8% SPX rally."
    }
  ],
  "sources": [
    {
      "id": "FRED_BAMLH0A0HYM2",
      "name": "ICE BofA HY OAS",
      "tier": "S",
      "accuracy_30d": 100,
      "cry_wolf_rate": 0,
      "freshness_lag": "same-day",
      "track_record": "Since 1995",
      "url": "https://fred.stlouisfed.org/series/BAMLH0A0HYM2"
    }
  ],
  "caveats": [
    {
      "id": "caveat-1",
      "text": "Positioning data lags 1 week (CFTC COT released Friday)",
      "affects_confidence": -5,
      "resolution": "Monitor via options flow, real-time alert when dealer gamma exposed"
    }
  ],
  "watchlist": [
    {
      "id": "watch-1",
      "condition": "HY spreads widen past 270 bps",
      "why": "Signals credit stress onset, equity correction likely to follow",
      "time_window": "Next 72 hours",
      "trigger_probability": "23%"
    }
  ],
  "metadata": {
    "published_at": "2026-05-12T08:15:00Z",
    "editor": "JJ",
    "sources_count": 7,
    "data_freshness": {
      "latest_data_point": "2026-05-11",
      "data_age_hours": 24,
      "any_missing_data": false
    }
  }
}
```

---

## Data Freshness SLA

| Data Source | Expected Freshness | SLA | Alert If | Fallback |
|---|---|---|---|---|
| FRED | Daily (1-7 day lag) | By 6 PM ET | Missing >7 days | Use prior day |
| CBOE VIX | Daily (same-day) | By 4:30 PM ET | Missing >4 hours | Use prior close |
| Treasury | Daily (same-day) | By 3:30 PM ET | Missing | Hard stop (yield curve critical) |
| CFTC COT | Weekly (Friday) | By 4:30 PM ET Friday | Missing | Note in brief ("data not yet available") |
| BLS | Monthly (1-2 week lag) | On release date | Missing >3 days | Use prior month |
| Alpha Vantage | Daily | By 6 PM ET | Missing >24h | Use prior close |
| CoinGecko | Real-time (1-min) | Continuous | Latency >5min | Note in brief |
| EDGAR 8-K | Real-time | Within 1 hour of filing | Missing | Monitored continuously |

---

## Monitoring & Alerting

### Data Quality Dashboard (Editor View)

```
Data Freshness Status
  FRED: ✓ Updated 5h ago
  VIX: ✓ Updated 24m ago
  Treasury: ✓ Updated 3h ago
  COT: Pending (Friday release expected 3:30 PM)
  BLS: Last update: May 10 (3d ago, normal for monthly)
  
Source Tier Confidence
  Tier S: 5/5 sources reporting
  Tier A: 2/2 sources reporting
  Tier B: 1/1 source reporting
  
Data Quality Alerts
  ⚠ Treasury yield curve has large bid-ask spread (>1 bp) — note in brief
  ⚠ CoinGecko latency: 4.2 min (within SLA but elevated)
  ✓ All required data present for brief publication
```

### Auto-Escalation Rules

```
IF any Tier S source missing >2 hours:
  → Email editor: "Critical data missing: [source]"
  → Delay brief publication until resolved
  → Or publish with caveat: "Awaiting [source] update"

IF data quality score drops <90%:
  → Flag brief as "partial" (not final)
  → Require editor acknowledgment before publish
  
IF watchlist trigger detected:
  → Immediately email subscribers
  → Add timestamp to watchlist resolution
  → Update brief in real-time
```

---

## Integration Points

### Batch Ingestion Job (Node.js, runs daily 8 AM)

```typescript
// /server/jobs/daily-brief-batch.ts
async function runDailyBatch() {
  const data = await Promise.all([
    fred.getLatestMacro(),
    cftc.getLatestCOT(), // if Friday
    cboe.getVIXSnapshot(),
    treasury.getYieldCurve(),
    sec.getLatest8Ks(),
    bls.getLatestLabor(), // if month-end
    alphavantage.getSPXPrice(),
    coingecko.getBTCPrice(),
  ]);
  
  const brief = transformToBriefSchema(data);
  await storage.saveBriefDraft(brief);
  
  // Editor reviews, publishes
  // Subscribers notified
}
```

### Real-Time Watchlist Checker (Runs every 10 min)

```typescript
// /server/jobs/watchlist-monitor.ts
async function checkWatchlistTriggers() {
  const activeBrief = await storage.getLatestBrief();
  
  for (const watchItem of activeBrief.watchlist) {
    const triggered = await evaluateTrigger(watchItem.condition);
    
    if (triggered) {
      await storage.updateWatchlistStatus(watchItem.id, 'triggered');
      await email.sendAlert(watchItem.id);
      await analytics.logEvent('watchlist_triggered', watchItem.id);
    }
  }
}
```

### Data Freshness Monitor (Runs every 1h)

```typescript
// /server/jobs/data-freshness-monitor.ts
async function checkDataFreshness() {
  const sources = await storage.getAllSources();
  
  for (const source of sources) {
    const freshness = await evaluateFreshness(source);
    
    if (freshness.statusCode === 'STALE') {
      await storage.logFreshnessAlert(source.id, freshness);
      await email.alertEditor(`Data stale: ${source.name}`);
    }
  }
}
```

---

## Cost Breakdown

| Component | Cost | Frequency | Notes |
|---|---|---|---|
| FRED API | $0 | Daily | Unlimited free tier |
| CBOE VIX | $0 | Daily | Downloaded as CSV |
| Treasury | $0 | Daily | REST API |
| CFTC COT | $0 | Weekly | Free API or Python wrapper |
| BLS | $0 | Monthly | Free API |
| SEC EDGAR | $0 | Real-time | Free REST API |
| Alpha Vantage | $0-60/mo | Daily | Free tier sufficient |
| CoinGecko | $0-129/mo | Real-time | Free tier sufficient |
| **Tier 1 Total** | **$0** | | |
| FlashAlpha | $79/mo | Daily | Options flow |
| Finnhub | $99/mo | Real-time | News + ETF flows |
| EODHD | $19/mo | Daily | Sentiment + fundamentals |
| **Tier 2 Total** | **$197/mo** | | |
| **Server hosting** | $50-100/mo | Continuous | Vercel + Railway |
| **Database** | $15-50/mo | Continuous | PostgreSQL managed |
| **Cache (Redis)** | $5-20/mo | Continuous | Optional, for scaling |
| **Monitoring** | $50-100/mo | Continuous | Sentry + basic monitoring |
| **MVP Total** | **$120-270/mo** | | Tier 1 + server costs |
| **v1 Paid Launch** | **$317-470/mo** | | Tier 1 + Tier 2 + server |

All free data sources are sufficient for MVP. Tier 2 unlocks real-time alerting + deeper analysis.
