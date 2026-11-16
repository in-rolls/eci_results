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
from eci_results.fetch import SOURCE
from eci_results.rules import CONTEST, DERIVED, derive


def agree(published, derived):
    both_empty = published.isna() & derived.isna()
    if pd.api.types.is_numeric_dtype(published):
        close = np.isclose(published, derived, atol=0.005)
        return close | both_empty
    return published.astype(str).eq(derived.astype(str)) | both_empty


def main():
    ref = json.loads(SOURCE.read_text())["reference"]
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


if __name__ == "__main__":
    main()
