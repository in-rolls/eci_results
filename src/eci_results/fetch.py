"""Download every input named in data/source.json and check its SHA-256.

Files already present with the right hash are left alone. Raw inputs are
committed under data/raw/; this restores them if deleted and downloads TCPD's
reference files into data/reference/, which are not redistributed. ECI's
statistical reports cannot be fetched by script (eci.gov.in refuses it).

    python -m eci_results.fetch
"""

import hashlib
import json
from pathlib import Path

import requests
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

SOURCE = Path("data/source.json")


def sha256(path):
    """SHA-256 of a file, or of a folder's relative paths and file contents."""
    path = Path(path)
    digest = hashlib.sha256()
    files = (
        sorted(p for p in path.rglob("*") if p.is_file()) if path.is_dir() else [path]
    )
    for file in files:
        if path.is_dir():
            digest.update(str(file.relative_to(path)).encode() + b"\0")
        with open(file, "rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
    return digest.hexdigest()


def fetch_folder(item):
    """Every file in one folder of a GitHub repository at a pinned commit."""
    tree = requests.get(
        f"https://api.github.com/repos/{item['repo']}/git/trees/{item['commit']}",
        params={"recursive": "1"},
        timeout=60,
    )
    tree.raise_for_status()
    prefix = item["folder"].rstrip("/") + "/"
    raw = f"https://raw.githubusercontent.com/{item['repo']}/{item['commit']}/"
    for entry in tree.json()["tree"]:
        name = entry["path"]
        if entry["type"] != "blob" or not name.startswith(prefix):
            continue
        if not name.endswith(item.get("suffix", "")):
            continue
        target = Path(item["path"]) / name[len(prefix) :]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(download(raw + name))


def throttled(error):
    response = getattr(error, "response", None)
    return response is not None and response.status_code in (429, 503)


# The Internet Archive answers bursts with 429; wait and try again.
@retry(
    retry=retry_if_exception(throttled),
    wait=wait_exponential(multiplier=10, max=300),
    stop=stop_after_attempt(6),
)
def download(url):
    response = requests.get(url, timeout=300)
    response.raise_for_status()
    return response.content


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
    yield from source.get("checks", [])
    yield from source["reference"].values()


def main():
    source = json.loads(SOURCE.read_text())
    for item in inputs(source):
        # Committed files obtained by hand (ECI reports) are never re-fetched.
        if "obtained" in item or ("url" not in item and "repo" not in item):
            continue
        path = Path(item["path"])
        if path.exists() and sha256(path) == item["sha256"]:
            continue
        if "repo" in item:
            fetch_folder(item)
            check(item)
            print(f"fetched {path}/")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(download(item["url"]))
        check(item)
        print(f"fetched {path}")


if __name__ == "__main__":
    main()
