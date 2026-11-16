"""Fetch archived ECI constituency result pages from the Wayback Machine.

results.eci.gov.in no longer serves the June 2024 assembly results for
Andhra Pradesh, Odisha, Arunachal Pradesh and Sikkim, nor the adjourned
Karanpur poll of January 2024. The Internet Archive holds every page. Each page
is fetched once, verbatim, into one gzipped JSONL per state (one line per
request: url, snapshot, status, fetched_at, html, ok, reason). Rerunning skips
what is already saved. Nothing here reads the pages; parse_wayback.py does.

    python -m eci_results.fetch_wayback
"""

import gzip
import json
import time
import zlib
from datetime import UTC, datetime
from pathlib import Path

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_delay,
    wait_exponential,
)

RAW = Path("data/raw/wayback")
ELECTIONS = [
    # folder on results.eci.gov.in, ECI state code, seats, state
    ("AcResultGen2ndJune2024", "S02", range(1, 61), "Arunachal Pradesh"),
    ("AcResultGen2ndJune2024", "S21", range(1, 33), "Sikkim"),
    ("AcResultGenJune2024", "S01", range(1, 176), "Andhra Pradesh"),
    ("AcResultGenJune2024", "S18", range(1, 148), "Odisha"),
    # Karanpur (Rajasthan 3): its 2023 general-election poll was adjourned to
    # January 2024 and ECI posted the result with that month's by-elections.
    ("AcResultByeJan2024", "S20", [3], "Rajasthan"),
]
PAGE = "https://results.eci.gov.in/{folder}/Constituencywise{code}{seat}.htm"
# Some captures are ECI refusing the archive's crawler ("Access Denied", 403);
# the CDX index names the captures that were saved with status 200.
CDX = (
    "https://web.archive.org/cdx/search/cdx"
    "?url={page}&fl=timestamp&filter=statuscode:200"
)
SNAPSHOT = "https://web.archive.org/web/{timestamp}id_/{page}"
PAUSE_SECONDS = 1.5
USER_AGENT = (
    "in-rolls/eci_results " "(research; https://github.com/in-rolls/eci_results)"
)


class Throttled(Exception):
    pass


@retry(
    retry=retry_if_exception_type(
        (requests.ConnectionError, requests.Timeout, Throttled)
    ),
    wait=wait_exponential(multiplier=5, max=900),
    stop=stop_after_delay(6 * 3600),
)
def get(session, url):
    response = session.get(url, timeout=60)
    if response.status_code in (429, 503):
        time.sleep(float(response.headers.get("Retry-After", 60)))
        raise Throttled(url)
    return response


def snapshot_url(session, page):
    """The latest capture of ``page`` saved with status 200, or None."""
    listing = get(session, CDX.format(page=page)).text.split()
    stamps = [t for t in listing if t.isdigit()]
    return SNAPSHOT.format(timestamp=max(stamps), page=page) if stamps else None


def done_urls(path):
    """URLs already fetched with a usable answer; tolerate a cut-short file."""
    seen = set()
    if not path.exists():
        return seen
    try:
        with gzip.open(path, "rt", encoding="utf-8") as lines:
            for line in lines:
                record = json.loads(line)
                if record["ok"]:
                    seen.add(record["url"])
    except (EOFError, OSError, zlib.error, json.JSONDecodeError):
        pass
    return seen


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT
    for folder, code, seats, state in ELECTIONS:
        path = RAW / f"{folder}_{code}.jsonl.gz"
        seen = done_urls(path)
        failures = 0
        todo = [
            s
            for s in seats
            if PAGE.format(folder=folder, code=code, seat=s) not in seen
        ]
        if not todo:
            # Opening the gzip file to append would add an empty member.
            print(f"{state}: all {len(seats)} seats already saved")
            continue
        with gzip.open(path, "at", encoding="utf-8") as out:
            for seat in seats:
                url = PAGE.format(folder=folder, code=code, seat=seat)
                if url in seen:
                    continue
                snapshot = snapshot_url(session, url)
                if snapshot is None:
                    record = {
                        "url": url,
                        "snapshot": None,
                        "status": None,
                        "fetched_at": datetime.now(UTC).isoformat(),
                        "ok": False,
                        "reason": "no capture with status 200",
                        "html": "",
                    }
                    out.write(json.dumps(record) + "\n")
                    failures += 1
                    continue
                response = get(session, snapshot)
                ok = response.status_code == 200 and "<table" in response.text
                record = {
                    "url": url,
                    "snapshot": response.url,
                    "status": response.status_code,
                    "fetched_at": datetime.now(UTC).isoformat(),
                    "ok": ok,
                    "reason": (
                        None if ok else f"HTTP {response.status_code} or no table"
                    ),
                    "html": response.text,
                }
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                out.flush()
                failures += not ok
                time.sleep(PAUSE_SECONDS)
        saved = len(seen)
        print(
            f"{state}: {len(seats)} seats, {saved} already saved, {failures} failures"
        )


if __name__ == "__main__":
    main()
