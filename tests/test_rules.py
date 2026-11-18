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


def test_parties_match_exact_labels_before_looser_ones():
    """JnP is Jana Sena and JNP Janata Party; CPI(M) is not CPI(ML) Red Star's
    CPIM. New parties keep their printed label and get no Party_ID."""
    lookup = {
        "label": {1605: "BJP", 17069: "JnP", 4406: "JP", 14635: "CPM", 2560: "CPIM"},
        "alias": {},
        "index": {
            "exact": {"JnP": [17069], "JNP": [4406], "CPI(M)": [14635], "CPIM": [2560]},
            "compact": {"JnP": [17069], "JNP": [4406], "CPIM": [14635, 2560]},
            "any case": {"JNP": [17069, 4406], "CPIM": [14635, 2560]},
            "name": {key("Bharatiya Janata Party"): [1605]},
        },
        "states": {14635: {"X"}, 2560: {"Y"}},
        "size": {14635: 900, 2560: 10},
        "eci_name": {},
    }
    labels = ["Bharatiya Janata Party", "Independent", "NOTA", "JnP", "CPI(M)", "New"]
    frame = pd.DataFrame({"State_Name": "X", "Party_Source": labels})
    out = map_parties(frame, lookup)
    assert out["Party"].tolist() == ["BJP", "IND", "NOTA", "JnP", "CPM", "New"]
    assert out["Party_ID"].tolist()[:5] == [1605, 10809, 5897, 17069, 14635]
    assert pd.isna(out["Party_ID"].iloc[5])


def test_eci_full_name_overrides_a_reused_abbreviation():
    """A label with ECI's full name matches by that name, not by PPI's
    abbreviation; KRS is in PPI, but not as the party ECI names."""
    lookup = {
        "label": {5671: "NPF", 777: "NPEP", 11393: "KRRS"},
        "alias": {},
        "index": {
            "exact": {"NPEP": [5671], "KRS": [11393]},
            "compact": {},
            "any case": {},
            "name": {key("National People's Party"): [777]},
        },
        "states": {},
        "size": {},
        "eci_name": {
            "NPEP": "National People's Party",
            "KRS": "Karnataka Rashtra Samithi",
        },
    }
    frame = pd.DataFrame({"State_Name": "X", "Party_Source": ["NPEP", "KRS"]})
    out = map_parties(frame, lookup)
    assert out["Party_ID"].iloc[0] == 777 and pd.isna(out["Party_ID"].iloc[1])
    assert out["Party_Match"].tolist() == ["ECI name", "unmatched"]


@pytest.mark.parametrize("layout", ["2023", "2024"])
def test_detailed_results_read_by_header_in_both_layouts(tmp_path, layout):
    """2024 reports say GENDER and add a percentage before TOTAL ELECTORS."""
    from eci_results.sources import read_eci_detailed

    head = ["STATE/UT NAME", "AC NO.", "AC NAME", "CANDIDATE NAME"]
    head += ["GENDER" if layout == "2024" else "SEX", "AGE", "CATEGORY", "PARTY"]
    head += ["SYMBOL", "GENERAL", "POSTAL", "TOTAL", "% OVER VALID VOTES"]
    head += ["% OVER TOTAL ELECTORS"] if layout == "2024" else []
    head += ["TOTAL ELECTORS"]
    rows = [
        ["Sikkim", 1, "Yoksam Tashiding (BL)", "1 Pema Lepcha", "MALE", 40, "BL"],
        ["Sikkim", 1, "Yoksam Tashiding (BL)", "2 Nota", None, None, None],
    ]
    rows[0] += ["SKM", "Flower", 900, 10, 910, 91.0]
    rows[1] += ["NOTA", "NOTA", 90, 0, 90, 9.0]
    for r in rows:
        r += [45.5] if layout == "2024" else []
        r += [2000]
    table = pd.DataFrame([["10 - Detailed Results"], [], [], head] + rows)
    path = tmp_path / "report.xlsx"
    table.to_excel(path, header=False, index=False)
    out = read_eci_detailed(path)
    assert out["Electors"].tolist() == [2000, 2000]
    assert out["Candidate"].tolist() == ["Pema Lepcha", "None of the Above"]
    assert out["Party_Source"].tolist() == ["SKM", "NOTA"]
    assert out["Constituency_Name"].iloc[0] == "YOKSAM TASHIDING"
    assert out["Constituency_Type"].iloc[0] == "BL"
    assert out["Candidate_Type"].iloc[0] == "BL" and out["Sex"].iloc[0] == "M"
