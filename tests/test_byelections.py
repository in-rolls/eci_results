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


def test_byelections_take_their_term_and_count_on_from_tcpd():
    import pandas as pd

    from eci_results.build import byelection_tables

    seat = {"State_Name": "X", "Constituency_No": 5, "DelimID": 4}
    generals = pd.DataFrame(
        [
            {**seat, "Year": 2016, "month": 5, "Assembly_No": 1},
            {**seat, "Year": 2021, "month": 5, "Assembly_No": 2},
        ]
    ).assign(Constituency_Name="ALPHA", Constituency_Type="GEN")
    # TCPD already has one by-election of this seat in the 2021 term.
    theirs = pd.DataFrame(
        [{"election": "assembly", "State_Name": "X", "Assembly_No": 2,
          "Constituency_No": 5, "Year": 2021, "Poll_No": 1}]
    )  # fmt: skip
    polls = [("01-03-2024", 2024, 3), ("01-03-2022", 2022, 3)]
    people = [("A", "Independent", 60), ("B", "Independent", 40)]
    people += [("None of the Above", "NOTA", 5)]
    rows = pd.DataFrame(
        [
            {"Poll_Date": date, "Year": year, "month": month, "Candidate": who,
             "Party_Source": party, "Votes": votes}
            for date, year, month in polls
            for who, party, votes in people
        ]  # fmt: skip
    ).assign(
        election="assembly",
        In_TCPD=False,
        State_Name="X",
        Constituency_No=5,
        Constituency_Name="ALPHA",
        Constituency_Type="GEN",
        Electors=200,
        Age=40,
        Sex="M",
        Candidate_Type="GEN",
    )
    lookup = {
        "alias": {},
        "index": {t: {} for t in ["exact", "compact", "any case", "name"]},
        "states": {},
        "size": {},
        "label": {},
    }
    out = byelection_tables(rows, {"assembly": generals}, theirs, lookup)["assembly"]
    numbers = out.drop_duplicates("Poll_Date").set_index("Year")
    assert numbers["Assembly_No"].to_dict() == {2022: 2, 2024: 2}
    assert numbers["Poll_No"].to_dict() == {2022: 2, 2024: 3}
    assert out["Valid_Votes"].eq(105).all() and out["N_Cand"].eq(2).all()
