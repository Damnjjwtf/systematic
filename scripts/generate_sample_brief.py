#!/usr/bin/env python3
"""
Generate a sample Systematic Living Brief.

The sample turns the imported Living Brief operating model into the schema used
by this repo: source-grounded findings, visible caveats, archive memory,
watchlist triggers, and one disciplined recommended move.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT / "samples"
OUTPUT_JSON = SAMPLES_DIR / "systematic_brief_2026-05-16.json"
OUTPUT_TXT = SAMPLES_DIR / "systematic_brief_2026-05-16.txt"


def finding(
    *,
    title: str,
    source: str,
    url: str,
    source_date: str,
    newness: str,
    source_tier: str,
    evidence: str,
    summary: str,
    systematic_signal: str,
    future_vector: str,
    arbitrage: str,
    moat_move: str,
    verification_status: str,
    confidence: str,
    caveat: str,
    signal_strength: str,
    regime_read: str | None = None,
    risk: str | None = None,
    data_point: dict[str, Any] | None = None,
    archive_memory: dict[str, Any] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "title": title,
        "source": source,
        "url": url,
        "source_date": source_date,
        "observed_at": "2026-05-16 06:00 America/New_York",
        "newness": newness,
        "source_tier": source_tier,
        "evidence": evidence,
        "summary": summary,
        "systematic_signal": systematic_signal,
        "arbitrage_moat": {
            "future_vector": future_vector,
            "arbitrage": arbitrage,
            "moat_move": moat_move,
        },
        "verification_status": verification_status,
        "confidence": confidence,
        "caveat": caveat,
        "signal_strength": signal_strength,
    }

    if regime_read:
        item["regime_read"] = regime_read
    if risk:
        item["risk"] = risk
    if data_point:
        item["data_point"] = data_point
    if archive_memory:
        item["archive_memory"] = archive_memory

    return item


def build_brief() -> dict[str, Any]:
    regime_watch = [
        finding(
            title="VIX remains elevated while credit spreads are not yet confirming stress",
            source="CBOE VIX and FRED ICE BofA spread series",
            url="https://fred.stlouisfed.org/series/VIXCLS",
            source_date="2026-05-15",
            newness="UPDATE",
            source_tier="TIER_1",
            evidence="Volatility is elevated, but high-yield spreads remain below the stress trigger defined in the operating docs.",
            summary="The tape is uncomfortable, not broken. Volatility is warning that positioning is fragile, while credit has not yet moved into a broad risk-off regime.",
            systematic_signal="Trend systems should treat this as regime friction, not as permission to override live rules.",
            regime_read="HOT: risk-on momentum with elevated volatility and partial confirmation only.",
            future_vector="If HY OAS widens through the watch threshold, this shifts from noisy volatility to confirmed credit stress.",
            arbitrage="Many readers will overreact to VIX alone; the edge is waiting for cross-asset confirmation.",
            moat_move="Track when volatility-only alerts resolve or fail so Systematic builds a source accuracy record.",
            verification_status="PARTIAL",
            confidence="MEDIUM",
            caveat="VIX can spike around event risk and options positioning without becoming a durable trend regime change.",
            signal_strength="MEDIUM",
            data_point={
                "metric": "VIX",
                "value": 22,
                "normal_range": "12-20",
                "status": "elevated",
            },
            archive_memory={
                "last_seen": "2026-04-02",
                "then": "VIX spike faded after three sessions without credit confirmation.",
                "lesson": "Do not treat volatility alone as a system change.",
            },
        )
    ]

    strategy_performance = [
        finding(
            title="Crowded equity futures positioning raises mean-reversion risk",
            source="CFTC Commitments of Traders",
            url="https://publicreporting.cftc.gov/",
            source_date="2026-05-15",
            newness="NEW",
            source_tier="TIER_1",
            evidence="Non-commercial ES positioning is described as crowded long in the sample operating model.",
            summary="Crowding is not a sell signal by itself, but it makes trend continuation more fragile. A reversal in next week's COT report would matter more than today's crowding headline.",
            systematic_signal="Positioning risk belongs in the watchlist and risk review, not in discretionary prediction.",
            future_vector="The actionable signal is a week-over-week reversal in positioning, not the existence of crowding alone.",
            arbitrage="Most commentary treats crowded positioning as immediate direction; Systematic can frame it as conditional risk.",
            moat_move="Build a COT archive that records whether crowded readings actually preceded systematic drawdowns.",
            verification_status="WATCHLIST",
            confidence="MEDIUM",
            caveat="COT data is delayed and should be cross-checked with price, volatility, and liquidity.",
            signal_strength="MEDIUM",
            data_point={
                "metric": "Non-commercial ES positioning",
                "status": "crowded_long",
                "freshness_lag": "weekly release",
            },
            archive_memory={
                "last_seen": "2026-02-12",
                "then": "Crowding preceded a short equity correction, but trend rules recovered without parameter changes.",
                "lesson": "Crowding informs heat, not trade direction.",
            },
        )
    ]

    research_edge = [
        finding(
            title="The useful research question is robustness, not fresh alpha",
            source="Systematic operating spec",
            url="docs/operations/brief_schema_mapping.md",
            source_date="2026-05-16",
            newness="NEW",
            source_tier="TIER_4",
            evidence="The operating docs prioritize signal design, out-of-sample skepticism, transaction costs, and implementation drag.",
            summary="The brief should not chase every new backtest. It should filter research through whether it changes robustness, execution, sizing, or regime classification.",
            systematic_signal="Research belongs in the brief only when it can change a system design assumption or an operational checklist.",
            future_vector="The research section should mature into a recurring implementation-quality score.",
            arbitrage="There is more reader value in rejecting weak research than summarizing lots of papers.",
            moat_move="Create a recurring archive of rejected research patterns and why they failed the Systematic filter.",
            verification_status="PARTIAL",
            confidence="MEDIUM",
            caveat="This is an internal operating principle, not an external market observation.",
            signal_strength="LOW",
        )
    ]

    regulatory_structure = [
        finding(
            title="Data licensing is a product risk, not just an engineering detail",
            source="Imported sources and data strategy",
            url="docs/operations/sources_and_data.md",
            source_date="2026-05-16",
            newness="NEW",
            source_tier="TIER_4",
            evidence="The source strategy distinguishes public-domain sources from proprietary data that may require attribution or limit republication.",
            summary="The MVP should lean on public and clearly citable sources. Premium sources can improve speed, but they also increase licensing, attribution, and cost obligations.",
            systematic_signal="A source-grounded brief is only defensible if its data rights and citation rules are operationally clean.",
            risk="Republishing proprietary data or news summaries too aggressively could create licensing exposure.",
            future_vector="Before paid launch, source rights should become a checklist item in the publication workflow.",
            arbitrage="A transparent source-rights posture can become trust infrastructure while competitors stay vague.",
            moat_move="Track source licensing status alongside source tier and source accuracy.",
            verification_status="PARTIAL",
            confidence="HIGH",
            caveat="Specific vendor terms still need direct legal/product review before commercial use.",
            signal_strength="HIGH",
        )
    ]

    cta_competitor_watch = [
        finding(
            title="The near-term moat is a disciplined archive, not a faster news feed",
            source="Living Briefs north star and GStack review",
            url="docs/living_briefs_north_star.md",
            source_date="2026-05-16",
            newness="UPDATE",
            source_tier="TIER_4",
            evidence="The north star defines archive memory, source reputation, and constrained conversation as the product advantage.",
            summary="Systematic should not compete with Bloomberg or Reuters on speed. It should compound memory around source reliability, repeated regimes, caveats, and decisions avoided.",
            systematic_signal="The archive is the product surface that turns daily publishing into accumulated edge.",
            future_vector="After 30 daily issues, comparison questions become a real feature; after 100, they become a moat.",
            arbitrage="Most newsletters discard yesterday. Systematic should make yesterday queryable.",
            moat_move="Store every finding, caveat, watch trigger, and recommended move as structured data from day one.",
            verification_status="VERIFIED",
            confidence="HIGH",
            caveat="The moat only compounds if the brief is published consistently and outcomes are reviewed.",
            signal_strength="HIGH",
        )
    ]

    findings = (
        regime_watch
        + strategy_performance
        + research_edge
        + regulatory_structure
        + cta_competitor_watch
    )

    return {
        "brief_name": "Systematic - The Living Brief for Systematic Traders",
        "date": "2026-05-16",
        "observed_at": "2026-05-16 06:00 America/New_York",
        "lead_signal": "Volatility is elevated, but Systematic should wait for cross-asset confirmation before treating this as a regime break.",
        "source_integrity": "This sample uses imported operating docs and public-source placeholders. Market values are illustrative until live ingestion is wired.",
        "sections": {
            "regime_watch": regime_watch,
            "strategy_performance_signals": strategy_performance,
            "research_edge": research_edge,
            "regulatory_structure": regulatory_structure,
            "cta_competitor_watch": cta_competitor_watch,
        },
        "arbitrage_moat": {
            "near_term_arbitrage": "Frame noisy market stress as conditional evidence instead of content urgency.",
            "future_signal": "If the watchlist triggers confirm, the brief can update from HOT to STRESSED without sounding reactive.",
            "moat_strategy": "Persist source tiers, caveats, archive memory, and outcome reviews for every finding.",
            "do_not_do": "Do not turn VIX, COT, or CTA commentary into discretionary override language.",
        },
        "systematic_takes": [
            {
                "voices": ["Parker", "Hite"],
                "take": "The job is to reduce heat, not invent a prediction.",
                "why_it_matters": "Crowding and volatility can make good systems feel broken before they actually are.",
                "action": "Review drawdown bands, margin exposure, and rule adherence before touching parameters.",
            },
            {
                "voices": ["Research Desk"],
                "take": "Rejecting weak research is part of the edge.",
                "why_it_matters": "Systematic traders are vulnerable to elegant backtests during uncomfortable regimes.",
                "action": "Only promote research that changes a testable implementation assumption.",
            },
        ],
        "discipline_check": "Do not override a live system because one volatility signal feels urgent.",
        "hallucination_guardrails": [
            "Market values in this sample are illustrative.",
            "COT positioning is delayed and should not be treated as real-time confirmation.",
            "Internal docs are useful operating sources but not external market evidence.",
            "No personalized financial advice is provided.",
        ],
        "systematic_synthesis": "The sample brief demonstrates the intended operating posture: source-grounded, conditional, archive-aware, and allergic to discretionary panic. The next build step is ingestion and storage, not more prose.",
        "recommended_move": "Create the first real archive entry and start tracking whether each watchlist trigger resolves, fails, or remains pending.",
        "watchlist": [
            {
                "item": "High-yield spread confirmation",
                "why": "Credit confirmation separates noisy volatility from broader market stress.",
                "trigger": "HY OAS widens through the configured stress threshold or rises sharply over five sessions.",
            },
            {
                "item": "COT reversal from crowded long positioning",
                "why": "A positioning reversal matters more than crowded exposure alone.",
                "trigger": "Next weekly COT report shows a material non-commercial reduction.",
            },
            {
                "item": "Source rights and licensing",
                "why": "The product promise depends on defensible citation and republication rules.",
                "trigger": "Any paid vendor data is used in subscriber-facing output.",
            },
        ],
        "strategic_prompt": "What will Systematic remember in 30 days that a normal market newsletter will have forgotten?",
        "next_search": "latest CFTC COT equity futures positioning managed futures trend following drawdown",
        "findings": findings,
        "data_freshness": {
            "freshness_status": "SAMPLE_ONLY",
            "latest_data_point": "2026-05-15",
            "missing_live_ingestion": True,
        },
    }


def validate_required_fields(brief: dict[str, Any]) -> None:
    required_top_level = [
        "brief_name",
        "date",
        "observed_at",
        "lead_signal",
        "source_integrity",
        "sections",
        "arbitrage_moat",
        "systematic_takes",
        "discipline_check",
        "hallucination_guardrails",
        "systematic_synthesis",
        "recommended_move",
        "watchlist",
        "strategic_prompt",
        "next_search",
        "findings",
    ]
    required_finding = [
        "title",
        "source",
        "url",
        "source_date",
        "observed_at",
        "newness",
        "source_tier",
        "evidence",
        "summary",
        "systematic_signal",
        "arbitrage_moat",
        "verification_status",
        "confidence",
        "caveat",
        "signal_strength",
    ]

    missing = [field for field in required_top_level if field not in brief]
    if missing:
        raise ValueError(f"Missing top-level fields: {', '.join(missing)}")

    for index, item in enumerate(brief["findings"], start=1):
        missing_finding = [field for field in required_finding if field not in item]
        if missing_finding:
            fields = ", ".join(missing_finding)
            raise ValueError(f"Finding {index} is missing required fields: {fields}")


def render_text(brief: dict[str, Any]) -> str:
    lines = [
        brief["brief_name"].upper(),
        brief["date"],
        "",
        f"Lead Signal: {brief['lead_signal']}",
        "",
        "Source Integrity",
        brief["source_integrity"],
        "",
        "Findings",
    ]

    for index, item in enumerate(brief["findings"], start=1):
        lines.extend(
            [
                "",
                f"{index}. {item['title']}",
                f"   Source: {item['source']} ({item['source_tier']})",
                f"   Confidence: {item['confidence']} | Signal: {item['signal_strength']}",
                f"   Summary: {item['summary']}",
                f"   Caveat: {item['caveat']}",
            ]
        )

    lines.extend(
        [
            "",
            "Systematic Synthesis",
            brief["systematic_synthesis"],
            "",
            f"Recommended Move: {brief['recommended_move']}",
            "",
            "Watchlist",
        ]
    )

    for item in brief["watchlist"]:
        lines.append(f"- {item['item']}: {item['trigger']}")

    lines.extend(["", f"Today's Strategic Prompt: {brief['strategic_prompt']}"])
    return "\n".join(lines) + "\n"


def main() -> None:
    brief = build_brief()
    validate_required_fields(brief)

    SAMPLES_DIR.mkdir(exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(brief, indent=2) + "\n", encoding="utf-8")
    OUTPUT_TXT.write_text(render_text(brief), encoding="utf-8")

    print(f"Wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {OUTPUT_TXT.relative_to(ROOT)}")
    print(f"Validated {len(brief['findings'])} findings against required fields")


if __name__ == "__main__":
    main()
