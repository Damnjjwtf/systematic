# PRD: Systematic - The Living Brief for Systematic Traders

## Product Summary
Systematic - The Living Brief for Systematic Traders is a daily intelligence brief for systematic futures traders.

It tracks market regimes, trend-following performance, systematic research, CTA behavior, futures market structure, regulation, and trader psychology. The brief turns daily signals into disciplined context: what changed, what matters, what is noise, what may break systems, and what a rules-based trader should do next.

The brief is built from the same operating DNA as The f.m Brief: source-grounded findings, visible uncertainty, persona-assisted synthesis, archive memory, and one concrete recommended move per day.

It is also the first expression of the Living Briefs product thesis: a source-grounded intelligence object that can eventually be queried, challenged, updated, remembered, and turned into action.

## Purpose
Systematic exists to help systematic traders stay informed without becoming discretionary.

It should answer:

- What changed in the world that matters to systematic futures traders?
- Is the current drawdown local, strategy-specific, or broad across CTAs?
- Are market regimes changing in ways that affect trend, carry, mean reversion, volatility, or correlation?
- What new research or implementation detail may become edge?
- What regulatory, margin, contract, or liquidity changes could affect execution?
- What is underpriced, misunderstood, or overreacted to?
- What should a disciplined system trader do, avoid, or monitor next?

## Core Thesis
Rules beat discretion over time. Drawdowns are information. Regime awareness is not permission to override the system.

The brief should protect that thesis while still surfacing regime shifts, structural risks, and research signals early enough to matter.

## Primary Users
Primary v1 users:

- JJ as builder/editor/operator of the brief
- Early systematic traders and futures-focused subscribers

Secondary future users:

- CTAs
- Quant researchers
- Algo traders
- Managed futures allocators
- Risk managers
- Strategy developers
- Future thought-leadership and subscriber pipeline

## Cadence
Daily at 6:00 AM Eastern.

Primary scheduler: GitHub Actions.

Fallback/dev runner: local script.

## Delivery
The brief is delivered by email to:

```text
subscribers@thesystematicbrief.com
```

It is also archived locally and in workflow artifacts as:

```text
JSON
TXT
HTML
```

## System Name
Public/internal product name:

```text
Systematic - The Living Brief for Systematic Traders
```

Underlying intelligence layer:

```text
SYSTEMATIC
```

## SYSTEMATIC Definition
SYSTEMATIC is the brief's internal intelligence layer.

It is a small council of curated lenses focused on:

- trend following philosophy
- systematic execution
- risk management
- expectancy and system design
- market structure
- research quality
- drawdown psychology
- regulatory and operational risk

The council is used to sharpen synthesis. It should not turn the brief into personality theater.

## SYSTEMATIC Personas
Core voices:

```text
Covel
Trend following philosophy, Turtle history, discipline over prediction, staying with convexity.

Parker
Systematic execution, real drawdown psychology, CTA operator perspective, process under pressure.

Hite
Risk management, position sizing, portfolio heat, survival, asymmetric patience.

Tharp
Expectancy, R-multiples, system design, trader psychology, beliefs as hidden system inputs.

Market Structure Desk
Contract specs, liquidity, margin, exchange notices, CFTC/NFA/regulatory mechanics.

Research Desk
Paper quality, methodology, backtest hygiene, out-of-sample skepticism, implementation drag.
```

## Brief Structure
Each email should include:

```text
SYSTEMATIC - THE LIVING BRIEF FOR SYSTEMATIC TRADERS
Date

Lead Signal

Source Integrity

Regime Watch

Strategy Performance Signals

Research & Edge

Regulatory / Structure

CTA / Competitor Watch

Arbitrage + Moat

Systematic Takes

Discipline Check

Hallucination Guardrails

Systematic Synthesis

Recommended Move

Watchlist

Today's Strategic Prompt

Next Search
```

## Section Requirements
## Lead Signal
A single sharp sentence describing the most important pattern of the day.

It should not be a prediction dressed as fact.

## Source Integrity
A short reliability note explaining source quality, uncertainty, stale data, promotional sources, missing dates, and anything that should not be over-trusted.

## Regime Watch
Market structure, volatility regime, trend breadth, correlation shifts, liquidity stress, macro cross-currents, and whipsaw conditions.

This section should help readers ask:

```text
Is the environment changing, or am I reacting to normal variance?
```

## Strategy Performance Signals
Context on what is working, what is suffering, and whether drawdowns appear idiosyncratic or broad.

Relevant areas:

- trend following
- managed futures
- time-series momentum
- cross-sectional momentum
- carry
- mean reversion
- volatility targeting
- risk parity
- short-term systematic strategies
- CTA indices and manager commentary

Performance claims require source URLs and source dates.

## Research & Edge
New papers, backtests, repos, methodology notes, or implementation details worth knowing.

Priority is not "interesting research." Priority is research that could affect:

- signal design
- robustness
- transaction costs
- position sizing
- portfolio construction
- regime classification
- execution
- risk controls

## Regulatory / Structure
Tracks legal, exchange, regulatory, and market access risk:

- CFTC
- NFA
- CME
- ICE
- margin changes
- position limits
- contract specs
- data licensing
- prop trading rules
- futures access
- brokerage risk
- clearing and collateral mechanics

## CTA / Competitor Watch
Tracks what other systematic managers, CTAs, allocators, research shops, and adjacent tools are doing or saying.

Promotional manager content must be caveated. Treat it as positioning unless supported by hard data.

## Arbitrage + Moat
A top-level strategic analysis with:

```json
{
  "near_term_arbitrage": "what is underpriced or misunderstood in the next 30-90 days",
  "future_signal": "where this cluster of signals may be headed",
  "moat_strategy": "how Systematic can convert this into durable audience, trust, data, or distribution advantage",
  "do_not_do": "one tempting but dangerous move to avoid"
}
```

## Systematic Takes
Persona-led theses.

Each take should include:

```json
{
  "voices": ["Parker", "Hite"],
  "take": "the sharp thesis",
  "why_it_matters": "why systematic traders should care",
  "action": "what to do, avoid, monitor, or hold"
}
```

Rules:

- Include 2-4 takes per brief.
- Use one persona when one lens is clearest.
- Use grouped personas when the combination makes the take stronger.
- Do not include every persona by default.
- Voices must earn their place.
- Takes should be opinionated, useful, and grounded in the day's findings.

## Discipline Check
A brief reminder of what not to do.

Examples:

- Do not override a trend model because one article says CTAs are crowded.
- Do not resize after a normal drawdown without a prewritten rule.
- Do not mistake community anxiety for regime evidence.
- Do not change parameters because the last 20 trades were ugly.

## Hallucination Guardrails
A visible section explaining uncertainty.

Should include:

- source weaknesses
- undated sources
- promotional manager material
- user-generated discourse
- unverified claims
- repeated sources
- stale performance data
- model limitations
- anything marked WATCHLIST

## Systematic Synthesis
A concise strategic paragraph answering:

```text
What does all of this mean for systematic traders today?
```

## Recommended Move
One concrete action.

Examples:

- hold course
- add one source to monitor
- review drawdown bands
- check margin exposure
- log current regime assumptions
- read one paper
- audit one strategy parameter for fragility
- compare personal drawdown to CTA index context

If there is no action, say:

```text
Recommended Move: Hold course.
```

## Watchlist
3-5 things to monitor next.

Each should include:

```json
{
  "item": "thing to watch",
  "why": "why it matters",
  "trigger": "what would make it actionable"
}
```

## Today's Strategic Prompt
One question for JJ and serious readers.

It should help with:

- product strategy
- subscriber positioning
- trader discipline
- thought leadership
- research agenda
- trust
- regulatory posture
- first wedge

## Next Search
One follow-up search query SYSTEMATIC recommends.

## Finding Schema
Every finding should include:

```json
{
  "title": "finding title",
  "source": "source or publication",
  "url": "direct source URL if available",
  "grounding_url": "Gemini grounding URL if applicable",
  "source_date": "published or updated date, or undated",
  "observed_at": "date this brief observed it",
  "newness": "NEW / UPDATE / REPEAT",
  "source_tier": "TIER_1 / TIER_2 / TIER_3 / TIER_4",
  "evidence": "short sourced fact or paraphrase",
  "summary": "2 concise sentences",
  "systematic_signal": "why this matters specifically for systematic futures traders",
  "regime_read": "for market regime findings only",
  "risk": "for regulatory, margin, execution, or operational findings only",
  "arbitrage_moat": {
    "future_vector": "where this specific signal may go next",
    "arbitrage": "what is underpriced or misunderstood",
    "moat_move": "how Systematic can build advantage"
  },
  "verification_status": "VERIFIED / PARTIAL / WATCHLIST",
  "confidence": "HIGH / MEDIUM / LOW",
  "caveat": "what could be wrong, missing, or overinterpreted",
  "signal_strength": "HIGH / MEDIUM / LOW"
}
```

## Future Vector
Future Vector must remain part of each individual finding.

It answers:

```text
Where is this specific signal likely headed?
```

Future Vector is not the same as Systematic Takes.

- Future Vector: directional read on one signal.
- Systematic Takes: persona-led thesis across signals.

## Source Strategy
Systematic should use a tiered source model.

## Tier 1: Primary / High Trust
Used for hard claims.

Examples:

- CFTC
- NFA
- CME
- ICE
- Federal Register
- court filings
- official exchange notices
- official company blogs
- official product announcements
- academic journals
- university publications
- SSRN/arXiv papers with clear authorship
- official CTA index methodology pages

## Tier 2: Trusted Analysis
Used for interpretation and context.

Examples:

- Societe Generale CTA and trend index commentary
- AQR
- Two Sigma
- Newfound Research
- ReSolve Asset Management
- Man Group research
- Alpha Architect
- Bloomberg
- Reuters
- Financial Times
- The Journal of Portfolio Management
- The Journal of Trading
- law firm regulatory analysis

## Tier 3: Community / Practitioner Discourse
Used for signals, not hard facts.

Examples:

- r/algotrading
- QuantConnect forums
- Elite Trader
- trader blogs
- X/Twitter systematic trading community
- podcast transcripts
- Substack essays
- GitHub discussions

These should be marked as community or practitioner discourse unless verified by stronger sources.

## Tier 4: Edge / Arbitrage Sources
Used for early weak signals.

Examples:

- small CTA blogs
- new GitHub repos
- conference proceedings
- lecture notes
- niche academic working papers
- backtest blogs
- broker implementation notes
- obscure exchange notices

## Source Rules
Hard claims require strong sources.

Community chatter is useful for positioning and temperature, but not treated as fact.

Wikipedia should not be used as a primary source for current claims.

Promotional manager content should be caveated.

Undated sources should lower confidence.

Repeated URLs should be marked UPDATE or REPEAT.

Performance data older than 30 days is stale unless explicitly framed as historical context.

Research older than 6 months is not stale by default, but should not be presented as newly discovered unless the archive confirms it is new to the brief.

## Freshness Rules
Each run should load recent archive memory.

Findings should be labeled:

```text
NEW
UPDATE
REPEAT
```

Rules:

- Prefer NEW findings.
- Use UPDATE when an older source has a material new development.
- Avoid REPEAT unless strategically necessary.
- Repeated URLs must not be presented as fresh.
- Repeated research themes should be synthesized, not re-announced.

## Hallucination Safeguards
The system must:

- require source URLs where possible
- require source dates or mark as undated
- require evidence
- strip or avoid inline citation markup
- resolve Gemini grounding URLs to direct publisher URLs where possible
- preserve original grounding URLs in JSON if useful
- downgrade weak sources
- expose caveats in email
- locally check for missing verification metadata
- never pretend uncertainty is certainty
- never claim "trend following is dead" from one weak signal
- never provide trade instructions or personalized financial advice

## Standing Queries
Daily standing queries:

```text
trend following drawdown 2026
CTA performance current month
SocGen CTA trend index latest
managed futures flows
futures market structure change
CFTC position limits futures
CME margin changes futures
momentum strategy research
volatility regime shift
correlation regime systematic trading
systematic trading regulation
managed futures research
```

Weekly rotating discovery queries:

```text
new mean reversion research futures
risk parity research update
carry strategy futures research
multi asset momentum paper
alternative data systematic futures
transaction costs trend following
execution slippage CTA futures
machine learning trend following futures
```

## Model Strategy
Default:

```text
Gemini 2.5 Flash with grounded search
```

Reason:

- cheap enough for daily use
- current web grounding
- good enough for daily intelligence
- fast enough for a 6:00 AM send

Fallback / deep work:

```text
Claude / Anthropic
```

Use for:

- weekly synthesis
- deeper drawdown memo
- subscriber positioning
- thesis refinement
- high-stakes writing
- launch copy

## Technical Requirements
The system should:

- run from `systematic_daily_brief.py`
- support provider switching
- load env vars
- call Gemini or Anthropic
- parse structured JSON
- run local integrity checks
- render plain text and HTML
- send via SMTP
- archive outputs
- support dry run mode
- support GitHub Actions scheduling
- support local manual fallback
- support test-list mode before subscriber launch

## Environment Variables
Required for Gemini:

```bash
GEMINI_API_KEY=
```

Required for Anthropic fallback:

```bash
ANTHROPIC_API_KEY=
```

Required for email:

```bash
SMTP_HOST=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
EMAIL_FROM=
SYSTEMATIC_BRIEF_TO=
```

Config:

```bash
SYSTEMATIC_BRIEF_PROVIDER=gemini
SYSTEMATIC_BRIEF_MODEL=gemini-2.5-flash
SYSTEMATIC_BRIEF_FROM_NAME=Systematic - The Living Brief for Systematic Traders
SYSTEMATIC_BRIEF_DRY_RUN=0
SYSTEMATIC_RESOLVE_GROUNDING_URLS=1
SYSTEMATIC_TEST_LIST=
```

## Config Example
```json
{
  "brief_name": "Systematic - The Living Brief for Systematic Traders",
  "slug": "systematic",
  "recipient": "subscribers@thesystematicbrief.com",
  "schedule": {
    "cron": "0 11 * * *",
    "timezone": "America/New_York"
  },
  "audiences": {
    "internal": "JJ as builder/editor/operator",
    "external": "systematic futures traders, CTAs, quant researchers, managed futures allocators"
  },
  "core_thesis": "Rules beat discretion over time. Drawdowns are information. Regime awareness is not permission to override the system.",
  "voice": "clinical, direct, no hype, process-first",
  "sections": [
    "Lead Signal",
    "Source Integrity",
    "Regime Watch",
    "Strategy Performance Signals",
    "Research & Edge",
    "Regulatory / Structure",
    "CTA / Competitor Watch",
    "Arbitrage + Moat",
    "Systematic Takes",
    "Discipline Check",
    "Hallucination Guardrails",
    "Systematic Synthesis",
    "Recommended Move",
    "Watchlist",
    "Today's Strategic Prompt",
    "Next Search"
  ],
  "personas": [
    {"name": "Covel", "focus": "trend following philosophy"},
    {"name": "Parker", "focus": "CTA operations and drawdown psychology"},
    {"name": "Hite", "focus": "risk management and position sizing"},
    {"name": "Tharp", "focus": "expectancy and system design"},
    {"name": "Market Structure Desk", "focus": "contracts, margin, exchange notices, regulation"},
    {"name": "Research Desk", "focus": "methodology, robustness, implementation drag"}
  ],
  "source_categories": {
    "tier_1": ["CFTC", "NFA", "CME", "ICE", "official filings", "academic journals"],
    "tier_2": ["SocGen", "AQR", "Two Sigma", "Newfound Research", "ReSolve", "Reuters", "Bloomberg"],
    "tier_3": ["r/algotrading", "QuantConnect forums", "Elite Trader", "trader blogs", "podcasts"],
    "tier_4": ["GitHub repos", "small CTA blogs", "conference notes", "backtest blogs"]
  },
  "minimum_findings": 3,
  "target_new_findings": 2,
  "max_read_time_minutes": 3
}
```

## Prompt Architecture
The v1 system should use four prompt layers.

## 1. System Prompt
```text
You are SYSTEMATIC, the intelligence layer for Systematic - The Living Brief for Systematic Traders.

Your job is to produce a daily, source-grounded intelligence brief for systematic futures traders. Be clinical, direct, skeptical, and process-first. Do not hype. Do not provide personalized financial advice. Do not recommend discretionary overrides unless the recommended action is to follow a prewritten rule.

Core thesis: Rules beat discretion over time. Drawdowns are information. Regime awareness is not permission to override the system.

Every hard claim needs a source, date, evidence, confidence, and caveat. Mark weak or social sources as discourse signals. Prefer new findings and meaningful updates. Preserve uncertainty.
```

## 2. Research Prompt
```text
Search for today's most relevant systematic futures trading signals across regime, CTA performance, research, regulation, and market structure.

Prioritize primary sources and trusted analysis. Use community/practitioner sources only as discourse signals. Return structured findings using the required schema. Include direct publisher URLs when available. Mark each finding NEW, UPDATE, or REPEAT based on archive memory.
```

## 3. Synthesis Prompt
```text
Synthesize the findings into Systematic - The Living Brief for Systematic Traders.

Use the required section order. Keep the brief readable in under 3 minutes. Include 2-4 Systematic Takes. Use personas only when their lens adds value. Include one Recommended Move. If there is no action, say Hold course.

Do not turn regime awareness into discretionary trading advice. Make drawdown context useful without becoming soothing fluff.
```

## 4. Integrity Prompt
```text
Before finalizing, audit the brief for missing URLs, missing source dates, weak evidence, stale data, repeated findings, unsupported performance claims, and overconfident language.

If a claim is weak, downgrade confidence or move it to WATCHLIST. If a source is promotional, say so. If a source is social/community discourse, label it as discourse. Preserve caveats in the email and JSON.
```

## Output Contract
The model should return JSON with:

```json
{
  "brief_name": "Systematic - The Living Brief for Systematic Traders",
  "date": "YYYY-MM-DD",
  "observed_at": "YYYY-MM-DD HH:MM timezone",
  "lead_signal": "",
  "source_integrity": "",
  "sections": {
    "regime_watch": [],
    "strategy_performance_signals": [],
    "research_edge": [],
    "regulatory_structure": [],
    "cta_competitor_watch": []
  },
  "arbitrage_moat": {
    "near_term_arbitrage": "",
    "future_signal": "",
    "moat_strategy": "",
    "do_not_do": ""
  },
  "systematic_takes": [],
  "discipline_check": "",
  "hallucination_guardrails": [],
  "systematic_synthesis": "",
  "recommended_move": "",
  "watchlist": [],
  "strategic_prompt": "",
  "next_search": "",
  "findings": []
}
```

## Rendering Requirements
TXT:

- scannable headings
- short paragraphs
- no markdown tables in email body
- source URLs visible

HTML:

- white background
- black text
- monospace font for data
- sans-serif for prose
- no images
- no decoration
- readable on mobile
- visible caveats

Recommended style:

```text
font-family: system-ui, Helvetica, Arial, sans-serif
data-font: Courier New, SF Mono, Consolas, monospace
max-width: 680px
background: #ffffff
color: #000000
```

## Scheduling
Primary production scheduler:

```text
GitHub Actions
```

Schedule:

```yaml
schedule:
  - cron: "0 11 * * *"
```

Note:

```text
6:00 AM Eastern is 11:00 UTC during Eastern Standard Time and 10:00 UTC during Eastern Daylight Time. GitHub Actions cron is UTC and does not support timezone keys directly. v1 should either accept the UTC offset tradeoff or use a script-level timezone check.
```

Manual run:

```text
workflow_dispatch
```

Fallback local runner:

```text
scripts/run_systematic_brief.sh
```

## Archive Requirements
Every successful run should produce:

```text
intelligence/systematic/YYYY-MM-DD-HHMM-systematic-brief.json
intelligence/systematic/YYYY-MM-DD-HHMM-systematic-brief.txt
intelligence/systematic/YYYY-MM-DD-HHMM-systematic-brief.html
```

Archive loaded before each run to prevent:

- repeating same research papers
- re-announcing known drawdowns
- duplicate regulatory updates
- pretending a known source is new
- losing thesis memory

## G-Stack Build Operating Model
Garry Tan's G-Stack is used as the build workflow, not as brief content.

Systematic should be built with this loop:

```text
Think -> Plan -> Build -> Review -> Test -> Ship -> Retro
```

How to apply it:

- Think: sharpen the wedge, audience, source strategy, and daily job-to-be-done.
- Plan: pressure-test scope, implementation risk, data flow, source integrity, and delivery.
- Build: implement the smallest reliable daily brief system before adding dashboards or advanced memory.
- Review: inspect for hallucination risk, source metadata gaps, broken email rendering, and bad archive behavior.
- Test: dry-run locally, validate JSON, render TXT/HTML, and send to test list.
- Ship: deploy GitHub Actions with secrets and manual trigger.
- Retro: after 7 runs, identify repeated weak sections, useless sources, and subscriber-facing improvements.

G-Stack should optimize the build process. It should not appear as a named section in the email.

## V1 Build Plan
1. Finalize this PRD as the executable spec.
2. Create `config/systematic.json`.
3. Create `systematic_daily_brief.py`.
4. Add provider adapters for Gemini and Anthropic.
5. Implement archive loading from `intelligence/systematic`.
6. Implement source/finding integrity checks.
7. Render JSON, TXT, and HTML.
8. Implement SMTP delivery with dry-run and test-list modes.
9. Add `scripts/run_systematic_brief.sh`.
10. Add GitHub Actions workflow with manual dispatch.
11. Run 7 local/test-list briefs.
12. Tighten voice, source list, and section value based on test runs.
13. Launch subscriber delivery.

## V1 Acceptance Criteria
The brief is successful if:

- JJ can run it locally in dry-run mode
- GitHub Actions can run it manually
- scheduled delivery is ready for daily production
- outputs are archived as JSON, TXT, and HTML
- every finding has source metadata, confidence, and caveat
- hard performance claims have source URLs
- findings are mostly NEW or meaningful UPDATEs
- uncertainty is clearly labeled
- each brief contains at least one useful strategic idea
- subscribers can read it in under 3 minutes
- it helps traders stay disciplined without encouraging discretionary overrides
- archives compound into a searchable knowledge base over time

## Non-Goals (v1)
Do not build a dashboard.

Do not scrape private communities.

Do not send live trade signals.

Do not build a backtesting engine.

Do not provide personalized financial advice.

Do not optimize for source quantity over quality.

Do not treat community discourse as verified fact.

Do not turn the brief into generic macro commentary.

Do not remove the discipline layer.

## Future Enhancements
- weekly Drawdown Context memo
- weekly Research Desk memo
- archive search
- source reputation scoring
- RSS ingestion
- automatic source registry
- CTA index tracker
- trend breadth tracker
- margin and exchange notice alert mode
- 30-day regime change report
- subscriber feedback buttons
- thought-leadership prompt generator
- research paper deduplication
- strategy teardown format
- backtest validation checklist
- "what changed in our thesis?" weekly report

## One-Line Definition
Systematic - The Living Brief for Systematic Traders is a daily, source-grounded intelligence system that helps systematic futures traders turn regime shifts, research, CTA performance, and market-structure signals into discipline, context, and durable edge.
