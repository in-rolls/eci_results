"""Read and check ECI's by-election index cards, from 2022 on.

ECI publishes each by-election as an "index card": an xlsx (and pdf) with the
seat in its heading, numbered sections for electors, voters, EVM and postal
votes, and a candidate table (section VIII) ending in a Total row. Lok Sabha
cards add a vote column per assembly segment; a candidate's total is the last
number on the row. The files are in data/raw/eci_reports/byelections/, listed
in MANIFEST.csv with their source page, SHA-256 and retrieval time; each file's
hash is checked against the manifest before it is read.

Each card is checked against itself before its rows are kept: the candidates'
votes equal the card's Total row, NOTA and electors are present, serial numbers
run 1..n, and the rows equal the card's count of contesting candidates. The
build stops if any card fails. A card whose candidates do not add up to its
"total valid votes" line passes with a note (see card_notes).

TCPD's files end with the assembly by-elections of June 2022 and the Lok Sabha
by-elections of 2021. `In_TCPD` marks the contests TCPD already has.

This module writes data/release/byelection_cards.csv, one row per contest.
build.py puts the candidates in TCPD's layout (byelection_tables).

    python -m eci_results.byelections
"""

import json
import re
from pathlib import Path

import pandas as pd

from eci_results.fetch import SOURCE, check, sha256
from eci_results.sources import NOTA_NAMES, tcpd_state

RAW = Path("data/raw/eci_reports/byelections")
RELEASE = Path("data/release")
CARDS_OUT = RELEASE / "byelection_cards.csv"
SEX = {"MALE": "M", "FEMALE": "F", "THIRD GENDER": "O", "THIRD": "O", "TG": "O"}
# Some 2022 cards record OBC candidates. OBC is not a category for contesting
# (TCPD's Candidate_Type is GEN, SC, ST or BL), so they are GEN here;
# Category_Source keeps what the card prints.
CATEGORY = {
    "GENERAL": "GEN",
    "GEN": "GEN",
    "OBC": "GEN",
    "SC": "SC",
    "ST": "ST",
    "BL": "BL",
}
ELECTION_TYPE = {
    "lok_sabha": "Lok Sabha Election (GE)",
    "assembly": "State Assembly Election (AE)",
}
HEADERS = {
    "name": r"Name of (the )?Contesting",
    "sex": r"^Sex",
    "age": r"^Age",
    "category": r"^Category",
    "party": r"Name of the Party|^Party",
}


def number(value):
    text = str(value).replace(",", "").strip()
    return int(float(text)) if re.fullmatch(r"-?\d+(\.0+)?", text) else None


def filled(row):
    return [v for v in row if pd.notna(v) and str(v).strip() != ""]


def section(rows, name, item, text=False):
    """The value on row `item` of a roman-numbered section: its last number,
    or its text after the label."""
    inside = False
    for row in rows:
        first = str(row[0]).strip().rstrip(".") if row else ""
        if re.fullmatch(r"[IVX]+", first):
            inside = first == name
            continue
        if inside and first == item:
            if text:
                return " ".join(str(v) for v in row[2:]).strip() or None
            numbers = [number(v) for v in row[1:] if number(v) is not None]
            return numbers[-1] if numbers else None
    return None


def read_eci_index_card(path):
    """One by-election index card: (seat facts, candidate rows with NOTA)."""
    raw = pd.read_excel(path, header=None, dtype=object)
    rows = [filled(raw.iloc[i].tolist()) for i in range(len(raw))]
    text = [" ".join(map(str, r)) for r in rows]
    where = next(t for t in text if re.search(r"Constituency of ", t, re.I))
    seat = next(t for t in text if re.search(r"No\.? and Name of", t, re.I))
    state = re.search(r"Constituency of\s+(.+?)(?:,\s*District.*)?$", where, re.I)[1]
    found = re.search(r"Constitu\w*\s+(\d+)\s*(?:\((\w+)\))?\s*-?\s*(.+)$", seat, re.I)
    head = next(i for i, r in enumerate(rows) if r and re.match(r"SL", str(r[0]), re.I))
    labels = [str(v) for v in raw.iloc[head].tolist()]
    column = {
        key: next(j for j, v in enumerate(labels) if re.search(pattern, v, re.I))
        for key, pattern in HEADERS.items()
    }
    candidates, total_row = [], None
    for i in range(head + 1, len(raw)):
        row = raw.iloc[i].tolist()
        first = str(row[0]).strip() if pd.notna(row[0]) else ""
        if re.fullmatch(r"total", first, re.I):
            total_row = [number(v) for v in row if number(v) is not None]
            break
        if number(first) is None:
            continue
        after_party = row[column["party"] + 1 :]
        votes = [number(v) for v in after_party if number(v) is not None]
        candidates.append(
            {
                "Serial": number(first),
                "Candidate": re.sub(r"\s+", " ", str(row[column["name"]])).strip(),
                "Sex": SEX.get(str(row[column["sex"]]).strip().upper()),
                "Age": number(row[column["age"]]),
                "Candidate_Type": CATEGORY.get(
                    str(row[column["category"]]).strip().upper()
                ),
                "Category_Source": str(row[column["category"]]).strip(),
                "Party_Source": re.sub(r"\s+", " ", str(row[column["party"]])).strip(),
                "Votes": votes[-1] if votes else None,
            }
        )
    kind = "lok_sabha" if re.search(r"Parliamentary", where, re.I) else "assembly"
    contested = section(rows, "I", "4")
    polled = section(rows, "VI", "1")
    # A seat won unopposed: one candidate, no votes polled, every count 0.
    unopposed = (
        contested == 1 and not polled and all(not c["Votes"] for c in candidates)
    )
    if unopposed:
        for c in candidates:
            c["Votes"] = None
    card = {
        "election": kind,
        "State_Name": tcpd_state(state),
        "Constituency_No": int(found[1]),
        "Constituency_Type": (found[2] or "GEN").upper(),
        "Constituency_Name": re.sub(r"\s+", " ", found[3]).strip().upper(),
        "Poll_Date": section(rows, "VII", "5", text=True),
        "Reason": section(rows, "VII", "11", text=True),
        "Electors": section(rows, "II", "4"),
        "Card_Valid_Votes": section(rows, "VI", "3"),
        "NOTA_Votes": section(rows, "VI", "4"),
        "Card_Total_Row": total_row[-1] if total_row else None,
        "Contested": contested,
        "Unopposed": unopposed,
    }
    return card, candidates


def card_failures(card, candidates):
    """Checks that stop the build. A card whose candidates add up to its own
    Total row but not to its total valid votes (VI 3) passes with a note:
    ECI's postal column then includes rejected and NOTA postal ballots."""
    votes = [c["Votes"] for c in candidates]
    total = sum(v for v in votes if v is not None)
    failures = []
    if not candidates:
        failures.append("no candidates")
    if card["Contested"] is not None and card["Contested"] != len(candidates):
        failures.append(
            f"{len(candidates)} rows, card says {card['Contested']} contested"
        )
    if [c["Serial"] for c in candidates] != list(range(1, len(candidates) + 1)):
        failures.append("serials not 1..n")
    for field in ("Sex", "Candidate_Type"):
        if any(c[field] is None for c in candidates):
            failures.append(f"unmapped {field}")
    if not card["Electors"]:
        failures.append("no electors")
    if card["Unopposed"]:
        return failures
    if any(v is None for v in votes):
        failures.append("a candidate without votes")
    if card["NOTA_Votes"] is None:
        failures.append("no NOTA count")
    if card["Card_Total_Row"] is not None and total != card["Card_Total_Row"]:
        failures.append(f"votes sum {total} != Total row {card['Card_Total_Row']}")
    if card["Card_Total_Row"] is None and total != card["Card_Valid_Votes"]:
        failures.append(f"votes sum {total} != total valid {card['Card_Valid_Votes']}")
    return failures


def card_notes(card, candidates):
    """Disagreements inside a card that do not stop the build."""
    total = sum(c["Votes"] or 0 for c in candidates)
    if card["Unopposed"]:
        return "won unopposed; no poll"
    if card["Card_Valid_Votes"] is not None and total != card["Card_Valid_Votes"]:
        valid = card["Card_Valid_Votes"]
        return (
            f"candidates' votes sum to {total}, the card's total valid votes are "
            f"{valid} (difference {total - valid})"
        )
    return ""


def tcpd_byelections(source):
    """TCPD's own by-elections: one row per contest, with its term and number."""
    frames = []
    for election, name in {"lok_sabha": "tcpd_GE", "assembly": "tcpd_AE"}.items():
        tcpd = pd.read_csv(check(source["reference"][name]), low_memory=False)
        tcpd = tcpd[tcpd["Poll_No"] > 0]
        cols = ["State_Name", "Assembly_No", "Constituency_No", "Year", "Poll_No"]
        frames.append(tcpd[cols].drop_duplicates().assign(election=election))
    return pd.concat(frames, ignore_index=True)


def read_cards(source):
    """Every card checked and read: (one row per card, one row per candidate
    with NOTA kept). Stops if a file's hash differs from the manifest or a card
    fails its own totals."""
    theirs = tcpd_byelections(source)
    in_tcpd = set(
        zip(theirs["election"], theirs["State_Name"], theirs["Constituency_No"],
            theirs["Year"])
    )  # fmt: skip
    frame = pd.read_csv(RAW / "MANIFEST.csv")
    cards, rows, bad = [], [], []
    for item in frame[frame["format"] == "xlsx"].itertuples():
        path = RAW / item.path
        if sha256(path) != item.sha256:
            raise SystemExit(f"{path}: SHA-256 differs from MANIFEST.csv")
        card, candidates = read_eci_index_card(path)
        failures = card_failures(card, candidates)
        date = pd.to_datetime(card["Poll_Date"], dayfirst=True, errors="coerce")
        seat = (card["election"], card["State_Name"], card["Constituency_No"])
        card.update(
            Year=date.year,
            month=date.month,
            In_TCPD=(*seat, date.year) in in_tcpd,
            Batch=item.batch,
            Source_File=str(path),
            Source_SHA256=item.sha256,
        )
        card["Notes"] = card_notes(card, candidates)
        cards.append(
            {
                **card,
                "candidates": len(candidates),
                "checks": "; ".join(failures) or "pass",
            }
        )
        if failures:
            bad.append(f"{path}: {'; '.join(failures)}")
            continue
        nota = {
            "Serial": None,
            "Candidate": "None of the Above",
            "Sex": None,
            "Age": None,
            "Candidate_Type": None,
            "Category_Source": None,
            "Party_Source": "NOTA",
            "Votes": card["NOTA_Votes"],
        }
        for c in candidates + ([] if card["Unopposed"] else [nota]):
            rows.append({**card, **c})
    if bad:
        raise SystemExit("index cards failing their own totals:\n" + "\n".join(bad))
    table = pd.DataFrame(rows)
    nota = table["Candidate"].str.upper().isin(NOTA_NAMES | {"NONE OF THE ABOVE"})
    table.loc[nota, "Party_Source"] = "NOTA"
    return pd.DataFrame(cards), table


def main():
    """Check every card and write byelection_cards.csv. `make build` also puts
    the candidates in TCPD's layout (build.py)."""
    cards, rows = read_cards(json.loads(SOURCE.read_text()))
    RELEASE.mkdir(parents=True, exist_ok=True)
    cards.to_csv(CARDS_OUT, index=False)
    print(
        f"{CARDS_OUT}: {len(cards)} cards, {len(rows)} rows, sha256 {sha256(CARDS_OUT)}"
    )


if __name__ == "__main__":
    main()
