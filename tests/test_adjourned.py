from pathlib import Path

import pandas as pd
import pytest

from eci_results.build import adjourned_term, constituency_summary
from eci_results.sources import (
    read_eci_detailed_pdf,
    read_eci_form20,
    read_eci_form20_table,
)

RAW = Path("data/raw/eci_reports/adjourned")


def tcpd_rows():
    """A state with general elections in 2016 and 2021 (seat 9 missing from
    2016) and a by-election in 2018 and in 2022."""
    rows = []
    for year, month, number, poll in [
        (2016, 5, 11, 0),
        (2018, 3, 11, 1),
        (2021, 4, 12, 0),
        (2022, 2, 12, 1),
    ]:
        for seat in [1, 2] + ([9] if year != 2016 else []):
            rows.append(
                {"State_Name": "X", "Year": year, "month": month,
                 "Assembly_No": number, "Poll_No": poll, "Constituency_No": seat}
            )  # fmt: skip
    return pd.DataFrame(rows)


def test_term_is_the_general_election_before_the_poll_not_the_latest():
    # The state's latest TCPD year is 2022 (a by-election) and its latest
    # general election is 2021, but a 2016 seat polled in November 2016
    # belongs to the 2016 assembly, with that election's year and month.
    term = adjourned_term(tcpd_rows(), "X", 9, 2016, "2016-11-19")
    assert term == {"Assembly_No": 11, "Year": 2016, "month": 5}


def test_by_elections_do_not_count_as_the_general_election():
    # The 2018 by-election is later than 2016 and before the poll; it must not
    # be taken for a newer general election.
    term = adjourned_term(tcpd_rows(), "X", 9, 2016, "2019-01-28")
    assert term["Assembly_No"] == 11


def test_gate_stops_a_seat_tcpd_already_has():
    with pytest.raises(SystemExit, match="already has this seat"):
        adjourned_term(tcpd_rows(), "X", 1, 2016, "2016-11-19")


def test_gate_stops_a_general_election_that_is_not_the_latest_before_the_poll():
    with pytest.raises(SystemExit, match="is not X's latest general election"):
        adjourned_term(tcpd_rows(), "X", 9, 2016, "2021-06-01")


def test_form20_reads_patkura_and_checks_its_own_totals():
    frame = read_eci_form20(RAW / "odisha_2019_patkura/Form20_AC096_Patkura.pdf")
    assert frame["Constituency_No"].eq(96).all()
    assert frame["Electors"].eq(244747).all()
    votes = dict(zip(frame["Candidate"], frame["Votes"]))
    assert votes["Sabitri Agarwalla"] == 96030 and votes["Bijoy Mohapatra"] == 78132
    assert votes["None of the Above"] == 368
    # Candidates add up to Form 20's total valid votes; NOTA is apart.
    assert frame.loc[frame["Party_Source"].ne("NOTA"), "Votes"].sum() == 177727


def test_form20_table_reads_thanjavur_and_its_sideways_header():
    frame = read_eci_form20_table(
        RAW / "tamil_nadu_2016_thanjavur/Form20_AC174_Thanjavur.pdf"
    )
    assert (frame["Constituency_No"].iloc[0], frame["Electors"].iloc[0]) == (
        174,
        268516,
    )
    votes = dict(zip(frame["Candidate"], frame["Votes"]))
    assert votes["RENGASAMY. M"] == 101362 and votes["ANJUGAM BOOPATHY"] == 74488
    assert votes["None of the Above"] == 2295
    assert frame["Votes"].sum() == 186444


def test_form20_table_sums_general_and_service_electors():
    frame = read_eci_form20_table(
        RAW / "tamil_nadu_2016_aravakurichi/Form20_AC134_Aravakurichi.pdf"
    )
    # Printed "200347+5".
    assert frame["Electors"].eq(200352).all()
    assert len(frame) == 40  # 39 candidates and NOTA


def test_detailed_results_pdf_reads_ramgarh_across_a_page_break():
    frame = read_eci_detailed_pdf(RAW / "rajasthan_2018/10-Detailed_Results.pdf")
    assert frame["Constituency_No"].nunique() == 200
    seat = frame[frame["Constituency_No"].eq(67)]
    assert len(seat) == 21  # 20 candidates and NOTA; the 21st row is on the next page
    assert seat["Votes"].max() == 83311 and seat["Electors"].eq(235638).all()


def test_seat_summary_reads_xlsx_and_pdf_pages():
    meghalaya = constituency_summary(
        RAW / "meghalaya_2023_including_ac23/8-Constituency_Data_Summery_Report.xlsx",
        23,
        "S15-23-Sohiong",
    )
    # The NOTA line, not the postal line that also mentions NOTA.
    assert meghalaya == {"contested": 6, "electors": 34790, "valid": 31889, "nota": 272}
    rajasthan = constituency_summary(
        RAW / "rajasthan_2018/09-Constituency_Data_Summary.pdf", 67
    )
    assert rajasthan == {
        "contested": 20,
        "electors": 235638,
        "valid": 185700,
        "nota": 241,
    }
