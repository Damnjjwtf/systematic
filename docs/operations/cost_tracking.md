# Cost Tracking Dashboard

**Purpose:** Monitor and optimize data + infrastructure costs monthly. Track Tier 1 vs. Tier 2 spending to inform go-live decisions.

**Target:** 15-minute setup, automatic monthly reporting.

---

## Architecture Overview

```
[API Call Log] → [Cost Attribution] → [Monthly Aggregation] → [Dashboard] → [Report]
  (Every fetch)      (Per-source)         (By date)           (Real-time)   (PDF/Slack)
```

---

## Cost Model

### Tier 1 (Free Data, $0/month)
- FRED: $0
- CFTC COT: $0
- Treasury: $0
- BLS: $0
- SEC EDGAR: $0
- CBOE VIX: $0
- Alpha Vantage: $0 (free tier sufficient)
- CoinGecko: $0 (free tier sufficient)

**Total Tier 1 Data:** $0

### Tier 2 (Paid APIs, ~$200/month)
- FlashAlpha: $79/mo
- Finnhub: $99/mo
- EODHD: $19/mo

**Total Tier 2 Data:** $197/mo

### Infrastructure (Baseline)
- Vercel hosting: $20-50/mo (standard plan)
- PostgreSQL database: $15-30/mo (managed, Neon)
- Monitoring + logging: $20-50/mo (Sentry, basic monitoring)
- Cache/Redis (optional): $5-20/mo

**Total Infrastructure:** $60-150/mo

### Grand Total
- **MVP (Tier 1 only):** $60-150/mo
- **v1 (Tier 1 + Tier 2):** $257-350/mo

---

## Data Collection Layer

### 1. Log Every API Call (Automatic)

Add to each API integration:

```typescript
// server/integrations/fred.ts

async function fetchFREDData(seriesId: string) {
  const startTime = Date.now();
  
  try {
    const response = await fetch(fredUrl);
    const duration = Date.now() - startTime;
    
    // Log cost attribution
    await costLog.record({
      source: 'FRED',
      seriesId: seriesId,
      tier: 'S',
      cost: 0,
      apiCalls: 1,
      duration: duration,
      success: response.ok,
      timestamp: new Date(),
      dataAge: calculateDataAge(response)
    });
    
    return response.json();
  } catch (error) {
    await costLog.record({
      source: 'FRED',
      seriesId: seriesId,
      tier: 'S',
      cost: 0,
      apiCalls: 1,
      duration: Date.now() - startTime,
      success: false,
      error: error.message,
      timestamp: new Date()
    });
    throw error;
  }
}
```

### 2. PostgreSQL Schema for Cost Tracking

```sql
CREATE TABLE cost_log (
  id UUID PRIMARY KEY,
  source_name TEXT NOT NULL, -- 'FRED', 'FlashAlpha', 'Vercel', etc.
  tier TEXT, -- 'S', 'A', 'B', or 'C' for data; 'Infrastructure' for services
  cost_per_unit DECIMAL, -- $0 for FRED, $79/month for FlashAlpha, etc.
  unit TEXT, -- 'API call', 'month', 'GB transfer'
  quantity INT, -- 1 for each call, 1 for monthly service
  total_cost DECIMAL, -- quantity * cost_per_unit
  api_calls INT, -- Count of API calls (for rate tracking)
  duration_ms INT, -- Latency (for performance tracking)
  date DATE,
  success BOOLEAN,
  
  INDEX (source_name, date DESC),
  INDEX (tier, date DESC),
  INDEX (date DESC)
);

-- Monthly aggregation (materialized view, refreshed daily)
CREATE TABLE cost_summary_monthly (
  month DATE, -- First day of month
  tier TEXT,
  source_name TEXT,
  total_cost DECIMAL,
  api_calls INT,
  avg_duration_ms INT,
  success_rate DECIMAL, -- 0-1
  
  INDEX (month DESC, tier),
  INDEX (source_name, month DESC)
);
```

### 3. Daily Aggregation Job

```typescript
// server/jobs/cost-aggregation.ts

async function aggregateCostsDaily() {
  // Run at 2 AM daily
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  
  const summary = await db
    .select({
      tier: costLog.tier,
      source: costLog.sourceName,
      totalCost: sql`SUM(${costLog.totalCost})`,
      apiCalls: sql`SUM(${costLog.apiCalls})`,
      avgDuration: sql`AVG(${costLog.durationMs})`,
      successRate: sql`SUM(CASE WHEN ${costLog.success} THEN 1 ELSE 0 END) / COUNT(*)`
    })
    .from(costLog)
    .where(eq(costLog.date, yesterday))
    .groupBy(costLog.tier, costLog.sourceName);
  
  // Store in cost_summary table
  for (const row of summary) {
    await db.insert(costSummary).values(row).onDuplicateKeyUpdate();
  }
  
  // Alert if spending spike detected
  const monthlyTotal = await getMonthlyTotal(new Date());
  const monthlyBudget = 400; // Max budget for v1
  
  if (monthlyTotal > monthlyBudget * 0.8) {
    await slack.send(`⚠️ Cost alert: ${monthlyTotal} YTD this month (80% of budget)`);
  }
}
```

---

## Dashboard (Real-Time View)

**Endpoint:** `GET /api/admin/costs`

```json
{
  "current_month": "2026-05-01",
  "spending_summary": {
    "tier_1_data": {
      "total": 0,
      "sources": {
        "FRED": 0,
        "CFTC": 0,
        "Treasury": 0,
        "BLS": 0,
        "SEC": 0,
        "CBOE": 0,
        "Alpha Vantage": 0,
        "CoinGecko": 0
      },
      "percentage_of_budget": 0
    },
    "tier_2_data": {
      "total": 145.33,
      "sources": {
        "FlashAlpha": 79.00,
        "Finnhub": 49.50,
        "EODHD": 16.83
      },
      "percentage_of_budget": 38
    },
    "infrastructure": {
      "total": 87.50,
      "breakdown": {
        "Vercel": 30,
        "PostgreSQL": 25,
        "Sentry": 32.50
      },
      "percentage_of_budget": 23
    },
    "total_this_month": 232.83,
    "budget": 400,
    "remaining": 167.17,
    "days_remaining_in_month": 15,
    "projected_total": 260
  },
  "api_efficiency": {
    "total_api_calls": 4823,
    "cost_per_api_call": 0.018, // (Total Tier 2 cost / API calls)
    "avg_latency_ms": 342,
    "success_rate": 0.997
  },
  "source_accuracy_vs_cost": [
    {
      "source": "FRED",
      "cost": 0,
      "monthly_accuracy": 0.98,
      "cry_wolf_rate": 0.01,
      "roi": "infinite (free + accurate)"
    },
    {
      "source": "FlashAlpha",
      "cost": 79,
      "monthly_accuracy": 0.85,
      "cry_wolf_rate": 0.08,
      "roi": "moderate ($93 value @ 85% accuracy)"
    }
  ],
  "tier_readiness": {
    "tier_1_only_cost": 60,
    "ready_for_mvp": true,
    "tier_1_plus_tier_2_cost": 232,
    "ready_for_v1": true,
    "upgrade_decision_deadline": "2026-06-01"
  }
}
```

---

## Monthly Report (Automated)

**Sent:** First day of each month via Slack + email

```markdown
# Living Brief Cost Report: May 2026

## Executive Summary
**Total Spending:** $232.83  
**Budget:** $400/mo  
**Remaining:** $167.17  
**Projected EOY:** $2,793.60  

**Decision Point:** Tier 1 only ($60/mo) is sufficient. Tier 2 adds $145/mo but improves accuracy by 3%. Recommend proceeding with v1 launch (Tier 1 + Tier 2) for launch credibility.

---

## Cost Breakdown

### Data Sources (Tier 1: $0)
| Source | Cost | API Calls | Avg Latency | Accuracy | Value |
|--------|------|-----------|-------------|----------|-------|
| FRED | $0 | 1,248 | 342ms | 98% | Highest (foundation) |
| CFTC | $0 | 4 | 1,200ms | 100% | Highest (positioning) |
| Treasury | $0 | 248 | 280ms | 100% | Highest (recession signal) |
| BLS | $0 | 4 | 450ms | 95% | High (labor market) |
| SEC EDGAR | $0 | 842 | 520ms | 92% | High (material events) |
| CBOE VIX | $0 | 31 | 200ms | 100% | Highest (regime) |
| Alpha Vantage | $0 | 248 | 320ms | 88% | Good (equity context) |
| CoinGecko | $0 | 1,198 | 150ms | 100% | Good (risk-on signal) |
| **TOTAL TIER 1** | **$0** | **3,823** | **398ms** | **97%** | **Excellent baseline** |

### Data Sources (Tier 2: $197/mo)
| Source | Cost | API Calls | Avg Latency | Accuracy | Value Added |
|--------|------|-----------|-------------|----------|-------------|
| FlashAlpha | $79 | 200 | 180ms | 85% | +2% brief accuracy |
| Finnhub | $99 | 600 | 420ms | 83% | +1% brief accuracy |
| EODHD | $19 | 200 | 380ms | 82% | +0.5% brief accuracy |
| **TOTAL TIER 2** | **$197** | **1,000** | **320ms** | **83%** | **+3.5% total** |

### Infrastructure: $87.50
| Service | Cost | Notes |
|---------|------|-------|
| Vercel | $30 | Standard plan, 2 deployments/day, edge computing |
| PostgreSQL (Neon) | $25 | 2 concurrent connections, 5GB storage |
| Sentry (error tracking) | $32.50 | 10K events/month, production monitoring |
| **TOTAL INFRASTRUCTURE** | **$87.50** | |

---

## Efficiency Metrics

**API Calls per Dollar Spent:**
- Tier 1: 3,823 calls / $0 = ∞ (free)
- Tier 2: 1,000 calls / $197 = 5.08 calls per dollar
- Infrastructure: 4,823 calls / $87.50 = 55 calls per dollar

**Accuracy per Dollar:**
- FRED: 98% accuracy / $0 = ∞
- FlashAlpha: 85% accuracy / $79 = 1.08% accuracy per dollar
- Tier 1 baseline: 97% accuracy / $0 = foundation

---

## Decision: MVP vs. v1

### Option A: MVP (Tier 1 Only)
| Metric | Value |
|--------|-------|
| Monthly Cost | $60 |
| Data Accuracy | 97% |
| Editorial Track Record | Excellent (free data only) |
| Real-Time Signals | Limited (no options flow) |
| Go-To-Market | Strong (free = low cost barrier) |
| Risk | Higher false-alarm rate, slower signal detection |

**Recommendation:** Choose this for bootstrap launch (months 1-3). Prove editor accuracy first.

### Option B: v1 (Tier 1 + Tier 2)
| Metric | Value |
|--------|-------|
| Monthly Cost | $257 |
| Data Accuracy | 100% (composite) |
| Editorial Track Record | Excellent (premium data validates judgment) |
| Real-Time Signals | Strong (gamma, news, sentiment included) |
| Go-To-Market | Premium positioning ($257/mo opex public) |
| Risk | Higher spend, customer expects perfection |

**Recommendation:** Choose this for funded round launch. Cost justified by accuracy.

---

## Optimization Opportunities

### Cost Reduction (If Budget Constrained)
1. **Drop EODHD** (-$19/mo): Finnhub sentiment sufficient
2. **Use Alpha Vantage free tier only** (-$20/mo): Acceptable for MVP
3. **Downgrade PostgreSQL to shared plan** (-$15/mo): Still 5GB for early users
4. **Use Vercel free tier during testing** (-$30/mo): Not recommended for production

**Total Reduction Potential:** -$84/mo (18% savings)

### ROI Improvement (If Budget Allows)
1. **Upgrade PostgreSQL for higher throughput** (+$15-30/mo)
2. **Add real-time Databento for order flow** (+$199/mo): Overkill for v1
3. **Upgrade Sentry to team plan** (+$20/mo): Better collaboration

---

## Annual Budget Projection

| Scenario | Monthly | Annual | Funding Runway (@ $50K) |
|----------|---------|--------|---------------------------|
| MVP (Tier 1) | $60 | $720 | 69 months (5.8 years) |
| v1 (Tier 1+2) | $257 | $3,084 | 16 months |
| v1 + Premium Infrastructure | $350 | $4,200 | 12 months |

**Implications:**
- MVP is effectively free to run at scale (pre-revenue)
- v1 requires revenue traction by month 16 to remain sustainable
- Tier 2 is a "go-to-market bet" (pay to reduce churn, improve accuracy, win market)

---

## Action Items

- [ ] **Week 1:** Implement cost_log table + daily aggregation job
- [ ] **Week 1:** Deploy dashboard at `/api/admin/costs`
- [ ] **Week 2:** Set up monthly Slack report (1st of month, 8 AM)
- [ ] **May 31:** First cost report review. Decision: MVP or v1 for launch?
- [ ] **June 1:** Implement budget alerts (>80%, >90% of budget)
- [ ] **June 15:** Quarterly cost review. Adjust Tier 2 subscriptions if needed.

---

## Links

- **Data Architecture:** DATA_ARCHITECTURE.md § Cost Breakdown
- **Tier System:** BRIEF_SCHEMA_MAPPING.md § Source Tier Assignment Rules
- **Implementation Timeline:** 90-Day Roadmap (SOURCES_AND_DATA.md § Weeks 5-8)
- **Dashboard Code:** `/server/routes/admin/costs.ts`
- **Aggregation Job:** `/server/jobs/cost-aggregation.ts`
