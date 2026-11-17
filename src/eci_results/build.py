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

import difflib
import json
import re
from pathlib import Path

import pandas as pd

from eci_results import byelections
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
OUTPUT = {"lok_sabha": "GE_2024.csv.gz", "assembly": "AE_2023_2026.csv.gz"}
BY_OUTPUT = {
    "lok_sabha": "GE_byelections_2022_2026.csv.gz",
    "assembly": "AE_byelections_2022_2026.csv.gz",
}
# A by-election's seat name must be this close to its term's general election
# (difflib ratio of the name keys), or the seat number is suspect.
SEAT_NAME_MATCH = 0.7
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
    cols = [c for c in SEAT_FACTS + ["Assembly_No", "Constituency_Name"] if c in rows]
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
        for col in seats.columns.drop(["Assembly_No", "Constituency_Name"]):
            carried = frame["Constituency_No"].map(seats[col])
            if col == "Constituency_Type" and col in frame:
                # ECI's report prints the reservation; it must agree with TCPD's.
                differ = frame[col].ne(carried) & carried.notna()
                if differ.any():
                    seats_off = sorted(frame.loc[differ, "Constituency_No"].unique())
                    raise SystemExit(
                        f"{state}: seat type differs from TCPD in {seats_off}"
                    )
                continue
            frame[col] = carried
        # Sources without seat names (the azadecon scrape) take TCPD's.
        named = frame["Constituency_Name"].fillna(
            frame["Constituency_No"].map(seats["Constituency_Name"])
        )
        frame["Constituency_Name"] = named
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


def compact(text):
    """Abbreviation key: punctuation and spaces dropped, case kept."""
    return re.sub(r"[^A-Za-z0-9]", "", str(text))


TIERS = [
    ("exact", str),
    ("compact", compact),
    ("any case", lambda t: compact(t).upper()),
]


def party_lookup(ppi, tcpd):
    """Everything needed to match a printed party label to a TCPD Party_ID.

    Labels are TCPD's own printed label for each Party_ID (CPM, not PPI's
    CPIM). Candidates come from PPI's abbreviations at three strictness
    levels (TIERS) and from PPI's names; data/party_aliases.csv holds checked
    matches that override them.
    """
    ppi = ppi[ppi["Party_ID"].notna()]
    recent = pd.concat(tcpd.values())
    recent = recent[recent["Year"].between(2014, 2023) & recent["Party_ID"].notna()]
    printed = recent.groupby("Party_ID")["Party"].agg(lambda s: s.mode().iloc[0])
    label = ppi.drop_duplicates("Party_ID", keep="last").set_index("Party_ID")
    label = printed.reindex(label.index).fillna(label["Frequent_Abbreviation"])
    abbrs = [
        (a, pid)
        for text, pid in zip(ppi["Abbreviations"], ppi["Party_ID"])
        for a in str(text).split("|")
    ]
    index = {}
    for tier, norm in TIERS:
        table = pd.DataFrame([(norm(a), pid) for a, pid in abbrs], columns=["k", "id"])
        index[tier] = table.drop_duplicates().groupby("k")["id"].agg(list).to_dict()
    names = pd.DataFrame({"k": ppi["Party_Name"].map(key), "id": ppi["Party_ID"]})
    index["name"] = names.drop_duplicates().groupby("k")["id"].agg(list).to_dict()
    aliases = pd.read_csv(ALIASES)
    return {
        "label": label.to_dict(),
        "alias": dict(zip(aliases["source_name"].map(key), aliases["Party_ID"])),
        "index": index,
        "states": ppi.groupby("Party_ID")["State_Name"].agg(set).to_dict(),
        "size": recent["Party_ID"].value_counts().to_dict(),
    }


def match_party(text, state, lookup):
    """(Party_ID, tier, number of candidate parties) for one printed label."""
    alias = lookup["alias"].get(key(text))
    if alias is not None:
        return alias, "alias", 1
    tiers = [(t, norm(text)) for t, norm in TIERS] + [("name", key(text))]
    for tier, k in tiers:
        found = lookup["index"][tier].get(k)
        if not found:
            continue
        # Prefer a party PPI records in this state, then the more common one.
        best = max(
            found,
            key=lambda pid: (
                state in lookup["states"].get(pid, ()),
                lookup["size"].get(pid, 0),
            ),
        )
        return best, tier, len(found)
    return None, "unmatched", 0


def map_parties(frame, lookup):
    source = frame["Party_Source"].astype(str)
    pairs = pd.DataFrame({"text": source, "state": frame["State_Name"]})
    matches = {
        (t, st): match_party(t, st, lookup)
        for t, st in pairs.drop_duplicates().itertuples(index=False)
    }
    found = [matches[(t, st)] for t, st in zip(pairs["text"], pairs["state"])]
    frame["Party_ID"] = pd.Series(
        [f[0] for f in found], index=frame.index, dtype="float"
    )
    frame["Party_Match"] = [f[1] for f in found]
    frame["Party_Candidates"] = [f[2] for f in found]
    frame["Party"] = frame["Party_ID"].map(lookup["label"]).fillna(source)
    ind = source.str.upper().isin(["IND", "INDEPENDENT"])
    nota = source.eq("NOTA")
    frame.loc[ind, ["Party", "Party_ID", "Party_Match"]] = [
        "IND",
        IND_ID,
        "independent",
    ]
    frame.loc[nota, ["Party", "Party_ID", "Party_Match"]] = ["NOTA", NOTA_ID, "nota"]
    return frame


def build_election(item, tcpd, parties, numbers):
    frame = READERS[item["format"]](check(item))
    if frame["State_Name"].isna().all():
        frame["State_Name"] = item["state"]
    if "only_seats" in item:
        frame = frame[frame["Constituency_No"].isin(item["only_seats"])].copy()
    if item["election"] == "lok_sabha":
        frame = carry_lok_sabha(number_lok_sabha(frame, numbers, tcpd), tcpd)
    else:
        frame = carry_assembly(frame, tcpd, item["state"])
    frame = map_parties(frame, parties)
    frame["Year"], frame["month"], frame["Poll_No"] = item["year"], item["month"], 0
    # A seat polled on another date (Karanpur, adjourned to January 2024).
    for seat, date in item.get("seat_dates", {}).items():
        here = frame["Constituency_No"].eq(int(seat))
        frame.loc[here, "Year"], frame.loc[here, "month"] = date["year"], date["month"]
    frame["Election_Type"] = ELECTION_TYPE[item["election"]]
    for col in ["Electors", "Age", "Assembly_No"]:
        frame[col] = pd.to_numeric(frame.get(col), errors="coerce")
    for col in ["Sex", "Candidate_Type"]:
        if col not in frame:
            frame[col] = None
    return derive(frame, CONTEST)


def general_seats(generals):
    """Every seat of every general election, with its date, term and facts."""
    cols = ["State_Name", "Year", "month", "Assembly_No", "Constituency_No"]
    cols += ["Constituency_Name"] + SEAT_FACTS
    seats = generals.reindex(columns=cols).dropna(subset=["Constituency_No"])
    seats = seats.drop_duplicates(["State_Name", "Year", "month", "Constituency_No"])
    return seats.assign(start=seats["Year"] * 100 + seats["month"])


def byelection_tables(rows, generals, theirs, parties):
    """By-election candidates (byelections.read_cards) in TCPD's layout.

    Each by-election belongs to the term of the state's latest general election
    on or before its poll date, and takes that election's Assembly_No and seat
    facts, as TCPD's own by-election rows do. Poll_No numbers a seat's
    by-elections within the term, 1, 2, ..., after any TCPD already has (TCPD's
    rule, checked on its rows). Contests TCPD already has are left out.
    """
    out = {}
    for election, frame in rows.groupby("election"):
        seats = general_seats(generals[election])
        frame = frame[~frame["In_TCPD"].astype(bool)].copy()
        frame["when"] = frame["Year"] * 100 + frame["month"]
        contest = ["State_Name", "Constituency_No", "Poll_Date"]
        facts, problems = [], []
        for c in frame.drop_duplicates(contest).itertuples():
            here = seats[
                seats["State_Name"].eq(c.State_Name)
                & seats["Constituency_No"].eq(c.Constituency_No)
            ]
            if here[here["Year"].eq(c.Year)]["start"].isna().any():
                problems.append(f"{c.State_Name} {c.Constituency_No}: general's month")
                continue
            before = here[here["start"] <= c.when].sort_values("start")
            if before.empty:
                problems.append(f"{c.State_Name} {c.Constituency_No}: no general")
                continue
            term = before.iloc[-1]
            theirs_name, ours = key(term["Constituency_Name"]), key(c.Constituency_Name)
            ratio = difflib.SequenceMatcher(None, theirs_name, ours).ratio()
            # SUAR is TCPD's SUAR TANDA: a name inside the other also matches.
            inside = ours in theirs_name or theirs_name in ours
            if ratio < SEAT_NAME_MATCH and not inside:
                problems.append(
                    f"{c.State_Name} {c.Constituency_No}: card says "
                    f"{c.Constituency_Name}, TCPD {term['Constituency_Name']}"
                )
            if c.Constituency_Type != term["Constituency_Type"] and pd.notna(
                term["Constituency_Type"]
            ):
                problems.append(
                    f"{c.State_Name} {c.Constituency_No}: type {c.Constituency_Type}, "
                    f"TCPD {term['Constituency_Type']}"
                )
            facts.append(
                {
                    **{col: getattr(c, col) for col in contest},
                    "Assembly_No": term["Assembly_No"],
                    **{
                        col: term[col]
                        for col in SEAT_FACTS + ["Constituency_Name"]
                        if col != "Constituency_Type"
                    },
                    "Constituency_Type": (
                        term["Constituency_Type"]
                        if pd.notna(term["Constituency_Type"])
                        else c.Constituency_Type
                    ),
                }
            )
        if problems:
            raise SystemExit(f"{election} by-elections:\n" + "\n".join(problems))
        facts = pd.DataFrame(facts)
        frame = frame.drop(columns=["Constituency_Name", "Constituency_Type"]).merge(
            facts, on=contest, how="left", validate="many_to_one"
        )
        # Poll_No: TCPD's by-elections in the same term come first.
        term_keys = ["State_Name", "Assembly_No", "Constituency_No"]
        prior = (
            theirs[theirs["election"].eq(election)]
            .groupby(term_keys, dropna=False)
            .size()
            .rename("prior")
        )
        order = frame.drop_duplicates(contest)[term_keys + ["Poll_Date", "when"]]
        order = order.sort_values("when")
        order["rank"] = order.groupby(term_keys, dropna=False).cumcount() + 1
        order = order.join(prior, on=term_keys)
        order["Poll_No"] = order["prior"].fillna(0).astype(int) + order["rank"]
        frame = frame.merge(
            order[["State_Name", "Constituency_No", "Poll_Date", "Poll_No"]],
            on=contest,
            how="left",
            validate="many_to_one",
        )
        frame["Election_Type"] = ELECTION_TYPE[election]
        frame = map_parties(frame, parties)
        for col in ["Electors", "Age", "Assembly_No", "Votes"]:
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
        out[election] = derive(frame, CONTEST)
        if out[election].duplicated(CONTEST + ["Position"]).any():
            raise SystemExit(f"{election} by-elections: duplicate positions")
    return out


def gate(frame, item, tcpd):
    """Stop the build if a seat is missing or the totals disagree."""
    label = f"{item['election']} {item['year']} {item['state']}"
    # Count seat numbers, not names: Bihar has two seats called Kalyanpur.
    seats = frame.groupby("State_Name")["Constituency_No"].nunique()
    if item["election"] == "assembly":
        top = EXPECTED_SEATS.get(item["state"]) or int(
            last_election(tcpd, item["state"]).index.max()
        )
        expected = set(item.get("only_seats") or range(1, top + 1))
        expected -= set(item.get("missing_seats", []))
        found = set(frame["Constituency_No"].astype(int))
        if found != expected:
            raise SystemExit(
                f"{label}: missing seats {sorted(expected - found)}, "
                f"unexpected {sorted(found - expected)}"
            )
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
    cards, by_rows = byelections.read_cards(source)
    generals = {e: pd.concat([tcpd[e], tables[e]], ignore_index=True) for e in OUTPUT}
    theirs = byelections.tcpd_byelections(source)
    by_tables = byelection_tables(by_rows, generals, theirs, parties)
    outputs = [(e, OUTPUT[e], tables[e]) for e in OUTPUT]
    outputs += [(e, BY_OUTPUT[e], by_tables[e]) for e in BY_OUTPUT]
    for election, name, table in outputs:
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
    cards.to_csv(byelections.CARDS_OUT, index=False)
    manifest["files"][str(byelections.CARDS_OUT)] = {
        "rows": len(cards),
        "sha256": sha256(byelections.CARDS_OUT),
    }
    audit = (
        pd.concat([*tables.values(), *by_tables.values()])
        .query("Party_Match not in ['independent', 'nota']")
        .groupby(
            [
                "Party_Source",
                "State_Name",
                "Party",
                "Party_ID",
                "Party_Match",
                "Party_Candidates",
            ],
            dropna=False,
        )
        .size()
        .rename("candidates")
        .reset_index()
        .sort_values("candidates", ascending=False)
    )
    audit_out = RELEASE / "party_matches.csv"
    audit.to_csv(audit_out, index=False)
    manifest["files"][str(audit_out)] = {"sha256": sha256(audit_out)}
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
