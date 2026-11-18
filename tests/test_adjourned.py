from pathlib import Path

from eci_results.build import constituency_summary
from eci_results.sources import read_eci_form20

RAW = Path("data/raw/eci_reports/adjourned")


def test_form20_reads_patkura_and_checks_its_own_totals():
    frame = read_eci_form20(RAW / "odisha_2019_patkura/Form20_AC096_Patkura.pdf")
    assert frame["Constituency_No"].eq(96).all()
    assert frame["Electors"].eq(244747).all()
    votes = dict(zip(frame["Candidate"], frame["Votes"]))
    assert votes["Sabitri Agarwalla"] == 96030 and votes["Bijoy Mohapatra"] == 78132
    assert votes["None of the Above"] == 368
    # Candidates add up to Form 20's total valid votes; NOTA is apart.
    assert frame.loc[frame["Party_Source"].ne("NOTA"), "Votes"].sum() == 177727


def test_seat_summary_reads_the_nota_line_not_the_postal_one():
    summary = constituency_summary(
        RAW / "meghalaya_2023_including_ac23/8-Constituency_Data_Summery_Report.xlsx",
        "S15-23-Sohiong",
    )
    assert summary == {"electors": 34790, "valid": 31889, "nota": 272}
