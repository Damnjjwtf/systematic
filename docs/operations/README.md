# Systematic Operations Layer

These docs were merged from the Living Brief PR and kept as the operating layer for Systematic.

## Reading Order

1. `sources_and_data.md` - source universe, costs, licensing posture, and rollout tiers.
2. `data_architecture.md` - ingestion flow, brief object shape, freshness SLAs, and storage plan.
3. `brief_schema_mapping.md` - how raw data becomes findings, caveats, confidence, and watchlist triggers.
4. `data_monitoring.md` - dashboard rules, alerts, accuracy scoring, and publication checklists.
5. `data_quality_debug.md` - incident triage for missing, stale, corrupt, or rate-limited data.
6. `on_call_playbook.md` - operational recovery guide for brief publication failures.
7. `cost_tracking.md` - cost model, API call attribution, and monthly budget reporting.
8. `gstack_review.md` - original CEO/design/engineering/DevEx review notes from the imported PR.

## Local Mapping

The imported PR used `S/A/B/C` source labels in places. Systematic's canonical schema uses:

```text
TIER_1 = primary / official / high-trust sources
TIER_2 = trusted analysis
TIER_3 = community or practitioner discourse
TIER_4 = edge, weak, experimental, or internal operating sources
```

Use the canonical `TIER_1` through `TIER_4` values in generated JSON.
