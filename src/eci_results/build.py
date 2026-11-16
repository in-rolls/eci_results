"""Lok Sabha 2024 and assembly 2024-2026 results in TCPD's column layout.

Every column TCPD publishes is present, in TCPD's order and coding. Each is
filled one of four ways, and only where the result is TCPD's quantity:

- from the source: Candidate, Votes, constituency number and name; for the
  2024 Lok Sabha also Sex, Age, Candidate_Type and Electors (ECI report 33);
- by TCPD's own rules (rules.py): Position, Valid_Votes, N_Cand,
  Vote_Share_Percentage, Margin, Margin_Percentage, Deposit_Lost,
  Turnout_Percentage;
- from the seat's previous TCPD general election: Constituency_Type,
  Sub_Region, District_Name, DelimID, and Assembly_No plus one (not for
  Jammu and Kashmir, redrawn in 2022);
- from TCPD's party list (TCPD-PPI): Party (TCPD's abbreviation) and
  Party_ID, where the party existed by 2021.

Left empty: ENOP (see rules.py), Party_Type_TCPD (ECI recognition at each
election, not in PPI), pid and the career columns built from it, education
and profession. Writes data/release/ and MANIFEST.json.

    python -m eci_results.build
"""

import json
import re
from pathlib import Path

import pandas as pd

from eci_results.fetch import SOURCE, check, sha256
from eci_results.rules import CONTEST, derive
from eci_results.sources import READERS, tcpd_state

RELEASE = Path("data/release")
MANIFEST = Path("MANIFEST.json")
ALIASES = Path("data/party_aliases.csv")
README = Path("README.md")
GZIP = {"method": "gzip", "mtime": 0}
ELECTION_TYPE = {
    "lok_sabha": "Lok Sabha Election (GE)",
    "assembly": "State Assembly Election (AE)",
}
TCPD_FILE = {"lok_sabha": "tcpd_GE", "assembly": "tcpd_AE"}
OUTPUT = {"lok_sabha": "GE_2024.csv.gz", "assembly": "AE_2024_2026.csv.gz"}
# TCPD-PPI's IDs for independents and NOTA.
IND_ID, NOTA_ID = 10809, 5897
# Seats redrawn since TCPD's last election there: J&K and Ladakh in 2022,
# Assam in 2023. Seat-level facts cannot be carried across a redrawing.
REDRAWN = {"Jammu_&_Kashmir", "Ladakh", "Assam"}
EXPECTED_SEATS = {"Assam": 126, "Jammu_&_Kashmir": 90}
# The two seats of Dadra & Nagar Haveli and Daman & Diu, merged in 2020,
# and their TCPD (state, seat number) before the merger.
MERGED = "Dadra_&_Nagar_Haveli_&_Daman_&_Diu"
CARRY_FROM = {
    (MERGED, 1): ("Daman_&_Diu", 1),
    (MERGED, 2): ("Dadra_&_Nagar_Haveli", 1),
}
SURAT = 24
SEAT_FACTS = ["DelimID", "Constituency_Type", "Sub_Region", "District_Name"]


def key(text):
    """Comparison key for constituency and party names."""
    text = str(text).upper().replace("&", " AND ")
    return re.sub(r"[^A-Z0-9]", "", re.sub(r"\((SC|ST)\)", "", text))


def read_tcpd(item):
    """TCPD's file; its header is the column order this repository copies."""
    tcpd = pd.read_csv(check(item), low_memory=False)
    return tcpd[tcpd["Poll_No"] == 0]


def last_election(tcpd, state):
    """Each seat's facts from the state's latest TCPD general election.

    A seat missing from that election is taken from the one before, on the
    same boundaries: Odisha's seat 96 (Patkura) voted late in 2019 and is not
    in TCPD's 2019 rows. Only missing seats fall back, because a state split
    (Andhra Pradesh, 2014) renumbers seats under the same DelimID.
    """
    rows = tcpd[(tcpd["State_Name"] == state) & (tcpd["DelimID"] == 4)]
    cols = [c for c in SEAT_FACTS + ["Assembly_No"] if c in rows]
    year = rows["Year"].max()
    latest = rows[rows["Year"] == year].drop_duplicates("Constituency_No")
    seats = latest.set_index("Constituency_No")[cols]
    missing = set(range(1, int(seats.index.max()) + 1)) - set(seats.index)
    earlier = rows[rows["Constituency_No"].isin(missing) & (rows["Year"] < year)]
    earlier = earlier.sort_values("Year").drop_duplicates(
        "Constituency_No", keep="last"
    )
    seats = pd.concat([seats, earlier.set_index("Constituency_No")[cols]])
    seats["Assembly_No"] = latest["Assembly_No"].max()
    return seats.sort_index()


def carry_assembly(frame, tcpd, state):
    seats = last_election(tcpd, state)
    frame["Assembly_No"] = (
        seats["Assembly_No"].max() + 1 if state != "Jammu_&_Kashmir" else pd.NA
    )
    if state not in REDRAWN:
        for col in seats.columns.drop("Assembly_No"):
            frame[col] = frame["Constituency_No"].map(seats[col])
    return frame


def number_lok_sabha(frame, numbers, tcpd):
    """Number report 33's seats by their order within each state.

    Report 33 lists each state's seats in seat-number order but prints no
    number. Surat (Gujarat 24), won unopposed, is not in the report, so the
    Gujarat seats after it move up one. Two checks stop the build: the order
    must equal TCPD's 2019 number for every seat matched by name outside the
    redrawn states, and its first digit must equal the scraped results site's
    seat number, which india-votes-data cut to one digit.
    """
    seats = frame.drop_duplicates(["State_Name", "Constituency_Name"]).copy()
    seats["Constituency_No"] = seats.groupby("State_Name").cumcount() + 1
    after_surat = seats["State_Name"].eq("Gujarat") & seats["Constituency_No"].ge(SURAT)
    seats.loc[after_surat, "Constituency_No"] += 1
    seats["name_key"] = seats["Constituency_Name"].map(key)

    latest = tcpd[tcpd["Year"] == tcpd["Year"].max()].copy()
    latest["name_key"] = latest["Constituency_Name"].map(key)
    known = seats.merge(
        latest.drop_duplicates(["State_Name", "Constituency_No"])[
            ["State_Name", "name_key", "Constituency_No"]
        ],
        on=["State_Name", "name_key"],
        suffixes=("", "_tcpd"),
    )
    known = known[~known["State_Name"].isin(REDRAWN)]
    off = known["Constituency_No"].ne(known["Constituency_No_tcpd"])
    if off.any():
        raise SystemExit(
            f"seat order differs from TCPD: {known[off].to_dict('records')}"
        )

    site = pd.read_csv(numbers, sep=";").drop_duplicates(["State", "Constituency"])
    site["State_Name"] = site["State"].map(tcpd_state)
    site["name_key"] = site["Constituency"].map(key)
    both = seats.merge(site, on=["State_Name", "name_key"])
    first = both["Constituency_No"].astype(str).str[0]
    if first.ne(both["Constituency ID"].astype(str)).any() or len(both) < 530:
        raise SystemExit("seat order disagrees with the results site's numbers")

    number = seats.set_index(["State_Name", "Constituency_Name"])["Constituency_No"]
    index = pd.MultiIndex.from_arrays([frame["State_Name"], frame["Constituency_Name"]])
    frame["Constituency_No"] = number.reindex(index).to_numpy()
    return frame


def carry_lok_sabha(frame, tcpd):
    latest = tcpd[tcpd["Year"] == tcpd["Year"].max()]
    seats = latest.drop_duplicates(["State_Name", "Constituency_No"])
    seats = seats.set_index(["State_Name", "Constituency_No"])
    frame["Assembly_No"] = latest["Assembly_No"].max() + 1
    origin = [
        CARRY_FROM.get((s, n), (s, n))
        for s, n in zip(frame["State_Name"], frame["Constituency_No"])
    ]
    index = pd.MultiIndex.from_tuples(origin)
    for col in [c for c in SEAT_FACTS if c in seats]:
        frame[col] = seats[col].reindex(index).to_numpy()
    frame.loc[frame["State_Name"].isin(REDRAWN), SEAT_FACTS[:3]] = pd.NA
    return frame


def party_lookup(ppi, tcpd):
    """Map party names and abbreviations to TCPD's label and Party_ID.

    The label is the one TCPD's own 2014-2023 rows print most often for the
    Party_ID (CPM, not PPI's CPIM), else PPI's most frequent abbreviation.
    data/party_aliases.csv holds checked matches where ECI's name differs
    from PPI's; parties founded after PPI's 2021 cutoff stay unmatched.
    """
    ppi = ppi[ppi["Party_ID"].notna()].sort_values("Last_Year")
    recent = pd.concat(tcpd.values())
    recent = recent[recent["Year"].between(2014, 2023) & recent["Party_ID"].notna()]
    printed = recent.groupby("Party_ID")["Party"].agg(lambda s: s.mode().iloc[0])
    label = ppi.drop_duplicates("Party_ID", keep="last").set_index("Party_ID")
    label = printed.reindex(label.index).fillna(label["Frequent_Abbreviation"])
    by_name, by_abbr = {}, {}
    for row in ppi.itertuples(index=False):
        value = (label[row.Party_ID], int(row.Party_ID))
        by_name[key(row.Party_Name)] = value
        for abbr in str(row.Abbreviations).split("|"):
            by_abbr[key(abbr)] = value
    aliases = pd.read_csv(ALIASES)
    for name, party_id in zip(aliases["source_name"], aliases["Party_ID"]):
        by_name[key(name)] = (label[party_id], int(party_id))
    return by_name, by_abbr


def map_parties(frame, by_name, by_abbr):
    label = frame["Party_Source"]
    ind = label.str.upper().isin(["IND", "INDEPENDENT"])
    nota = label.eq("NOTA")
    keys = label.map(key)
    found = keys.map(by_name).fillna(keys.map(by_abbr))
    frame["Party"] = found.map(lambda v: v[0], na_action="ignore").fillna(label)
    frame["Party_ID"] = found.map(lambda v: v[1], na_action="ignore")
    frame.loc[ind, ["Party", "Party_ID"]] = ["IND", IND_ID]
    frame.loc[nota, ["Party", "Party_ID"]] = ["NOTA", NOTA_ID]
    return frame


def build_election(item, tcpd, parties, numbers):
    frame = READERS[item["format"]](check(item))
    if item["election"] == "lok_sabha":
        frame = carry_lok_sabha(number_lok_sabha(frame, numbers, tcpd), tcpd)
    else:
        frame = carry_assembly(frame, tcpd, item["state"])
    frame = map_parties(frame, *parties)
    frame["Year"], frame["month"], frame["Poll_No"] = item["year"], item["month"], 0
    frame["Election_Type"] = ELECTION_TYPE[item["election"]]
    for col in ["Electors", "Age", "Assembly_No"]:
        frame[col] = pd.to_numeric(frame.get(col), errors="coerce")
    for col in ["Sex", "Candidate_Type"]:
        if col not in frame:
            frame[col] = None
    return derive(frame, CONTEST)


def gate(frame, item, tcpd):
    """Stop the build if a seat is missing or the totals disagree."""
    label = f"{item['election']} {item['year']} {item['state']}"
    # Count seat numbers, not names: Bihar has two seats called Kalyanpur.
    seats = frame.groupby("State_Name")["Constituency_No"].nunique()
    if item["election"] == "assembly":
        expected = EXPECTED_SEATS.get(item["state"]) or int(
            last_election(tcpd, item["state"]).index.max()
        )
        if seats.sum() != expected:
            raise SystemExit(f"{label}: {seats.sum()} seats, expected {expected}")
    unnumbered = frame["Constituency_No"].isna().sum()
    if unnumbered:
        missing = frame.loc[frame["Constituency_No"].isna(), "Constituency_Name"]
        raise SystemExit(f"{label}: {unnumbered} rows unnumbered: {missing.unique()}")
    if "Source_Valid_Votes" in frame:
        # ECI's "Valid Votes" leaves out NOTA; TCPD's Valid_Votes counts it.
        nota = frame["Votes"].where(frame["Party"].eq("NOTA"), 0)
        contest = [frame[c] for c in CONTEST]
        without_nota = frame["Valid_Votes"] - nota.groupby(contest).transform("sum")
        off = without_nota.ne(frame["Source_Valid_Votes"])
        if off.any():
            bad = frame.loc[off, "Constituency_Name"].unique()
            raise SystemExit(f"{label}: Valid_Votes differs from ECI in {bad}")
    if frame.duplicated(CONTEST + ["Position"]).any():
        raise SystemExit(f"{label}: duplicate positions")
    return f"{label}: {seats.sum()} seats, {len(frame)} rows"


def coverage(tables):
    """Markdown table of elections, seats and candidates for the README."""
    rows = []
    for election, table in tables.items():
        real = table[table["Party"].ne("NOTA")]
        grouped = real.groupby(["State_Name", "Year"])
        summary = grouped.agg(
            seats=("Constituency_No", "nunique"), candidates=("Candidate", "size")
        )
        summary.insert(0, "Election", ELECTION_TYPE[election].split(" (")[0])
        rows.append(summary.reset_index())
    table = pd.concat(rows).rename(columns={"State_Name": "State"})
    lines = [
        "| Election | State | Year | Seats | Candidates |",
        "|---|---|---:|---:|---:|",
    ]
    for r in table.itertuples(index=False):
        state = r.State.replace("_", " ")
        lines.append(
            f"| {r.Election} | {state} | {r.Year} | {r.seats:,} | {r.candidates:,} |"
        )
    return "\n".join(lines)


def update_readme(text):
    readme = README.read_text()
    start, end = "<!-- coverage:start -->", "<!-- coverage:end -->"
    head, rest = readme.split(start)
    _, tail = rest.split(end)
    README.write_text(f"{head}{start}\n{text}\n{end}{tail}")


def main():
    source = json.loads(SOURCE.read_text())
    ref = source["reference"]
    tcpd = {e: read_tcpd(ref[f]) for e, f in TCPD_FILE.items()}
    parties = party_lookup(pd.read_csv(check(ref["ppi"])), tcpd)
    numbers = check(ref["ls_2024_numbers"])
    frames = {e: [] for e in OUTPUT}
    for item in source["results"]:
        frame = build_election(item, tcpd[item["election"]], parties, numbers)
        print(gate(frame, item, tcpd[item["election"]]))
        frames[item["election"]].append(frame)

    RELEASE.mkdir(parents=True, exist_ok=True)
    manifest = {"files": {}}
    unmatched = []
    tables = {e: pd.concat(frames[e], ignore_index=True) for e in OUTPUT}
    for election, name in OUTPUT.items():
        table = tables[election]
        named = table["Party"].ne("IND") & table["Party"].ne("NOTA")
        unmatched.append(
            table[named & table["Party_ID"].isna()]
            .groupby(["State_Name", "Year", "Party"])
            .size()
            .rename("candidates")
            .reset_index()
            .assign(election=election)
        )
        table = table.reindex(columns=tcpd[election].columns)
        path = RELEASE / name
        table.to_csv(path, index=False, compression=GZIP)
        manifest["files"][str(path)] = {
            "rows": len(table),
            "contests": int(table.groupby(CONTEST, dropna=False).ngroups),
            "sha256": sha256(path),
            "filled_share": table.notna().mean().round(4).to_dict(),
        }
    parties_out = RELEASE / "parties_not_in_ppi.csv"
    pd.concat(unmatched).sort_values("candidates", ascending=False).to_csv(
        parties_out, index=False
    )
    manifest["files"][str(parties_out)] = {"sha256": sha256(parties_out)}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    update_readme(coverage(tables))
    print(f"wrote {', '.join(manifest['files'])}")


if __name__ == "__main__":
    main()
