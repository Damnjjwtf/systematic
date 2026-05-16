# Financial Data Sources & Integration Strategy

## Overview

Living Briefs synthesizes macro regime signals from free/public and low-cost APIs. All data is cited by tier (S/A/B/C) for reproducibility and trust.

**MVP Stack:** $0 (free, 2-week integration)  
**v1 Commercial:** $200-400/mo (adds real-time options flow, sentiment, news)  
**Institutional Scale:** $8K+/mo (premium data, fund flows, tick-level order book)

---

## Tier 1: Free/Public Data (MVP Foundation)

### FRED — Macro + Credit Spreads + Yields
- **URL:** https://fred.stlouisfed.org/api/
- **Data:** 840K+ US economic series (labor, inflation, credit spreads, yields)
- **Freshness:** 1-7 days lag depending on series
- **Access:** REST API (free key, no rate limits)
- **Cost:** $0
- **Licensing:** Public domain
- **Key Series:** BAMLC0A0CM (IG OAS), BAMLH0A0HYM2 (HY OAS), VIXCLS (VIX), DGS2/DGS10 (yields)
- **Why:** Foundation for regime classification. Credit spreads = first warning system.

### CFTC Commitments of Traders (COT)
- **URL:** https://publicreporting.cftc.gov/
- **Data:** Large trader positioning in futures (Commercials vs. Non-Commercials)
- **Freshness:** Weekly Friday 3:30 PM ET
- **Access:** JSON API (no auth) or Python wrapper `cot_reports`
- **Cost:** $0
- **Licensing:** Public domain
- **Key Use:** Hedge fund consensus positioning. Divergence (spec long, commercial short) = reversal signal.
- **Caveat:** 1-week lag. Disaggregated report (since 2006) separates hedge funds from hedgers.

### CBOE VIX Data
- **URL:** https://www.cboe.com/tradable_products/vix/vix_historical_data
- **Data:** VIX (30-day SPX implied vol), VVIX (vol of vol), SKEW (tail risk)
- **Freshness:** Daily (end-of-day), real-time quotes available
- **Access:** CSV download, FRED API, Yahoo Finance
- **Cost:** $0
- **Licensing:** Public domain
- **Key Use:** VIX >30 = alert, term structure (contango/backwardation) = regime shift setup

### U.S. Treasury Yields
- **URL:** https://home.treasury.gov/resource-center/data-chart-center/interest-rates/
- **Data:** Daily par yield curve (3-mo to 30Y), Treasury spreads
- **Freshness:** Daily (3:30 PM ET)
- **Access:** CSV download, REST API (fiscaldata.treasury.gov), FRED
- **Cost:** $0
- **Licensing:** Public domain
- **Key Use:** 10-2 spread (recession predictor), curve shape (growth vs. crisis)

### SEC EDGAR (8-K + Form 4)
- **URL:** https://www.sec.gov/search-filings/
- **Data:** Real-time material events (8-K), insider Form 4 trades
- **Freshness:** Same-day (8-K filed within 4 days of event)
- **Access:** REST API (data.sec.gov), Python `EdgarTools`
- **Cost:** $0
- **Licensing:** Public domain
- **Key Use:** 8-K = breaking news on bankruptcies, debt raises, material events. Form 4 = insider smart money.

### BLS — Labor Data
- **URL:** https://www.bls.gov/bls/api_features.htm
- **Data:** Employment, unemployment, JOLTS (job openings), wages
- **Freshness:** 1-2 week lag for monthly employment
- **Access:** Proprietary BLS API (free, 500 queries/day)
- **Cost:** $0
- **Licensing:** Public domain
- **Key Use:** JOLTS = growth expectations, unemployment = Fed policy, wage growth = inflation.

### Census Bureau — Housing Data
- **URL:** https://www.census.gov/data/developers/
- **Data:** Starts, permits, new home sales, vacancy
- **Freshness:** 1-2 month lag
- **Access:** REST API
- **Cost:** $0
- **Licensing:** Public domain
- **Key Use:** Leading indicator for GDP/employment.

### Alpha Vantage — Equity Prices + Sentiment
- **URL:** https://www.alphavantage.co/
- **Data:** OHLCV for 3K+ stocks, technical indicators, sentiment scores
- **Freshness:** Daily (end-of-day)
- **Access:** REST API
- **Cost:** Free tier (5 calls/min, 100/day), $20-60/mo paid
- **Licensing:** Proprietary (exchange-licensed data)
- **Key Use:** SPX/sector prices, retail sentiment filter.

### CoinGecko — Crypto Prices
- **URL:** https://www.coingecko.com/en/api
- **Data:** Real-time & historical prices, market cap, dominance, on-chain metrics
- **Freshness:** Real-time (1-min updates)
- **Access:** REST API (JSON)
- **Cost:** Free tier (30 calls/min, 10K/month), paid from $129/mo
- **Licensing:** Proprietary aggregation
- **Key Use:** BTC dominance (risk-on/risk-off signal), stablecoin flows (liquidity).

---

## Tier 2: Low-Cost Add-Ons ($200-400/mo)

### FlashAlpha — Options Flow + Gamma Exposure
- **URL:** https://flashalpha.com/
- **Data:** IV, skew, GEX (gamma exposure), options flow (dealer vs. retail)
- **Freshness:** Daily (end-of-day), real-time metrics available
- **Access:** REST API
- **Cost:** Free tier (5 req/day), $79/mo production
- **Licensing:** Proprietary (built on OPRA public data)
- **Key Use:** GEX predicts dealer rebalancing (1-2 day lead). Skew = tail risk pricing.

### Finnhub — Real-Time News + ETF Flows
- **URL:** https://finnhub.io/
- **Data:** Real-time quotes, breaking news, company fundamentals, ETF holdings, sentiment
- **Freshness:** Real-time for prices, 15-30 min for news
- **Access:** REST API
- **Cost:** Free tier (60 calls/min), $99/mo+ production
- **Licensing:** Proprietary
- **Key Use:** Real-time news alerts, ETF buying/selling, smart money tracking.

### EODHD — Historical Data + Sentiment + Fundamentals
- **URL:** https://eodhd.com/
- **Data:** OHLCV (adjusted), fundamentals, earnings, dividends, news with sentiment
- **Freshness:** Daily (end-of-day)
- **Access:** REST API, Python library (returns pandas)
- **Cost:** Free tier (20 calls/day), plans from $19/mo
- **Licensing:** Proprietary
- **Key Use:** Backtest-friendly sentiment data, fundamental changes.

### Databento — Tick-Level Order Flow
- **URL:** https://databento.com/
- **Data:** Real-time & historical tick-level data (equities, futures, options, order book)
- **Freshness:** Real-time or daily snapshots
- **Access:** REST API, WebSocket
- **Cost:** Free $125 credit, $199+/mo subscription
- **Licensing:** Proprietary
- **Key Use:** Order imbalances, dealer positioning via order book, vol spikes.

---

## Tier 3: Premium (Institutional, $8K+/mo)

- **LexisNexis News API:** Highest-quality financial journalism ($1K+/mo)
- **EPFR:** Fund flows & asset allocation ($5K+/mo)
- **ICE/CME Real-Time Feeds:** Futures & options market data ($500+/mo)
- **Bloomberg Terminal:** For editorial review & validation ($2K/mo)

---

## Integration Reality

| Source | API | Scrape | Manual | Latency | Reliability |
|--------|-----|--------|--------|---------|-------------|
| FRED | ✓ REST | - | ✓ | 1-7d | Excellent |
| CFTC COT | ✓ JSON | ✓ | ✓ | Weekly | Excellent |
| CBOE VIX | - | ✓ | ✓ | Daily | Excellent |
| Treasury | ✓ REST | - | ✓ | Same-day | Excellent |
| SEC EDGAR | ✓ REST | - | ✓ | Real-time | Excellent |
| BLS | ✓ API | - | ✓ | 1-2w | Excellent |
| Alpha Vantage | ✓ REST | - | - | Daily | Good |
| CoinGecko | ✓ REST | - | - | Real-time | Excellent |
| FlashAlpha | ✓ REST | - | - | Daily | High |
| Finnhub | ✓ REST | - | - | Real-time | Good |
| EODHD | ✓ REST | - | - | Daily | Good |
| Databento | ✓ REST/WS | - | - | Tick-level | Excellent |

---

## Licensing Summary

**Can cite freely (public domain):**
- FRED, BLS, Treasury, CFTC, SEC EDGAR, Census

**Can cite with attribution (check TOS):**
- CBOE VIX, Alpha Vantage, Finnhub, EODHD, CoinGecko, FlashAlpha

**Cannot republish (fair use limits):**
- Full news articles (link instead)
- Bloomberg/Reuters (licensed)
- Premium fund flow data

**Best practice:** Always include data source in brief footnotes. Builds trust + reproducibility.

---

## 90-Day Implementation Roadmap

**Weeks 1-2 (MVP, $0):**
- FRED API integration (macro + credit spreads)
- CFTC COT weekly ingestion
- CBOE VIX daily snapshot
- Treasury yields daily pull
- SEC EDGAR 8-K alert scrape
- BLS labor data monthly batch
- Alpha Vantage equity prices

**Weeks 3-4 ($0 + paid tier evaluation):**
- FlashAlpha API integration ($79/mo)
- Finnhub news aggregation ($99/mo)
- EODHD sentiment layer ($19/mo)
- Build monitoring + alerting

**Weeks 5-8 (Optimization):**
- Databento order flow (if budget allows)
- Source reliability tracking (which sources have best accuracy in our brief)
- Real-time watchlist triggering (COT divergence, credit spread spike alerts)

**Weeks 9-12 (Polish):**
- Data export for trader reports (CSV, PDF)
- Archive search indexing (find all briefs mentioning "yield curve inversion")
- Source tier public scoreboard (accuracy dashboard)
