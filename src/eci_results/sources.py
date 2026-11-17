"""Readers for each source, returning one row per candidate with NOTA kept.

Common columns: State_Name, Constituency_No, Constituency_Name, Candidate,
Party_Source (the party as the source prints it), Votes, and, where the
source has them, Sex, Age, Candidate_Type and Electors.
"""

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


READERS = {
    "eci_detailed": read_eci_detailed,
    "azadecon": read_azadecon,
    "eci_report": read_eci_report,
    "india_votes_data": read_india_votes_data,
    "wayback": read_india_votes_data,
}
