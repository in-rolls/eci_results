"""Check the rules in rules.py against TCPD's own rows.

Re-derives every rule-based column for TCPD's general-election rows of
2014-2023 from Votes, Party and Electors alone, and compares with what TCPD
published. Writes data/release/rule_check.csv: one row per column and file,
with the share of rows that agree (numbers within 0.005, text equal, both
empty counts as agreement).

    python -m eci_results.validate
"""

import json

import numpy as np
import pandas as pd

from eci_results.build import (
    ELECTION_TYPE,
    RELEASE,
    TCPD_FILE,
    map_parties,
    party_lookup,
    read_tcpd,
)
from eci_results.fetch import SOURCE, check
from eci_results.rules import CONTEST, DERIVED, derive
from eci_results.sources import READERS


def agree(published, derived):
    both_empty = published.isna() & derived.isna()
    if pd.api.types.is_numeric_dtype(published):
        close = np.isclose(published, derived, atol=0.005)
        return close | both_empty
    return published.astype(str).eq(derived.astype(str)) | both_empty


def scrape_check(source, parties):
    """Compare each scrape of ECI's results website with ECI's report.

    A seat is identical when the sorted vote counts of all its rows, NOTA
    included, agree. Writes data/release/scrape_check.csv.
    """
    reports = {
        (i["state"], i["year"]): i
        for i in source["results"]
        if i["format"] in ("eci_detailed",)
    }
    rows = []
    for item in source["checks"]:
        scrape = READERS[item["format"]](check(item))
        if "only_seats" in item:
            scrape = scrape[scrape["Constituency_No"].isin(item["only_seats"])]
        report = READERS["eci_detailed"](check(reports[(item["state"], item["year"])]))
        report = report[report["Votes"].notna()]
        scrape = scrape[scrape["Votes"].notna()]
        both = sorted(set(scrape["Constituency_No"]) & set(report["Constituency_No"]))
        votes = [
            f[f["Constituency_No"].isin(both)]
            .groupby("Constituency_No")["Votes"]
            .apply(lambda v: tuple(sorted(v)))
            for f in (scrape, report)
        ]
        totals = [
            f[f["Constituency_No"].isin(both)].groupby("Constituency_No")["Votes"].sum()
            for f in (scrape, report)
        ]
        same = votes[0].eq(votes[1])
        sizes = [
            f[f["Constituency_No"].isin(both)].groupby("Constituency_No").size()
            for f in (scrape, report)
        ]
        winners = [
            map_parties(
                f[f["Constituency_No"].isin(both)]
                .sort_values("Votes", ascending=False)
                .drop_duplicates("Constituency_No")
                .copy(),
                parties,
            ).set_index("Constituency_No")["Party_ID"]
            for f in (scrape, report)
        ]
        winners[1] = winners[1].reindex(winners[0].index)
        known = winners[0].notna() & winners[1].notna()
        rows.append(
            {
                "state": item["state"],
                "year": item["year"],
                "scrape": item["format"],
                "seats_compared": len(both),
                "seats_identical": int(same.sum()),
                "seats_same_candidate_count": int(
                    sizes[0].eq(sizes[1].reindex(sizes[0].index)).sum()
                ),
                "winner_party_compared": int(known.sum()),
                "winner_party_same": int(winners[0].eq(winners[1])[known].sum()),
                "largest_total_gap": int((totals[0] - totals[1]).abs().max()),
                "seats_only_in_scrape": len(set(scrape["Constituency_No"]) - set(both)),
                "seats_only_in_report": len(set(report["Constituency_No"]) - set(both)),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(RELEASE / "scrape_check.csv", index=False)
    print(table.to_string(index=False))


def main():
    source = json.loads(SOURCE.read_text())
    ref = source["reference"]
    rows = []
    for election, name in TCPD_FILE.items():
        tcpd = read_tcpd(ref[name])
        tcpd = tcpd[tcpd["Year"].between(2014, 2023)].copy()
        tcpd["Election_Type"] = ELECTION_TYPE[election]
        inputs = tcpd.drop(columns=DERIVED)
        derived = derive(inputs, CONTEST).loc[tcpd.index]
        for column in DERIVED:
            ok = agree(tcpd[column], derived[column])
            rows.append(
                {
                    "file": name,
                    "column": column,
                    "rows": len(tcpd),
                    "agree_share": round(float(ok.mean()), 4),
                }
            )
    table = pd.DataFrame(rows)
    RELEASE.mkdir(parents=True, exist_ok=True)
    table.to_csv(RELEASE / "rule_check.csv", index=False)
    print(table.to_string(index=False))
    tcpd = {e: read_tcpd(ref[f]) for e, f in TCPD_FILE.items()}
    scrape_check(source, party_lookup(pd.read_csv(check(ref["ppi"])), tcpd))


if __name__ == "__main__":
    main()
