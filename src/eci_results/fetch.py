"""Download every input named in data/source.json and check its SHA-256.

Files already present with the right hash are left alone. The archived ECI
pages (data/wayback/) are committed, not downloaded; parse_wayback.py turns
them into the CSVs listed with format "wayback".

    python -m eci_results.fetch
"""

import hashlib
import json
from pathlib import Path

import requests

SOURCE = Path("data/source.json")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def check(item):
    path = Path(item["path"])
    if not path.exists():
        raise SystemExit(f"{path}: missing; run make fetch (or make wayback)")
    found = sha256(path)
    if found != item["sha256"]:
        raise SystemExit(f"{path}: sha256 {found}, expected {item['sha256']}")
    return path


def inputs(source):
    yield from source["results"]
    yield from source["reference"].values()


def main():
    source = json.loads(SOURCE.read_text())
    for item in inputs(source):
        if "url" not in item:
            continue
        path = Path(item["path"])
        if path.exists() and sha256(path) == item["sha256"]:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        response = requests.get(item["url"], timeout=300)
        response.raise_for_status()
        path.write_bytes(response.content)
        check(item)
        print(f"fetched {path}")


if __name__ == "__main__":
    main()
