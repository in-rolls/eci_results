from pathlib import Path

import pandas as pd
import pytest

from eci_results.build import facts_before, same_seat
from eci_results.sources import read_eci_bye_page, read_eci_uncontested

RAW = Path("data/raw/eci_reports/adjourned")


@pytest.mark.skipif(not RAW.exists(), reason="raw reports not present")
def test_bye_page_rows_add_up_to_its_valid_votes():
    frame = read_eci_bye_page(RAW / "eci_bye_1996_11/LA_AS_52.htm")
    assert frame["Votes"].sum() == 84551
    assert len(frame) == 5
    assert set(frame["Poll_Date"]) == {"1996-10-11"}
    assert set(frame["Electors"]) == {161769}
    # The page leaves Sex blank for four candidates; it stays blank.
    assert frame["Sex"].isna().sum() == 4


@pytest.mark.skipif(not RAW.exists(), reason="raw reports not present")
def test_bye_page_without_total_row_checks_against_valid_votes():
    frame = read_eci_bye_page(RAW / "eci_bye_1997_02/UP-385-LA.html")
    assert frame["State_Name"].iloc[0] == "Uttar_Pradesh"
    assert frame["Constituency_Type"].iloc[0] == "SC"
    assert frame["Votes"].sum() == 92714


@pytest.mark.skipif(not RAW.exists(), reason="raw reports not present")
def test_uncontested_seats_are_those_with_one_contestant():
    frame = read_eci_uncontested(RAW / "arunachal_pradesh_1999/Statistical_Report.pdf")
    assert frame["Constituency_No"].tolist() == [2, 41, 43, 55]
    anini = frame[frame["Constituency_No"].eq(41)].iloc[0]
    assert (anini["Candidate"], anini["Party_Source"]) == ("RAJESH TACHO", "INC")
    assert (anini["Electors"], anini["Votes"]) == (3710, 0)


def test_facts_come_from_the_same_boundaries_only():
    rows = pd.DataFrame(
        [
            {"State_Name": "X", "Year": y, "Poll_No": 0, "DelimID": d,
             "Constituency_No": 5, "Constituency_Name": n}
            for y, d, n in [(1972, 2, "OLD"), (1977, 3, "NEW"), (1985, 3, "NEWER")]
        ]
        + [{"State_Name": "X", "Year": 1980, "Poll_No": 0, "DelimID": 3,
            "Constituency_No": 6, "Constituency_Name": "OTHER"}]
    )  # fmt: skip
    # Seat 5 is missing in 1980; its facts are 1977's, not 1985's or 1972's.
    assert facts_before(rows, "X", 5, 1980)["Constituency_Name"] == "NEW"
    with pytest.raises(SystemExit):
        facts_before(rows, "X", 7, 1980)


def test_seat_names_allow_eci_spellings():
    assert same_seat("DERGAON", "DERGOAN")
    assert not same_seat("NAZIRA", "MARGHERITA")
