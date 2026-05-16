# Systematic - The Living Brief for Systematic Traders

A daily, source-grounded intelligence brief for systematic futures traders.

The brief tracks market regimes, CTA performance, systematic research, futures market structure, regulation, and trader discipline. Its core thesis:

> Rules beat discretion over time. Drawdowns are information. Regime awareness is not permission to override the system.

## Current V1 Artifacts

- `systematic_brief_prd.md` - executable product and build spec
- `docs/living_briefs_north_star.md` - category and product north star
- `config/systematic.json` - operating config
- `prompts/systematic_brief_prompts.md` - prompt architecture
- `schemas/systematic_brief.schema.json` - structured output contract
- `docs/operations/` - merged Living Brief operating layer: data architecture, source strategy, monitoring, costs, debugging, and on-call playbooks
- `scripts/generate_sample_brief.py` - local sample generator for the Systematic brief schema
- `samples/` - generated JSON/TXT examples for review and iteration

## Merged Living Brief Layer

This repo now combines the Systematic product spec with the operational blueprint from the Living Brief PR:

- source-grounded brief objects
- source tiers and caveats
- data freshness and monitoring rules
- cost tracking and vendor strategy
- watchlist trigger procedures
- archive memory as the long-term moat

The merge keeps Systematic's futures-trader focus and maps the imported architecture into this repo's `TIER_1` through `TIER_4` source model.

## Local Sample Build

Generate a sample brief:

```bash
python3 scripts/generate_sample_brief.py
```

This writes:

```text
samples/systematic_brief_2026-05-16.json
samples/systematic_brief_2026-05-16.txt
```

The script performs lightweight required-field validation so the sample remains aligned with `schemas/systematic_brief.schema.json`.

## Daily Email

Render and archive the daily email without sending:

```bash
python3 scripts/send_daily_brief.py --dry-run
```

Send it through Resend:

```bash
python3 scripts/send_daily_brief.py --send
```

Default recipient:

```text
jj@damnjj.wtf
```

Required Resend environment:

```bash
RESEND_API_KEY=
EMAIL_FROM=
SYSTEMATIC_BRIEF_TO=jj@damnjj.wtf
```

The scheduled GitHub Action in `.github/workflows/daily-systematic-brief.yml` runs at 11:00 UTC, which is 6:00 AM Eastern during standard time. Add `RESEND_API_KEY`, `EMAIL_FROM`, and `SYSTEMATIC_BRIEF_TO` as repository secrets before enabling live sends.

## Next Build Targets

1. Add ingestion modules for the first Tier 1 sources: CFTC, CME/ICE notices, Federal Register, and official CTA index data.
2. Persist every finding, caveat, watchlist item, and recommended move as archive memory.
3. Add a brief renderer that turns the JSON object into email-ready HTML/TXT.
4. Add a daily runner that loads config, gathers sources, validates output, writes archive artifacts, and prepares delivery.

## Build Loop

Garry Tan's G-Stack is used as the build operating model:

```text
Think -> Plan -> Build -> Review -> Test -> Ship -> Retro
```

G-Stack governs how this system is built. It is not a visible editorial section in the daily brief.
