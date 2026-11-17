from pathlib import Path

from eci_results.byelections import card_failures, read_eci_index_card

CARDS = Path("data/raw/eci_reports/byelections/2026_09-10")


def test_assembly_card():
    card, candidates = read_eci_index_card(
        CARDS / "101-Tamil_Nadu-Dharapuram_1791797899.xlsx"
    )
    assert card["election"] == "assembly"
    assert (card["State_Name"], card["Constituency_No"]) == ("Tamil_Nadu", 101)
    assert card["Constituency_Type"] == "SC"
    assert card["Constituency_Name"] == "DHARAPURAM"
    assert card["Electors"] == 223333 and card["NOTA_Votes"] == 677
    assert len(candidates) == 22
    assert candidates[0]["Candidate"] == "SATHYABAMA.P"
    assert candidates[0]["Votes"] == 66841 and candidates[0]["Sex"] == "F"
    assert card_failures(card, candidates) == []


def test_lok_sabha_card_takes_the_total_after_segment_columns():
    card, candidates = read_eci_index_card(CARDS / "9-Assam-Nagaon_1791798166.xlsx")
    assert card["election"] == "lok_sabha"
    assert (card["State_Name"], card["Constituency_No"]) == ("Assam", 9)
    assert candidates[0]["Candidate"] == "DEVASISH SHARMA"
    assert candidates[0]["Votes"] == 714349
    assert card_failures(card, candidates) == []
