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

from eci_results.build import ELECTION_TYPE, RELEASE, TCPD_FILE, read_tcpd
from eci_results.fetch import SOURCE, check
from eci_results.rules import CONTEST, DERIVED, derive
from eci_results.sources import read_azadecon, read_eci_detailed


def agree(published, derived):
    both_empty = published.isna() & derived.isna()
    if pd.api.types.is_numeric_dtype(published):
        close = np.isclose(published, derived, atol=0.005)
        return close | both_empty
    return published.astype(str).eq(derived.astype(str)) | both_empty


def scrape_check(source):
    """How far the counting-day scrape used for Rajasthan, Madhya Pradesh and
    Chhattisgarh 2023 is from ECI's report, in the two states that have both."""
    official = {
        i["state"]: i for i in source["results"] if i["format"] == "eci_detailed"
    }
    rows = []
    for state, folder in [("Telangana", "ts"), ("Mizoram", "mz")]:
        scrape = read_azadecon(check(source["reference"][f"scrape_check_{folder}"]))
        report = read_eci_detailed(check(official[state]))
        votes = [
            frame.groupby("Constituency_No")["Votes"].apply(lambda v: tuple(sorted(v)))
            for frame in (scrape, report)
        ]
        totals = [
            frame.groupby("Constituency_No")["Votes"].sum()
            for frame in (scrape, report)
        ]
        same = votes[0].eq(votes[1].reindex(votes[0].index))
        gap = (totals[0] - totals[1]).abs()
        rows.append(
            {
                "state": state,
                "seats": len(same),
                "seats_identical": int(same.sum()),
                "largest_total_gap": int(gap.max()),
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
    scrape_check(source)


if __name__ == "__main__":
    main()
