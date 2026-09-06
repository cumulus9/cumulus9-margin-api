#!/usr/bin/env python3
"""Check the public API contract, local links, and dated example contracts."""

from __future__ import annotations

import calendar
import datetime as dt
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "open-api-schema.yaml"
README = ROOT / "README.md"

PUBLIC_OPERATIONS = {
    ("POST", "/portfolios"),
    ("POST", "/portfolios/optimize"),
    ("POST", "/portfolios/batch"),
    ("GET", "/portfolios/batch/{batch_id}"),
    ("GET", "/portfolios/batch/{batch_id}/results"),
    ("GET", "/results"),
    ("GET", "/results/accounts"),
    ("GET", "/stress-test/scenarios"),
    ("POST", "/stress-test/scenarios"),
    ("DELETE", "/stress-test/scenarios"),
    ("GET", "/validation-reference/exchanges"),
    ("GET", "/validation-reference/contracts/{exchange_code}"),
    ("GET", "/validation-reference/contract-type/{exchange_code}/{contract_code}"),
    ("GET", "/validation-reference/expiries/{exchange_code}/{contract_code}/{contract_type}"),
    ("GET", "/validation-reference/strikes/{exchange_code}/{contract_code}/{contract_type}/{expiry}"),
    ("GET", "/validation-reference/fi-reference"),
    ("GET", "/validation-reference/irs-reference"),
    ("GET", "/validation-reference/ladder-reference"),
    ("GET", "/validation-reference/fx-symbols"),
    ("POST", "/validation-reference/portfolios"),
    ("GET", "/validation-reference/events/search"),
    ("GET", "/validation-reference/events/contracts"),
    ("POST", "/portfolios/stage"),
    ("POST", "/portfolios/stage/submit"),
}

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}
SAMPLE_SUFFIXES = {".py", ".js", ".sh", ".cs", ".r", ".md", ".yaml", ".csv"}
MONTHS = {month.upper(): index for index, month in enumerate(calendar.month_abbr) if month}
DOCUMENTED_OPERATION_PATTERNS = [
    re.compile(r"`(GET|POST|PUT|PATCH|DELETE)`\s*\|\s*`(/[^`\s|]+)`"),
    re.compile(r"`?(GET|POST|PUT|PATCH|DELETE)`?\s+`?(/[A-Za-z0-9_{}./:-]+)"),
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def operations(document: dict) -> set[tuple[str, str]]:
    return {
        (method.upper(), path)
        for path, item in document.get("paths", {}).items()
        for method in item
        if method.lower() in HTTP_METHODS
    }


def documented_operations(text: str) -> set[tuple[str, str]]:
    return {
        (match.group(1), match.group(2).split("?", 1)[0].rstrip(".,;:)"))
        for pattern in DOCUMENTED_OPERATION_PATTERNS
        for match in pattern.finditer(text)
    }


def check_contract(document: dict) -> None:
    actual = operations(document)
    if actual != PUBLIC_OPERATIONS:
        missing = sorted(PUBLIC_OPERATIONS - actual)
        extra = sorted(actual - PUBLIC_OPERATIONS)
        fail(f"public endpoint mismatch. Missing: {missing}. Extra: {extra}.")

    for path, item in document["paths"].items():
        for method, operation in item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            parameters = operation.get("parameters", [])
            if any(parameter.get("name") == "username" for parameter in parameters if isinstance(parameter, dict)):
                fail(f"{method.upper()} {path} documents the internal username query parameter")

    combined = SCHEMA.read_text().lower() + README.read_text().lower()
    if "/healthcheck" in combined:
        fail("healthcheck endpoints must remain undocumented until their contract is resolved")

    documented = documented_operations(README.read_text())
    if documented != PUBLIC_OPERATIONS:
        missing = sorted(PUBLIC_OPERATIONS - documented)
        extra = sorted(documented - PUBLIC_OPERATIONS)
        fail(f"README endpoint mismatch. Missing: {missing}. Extra: {extra}.")


def check_local_links() -> None:
    markdown_link = re.compile(r"\[[^]]*]\(([^)]+)\)")
    for document in [README, *ROOT.glob("**/*.md")]:
        relative_parts = document.relative_to(ROOT).parts
        if "node_modules" in relative_parts or any(part.startswith(".") for part in relative_parts):
            continue
        for target in markdown_link.findall(document.read_text(errors="ignore")):
            target = target.strip().strip("<>").split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (document.parent / unquote(target)).resolve()
            if not resolved.exists():
                fail(f"broken local link in {document.relative_to(ROOT)}: {target}")


def expiry_date(value: str) -> dt.date | None:
    value = value.upper()
    if re.fullmatch(r"\d{6}(?:00)?", value):
        year, month = int(value[:4]), int(value[4:6])
        return dt.date(year, month, calendar.monthrange(year, month)[1])
    if re.fullmatch(r"\d{8}", value):
        return dt.datetime.strptime(value, "%Y%m%d").date()
    match = re.fullmatch(r"([A-Z]{3})-(\d{2})", value)
    if match and match.group(1) in MONTHS:
        year, month = 2000 + int(match.group(2)), MONTHS[match.group(1)]
        return dt.date(year, month, calendar.monthrange(year, month)[1])
    match = re.fullmatch(r"(\d{2})-([A-Z]{3})-(\d{2})", value)
    if match and match.group(2) in MONTHS:
        return dt.date(2000 + int(match.group(3)), MONTHS[match.group(2)], int(match.group(1)))
    return None


def check_sample_expiries() -> None:
    cutoff = dt.date.today() + dt.timedelta(days=90)
    patterns = [
        re.compile(r"contract_expiry\s*[=:]\s*[\"']([^\"']+)[\"']", re.IGNORECASE),
        re.compile(r'"contract_expiry"\s*:\s*"([^"]+)"', re.IGNORECASE),
        re.compile(r'""contract_expiry""\s*:\s*""([^"]+)""', re.IGNORECASE),
    ]
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or path.suffix.lower() not in SAMPLE_SUFFIXES
            or ".git" in path.parts
            or "node_modules" in path.parts
        ):
            continue
        text = path.read_text(errors="ignore")
        values = {value for pattern in patterns for value in pattern.findall(text)}
        if path.name == "sample_portfolio.csv":
            values.update(line.split(",")[4] for line in text.splitlines()[1:] if len(line.split(",")) > 4)
        for value in values:
            parsed = expiry_date(value)
            if parsed is not None and parsed < cutoff:
                fail(
                    f"sample contract in {path.relative_to(ROOT)} expires {parsed}; "
                    f"roll it to at least {cutoff}"
                )
        for ticker in re.findall(r"ticker[\"']?\s*[:=]\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE):
            match = re.search(r"-(\d{2})([A-Z]{3})(\d{2})(?:-|$)", ticker.upper())
            if match is None or match.group(2) not in MONTHS:
                continue
            parsed = dt.date(2000 + int(match.group(1)), MONTHS[match.group(2)], int(match.group(3)))
            if parsed < cutoff:
                fail(
                    f"sample event contract in {path.relative_to(ROOT)} expires {parsed}; "
                    f"roll it to at least {cutoff}"
                )


def main() -> None:
    document = yaml.safe_load(SCHEMA.read_text())
    check_contract(document)
    check_local_links()
    check_sample_expiries()
    print(f"Documentation policy checks passed for {len(PUBLIC_OPERATIONS)} public operations.")


if __name__ == "__main__":
    main()
