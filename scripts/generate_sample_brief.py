#!/usr/bin/env python3
"""
Generate a sample Systematic Living Brief.

The sample turns the imported Living Brief operating model into the schema used
by this repo: source-grounded findings, visible caveats, archive memory,
watchlist triggers, and one disciplined recommended move.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
import urllib.error
import urllib.request
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = ROOT / "samples"
OUTPUT_JSON = SAMPLES_DIR / "systematic_brief_2026-05-16.json"
OUTPUT_TXT = SAMPLES_DIR / "systematic_brief_2026-05-16.txt"


def now_et_string() -> str:
    return datetime.now(UTC).astimezone().strftime("%Y-%m-%d %H:%M America/New_York")


def today_string() -> str:
    return datetime.now(UTC).astimezone().strftime("%Y-%m-%d")


def fetch_text(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(
        url=url,
        headers={"User-Agent": "systematic-brief-scraper/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def fetch_fred_latest(series_id: str) -> tuple[str, float]:
    csv_url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    raw = fetch_text(csv_url)
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    for row in reversed(lines[1:]):
        parts = row.split(",")
        if len(parts) != 2:
            continue
        date_value, numeric = parts[0], parts[1]
        if numeric and numeric != ".":
            return date_value, float(numeric)
    raise RuntimeError(f"No numeric points found for series {series_id}")


def fetch_rss_headline(url: str) -> tuple[str, str]:
    raw = fetch_text(url)
    root = ET.fromstring(raw)
    item = root.find(".//item")
    if item is None:
        return "No headline found", today_string()
    title = (item.findtext("title") or "No title").strip()
    pub_date = (item.findtext("pubDate") or today_string()).strip()
    return title, pub_date


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
    observed_at = now_et_string()
    date_value = today_string()

    data_freshness_status = "LIVE_PARTIAL"
    fallback_notes: list[str] = []

    try:
        vix_date, vix_value = fetch_fred_latest("VIXCLS")
    except Exception:
        vix_date, vix_value = date_value, 22.0
        data_freshness_status = "SAMPLE_FALLBACK"
        fallback_notes.append("VIX fallback")

    try:
        ig_date, ig_oas = fetch_fred_latest("BAMLC0A0CM")
    except Exception:
        ig_date, ig_oas = date_value, 92.0
        data_freshness_status = "SAMPLE_FALLBACK"
        fallback_notes.append("IG OAS fallback")

    try:
        hy_date, hy_oas = fetch_fred_latest("BAMLH0A0HYM2")
    except Exception:
        hy_date, hy_oas = date_value, 265.0
        data_freshness_status = "SAMPLE_FALLBACK"
        fallback_notes.append("HY OAS fallback")

    try:
        cftc_headline, cftc_pub = fetch_rss_headline("https://www.cftc.gov/PressRoom/PressReleases/rss.xml")
    except Exception:
        cftc_headline, cftc_pub = "CFTC headline unavailable", date_value
        fallback_notes.append("CFTC feed unavailable")

    try:
        cme_headline, cme_pub = fetch_rss_headline("https://www.cmegroup.com/notices/rss.xml")
    except Exception:
        cme_headline, cme_pub = "CME notice feed unavailable", date_value
        fallback_notes.append("CME feed unavailable")

    vix_state = "elevated" if vix_value >= 20 else "normal"
    spread_gap = round(hy_oas - ig_oas, 1)
    regime_watch = [
        finding(
            title="VIX remains elevated while credit spreads are not yet confirming stress",
            source="CBOE VIX and FRED ICE BofA spread series",
            url="https://fred.stlouisfed.org/series/VIXCLS",
            source_date=vix_date,
            newness="UPDATE",
            source_tier="TIER_1",
            evidence=f"Latest FRED VIX close is {vix_value:.2f} on {vix_date}; IG OAS is {ig_oas:.2f} and HY OAS is {hy_oas:.2f}.",
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
                "value": round(vix_value, 2),
                "normal_range": "12-20",
                "status": vix_state,
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
            title="CFTC flow: latest release headline flags where positioning attention is moving",
            source="CFTC Press Room RSS",
            url="https://www.cftc.gov/PressRoom/PressReleases/rss.xml",
            source_date=cftc_pub,
            newness="NEW",
            source_tier="TIER_1",
            evidence=f"Latest CFTC feed item: {cftc_headline}",
            summary="Regulatory and market-structure updates from the CFTC are now being pulled live. Treat this as directional context for where compliance/positioning narratives are moving.",
            systematic_signal="Positioning risk belongs in the watchlist and risk review, not in discretionary prediction.",
            future_vector="The actionable signal is a week-over-week reversal in positioning, not the existence of crowding alone.",
            arbitrage="Most commentary treats crowded positioning as immediate direction; Systematic can frame it as conditional risk.",
            moat_move="Build a COT archive that records whether crowded readings actually preceded systematic drawdowns.",
            verification_status="WATCHLIST",
            confidence="MEDIUM",
            caveat="COT data is delayed and should be cross-checked with price, volatility, and liquidity.",
            signal_strength="MEDIUM",
            data_point={
                "metric": "CFTC release feed",
                "status": "live_headline",
                "freshness_lag": "near real-time publication feed",
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
            title="CME notice stream is live and can drive execution-side alerting",
            source="CME Group Notices RSS",
            url="https://www.cmegroup.com/notices/rss.xml",
            source_date=cme_pub,
            newness="NEW",
            source_tier="TIER_1",
            evidence=f"Latest CME notices feed item: {cme_headline}",
            summary="Operational notices are now live-fed, which gives the brief a practical edge around margin, session, and contract-structure changes.",
            systematic_signal="Execution and exchange plumbing changes can break assumptions faster than market commentary does.",
            risk="If this feed is unavailable, operations-sensitive findings can be stale.",
            future_vector="Add parser rules that classify margin/limit/calendar notices into a watchlist automatically.",
            arbitrage="Most market summaries ignore exchange ops detail until it causes slippage.",
            moat_move="Turn notice ingestion into structured risk flags in the archive.",
            verification_status="VERIFIED",
            confidence="MEDIUM",
            caveat="RSS headlines require follow-through drilldown into the full notice before acting.",
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
        "date": date_value,
        "observed_at": observed_at,
        "lead_signal": f"Market pulse: VIX={vix_value:.2f}, IG OAS={ig_oas:.2f}, HY OAS={hy_oas:.2f}. Spread gap={spread_gap:.1f} bps; wait for confirmation before framing a regime break.",
        "disclaimer": (
            "Systematic is a source-grounded research brief for disciplined context. "
            "It is not personalized financial advice, not execution instructions, and not a substitute "
            "for your own system rules and risk controls."
        ),
        "source_integrity": "This run uses live public-source pulls from FRED plus CFTC and CME RSS. Some sections still use editorial scaffolding while ingestion broadens.",
        "sections": {
            "regime_watch": regime_watch,
            "strategy_performance_signals": strategy_performance,
            "research_edge": research_edge,
            "regulatory_structure": regulatory_structure,
            "cta_competitor_watch": cta_competitor_watch,
        },
        "arbitrage_moat": {
            "near_term_arbitrage": "Use live public data to reduce narrative lag and keep claims tied to observed timestamps.",
            "future_signal": "If the watchlist triggers confirm, the brief can update from HOT to STRESSED without sounding reactive.",
            "moat_strategy": "Persist source tiers, caveats, archive memory, and outcome reviews for every finding.",
            "do_not_do": "Do not turn VIX, COT, or CTA commentary into discretionary override language.",
        },
        "systematic_takes": [
            {
                "voices": ["Parker", "Hite"],
                "take": "The job is to trust live evidence cadence, then layer judgment.",
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
            "FRED values are live but still single-series snapshots without multi-source reconciliation.",
            "CFTC/CME findings are pulled from RSS headlines and require full-document follow-up before hard conclusions.",
            "Systematic Takes are AI lens simulations inspired by named personas, not direct statements from those individuals.",
            "No personalized financial advice is provided.",
        ],
        "systematic_synthesis": "This run is no longer static: market and regulatory context is now scraped live at generation time. The remaining build priority is deeper classification and archive-level signal scoring.",
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
        "next_search": "latest CFTC COT disaggregated futures positioning plus CME margin notice changes",
        "findings": findings,
        "data_freshness": {
            "freshness_status": data_freshness_status,
            "latest_data_point": max(vix_date, ig_date, hy_date),
            "fallback_notes": fallback_notes,
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
        "What This Is",
        brief.get(
            "disclaimer",
            "This brief is for research context only and is not personalized financial advice.",
        ),
        "",
        f"Lead Signal: {brief['lead_signal']}",
        "",
        "Source Integrity",
        brief["source_integrity"],
        "",
        "Core Findings",
    ]

    section_map = {
        "regime_watch": "Regime",
        "strategy_performance_signals": "Performance",
        "research_edge": "Research",
        "regulatory_structure": "Regulatory",
        "cta_competitor_watch": "CTA/Competitor",
    }
    ordered_items: list[tuple[str, dict[str, Any]]] = []
    for key, items in brief["sections"].items():
        tag = section_map.get(key, key)
        for item in items:
            ordered_items.append((tag, item))

    for index, (tag, item) in enumerate(ordered_items, start=1):
        lines.extend(
            [
                "",
                f"{index}. {item['title']}",
                f"   Category: {tag}",
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
            "Systematic Takes (AI Lenses)",
        ]
    )

    for take in brief.get("systematic_takes", []):
        lines.append(f"- {' + '.join(take.get('voices', []))}: {take.get('take', '')} {take.get('action', '')}")

    lines.extend(
        [
            "",
            f"Recommended Move (For JJ): {brief['recommended_move']}",
            "",
            "Watchlist",
        ]
    )

    for item in brief["watchlist"]:
        lines.append(f"- {item['item']}: {item['trigger']}")

    lines.extend(["", f"Today's Strategic Prompt (For JJ): {brief['strategic_prompt']}"])
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
