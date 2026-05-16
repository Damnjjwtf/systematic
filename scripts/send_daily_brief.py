#!/usr/bin/env python3
"""
Render, archive, and optionally email the daily Systematic brief.

This is intentionally provider-light: it uses the sample generator until live
source ingestion is wired, renders plain text and HTML, then sends through SMTP
when called with --send and the SMTP environment variables are present.
"""

from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
import sys
import urllib.error
import urllib.request
from datetime import datetime
from email.message import EmailMessage
from html import escape
from pathlib import Path
from typing import Any

from generate_sample_brief import build_brief, render_text, validate_required_fields


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "systematic.json"
ARCHIVE_DIR = ROOT / "intelligence" / "systematic"


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def recipients(config: dict[str, Any]) -> list[str]:
    raw = os.getenv(config.get("recipient_env", "SYSTEMATIC_BRIEF_TO"))
    if not raw:
        raw = config["default_recipient"]
    return [item.strip() for item in raw.split(",") if item.strip()]


def sender_name() -> str:
    return os.getenv(
        "SYSTEMATIC_BRIEF_FROM_NAME",
        "Systematic - The Living Brief for Systematic Traders",
    )


def sender_address() -> str:
    return os.getenv("EMAIL_FROM", os.getenv("SMTP_USERNAME", "systematic@localhost"))


def extract_email_address(value: str) -> str:
    if "<" in value and ">" in value:
        start = value.find("<") + 1
        end = value.find(">", start)
        if end > start:
            return value[start:end].strip()
    return value.strip()


def preflight_resend(to: list[str]) -> None:
    from_addr = extract_email_address(sender_address()).lower()
    if not from_addr or "@" not in from_addr:
        raise RuntimeError(
            "EMAIL_FROM is missing or invalid. Use a real sender like "
            "'Systematic <brief@your-verified-domain.com>'."
        )

    if from_addr.endswith("@resend.dev"):
        unverified_recipients = [addr for addr in to if not addr.lower().endswith("@resend.dev")]
        if unverified_recipients:
            raise RuntimeError(
                "Resend test sender detected (resend.dev). You can only send to verified/test recipients "
                "with this sender. Set EMAIL_FROM to an address on a verified domain in your Resend workspace."
            )


def subject_for(brief: dict[str, Any]) -> str:
    return f"Systematic Brief - {brief['date']}"


def section_title(value: str) -> str:
    return value.replace("_", " ").upper()


def section_tag(value: str) -> str:
    labels = {
        "regime_watch": "Regime",
        "strategy_performance_signals": "Performance",
        "research_edge": "Research",
        "regulatory_structure": "Regulatory",
        "cta_competitor_watch": "CTA/Competitor",
    }
    return labels.get(value, value.replace("_", " ").title())


def finding_html(item: dict[str, Any], tag: str) -> str:
    source = escape(item["source"])
    title = escape(item["title"])
    summary = escape(item["summary"])
    caveat = escape(item["caveat"])
    signal = escape(item["systematic_signal"])
    url = escape(item["url"], quote=True)
    confidence = escape(item["confidence"])
    tier = escape(item["source_tier"])

    return f"""
      <article style="margin:0 0 18px;">
        <p style="margin:0 0 4px;font-family:'Courier New','SF Mono',Consolas,monospace;font-size:12px;color:#4b5563;">{escape(tag)}</p>
        <p style="margin:0 0 6px;"><strong>{title}</strong></p>
        <p style="margin:0 0 6px;">{summary}</p>
        <p style="margin:0 0 6px;"><strong>Signal:</strong> {signal}</p>
        <p style="margin:0 0 6px;"><strong>Caveat:</strong> {caveat}</p>
        <p style="margin:0;font-family:'Courier New','SF Mono',Consolas,monospace;font-size:13px;">
          {tier} | {confidence} | <a href="{url}">{source}</a>
        </p>
      </article>
    """


def render_html(brief: dict[str, Any]) -> str:
    title = escape(f"{brief['brief_name']} - {brief['date']}")
    findings_html: list[str] = []

    for key, items in brief["sections"].items():
        tag = section_tag(key)
        for item in items:
            findings_html.append(finding_html(item, tag))

    takes = "\n".join(
        f"""
      <p style="margin:0 0 10px;"><strong>{escape(' + '.join(take['voices']))}:</strong>
      {escape(take['take'])} {escape(take['action'])}</p>
        """
        for take in brief["systematic_takes"]
    )
    guardrails = "\n".join(
        f"<p style=\"margin:0 0 6px;\">- {escape(item)}</p>"
        for item in brief["hallucination_guardrails"]
    )
    watchlist = "\n".join(
        f"""
      <p style="margin:0 0 10px;"><strong>{escape(item['item'])}:</strong>
      {escape(item['trigger'])}</p>
        """
        for item in brief["watchlist"]
    )
    arbitrage = brief["arbitrage_moat"]

    disclaimer = escape(
        brief.get(
            "disclaimer",
            "This brief is for research context only and is not personalized financial advice.",
        )
    )

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{title}</title>
  </head>
  <body style="margin:0;background:#ffffff;color:#000000;font-family:system-ui,Helvetica,Arial,sans-serif;line-height:1.5;">
    <main style="max-width:680px;margin:0 auto;padding:28px 18px;">
      <h1 style="font-size:22px;margin:0 0 4px;">SYSTEMATIC - THE LIVING BRIEF FOR SYSTEMATIC TRADERS</h1>
      <p style="margin:0 0 24px;font-family:'Courier New','SF Mono',Consolas,monospace;font-size:13px;">
        {escape(brief['date'])} | Observed {escape(brief['observed_at'])}
      </p>

      <p style="margin:0 0 18px;padding:12px;border:1px solid #e5e7eb;border-radius:8px;background:#f9fafb;font-size:13px;">
        {disclaimer}
      </p>

      <h2 style="font-size:14px;margin:24px 0 8px;">LEAD SIGNAL</h2>
      <p>{escape(brief['lead_signal'])}</p>

      <h2 style="font-size:14px;margin:24px 0 8px;">SOURCE INTEGRITY</h2>
      <p>{escape(brief['source_integrity'])}</p>

      <h2 style="font-size:14px;margin:24px 0 8px;">CORE FINDINGS</h2>
      {''.join(findings_html)}

      <h2 style="font-size:14px;margin:24px 0 8px;">ARBITRAGE + MOAT</h2>
      <p><strong>Near-term arbitrage:</strong> {escape(arbitrage['near_term_arbitrage'])}</p>
      <p><strong>Future signal:</strong> {escape(arbitrage['future_signal'])}</p>
      <p><strong>Moat strategy:</strong> {escape(arbitrage['moat_strategy'])}</p>
      <p><strong>Do not do:</strong> {escape(arbitrage['do_not_do'])}</p>

      <h2 style="font-size:14px;margin:24px 0 8px;">SYSTEMATIC TAKES (AI LENSES)</h2>
      {takes}

      <h2 style="font-size:14px;margin:24px 0 8px;">DISCIPLINE CHECK</h2>
      <p>{escape(brief['discipline_check'])}</p>

      <h2 style="font-size:14px;margin:24px 0 8px;">HALLUCINATION GUARDRAILS</h2>
      {guardrails}

      <h2 style="font-size:14px;margin:24px 0 8px;">SYSTEMATIC SYNTHESIS</h2>
      <p>{escape(brief['systematic_synthesis'])}</p>

      <h2 style="font-size:14px;margin:24px 0 8px;">RECOMMENDED MOVE (FOR JJ)</h2>
      <p>{escape(brief['recommended_move'])}</p>

      <h2 style="font-size:14px;margin:24px 0 8px;">WATCHLIST</h2>
      {watchlist}

      <h2 style="font-size:14px;margin:24px 0 8px;">TODAY'S STRATEGIC PROMPT (FOR JJ)</h2>
      <p>{escape(brief['strategic_prompt'])}</p>

      <h2 style="font-size:14px;margin:24px 0 8px;">NEXT SEARCH</h2>
      <p style="font-family:'Courier New','SF Mono',Consolas,monospace;font-size:13px;">{escape(brief['next_search'])}</p>
    </main>
  </body>
</html>
"""


def archive_paths(brief: dict[str, Any]) -> tuple[Path, Path, Path]:
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    base = ARCHIVE_DIR / f"{timestamp}-systematic-brief"
    return base.with_suffix(".json"), base.with_suffix(".txt"), base.with_suffix(".html")


def write_archive(brief: dict[str, Any], text: str, html: str) -> tuple[Path, Path, Path]:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    json_path, txt_path, html_path = archive_paths(brief)
    json_path.write_text(json.dumps(brief, indent=2) + "\n", encoding="utf-8")
    txt_path.write_text(text, encoding="utf-8")
    html_path.write_text(html, encoding="utf-8")
    return json_path, txt_path, html_path


def smtp_required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required SMTP environment variable: {name}")
    return value


def send_email_smtp(*, to: list[str], subject: str, text: str, html: str) -> None:
    host = smtp_required("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = smtp_required("SMTP_USERNAME")
    password = smtp_required("SMTP_PASSWORD")
    from_addr = sender_address()

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{sender_name()} <{from_addr}>"
    message["To"] = ", ".join(to)
    message.set_content(text)
    message.add_alternative(html, subtype="html")

    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=30) as smtp:
            smtp.login(username, password)
            smtp.send_message(message)
        return

    with smtplib.SMTP(host, port, timeout=30) as smtp:
        if env_bool("SMTP_USE_TLS", True):
            smtp.starttls()
        smtp.login(username, password)
        smtp.send_message(message)


def send_email_resend(*, to: list[str], subject: str, text: str, html: str) -> None:
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise RuntimeError("Missing required environment variable: RESEND_API_KEY")
    preflight_resend(to)

    payload = {
        "from": extract_email_address(sender_address()),
        "to": to,
        "subject": subject,
        "text": text,
        "html": html,
    }
    request = urllib.request.Request(
        url="https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "systematic-brief/1.0 (+https://futurestrader.news)",
        },
        method="POST",
    )

    ssl_context = None
    try:
        import certifi  # type: ignore

        ssl_context = ssl.create_default_context(cafile=certifi.where())
    except Exception:
        ssl_context = ssl.create_default_context()

    try:
        with urllib.request.urlopen(request, timeout=30, context=ssl_context) as response:
            body = response.read().decode("utf-8")
            if response.status >= 300:
                raise RuntimeError(f"Resend returned status {response.status}: {body}")
    except ssl.SSLError as error:
        raise RuntimeError(
            "TLS certificate verification failed. Install certifi (`python3 -m pip install certifi`) "
            "or run the macOS Install Certificates command for your Python distribution."
        ) from error
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8")
        if error.code == 403:
            raise RuntimeError(
                "Resend rejected this request (403). Most likely causes: sender domain not verified, "
                "sender belongs to another workspace, or using resend.dev sender with unverified recipients. "
                "Verify domain in Resend and set EMAIL_FROM to that domain. "
                f"Resend detail: {detail}"
            ) from error
        raise RuntimeError(f"Resend API error ({error.code}): {detail}") from error


def send_email(*, to: list[str], subject: str, text: str, html: str) -> None:
    provider = os.getenv("SYSTEMATIC_BRIEF_EMAIL_PROVIDER", "").strip().lower()

    if provider == "resend" or (not provider and os.getenv("RESEND_API_KEY")):
        send_email_resend(to=to, subject=subject, text=text, html=html)
        return

    send_email_smtp(to=to, subject=subject, text=text, html=html)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render/archive/send the daily Systematic brief.")
    parser.add_argument("--send", action="store_true", help="Send through SMTP after rendering.")
    parser.add_argument("--dry-run", action="store_true", help="Render and archive without sending.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config()
    to = recipients(config)
    brief = build_brief()
    validate_required_fields(brief)
    text = render_text(brief)
    html = render_html(brief)
    json_path, txt_path, html_path = write_archive(brief, text, html)

    print(f"Archived JSON: {json_path.relative_to(ROOT)}")
    print(f"Archived TXT:  {txt_path.relative_to(ROOT)}")
    print(f"Archived HTML: {html_path.relative_to(ROOT)}")
    print(f"Recipient(s):  {', '.join(to)}")

    should_send = args.send and not args.dry_run and not env_bool("SYSTEMATIC_BRIEF_DRY_RUN")
    if not should_send:
        print("Dry run: email not sent")
        return 0

    send_email(to=to, subject=subject_for(brief), text=text, html=html)
    print("Email sent")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(1)
