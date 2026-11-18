"""Readers for each source, returning one row per candidate with NOTA kept.

Common columns: State_Name, Constituency_No, Constituency_Name, Candidate,
Party_Source (the party as the source prints it), Votes, and, where the
source has them, Sex, Age, Candidate_Type and Electors.
"""

import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

STATE_CODES = {
    "HR": "Haryana", "JH": "Jharkhand", "JK": "Jammu_&_Kashmir", "MH": "Maharashtra",
    "BR": "Bihar", "DL": "Delhi", "AS": "Assam", "KL": "Kerala", "PY": "Puducherry",
    "TN": "Tamil_Nadu", "WB": "West_Bengal", "AP": "Andhra_Pradesh",
    "AR": "Arunachal_Pradesh", "OD": "Odisha", "SK": "Sikkim",
}  # fmt: skip
NOTA_NAMES = {"NOTA", "NONE OF THE ABOVE"}
# TCPD's majority codings (it mixes M/MALE and GEN/GENERAL across years).
SEX = {"MALE": "M", "FEMALE": "F", "THIRD": "O", "OTHERS": "O", "TG": "O"}
# BL is Sikkim's Bhutia-Lepcha seat category, which TCPD also uses.
CATEGORY = {"GENERAL": "GEN", "SC": "SC", "ST": "ST", "BL": "BL"}


# ECI names TCPD writes differently.
STATE_NAMES = {"NCT_OF_Delhi": "Delhi", "NCT_of_Delhi": "Delhi"}


def tcpd_state(name):
    state = str(name).strip().replace(" and ", " & ").replace(" ", "_")
    return STATE_NAMES.get(state, state)


def mark_nota(frame):
    nota = frame["Candidate"].str.upper().str.strip().isin(NOTA_NAMES)
    frame.loc[nota, "Candidate"] = "None of the Above"
    frame.loc[nota, "Party_Source"] = "NOTA"
    return frame


def read_eci_report(path):
    """ECI statistical report 33, Constituency Wise Detailed Result (GE 2024)."""
    report = pd.read_csv(path, encoding="utf-8-sig")
    report = report[report["Candidate Name"].notna()]
    frame = pd.DataFrame(
        {
            "State_Name": report["State Name"].map(tcpd_state),
            "Constituency_No": pd.NA,
            "Constituency_Name": report["PC Name"].str.strip().str.upper(),
            "Candidate": report["Candidate Name"].str.strip(),
            "Party_Source": report["Party Name"].str.strip(),
            "Votes": pd.to_numeric(report["Total"], errors="coerce"),
            "Sex": report["Gender"].str.upper().map(SEX),
            "Age": pd.to_numeric(report["Age"], errors="coerce"),
            "Candidate_Type": report["Category"].str.upper().map(CATEGORY),
            "Electors": pd.to_numeric(report["Total Electors"], errors="coerce"),
            "Source_Valid_Votes": pd.to_numeric(report["Valid Votes"], errors="coerce"),
        }
    )
    return mark_nota(frame)


def read_india_votes_data(path):
    """thecont1/india-votes-data CSV, or our parse of archived ECI pages."""
    table = pd.read_csv(path)
    votes = (
        table["total_votes"]
        if "total_votes" in table
        else table["evm_votes"] + table["postal_votes"]
    )
    frame = pd.DataFrame(
        {
            "State_Name": table["election_state"].map(STATE_CODES),
            "Constituency_No": table["constituency_no"],
            "Constituency_Name": table["constituency"].str.strip().str.upper(),
            "Candidate": table["candidate"].str.strip(),
            "Party_Source": table["party"].str.strip(),
            "Votes": pd.to_numeric(votes, errors="coerce"),
        }
    )
    return mark_nota(frame)


def read_eci_detailed(path):
    """ECI statistical report "10 - Detailed Results" workbook (assemblies).

    One row per candidate, NOTA included. Columns are found by header, because
    the layout changed in 2024: GENDER for SEX, and a second vote percentage
    that pushes TOTAL ELECTORS one column right. Names carry their ballot
    serial ("1 Robert Romawia Royte"), which is dropped.
    """
    raw = pd.read_excel(path, header=None)
    header = raw.index[raw[0].astype(str).str.strip().eq("STATE/UT NAME")][0]
    names = raw.loc[header].astype(str).str.strip().tolist()
    table = raw.loc[header + 1 :]
    table.columns = names
    table = table[pd.to_numeric(table["AC NO."], errors="coerce").notna()]
    sex = "GENDER" if "GENDER" in names else "SEX"
    return mark_nota(
        pd.DataFrame(
            {
                "State_Name": table["STATE/UT NAME"].map(tcpd_state),
                "Constituency_No": table["AC NO."].astype(int),
                "Constituency_Name": table["AC NAME"]
                .astype(str)
                .str.replace(r"\s*\((SC|ST|BL)\)\s*$", "", regex=True)
                .str.strip()
                .str.upper(),
                "Constituency_Type": table["AC NAME"]
                .astype(str)
                .str.extract(r"\((SC|ST|BL)\)\s*$")[0]
                .fillna("GEN"),
                "Candidate": table["CANDIDATE NAME"]
                .astype(str)
                .str.replace(r"^\d+\s+", "", regex=True)
                .str.strip(),
                "Party_Source": table["PARTY"].astype(str).str.strip(),
                "Votes": pd.to_numeric(table["TOTAL"], errors="coerce"),
                "Sex": table[sex].astype(str).str.upper().map(SEX),
                "Age": pd.to_numeric(table["AGE"], errors="coerce"),
                "Candidate_Type": table["CATEGORY"]
                .astype(str)
                .str.upper()
                .map(CATEGORY),
                "Electors": pd.to_numeric(table["TOTAL ELECTORS"], errors="coerce"),
            }
        )
    )


def read_azadecon(folder):
    """azadecon/assembly_elections_2023: one workbook per seat, scraped from
    results.eci.gov.in on counting day. Each ends with a Total row."""
    frames = []
    for path in sorted(Path(folder).glob("*.xlsx")):
        seat = pd.read_excel(path)
        seat = seat[seat["s_n"].notna()]
        frames.append(seat)
    table = pd.concat(frames, ignore_index=True)
    return mark_nota(
        pd.DataFrame(
            {
                "State_Name": None,
                "Constituency_No": table["constituency"].astype(int),
                "Constituency_Name": pd.NA,
                "Candidate": table["candidate"].astype(str).str.strip(),
                "Party_Source": table["party"].astype(str).str.strip(),
                "Votes": pd.to_numeric(table["total_votes"], errors="coerce"),
            }
        )
    )


def form20_columns(page, count):
    """Each vote column's header text on Form 20's first page, from the
    words above the first booth row, grouped by the column they sit over."""
    words = page.extract_words()
    lines = defaultdict(list)
    for word in words:
        lines[round(word["top"])].append(word)
    first = next(
        top
        for top in sorted(lines)
        if len(lines[top]) == count
        and all(w["text"].isdigit() for w in lines[top])
        and min(lines[top], key=lambda w: w["x0"])["text"] == "1"
    )
    centers = [
        (w["x0"] + w["x1"]) / 2 for w in sorted(lines[first], key=lambda w: w["x0"])
    ]
    booth = max(w["top"] for w in words if w["text"] == "Booth" and w["top"] < first)
    heads = defaultdict(list)
    for word in words:
        if booth - 2 <= word["top"] < first - 2:
            middle = (word["x0"] + word["x1"]) / 2
            heads[min(range(count), key=lambda k: abs(middle - centers[k]))].append(
                word
            )
    return [
        " ".join(
            w["text"]
            for w in sorted(heads[k], key=lambda w: (round(w["top"]), w["x0"]))
        )
        for k in range(count)
    ]


def read_eci_form20(path):
    """Form 20, the final result sheet of one assembly seat (a PDF with one
    row per polling station, then postal votes and totals).

    Candidate names and parties are listed, in column order, in
    candidates.csv beside the PDF, because the PDF breaks them across lines;
    each must equal its column's header text in the PDF, spaces aside. The
    booth rows must add up to the "recorded at polling station" row, that row
    plus postal votes to the totals, and the candidates to total valid votes.
    Form 20 does not record candidates' sex, age or category.
    """
    import pdfplumber

    path = Path(path)
    people = pd.read_csv(path.with_name("candidates.csv")).sort_values("column")
    count = len(people) + 6  # booth, candidates, valid, rejected, NOTA, total, tendered
    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text(layout=True) or "" for page in pdf.pages)
        heads = form20_columns(pdf.pages[0], count)
    squash = lambda t: re.sub(r"\s+", "", str(t)).upper()  # noqa: E731
    for k, row in enumerate(people.itertuples(), start=1):
        if squash(heads[k]) != squash(f"{row.Candidate} {row.Party_Source}"):
            raise SystemExit(f"{path}: column {k} reads {heads[k]!r}")
    booths, totals = [], []
    for line in text.splitlines():
        words = line.split()
        tail = len(words)
        while tail and words[tail - 1].isdigit():
            tail -= 1
        values = [int(x) for x in words[tail:]]
        if tail == 0 and len(values) == count:
            booths.append(values)
        elif len(values) == count - 1:  # a totals row, its label maybe in front
            totals.append(values)
    recorded, postal, total = totals[-3:]
    if [r[0] for r in booths] != list(range(1, len(booths) + 1)):
        raise SystemExit(f"{path}: booth numbers do not run 1..n")
    if [sum(col) for col in zip(*(r[1:] for r in booths))] != recorded:
        raise SystemExit(f"{path}: booths do not add up to the recorded votes")
    if [a + b for a, b in zip(recorded, postal)] != total:
        raise SystemExit(f"{path}: recorded and postal votes do not add up")
    votes, valid, nota = (
        total[: len(people)],
        total[len(people)],
        total[len(people) + 2],
    )
    if sum(votes) != valid:
        raise SystemExit(f"{path}: candidates do not add up to total valid votes")
    seat = re.search(r"Name of the Assembly Constituency\s*:\s*(\d+)-(.+?)\s+AC", text)
    electors = int(re.search(r"Total No\.? of Electors[^:]*:\s*(\d+)", text)[1])
    frame = pd.DataFrame(
        {
            "Constituency_No": int(seat[1]),
            "Constituency_Name": seat[2].strip().upper(),
            "Candidate": list(people["Candidate"]) + ["None of the Above"],
            "Party_Source": list(people["Party_Source"]) + ["NOTA"],
            "Votes": votes + [nota],
            "Electors": electors,
        }
    )
    return mark_nota(frame)


READERS = {
    "eci_form20": read_eci_form20,
    "eci_detailed": read_eci_detailed,
    "azadecon": read_azadecon,
    "eci_report": read_eci_report,
    "india_votes_data": read_india_votes_data,
    "wayback": read_india_votes_data,
}
