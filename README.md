# Indian election results after TCPD

Every candidate's votes in the Lok Sabha election of 2024 and the state assembly
elections from November 2023 to May 2026, in the column layout of TCPD's Lok
Dhaba files, so they can be appended to TCPD's data without reshaping. The
results are the Election Commission of India's (ECI) official statistical
reports, which are committed here along with the code that turns them into
TCPD's layout.

The Trivedi Centre for Political Data (TCPD) at Ashoka University publishes the
standard candidate-level files for Indian elections, `All_States_GE` and
`All_States_AE`. They end with the 2019 Lok Sabha and the assemblies of May
2023. As of November 2026 the Lok Dhaba download site refuses connections and
TCPD's GitHub archive was last updated in June 2023
([we asked whether updates are planned](https://github.com/tcpd/tcpd-ld-data-archive/issues/1)).

- [`data/release/GE_2024.csv.gz`](data/release/GE_2024.csv.gz): Lok Sabha 2024.
- [`data/release/AE_2023_2026.csv.gz`](data/release/AE_2023_2026.csv.gz):
  assemblies, November 2023 to May 2026.

Each file has one row per candidate per seat, with NOTA as a row of its own,
and TCPD's columns in TCPD's order:

```python
import pandas as pd

url = "https://raw.githubusercontent.com/in-rolls/eci_results/main/data/release/"
tcpd = pd.read_csv("TCPD_AE_All_States.csv.gz", low_memory=False)
assemblies = pd.concat([tcpd, pd.read_csv(url + "AE_2023_2026.csv.gz")])

winners = assemblies[(assemblies.Position == 1) & (assemblies.Poll_No == 0)]
winners[winners.State_Name == "Telangana"].groupby("Year").Party.value_counts()
# 2014: TRS 63, INC 21, TDP 15; 2018: TRS 88, INC 19, AIMIM 7;
# 2023: INC 64, TRS 39, BJP 8
```

## Coverage

<!-- coverage:start -->
| Election | State | Year | Seats | Candidates |
|---|---|---:|---:|---:|
| Lok Sabha Election | Andaman & Nicobar Islands | 2024 | 1 | 12 |
| Lok Sabha Election | Andhra Pradesh | 2024 | 25 | 454 |
| Lok Sabha Election | Arunachal Pradesh | 2024 | 2 | 14 |
| Lok Sabha Election | Assam | 2024 | 14 | 143 |
| Lok Sabha Election | Bihar | 2024 | 40 | 497 |
| Lok Sabha Election | Chandigarh | 2024 | 1 | 19 |
| Lok Sabha Election | Chhattisgarh | 2024 | 11 | 220 |
| Lok Sabha Election | Dadra & Nagar Haveli & Daman & Diu | 2024 | 2 | 12 |
| Lok Sabha Election | Delhi | 2024 | 7 | 162 |
| Lok Sabha Election | Goa | 2024 | 2 | 16 |
| Lok Sabha Election | Gujarat | 2024 | 25 | 265 |
| Lok Sabha Election | Haryana | 2024 | 10 | 223 |
| Lok Sabha Election | Himachal Pradesh | 2024 | 4 | 37 |
| Lok Sabha Election | Jammu & Kashmir | 2024 | 5 | 100 |
| Lok Sabha Election | Jharkhand | 2024 | 14 | 244 |
| Lok Sabha Election | Karnataka | 2024 | 28 | 474 |
| Lok Sabha Election | Kerala | 2024 | 20 | 194 |
| Lok Sabha Election | Ladakh | 2024 | 1 | 3 |
| Lok Sabha Election | Lakshadweep | 2024 | 1 | 4 |
| Lok Sabha Election | Madhya Pradesh | 2024 | 29 | 369 |
| Lok Sabha Election | Maharashtra | 2024 | 48 | 1,121 |
| Lok Sabha Election | Manipur | 2024 | 2 | 10 |
| Lok Sabha Election | Meghalaya | 2024 | 2 | 10 |
| Lok Sabha Election | Mizoram | 2024 | 1 | 6 |
| Lok Sabha Election | Nagaland | 2024 | 1 | 3 |
| Lok Sabha Election | Odisha | 2024 | 21 | 207 |
| Lok Sabha Election | Puducherry | 2024 | 1 | 26 |
| Lok Sabha Election | Punjab | 2024 | 13 | 328 |
| Lok Sabha Election | Rajasthan | 2024 | 25 | 266 |
| Lok Sabha Election | Sikkim | 2024 | 1 | 14 |
| Lok Sabha Election | Tamil Nadu | 2024 | 39 | 950 |
| Lok Sabha Election | Telangana | 2024 | 17 | 525 |
| Lok Sabha Election | Tripura | 2024 | 2 | 18 |
| Lok Sabha Election | Uttar Pradesh | 2024 | 80 | 851 |
| Lok Sabha Election | Uttarakhand | 2024 | 5 | 55 |
| Lok Sabha Election | West Bengal | 2024 | 42 | 507 |
| State Assembly Election | Andhra Pradesh | 2024 | 175 | 2,387 |
| State Assembly Election | Arunachal Pradesh | 2024 | 60 | 143 |
| State Assembly Election | Assam | 2026 | 126 | 722 |
| State Assembly Election | Bihar | 2025 | 243 | 2,616 |
| State Assembly Election | Chhattisgarh | 2023 | 90 | 1,181 |
| State Assembly Election | Delhi | 2025 | 70 | 699 |
| State Assembly Election | Haryana | 2024 | 90 | 1,031 |
| State Assembly Election | Jammu & Kashmir | 2024 | 90 | 873 |
| State Assembly Election | Jharkhand | 2024 | 81 | 1,211 |
| State Assembly Election | Kerala | 2026 | 140 | 883 |
| State Assembly Election | Madhya Pradesh | 2023 | 230 | 2,534 |
| State Assembly Election | Maharashtra | 2024 | 288 | 4,136 |
| State Assembly Election | Mizoram | 2023 | 40 | 174 |
| State Assembly Election | Odisha | 2024 | 147 | 1,285 |
| State Assembly Election | Puducherry | 2026 | 30 | 294 |
| State Assembly Election | Rajasthan | 2023 | 199 | 1,863 |
| State Assembly Election | Rajasthan | 2024 | 1 | 12 |
| State Assembly Election | Sikkim | 2024 | 32 | 146 |
| State Assembly Election | Tamil Nadu | 2026 | 234 | 4,023 |
| State Assembly Election | Telangana | 2023 | 119 | 2,290 |
| State Assembly Election | West Bengal | 2026 | 294 | 2,926 |
<!-- coverage:end -->

Karanpur (Rajasthan, seat 3) is dated January 2024: ECI's 2023 report includes
it, but its poll was adjourned to 5 January 2024 after a candidate died.
Surat (Lok Sabha 2024) is missing because its candidate was elected unopposed
and ECI's report leaves it out. By-elections are in a file of their own (below).

## By-elections, 2022 to 2026

Every assembly and Lok Sabha by-election ECI lists from March 2022 to October
2026 that TCPD does not have, in TCPD's column layout, ready to append to
TCPD's files:

- [`AE_byelections_2022_2026.csv.gz`](data/release/AE_byelections_2022_2026.csv.gz):
  157 assembly by-elections in 29 states, 1,863 rows.
- [`GE_byelections_2022_2026.csv.gz`](data/release/GE_byelections_2022_2026.csv.gz):
  9 Lok Sabha by-elections, 127 rows.

TCPD's files end with the assembly by-elections of June 2022 and the Lok Sabha
by-elections of 2021. The four contests TCPD already has (Tripura, June 2022)
are left out, and serve as a check (below).
[`byelection_cards.csv`](data/release/byelection_cards.csv) has one row for
each of the 170 contests ECI lists, those four included, with the card's own
totals, poll date and the reason for the by-election (resignation, death,
disqualification).

The source is ECI's "index card" for each seat
([`byelections.py`](src/eci_results/byelections.py)). Each card is checked
against itself: candidates' votes must equal the card's Total row, NOTA and
electors must be present, and the number of rows must equal the card's count of
contesting candidates. All 170 pass. Four carry a note:

- Lumla (Arunachal Pradesh, 2023), Soreng-Chakung and Namchi-Singhithang
  (Sikkim, 2024) were won unopposed: one row each, no votes and no NOTA row.
- Maniktala (West Bengal, 2024): the candidates' postal votes include 27
  rejected and NOTA postal ballots, so their votes sum to 114,968 while the
  card's total valid votes are 114,941. The rows keep the card's figures.

TCPD's by-election rows follow three rules, recovered from those rows:

- `Assembly_No` is the term of the state's latest general election before
  the by-election (for the Lok Sabha, the 17th or 18th), and `DelimID`,
  `Constituency_Type`, `Sub_Region` and `District_Name` are that general
  election's for the seat.
- `Poll_No` numbers a seat's by-elections within one term: 1, then 2. The two
  Erode (East) by-elections of 2023 and 2025 are 1 and 2.
- `Constituency_Name` is the term's general-election name. The build stops if
  a card's seat name does not match the name TCPD has for that seat number, or
  if the reservation differs.

`month` is filled from the poll date; TCPD leaves it empty for by-elections.
Parties are matched to TCPD-PPI as for general elections; 84% of party
candidates and 97% of party votes match. Most unmatched votes go to parties
formed after TCPD-PPI ends in 2021 (Bharat Adivasi Party, Tamilaga Vettri
Kazhagam, Jan Suraaj, Shiv Sena (UBT), NCP (Sharadchandra Pawar)); all are
listed in `parties_not_in_ppi.csv`. Five checked matches were added to
`data/party_aliases.csv`. Two 2022 cards record some
candidates as OBC; OBC is not a category for contesting, so `Candidate_Type` is
GEN for them.

**Check.** Rebuilt from ECI's cards as if TCPD lacked them, the four Tripura
by-elections TCPD has match TCPD's rows in every seat fact, every candidate's
votes, position, party and deposit, and NOTA's votes
([`byelection_check.csv`](data/release/byelection_check.csv), `make validate`).

## What each column holds

A column is filled only where the value is the quantity TCPD's column holds.
Otherwise it is empty. [`MANIFEST.json`](MANIFEST.json) gives the share of each
column filled, by file.

| Columns | Filled from |
|---|---|
| `Candidate`, `Votes`, `Constituency_No`, `Constituency_Name` | The source. |
| `Sex`, `Age`, `Candidate_Type`, `Electors`, `Turnout_Percentage` | ECI's statistical reports. Empty for Arunachal Pradesh's ten seats won unopposed, which the report leaves out. |
| `Position`, `Valid_Votes`, `N_Cand`, `Vote_Share_Percentage`, `Margin`, `Margin_Percentage`, `Deposit_Lost` | TCPD's rules, recovered from TCPD's own rows (below). |
| `Constituency_Type` | ECI's report, which marks reserved seats in their names ("Hachhek (ST)"). The build stops if it disagrees with TCPD's type for the same seat. For the Lok Sabha, TCPD's 2019 type, empty for Assam, Jammu and Kashmir and Ladakh. |
| `Sub_Region`, `District_Name`, `DelimID` | The seat's latest election in TCPD's files. Empty for Assam, Jammu and Kashmir and Ladakh, whose seats were redrawn in 2022 and 2023, except `DelimID`: TCPD's codes run 1 to 4, one per national delimitation, and the two redrawings (Jammu and Kashmir, 2022; Assam, ECI's order of August 2023) are 5. Ladakh, one seat that TCPD files under Jammu and Kashmir, stays empty. |
| `Assembly_No` | TCPD's previous number plus one; the 2024 Lok Sabha is the 18th. Jammu and Kashmir's 2024 assembly is 11: it is the Union Territory's first, but TCPD's `Jammu_&_Kashmir` already has an assembly 1 (1962). |
| `Party`, `Party_ID` | TCPD's party list (TCPD-PPI, 1962 to 2021). `Party` is the label TCPD's rows print for that party: CPM, not CPI(M). A label with a full name on ECI's results site (every party in the 2024 Lok Sabha, from joining report 33 to [india-votes-data](https://github.com/thecont1/india-votes-data) by candidate) is matched by that name only, because PPI reuses abbreviations across parties: ECI's `KRS` is the Karnataka Rashtra Samithi, PPI's the Karnataka Rajya Ryota Sangha. Other labels are matched to PPI's abbreviations exactly first, then with punctuation and then case ignored (`JnP` is Jana Sena, `JNP` Janata Party); a label several parties share goes to the one PPI records in that state. [`party_matches.csv`](data/release/party_matches.csv) lists every label, its match and how it was made; [`data/party_aliases.csv`](data/party_aliases.csv) holds matches checked by hand. Parties founded after 2021, such as Jan Suraaj (`JNSRJP`) and Tamilaga Vettri Kazhagam (`TVK`), keep ECI's abbreviation and have no `Party_ID`; [`parties_not_in_ppi.csv`](data/release/parties_not_in_ppi.csv) lists them. |
| `ENOP` | Empty. No formula over TCPD's vote columns reproduces TCPD's values: the effective number of candidates is within 0.05 of TCPD's figure in only 72% of contests. |
| `Party_Type_TCPD` | Empty. It records a party's ECI recognition at each election, which PPI does not carry. |
| `pid` and the columns built on it (`last_poll`, `Contested`, `Last_Party`, `Last_Party_ID`, `Last_Constituency_Name`, `Same_Constituency`, `Same_Party`, `No_Terms`, `Turncoat`, `Incumbent`, `Recontest`); `MyNeta_education`; `TCPD_Prof_*` | Empty. They need TCPD's linking of candidates across elections, or sources other than ECI's results. |

### TCPD's rules

We recovered each rule by recomputing the column from `Votes`, `Party` and
`Electors` for every general-election row TCPD publishes for 2014 to 2023.
Each rule reproduces TCPD's value for at least 99.97% of rows
([`rule_check.csv`](data/release/rule_check.csv), `make validate`).

- `Valid_Votes` counts NOTA. ECI's own "valid votes" does not.
- `Position` ranks every row by votes, NOTA included.
- `N_Cand` counts candidates and leaves out NOTA.
- `Margin` is a row's votes minus the next row's, NOTA included, and 0 for the
  last row. `Margin_Percentage` divides it by `Valid_Votes`.
- `Deposit_Lost` is `yes` below one sixth of `Valid_Votes` and empty for NOTA.
- `Turnout_Percentage` is `Valid_Votes` divided by `Electors`.
- NOTA's party is `NOTA`. TCPD writes `None of the Above` from 2022 on.

### Checks

`make build` stops unless all of these hold:

- every seat of every election is present;
- Lok Sabha seat numbers, which ECI's report gives only through the order of
  its rows, equal TCPD's 2019 numbers wherever seat names match, and agree
  with the first digit of the results website's numbers;
- Lok Sabha `Valid_Votes` less NOTA equals ECI's valid votes in every seat;
- no two rows of a seat share a `Position`.

Seats won by party match ECI's declared results in every election, including
the 2024 Lok Sabha (BJP 240 with Surat, INC 99, SP 37, AITC 29, DMK 22).

## Sources and raw data

Every input is committed under [`data/raw/`](data/raw/) and pinned by SHA-256
in [`data/source.json`](data/source.json).

- [`data/raw/eci_reports/`](data/raw/eci_reports/): ECI's statistical reports,
  table "10 - Detailed Results", in xlsx and pdf, for every assembly election,
  and report 33 for the 2024 Lok Sabha. eci.gov.in refuses this repository's
  requests, so Priyadarshi Amar downloaded the 2023-2026 assembly reports on
  16 November 2026; `MANIFEST_*.csv` and `fetch_log.jsonl` record each file's
  URL, SHA-256, server date and retrieval time. Mizoram and Telangana 2023
  come from Internet Archive captures, and the Lok Sabha report from
  [in-rolls/wasted_votes](https://github.com/in-rolls/wasted_votes).
- [`data/raw/eci_reports/byelections/`](data/raw/eci_reports/byelections/):
  ECI's by-election index cards, xlsx and pdf, March 2022 to October 2026,
  downloaded by Priyadarshi Amar on 17 November 2026 from the "Bye-Election
  Results" listings of eci.gov.in (2025 on) and old.eci.gov.in (2022 to 2024).
  `MANIFEST.csv` gives each file's source page, address or file id, SHA-256,
  server date and retrieval time; `fetch_log.jsonl` has every request.
- [`data/raw/wayback/`](data/raw/wayback/): ECI's results website as archived by
  the Internet Archive, fetched by
  [`fetch_wayback.py`](src/eci_results/fetch_wayback.py) and parsed by
  [`parse_wayback.py`](src/eci_results/parse_wayback.py). They supply
  Arunachal Pradesh's ten seats won unopposed, which the report leaves out.
- [`data/raw/scrapes/`](data/raw/scrapes/): two earlier scrapes of the results
  website, [thecont1/india-votes-data](https://github.com/thecont1/india-votes-data)
  (MIT) and [azadecon/assembly_elections_2023](https://github.com/azadecon/assembly_elections_2023)
  (GPL-3.0), each with its license. They are used only to check the reports.

ECI's later reports and its counting-day results website disagree in a few
seats. Of the 2,768 assembly seats in both, 2,746 are identical in every vote
count, NOTA included. All 2,768 list the same number of candidates, and in all
2,522 seats where both sources' winning party can be matched to TCPD's party
list, it is the same party. The largest difference in a seat's total is 3,660
votes, in Andhra Pradesh
([`scrape_check.csv`](data/release/scrape_check.csv), `make validate`).

TCPD's files and TCPD-PPI are not redistributed. `make fetch` downloads them
into `data/reference/`; they supply seat facts and party labels and are the
basis for recovering TCPD's rules.

## Open work

Contributions are welcome on any of these.

- `Party_Type_TCPD`, from ECI's notifications of recognized parties for each
  election.
- How TCPD computes `ENOP`.
- Person IDs linking these candidates to their earlier TCPD records, which
  would fill `pid`, `Incumbent` and the other career columns.

If TCPD resumes publishing, these files are meant to fold into theirs.
[in-rolls/candidate_namesakes](https://github.com/in-rolls/candidate_namesakes),
a study of namesake candidates in Indian elections, uses them to extend its
analysis past 2023.
[in-rolls/eci_candidate_photos](https://github.com/in-rolls/eci_candidate_photos)
has every 2024 Lok Sabha candidate's photograph from ECI's results website.
Six columns identify a candidate here, and its join file carries all six, so
one merge attaches the photos. Names will not do, because 16 pairs of
candidates share a name and a seat.

```python
photos = pd.read_csv(
    "https://raw.githubusercontent.com/in-rolls/eci_candidate_photos/main/"
    "data/eci_results_join.csv"
)
key = ["State_Name", "Year", "month", "Poll_No", "Constituency_No", "Position"]
ls = pd.read_csv(url + "GE_2024.csv.gz").merge(
    photos[key + ["photo_path"]], on=key, how="left"
)
# every candidate but NOTA gets a photo_path, relative to that repository
```

## Rebuild

```
make fetch      # download TCPD's reference files; check every input's SHA-256
make build      # parse archived pages and by-election cards; write data/release and MANIFEST.json
make byelections  # check the by-election index cards; write byelection_cards.csv
make validate   # recompute TCPD's rules on TCPD's rows; compare scrape and report
make test
```

`make wayback` fetches archived pages again. It is slow, and the pages are
already committed. ECI's reports cannot be fetched by script.

## Citation and terms

Cite ECI for the results. Where you use the columns derived from TCPD (`Party`,
`Party_ID`, the seat facts) or append these rows to TCPD's files, also cite
Agarwal, Ananay, et al. 2021, "TCPD Indian Elections Data v2.0," and "TCPD
Political Parties of India Dataset (TCPD-PPI), 1962-2021," both Trivedi Centre
for Political Data, Ashoka University. TCPD's data are free for non-commercial
use with citation. This repository is not affiliated with TCPD or endorsed by
it. The code is MIT-licensed.
