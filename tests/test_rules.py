import pandas as pd
import pytest

from eci_results.build import key, map_parties
from eci_results.rules import derive


def contest():
    """One seat: three candidates and NOTA, 1,000 valid votes, 2,000 electors."""
    return pd.DataFrame(
        {
            "Election_Type": "AE",
            "State_Name": "X",
            "Assembly_No": 1,
            "Constituency_No": 1,
            "Poll_No": 0,
            "Party": ["A", "NOTA", "B", "IND"],
            "Votes": [600.0, 50.0, 300.0, 50.0],
            "Electors": 2000.0,
        }
    )


def test_tcpd_rules_on_one_contest():
    out = derive(contest()).set_index("Party")
    assert out["Valid_Votes"].eq(1000).all()
    assert out["N_Cand"].eq(3).all()
    assert out.loc["A", "Position"] == 1 and out.loc["NOTA", "Position"] == 3
    # Margin runs down the placings, NOTA included; the last place gets 0.
    assert out["Margin"].to_dict() == {"A": 300, "B": 250, "NOTA": 0, "IND": 0}
    assert out.loc["B", "Vote_Share_Percentage"] == 30.0
    assert out.loc["B", "Deposit_Lost"] == "no"
    assert out.loc["IND", "Deposit_Lost"] == "yes"
    assert pd.isna(out.loc["NOTA", "Deposit_Lost"])
    assert out.loc["A", "Turnout_Percentage"] == 50.0


def test_nota_written_out_in_full_is_still_nota():
    frame = contest().assign(Party=["A", "None of the Above", "B", "IND"])
    assert derive(frame)["N_Cand"].eq(3).all()


def test_uncontested_seat_has_no_vote_totals():
    frame = contest().iloc[:1].assign(Votes=float("nan"))
    out = derive(frame)
    assert pd.isna(out["Valid_Votes"].iloc[0]) and out["Position"].iloc[0] == 1


@pytest.mark.parametrize(
    "a, b",
    [("ARAKU (ST)", "Araku"), ("Daman & Diu", "DAMAN AND DIU"), ("CPI(M)", "CPIM")],
)
def test_key_ignores_case_punctuation_and_reservation(a, b):
    assert key(a) == key(b)


def test_parties_map_to_tcpd_labels_and_new_parties_keep_their_name():
    by_name = {key("Bharatiya Janata Party"): ("BJP", 1605)}
    frame = pd.DataFrame(
        {"Party_Source": ["Bharatiya Janata Party", "Independent", "NOTA", "New"]}
    )
    out = map_parties(frame, by_name, {})
    assert out["Party"].tolist() == ["BJP", "IND", "NOTA", "New"]
    assert out["Party_ID"].tolist()[:3] == [1605, 10809, 5897]
    assert pd.isna(out["Party_ID"].iloc[3])
