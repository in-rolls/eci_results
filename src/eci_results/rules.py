"""TCPD's derived columns, recovered from TCPD's own rows.

Each rule was checked against every general-election row TCPD publishes for
2014-2023 (``make validate`` reruns the check and writes the match rates to
``data/release/rule_check.csv``). NOTA is a row of its own: it counts in
Valid_Votes, takes a Position, and sits in the Margin sequence, but not in
N_Cand, and its Deposit_Lost is empty.

ENOP is not here: no formula over TCPD's vote columns reproduces TCPD's own
values (the Laakso-Taagepera index over candidates is within 0.05 of TCPD's
figure for 72% of contests), so the column is left empty rather than filled
with a different quantity under TCPD's name.
"""

import numpy as np
import pandas as pd

CONTEST = ["Election_Type", "State_Name", "Assembly_No", "Constituency_No", "Poll_No"]
DERIVED = [
    "Position",
    "Valid_Votes",
    "N_Cand",
    "Vote_Share_Percentage",
    "Margin",
    "Margin_Percentage",
    "Deposit_Lost",
    "Turnout_Percentage",
]


def is_nota(frame):
    # TCPD writes NOTA's party as "NOTA" before 2022 and "None of the Above" after.
    return frame["Party"].isin(["NOTA", "None of the Above"])


def derive(frame, keys=CONTEST):
    """Add TCPD's derived columns to candidate rows (NOTA included)."""
    f = frame.copy()
    nota = is_nota(f)
    group = f.groupby(keys, dropna=False, sort=False)
    # An uncontested seat has no vote count, so no Valid_Votes either.
    counted = group["Votes"].transform("count") > 0
    f["Valid_Votes"] = group["Votes"].transform("sum").where(counted)
    f["Position"] = (
        group["Votes"].rank(ascending=False, method="first", na_option="bottom")
    ).astype(int)
    f["N_Cand"] = (~nota).groupby([f[k] for k in keys], dropna=False).transform("sum")
    f["Vote_Share_Percentage"] = (100 * f["Votes"] / f["Valid_Votes"]).round(2)
    f = f.sort_values(keys + ["Position"])
    below = f.groupby(keys, dropna=False, sort=False)["Votes"].shift(-1)
    f["Margin"] = (f["Votes"] - below).fillna(0).where(f["Votes"].notna())
    f["Margin_Percentage"] = (100 * f["Margin"] / f["Valid_Votes"]).round(2)
    lost = np.where(f["Votes"] < f["Valid_Votes"] / 6, "yes", "no")
    f["Deposit_Lost"] = pd.Series(lost, index=f.index).where(
        ~is_nota(f) & f["Votes"].notna()
    )
    f["Turnout_Percentage"] = (100 * f["Valid_Votes"] / f["Electors"]).round(2)
    return f
