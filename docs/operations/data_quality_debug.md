# Data Quality Debugging Guide

**Purpose:** When data quality metric drops below 90%, use this flowchart to isolate the root cause in <10 minutes.

---

## Quick Diagnosis (2 minutes)

```
START: Data quality dashboard shows RED

    ↓
    
Have any data sources recently gone down/unavailable?
    ├─ YES → Go to: Scenario A (Source Unavailable)
    └─ NO → Continue

    ↓
    
Are the values NaN, NULL, or zero (unexpected)?
    ├─ YES → Go to: Scenario B (Parser Error / Format Change)
    └─ NO → Continue

    ↓
    
Are values extreme (e.g., HY OAS 500 bps, VIX 100)?
    ├─ YES → Go to: Scenario C (Data Corruption / Outlier)
    └─ NO → Continue

    ↓
    
Is data >6 hours stale (expected < 4 hours)?
    ├─ YES → Go to: Scenario D (Network / Rate Limit)
    └─ NO → System healthy, alert is false positive

    ↓
    
Update SLA threshold, document, move on.
```

---

## Scenario A: Source Unavailable

**Symptoms:** HTTP 503, 404, timeout, or connection refused

**Diagnosis (1 minute):**

```bash
# 1. Try direct API call
curl -v "https://api.example.com/endpoint" 2>&1 | grep -i "error\|timeout\|503\|404"

# 2. Check status page (see ON_CALL_PLAYBOOK.md for source-specific URLs)
# Example for FRED:
curl https://stlouisfed.org/status 2>&1 | grep -i "maintenance\|degraded"

# 3. Check rate limit headers
curl -v "https://api.example.com/endpoint" 2>&1 | grep -i "x-ratelimit\|retry-after"
```

**Root Cause Matrix:**

| Status Code | Likely Cause | Fix |
|-------------|-------------|-----|
| 503 | Server maintenance | Wait 5-10 min, retry |
| 429 | Rate limit exceeded | Implement backoff, see Scenario D |
| 404 | Endpoint changed/moved | Check API docs, update URL |
| Connection timeout | Network issue or firewall | Check VPN/firewall rules, retry |
| Empty response | Format change | See Scenario B |

**Action:**
- **Expected downtime <30 min:** Publish with caveat ("Source temporarily unavailable, using cached data from [time]")
- **Expected downtime >1 hour:** Skip publication or use fallback source (see ON_CALL_PLAYBOOK.md)
- **Unexpected format:** Escalate to engineering (schema change needed)

---

## Scenario B: Parser Error / Format Change

**Symptoms:** JSON parse error, KeyError on expected field, unexpected field structure

**Diagnosis (2 minutes):**

```bash
# 1. Get raw API response
RESPONSE=$(curl -s "https://api.example.com/endpoint")
echo $RESPONSE | jq '.' | head -50

# 2. Check what we expect vs. got
echo $RESPONSE | jq '.data | keys' # Expected: ["value", "date", "unit"]
echo $RESPONSE | jq '.data | keys' # Got: ["price", "timestamp", "currency"]

# 3. Check if format matches recent commit
git log --oneline -10 server/integrations/*.ts | head -5
git diff HEAD~1 server/integrations/fred.ts | grep -A3 -B3 "parse\|transform"

# 4. Check changelog/announcements
# For FRED: https://fred.stlouisfed.org/api/docs
# For CFTC: https://www.cftc.gov/MarketReports/CommitmentsOfTraders/
```

**Root Cause Matrix:**

| Indicator | Likely Cause | Fix |
|-----------|-------------|-----|
| Field missing (KeyError) | API schema changed | Update parser to handle both old + new schema |
| Array instead of object | Response structure changed | Update transformation logic |
| Null values where expected | Source data missing for date | Add null check, use fallback |
| Type mismatch (string vs number) | Field serialization changed | Add type coercion in parser |

**Action:**
```bash
# 1. Make fix in code
vim server/integrations/fred.ts  # Update parse logic to handle new format

# 2. Test locally
node -e "const p = require('./server/integrations/fred'); p.fetch().then(console.log)"

# 3. Validate matches schema
# Run type checker to confirm fix matches expected schema

# 4. Redeploy and retry
git add . && git commit -m "Fix FRED parser for new response format"
git push && vercel deploy
npm run batch  # Trigger batch job to re-fetch with new parser
```

---

## Scenario C: Data Corruption / Extreme Values

**Symptoms:** Values are real numbers but look impossible (HY OAS 500 bps, VIX 100, yields 20%)

**Diagnosis (2 minutes):**

```bash
# 1. Check if it's a real market event (check news, other sources)
curl https://www.cnbc.com/markets/  # Is market actually in crisis?
curl https://www.bloomberg.com/quote/USGG10YR:IND  # Check competing data

# 2. Compare to recent history
sqlite> SELECT * FROM data_freshness_log 
        WHERE source_name = 'FRED_BAMLH0A0HYM2' 
        ORDER BY date DESC LIMIT 7;
# Look for pattern: is it trending up or sudden spike?

# 3. Check calculation chain
# Is our derived signal wrong? (e.g., we calculate "HY OAS widening 50 bps" but API shows stable)
git log -p server/transforms/regime.ts | grep -A10 "HY.*spread" | head -20
```

**Root Cause Matrix:**

| Pattern | Likely Cause | Fix |
|---------|-------------|-----|
| Single spike, reverts next day | Real intraday move | Valid. Add to archive history. |
| Steady trend up (3+ days) | Real market event | Valid. Mark as "crisis regime" in brief. |
| Value jumps 10x in 1 reading | Parser decimal error | Check if dividing by 100 instead of 1. Fix: `.toFixed(2)` |
| Value negative/impossible | Calculation error | Review transform logic. Add validation. |
| Source 1 normal, source 2 extreme | Source divergence | Cross-check which is correct. Demote unreliable source. |

**Action:**
- **Real event:** Document in archive. Update brief. No code fix needed.
- **Parser error:** Fix calculation, re-fetch data, validate trend looks normal.
- **Source divergence:** Log in source accuracy tracking. If persistent, demote source tier.

```bash
# Example: HY OAS should be in range 200-400 bps
# Add validation gate
if (hyOAS < 150 || hyOAS > 500) {
  console.warn(`HY OAS out of expected range: ${hyOAS} bps`);
  // Use prior day's value or alert operator
}
```

---

## Scenario D: Network / Rate Limit

**Symptoms:** Requests timing out, getting slower over time, or 429 errors

**Diagnosis (2 minutes):**

```bash
# 1. Check request latency trend
# (Using monitoring dashboard)
# Is latency 50ms (normal) or 5000ms (degraded)?

# 2. Check rate limit status
curl -i "https://api.example.com/endpoint" 2>&1 | grep -E "X-RateLimit|Retry-After|429"

# 3. Count recent requests to this source
grep "fredapi.stlouisfed.org" /var/logs/batch-*.log | wc -l
# Compare to rate limit (e.g., FRED allows 120 calls/min)

# 4. Check for connection leaks (zombie connections hanging)
netstat -an | grep ESTABLISHED | wc -l  # Growing count = leak?
ps aux | grep "node" | grep batch  # Is batch job stuck?
```

**Root Cause Matrix:**

| Indicator | Likely Cause | Fix |
|-----------|-------------|-----|
| Latency >2s, increasing | API server under load | Back off, retry with exponential delay |
| 429 + "X-RateLimit: 0" | Rate limit exhausted | Reduce request batch size, spread over time |
| Timeout after 30s | Connection timeout or firewall | Check firewall rules, increase timeout, use VPN |
| Pool exhaustion (connection limit) | Too many concurrent requests | Reduce parallelism, add connection pooling |

**Action:**

```bash
# Implement exponential backoff with jitter
async function fetchWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, { timeout: 10000 });
      return response;
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      
      // Exponential backoff: 1s, 2s, 4s ± 25% jitter
      const baseDelay = Math.pow(2, i) * 1000;
      const jitter = (Math.random() - 0.5) * baseDelay * 0.5;
      await sleep(baseDelay + jitter);
    }
  }
}

// Limit concurrent requests
const queue = pQueue({ concurrency: 2 });
for (const source of sources) {
  await queue.add(() => fetchWithRetry(source.url));
}
```

**Prevention:**
- Reduce batch request parallelism (2-3 concurrent instead of 10)
- Spread requests over time (don't fetch all 8 sources at once)
- Implement circuit breaker (skip source for 5 min if fails twice in a row)

---

## Decision Tree for 90-Score Debugging

```
Quality score < 90%?

    ├─ Is a major source returning errors/timeouts?
    │  └─ YES → Follow Scenario A
    │
    ├─ Is data shape/format unexpected?
    │  └─ YES → Follow Scenario B
    │
    ├─ Are values extreme/impossible?
    │  └─ YES → Follow Scenario C
    │
    ├─ Are requests timing out or slow?
    │  └─ YES → Follow Scenario D
    │
    └─ None of the above?
       └─ False positive. Investigate alert threshold logic.
          (Quality metric may be too sensitive.)
          
           Action: Review last 50 runs. Is score <90% intermittent or persistent?
           - Intermittent (<10% of the time) → Increase threshold to 85%
           - Persistent (>50% of the time) → Real issue, identify root
```

---

## Data Quality Checklist (Daily)

Run this every morning during data refresh:

- [ ] All 8 sources fetched successfully (check logs for 200 status)
- [ ] No parser errors in transformation (check stderr)
- [ ] All values pass basic sanity checks (range validation, type checking)
- [ ] Quality score ≥90% (green on dashboard)
- [ ] Data freshness <4 hours old (none stale beyond SLA)
- [ ] No watchlist false positives fired (if yes, investigate threshold)
- [ ] Brief published on time (8:15 AM within 5-min window)

---

## Reference: Source-Specific SLA & Validation Ranges

| Source | Expected Freshness | Normal Range | Alert If |
|--------|-------------------|--------------|----------|
| FRED HY OAS | Same-day | 150-400 bps | <100 or >500 bps |
| FRED IG OAS | Same-day | 50-150 bps | <30 or >200 bps |
| CBOE VIX | Same-day | 10-50 | <5 or >100 |
| Treasury 10Y | Same-day | 2%-6% | <0.5% or >8% |
| CFTC COT | Friday 3:30 PM | Positioning varies | None (alert on divergence in analysis layer) |
| BLS JOLTS | Monthly, 1-2 weeks old | 3M-5.5M openings | <2M or >6M |
| SEC 8-K | Real-time | Count varies | No new 8-Ks for >24h (in bull market) |

---

## Escalation Path

| Issue Type | Debug Time | Escalate If | To |
|------------|-----------|-------------|-----|
| Network timeout | 2 min | Persists >5 min | DevOps |
| Parser error | 5 min | Requires code change | Backend engineer |
| Source API down | 1 min | Down >30 min | Source vendor (file ticket) |
| Rate limit | 3 min | Requires tier upgrade | Product (budget decision) |
| Unclear root cause | 10 min | Still unclear | Tech lead + incident Slack |

---

## Quick Copy-Paste Commands

```bash
# Check all sources at once (if they all expose status endpoints)
for source in fred cftc cboe treasury bls sec coingecko alphavantage; do
  echo "=== $source ==="
  case $source in
    fred) curl -s https://fred.stlouisfed.org/api/series/BAMLH0A0HYM2/observations?api_key=$FRED_KEY | jq '.observations[-1]' ;;
    cboe) curl -s "https://www.cboe.com/json/quote?symbols=VIX" | jq '.data[0]' ;;
    *) echo "Implement for $source" ;;
  esac
done

# Watch logs in real-time during batch job
tail -f /var/logs/batch-$(date +%Y%m%d).log | grep -E "ERROR|WARN|parsed|transformed"

# Compare today's data to yesterday's
sqlite3 brief.db "SELECT source_name, last_value, date FROM data_freshness_log 
  WHERE date IN (CURRENT_DATE, CURRENT_DATE - 1) 
  ORDER BY source_name, date DESC;"

# Kill hung batch process (if stuck >20 min)
ps aux | grep "batch-job" | grep -v grep | awk '{print $2}' | xargs kill -9
# Then manually re-trigger: npm run batch
```

---

## Links

- **Data Architecture**: DATA_ARCHITECTURE.md § Data Freshness SLA
- **Source Reference**: SOURCES_AND_DATA.md
- **On-Call Playbook**: ON_CALL_PLAYBOOK.md
- **Monitoring Dashboard**: https://brief.app/admin/data-status
- **Incident Log**: https://brief.app/admin/incidents
