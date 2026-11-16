"""Readers for each source, returning one row per candidate with NOTA kept.

Common columns: State_Name, Constituency_No, Constituency_Name, Candidate,
Party_Source (the party as the source prints it), Votes, and, where the
source has them, Sex, Age, Candidate_Type and Electors.
"""

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
CATEGORY = {"GENERAL": "GEN", "SC": "SC", "ST": "ST"}


# ECI names TCPD writes differently.
STATE_NAMES = {"NCT_OF_Delhi": "Delhi"}


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


READERS = {
    "eci_report": read_eci_report,
    "india_votes_data": read_india_votes_data,
    "wayback": read_india_votes_data,
}
