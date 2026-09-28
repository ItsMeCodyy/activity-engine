from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


DATA_FILE = Path("activity.json")
README_FILE = Path("README.md")


# Strict ISO-8601 UTC timestamp validation
ISO_UTC_RE = re.compile(
    r"""
    ^
    (?P<year>\d{4})
    -
    (?P<month>0[1-9]|1[0-2])
    -
    (?P<day>0[1-9]|[12]\d|3[01])
    T
    (?P<hour>[01]\d|2[0-3])
    :
    (?P<minute>[0-5]\d)
    :
    (?P<second>[0-5]\d)
    Z
    $
    """,
    re.VERBOSE,
)


def default_data() -> dict:
    return {
        "runs": 0,
        "first_run": None,
        "last_run": None,
        "history": [],
    }


def load_data() -> dict:
    if not DATA_FILE.exists():
        return default_data()

    try:
        raw = DATA_FILE.read_text(encoding="utf-8")
        data = json.loads(raw)

        if not isinstance(data, dict):
            return default_data()

        data.setdefault("runs", 0)
        data.setdefault("first_run", None)
        data.setdefault("last_run", None)
        data.setdefault("history", [])

        return data

    except (json.JSONDecodeError, OSError):
        return default_data()


def valid_timestamp(value: str) -> bool:
    if not isinstance(value, str):
        return False

    match = ISO_UTC_RE.fullmatch(value)

    if not match:
        return False

    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
        return True
    except ValueError:
        return False


def create_timestamp() -> str:
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    if not valid_timestamp(timestamp):
        raise ValueError("Generated timestamp failed validation.")

    return timestamp


def update_activity() -> dict:
    data = load_data()

    now = create_timestamp()

    try:
        current_runs = int(data.get("runs", 0))
    except (TypeError, ValueError):
        current_runs = 0

    data["runs"] = current_runs + 1

    if not data.get("first_run"):
        data["first_run"] = now

    data["last_run"] = now

    history = data.get("history", [])

    if not isinstance(history, list):
        history = []

    history.append(
        {
            "run": data["runs"],
            "timestamp": now,
        }
    )

    # Keep only the most recent 100 runs
    data["history"] = history[-100:]

    DATA_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    return data


def update_readme(data: dict) -> None:
    runs = data["runs"]
    first_run = data["first_run"]
    last_run = data["last_run"]

    content = (
        "# Activity Engine\n\n"
        "A tiny Python automation project that records its own "
        "scheduled activity.\n\n"
        "```text\n"
        f"runs      : {runs}\n"
        f"first run : {first_run}\n"
        f"last run  : {last_run}\n"
        "```\n\n"
        "## What it does\n\n"
        "Every scheduled run:\n\n"
        "- executes a Python automation\n"
        "- generates a validated UTC timestamp\n"
        "- updates structured JSON data\n"
        "- records execution history\n"
        "- updates this README\n"
        "- commits the changes automatically through GitHub Actions\n\n"
        "## Stack\n\n"
        "```text\n"
        "Python\n"
        "GitHub Actions\n"
        "JSON\n"
        "Regex\n"
        "Git\n"
        "```\n\n"
        "Built for fun because automation is cool.\n"
    )

    README_FILE.write_text(
        content,
        encoding="utf-8",
    )


def print_summary(data: dict) -> None:
    print("=" * 50)
    print("ACTIVITY ENGINE")
    print("=" * 50)
    print(f"Run:       #{data['runs']}")
    print(f"First run: {data['first_run']}")
    print(f"Last run:  {data['last_run']}")
    print("=" * 50)


def main() -> None:
    data = update_activity()

    update_readme(data)

    print_summary(data)


if __name__ == "__main__":
    main()
