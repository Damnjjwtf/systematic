# On-Call Playbook: Living Brief Operations

**Purpose:** Quick decision tree for on-call engineer when brief fails to publish, data stales, or alerts fire.

**Assumption:** Editor and subscribers are waiting. Speed > perfection.

---

## Incident: Brief Did Not Publish (8:15 AM Target Miss)

### 1. Check Status (30 seconds)
```bash
curl https://brief.app/health
```
- ✓ API up, DB up → Problem is data or transformation. Go to Step 2.
- ✗ Service down → Restart service on Vercel. Go to Step 3 if restart fails.

### 2. Check Data Freshness (1 minute)
Open: `https://brief.app/admin/data-status`

**All green (✓)?** → Problem is downstream (schema error, validation, storage).
- Check recent schema changes: `git log -3 --oneline shared/schema.ts`
- Check transformation logs: `tail -100 /var/logs/brief-batch.log`
- If logs show clear error: fix code, redeploy, re-trigger batch.
- If logs unclear: rollback last deploy, re-trigger.

**Any red (⚠)?** → Problem is data source down or rate-limited.
- See "Data Source Specific Issues" below.

### 3. If Service Restarted but Still Down (2 minutes)
- Check Vercel deployment status: `vercel status`
- If deploying/broken: rollback to previous version, trigger batch again.
- If healthy but not running: restart via Vercel dashboard or `vercel restart`.

**Still broken after restart?** → Page on-call engineer (likely DB issue, outside scope here).

### 4. Decision: Publish or Delay?
- **Publish with caveat**: If only 1-2 sources missing, publish brief with note: "FRED not available, using cached yields."
- **Skip day**: If >2 Tier S sources missing, skip publication (better than wrong brief).

---

## Data Source Specific Issues

### FRED (IG OAS, HY OAS, Yields, VIX, VVIX)
**Status page:** https://stlouisfed.org/status  
**Symptoms:** 503, timeout, or blank JSON response

**Action:**
1. Check status page. If down: wait 5 min, retry. Publish with caveat if still down after 10 min.
2. If responding slowly (latency >10s): reduce request batch size, retry individually.
3. If returning 0 values: check URL parameters. FRED resets some series on specific dates.

**Fallback:** Use prior day's data. Add caveat: "Credit spreads from May 15 (using cached data)."

### CFTC COT (Released Friday 3:30 PM only)
**Status page:** https://www.cftc.gov (rare outages)  
**Symptoms:** 404, missing file, or parse error

**Action:**
1. Check if it's after 3:30 PM ET. If before: file not released yet, publish without COT data (normal).
2. If after 3:30 PM and missing: check CFTC website manually. Usually available within 30 min.
3. If format changed (parse error): check CFTC announcement page. Escalate to engineering (schema change needed).

**Fallback:** Publish with caveat: "COT data delayed, using prior week's data."

### Treasury Yields (10Y, 2Y, Spreads)
**Status page:** https://home.treasury.gov (very rare outages)  
**Symptoms:** 503, missing series, or NaN values

**Action:**
1. Check Treasury status page.
2. If down <10 min: wait and retry. This is critical; delay brief if needed.
3. If down >10 min: HARD STOP. Do not publish brief without yield curve. This is a recession signal source; missing it is worse than delayed publication.

**Fallback:** None. Wait for Treasury to recover (usually <30 min). Notify subscribers of delay.

### SEC EDGAR (8-K Filings, Real-Time)
**Status page:** https://www.sec.gov/cgi-bin/browse-edgar  
**Symptoms:** Timeout, empty results, or network error

**Action:**
1. Check SEC status page.
2. If down: gracefully degrade. Remove real-time 8-K section from brief, publish without it.
3. If slow (latency >5s per request): reduce number of 8-Ks fetched (show top 5 instead of 20).

**Fallback:** Publish brief without real-time 8-K section. Add caveat: "8-K data unavailable."

### CBOE VIX (Daily Snapshot)
**Status page:** https://www.cboe.com (rare downtime)  
**Symptoms:** 503, blank, or stale data (>6 hours old)

**Action:**
1. Check CBOE status page.
2. If stale but available: use it anyway (VIX yesterday is better than no VIX). Add caveat if >1 day old.
3. If unavailable: fetch from FRED VIXCLS series as fallback.

**Fallback:** Use FRED VIX series. Caveat: "Using FRED VIX; CBOE unavailable."

### BLS (Employment, JOLTS, Unemployment)
**Status page:** https://www.bls.gov (rare downtime)  
**Symptoms:** API timeout, 503, or empty response

**Action:**
1. Check BLS status page.
2. BLS data is monthly only. If monthly data not ready, use prior month's cached value. Add caveat: "April JOLTS; May not yet released."
3. If unavailable: skip this finding from brief. It's not a daily signal anyway.

**Fallback:** Use most recent cached value. Caveat: "JOLTS data is 1+ month old."

### Alpha Vantage (SPX Prices, Sentiment)
**Status page:** https://www.alphavantage.co/performance  
**Symptoms:** 503, slow (>5s), or rate limited (HTTP 429)

**Action:**
1. Check if rate limit hit. If yes: back off, wait 1 min, retry.
2. If 503: use cached closing price from prior day.
3. Sentiment is optional; skip it if source unreliable.

**Fallback:** Use prior day's SPX close. Caveat: "SPX data from May 15."

### CoinGecko (Crypto Prices, BTC Dominance)
**Status page:** https://status.coingecko.com  
**Symptoms:** Timeout, 503, or stale data

**Action:**
1. CoinGecko has real-time data but occasional latency. If latency >5s: use cached.
2. If 503: use cached value from <30 min ago.
3. This is Tier B (not Tier S); skip if unreliable.

**Fallback:** Skip crypto section from brief if unavailable.

---

## Incident: Data Quality Alert (Freshness <90%)

### 1. Check Alert Dashboard (2 minutes)
Go to: `https://brief.app/admin/data-quality`

**Identify:** Which source(s) are problematic?

### 2. Investigate (3 minutes)
```bash
# Example: FRED HY OAS looks wrong
curl 'https://fred.stlouisfed.org/api/series/BAMLH0A0HYM2/observations?api_key=...' | jq '.observations[-3:]'

# Compare to yesterday
git log --all --grep="BAMLH0A0HYM2" --format="%H %ai %b" | head -5
```

**Is value realistic?** (Does it match market conditions, recent trend?)
- **Yes:** Alert is false positive (data quality check is too sensitive). Document and update SLA threshold.
- **No:** Likely parser error or API format change. See "Data Source Specific Issues" above.

### 3. Decision: Publish or Fix?
- **Minor issue (single outlier, isolated source):** Publish with caveat. Add note about data quality in metadata.
- **Major issue (multiple sources, regime affects finding):** Hold publication. Investigate root cause. Re-trigger batch when fixed.

---

## Incident: Watchlist Trigger Fired (Alert Sent)

**Scenario:** Your phone buzzes at 2 PM. "Credit spread spike alert sent to subscribers."

### 1. Validate Signal (1 minute)
Check if it's real:
```bash
# Fetch latest HY OAS
curl 'https://fred.stlouisfed.org/api/series/BAMLH0A0HYM2/observations?api_key=...' | jq '.observations[-1]'
```

**Is spread really >30 bps wider than yesterday?**
- **Yes:** Signal is valid. Brief will update at next scheduled publish. No action needed unless it's intraday (handled separately below).
- **No:** False positive. Likely data lag or transient spike. Monitor next update.

### 2. If Intraday (Data Published Today, Signal Just Fired)
- Update brief in real-time if this is a material change. Go to: `https://brief.app/admin/briefs/[today's-id]`
- Revise: findings, watchlist status, move confidence.
- Re-send email: "Brief update: [change summary]"
- Subscribers will see "Updated at [time]" on app.

### 3. Assess Impact (2 minutes)
- **Watchlist had high probability (>20%):** Signal validation confirms brief quality.
- **Watchlist had low probability (<10%):** False alarm. Log and investigate why.
  - Did market conditions change (regime shift)? Update confidence.
  - Is source accuracy degrading? Log in monthly review.

---

## Incident: On-Call Handoff (End of Shift)

**At shift end (or before), update the log:**

```markdown
# On-Call Log [Date]

**Incidents:**
- 8:15 AM: Brief published successfully. FRED latency elevated (+2s) but within SLA.
- 2:30 PM: Credit spread watchlist triggered (valid signal, SPX -1.2% confirmed).
- 5:00 PM: Alpha Vantage rate limited. Cached data used. No impact to publication.

**Actions Taken:**
- None. All systems healthy.

**Handoff Notes:**
- Watch CFTC COT release tomorrow (Friday 3:30 PM). New format may require parser update.
- Treasury yields had 1 sec lag today (monitor for degradation).

**Incoming on-call engineer review:** Review actions, confirm all alerts resolved.
```

---

## Decision Tree (Quick Reference)

```
Brief didn't publish?
├─ Service down?
│  └─ Restart Vercel. If still down: page engineer.
└─ Service up?
   ├─ Data fresh?
   │  └─ No → Investigate specific source (see table above)
   └─ Data stale?
      ├─ 1-2 sources → Publish with caveat
      └─ >2 sources → Skip publication

Watchlist fired?
├─ Signal valid?
│  ├─ Yes → Expected. Log accuracy.
│  └─ No → False positive. Investigate source.

Data quality alert?
├─ Issue real?
│  ├─ Yes → Fix or publish with caveat
│  └─ No → Adjust alert threshold
```

---

## Escalation Contacts

| Issue | Primary | Backup | Page If |
|-------|---------|--------|---------|
| Service/API down | DevOps slack | PagerDuty | >10 min unresolved |
| Database down | DBA on-call | CTO | >5 min unresolved |
| Data source down (FRED, CFTC, etc.) | Monitor status page | Slack channel | Affects >2 sources |
| Parser/schema error | Backend engineer | Tech lead | Code change needed |
| Ambiguous decision | Editor (JJ) | Product owner | Impact >24h publication |

---

## Prevention Checklist (Weekly)

Every Friday EOD, review:
- [ ] All source integrations tested (manual curl to each API)
- [ ] Freshness SLA met all week (check dashboard history)
- [ ] Zero false alarm watchlist triggers this week? If >1, adjust sensitivity.
- [ ] Accuracy tracking: which sources had best/worst week? Update tier if needed.
- [ ] Database health: check query performance, index utilization.

---

## Recovery from Common Failures

### "Parser Error on FRED Data"
```bash
# 1. Check schema change
git diff HEAD~1 shared/schema.ts | grep -A5 -B5 FRED

# 2. If format changed, update parser
grep -r "FRED.*parse" server/ | head -3

# 3. Test fix locally
node ./server/jobs/test-fred-parse.js

# 4. Redeploy and re-trigger
git push && vercel deploy && npm run batch
```

### "PostgreSQL Connection Pooling Exhausted"
```bash
# 1. Check current connections
psql -h $DB_HOST -U $DB_USER -d postgres -c "SELECT datname, usename, state, count(*) FROM pg_stat_activity GROUP BY datname, usename, state;"

# 2. Kill idle connections (if safe)
psql -h $DB_HOST -U $DB_USER -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state='idle' AND state_change < now() - interval '5 minutes';"

# 3. Check for connection leak in batch jobs
grep -r "\.close\|\.disconnect" server/jobs/ | wc -l
# If low count, add proper cleanup
```

### "Rate Limit Hit on Free API Tier"
```bash
# 1. Check which API
grep "429\|rate" /var/logs/*.log

# 2. Implement exponential backoff + jitter
# Example: wait 1s, 2s, 4s with ±25% jitter

# 3. Switch to paid tier if frequent
# Review: SOURCES_AND_DATA.md section "Tier 2"
```

---

## Links & References

- **Data Monitoring Dashboard**: https://brief.app/admin/data-status
- **Data Quality SLA**: DATA_ARCHITECTURE.md § Data Freshness SLA
- **Incident Log**: https://brief.app/admin/incidents
- **Slack**: #brief-ops
- **Runbook**: This file (ON_CALL_PLAYBOOK.md)
- **Architecture**: DATA_ARCHITECTURE.md
- **Source Tier Definitions**: BRIEF_SCHEMA_MAPPING.md § Source Tier Assignment Rules
