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
| State Assembly Election | Rajasthan | 2023 | 200 | 1,875 |
| State Assembly Election | Sikkim | 2024 | 32 | 146 |
| State Assembly Election | Tamil Nadu | 2026 | 234 | 4,023 |
| State Assembly Election | Telangana | 2023 | 119 | 2,290 |
| State Assembly Election | West Bengal | 2026 | 294 | 2,926 |
<!-- coverage:end -->

Karanpur (Rajasthan, seat 3) is in ECI's 2023 report, though its poll was
adjourned to 5 January 2024 after a candidate died. Like every adjourned poll
here it carries the general election's year and month (2023, December), as
TCPD codes adjourned polls (below).
Surat (Lok Sabha 2024) is missing because its candidate was elected unopposed
and ECI's report leaves it out. By-elections, and the five adjourned polls
missing from TCPD's own general elections, are in files of their own (below).

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

## Adjourned polls missing from TCPD

[`AE_adjourned_2016_2023.csv.gz`](data/release/AE_adjourned_2016_2023.csv.gz)
has the seats whose poll was adjourned and held after a general election TCPD
covers, and which TCPD's rows lack. Since the 2008 delimitation these are all
five such seats: checking every TCPD assembly general election since then for
seat numbers missing from 1 to the state's last seat finds exactly these
(renumbering after the Andhra Pradesh split aside).

| Seat | General election | Poll held | Source |
|---|---|---|---|
| Aravakurichi (Tamil Nadu, 134) | 2016, assembly 11 | 19 November 2016 | Form 20, Chief Electoral Officer, Tamil Nadu |
| Thanjavur (Tamil Nadu, 174) | 2016, assembly 11 | 19 November 2016 | Form 20, Chief Electoral Officer, Tamil Nadu |
| Ramgarh (Rajasthan, 67) | 2018, assembly 15 | 28 January 2019 | ECI's Rajasthan 2018 report, "10 - Detailed Results" (PDF), checked against Ramgarh's page of "09 - Constituency Data Summary" |
| Patkura (Odisha, 96) | 2019, assembly 16 | 20 July 2019 | Form 20, Chief Electoral Officer, Odisha |
| Sohiong (Meghalaya, 23) | 2023, assembly 11 | 10 May 2023 | ECI's Meghalaya 2023 report "Including AC-23", "10 - Detailed Results", checked against Sohiong's page of "8 - Constituency Data Summary" |

Each is coded as part of its general election, as TCPD codes the two
adjourned polls its own files have: Jayanagar (Karnataka, 173), polled on
11 June 2018, is Year 2018, month 5, Poll_No 0, like the rest of Karnataka's
May 2018 election; Vellore (Lok Sabha, Tamil Nadu 8), polled on 5 August 2019,
is Year 2019, month 4, Poll_No 0. So `Poll_No` is 0, and `Assembly_No`, `Year`
and `month` are the general election's own (the poll dates are in the table).
The seat's facts (district, sub-region, reservation, `DelimID`) come from its
latest TCPD row on the same boundaries. The build stops unless the named
election is the state's latest TCPD general election before the poll (rows
with Poll_No above 0 do not count), TCPD's rows for it lack the seat, and the
seat's name and reservation match TCPD's; where ECI publishes a seat summary,
its candidates, electors, total valid votes and NOTA must equal the rows.

- **Form 20.** ECI's reports leave out Aravakurichi, Thanjavur and Patkura: the
  Tamil Nadu 2016 report lists the two seats' candidates without votes, and the
  Odisha 2019 report has 146 of 147 seats (both in `data/raw/eci_reports/adjourned/`).
  No index card or archived results page turned up, so the source is the Chief
  Electoral Officer's Form 20, the final result sheet. The readers check each
  against itself: polling-station rows add up to the recorded votes, recorded
  and postal votes to the totals, and the candidates to total valid votes. The
  candidates and parties in each seat's `candidates.csv` must have the same
  letters as their column's header in the PDF (the Tamil Nadu headers are set
  sideways, and some names run past the printed cell; the PDF keeps the full
  text). For the Tamil Nadu seats the order and parties also agree with the
  Form 7A list of contesting candidates of 5 November 2016, checked by eye.
  Form 20 does not record sex, age or category, which are empty. Aravakurichi's
  electors are printed "200347+5", general and service electors. Thanjavur's
  sheet misspells DMDK as "DRAVIA"; it is kept as printed and matched in
  `party_aliases.csv`.
- **Ramgarh.** ECI's Rajasthan 2018 report is a PDF only. `read_eci_detailed_pdf`
  reads all 200 seats and checks each row's general and postal votes against
  its total and each seat's rows against its TURNOUT row. On the other 199
  seats it equals TCPD's 2018 rows in every vote count in 193; in seats 1, 43,
  97, 119, 149 and 153 a row differs, by up to 689 votes. TCPD's electors there
  are below the report's total in every seat (median 235), as if service
  electors were left out; the rows here keep ECI's total. Ramgarh's seat summary
  gives its declaration as 31 January 2019 but its polling date as 7 December
  2018, the original schedule.
- **Sohiong.** The Meghalaya report that includes Sohiong leaves out the NOTA
  rows of the other 59 seats. Its candidate rows for those seats equal the
  version without Sohiong. TCPD's 2023 rows equal that version in every vote
  count in 55 of the 59 seats; in seats 44, 49, 50 and 52 a row differs, by up
  to 155 votes.

## Seats TCPD lacks before 2008

Before the 2008 delimitation, TCPD's general elections lack 70 seats, found the
same way (seat numbers missing from 1 to the state's last seat) and listed as
59 entries, Assam's twelve 1980 Lok Sabha seats being one.
[`data/tcpd_gaps.csv`](data/tcpd_gaps.csv) classifies each one, with the ECI
document that decides it (a file under `data/raw/eci_reports/adjourned/`) and
the line of evidence. The build checks that file: every seat it lists must be
missing from TCPD's general election of that year, every source must be in
`MANIFEST.csv`, and the seats marked added must be exactly the seats built.

[`AE_missing_before_2008.csv.gz`](data/release/AE_missing_before_2008.csv.gz)
has the 13 that ECI reports with every candidate, 37 rows. ECI's report decides
the coding. A seat in the general election's own report is `Poll_No` 0 with
that election's `Assembly_No`, `Year` and `month`; a seat ECI lists among
by-elections is coded as the by-elections file codes one (the term's
`Assembly_No`, the poll's year and month, `Poll_No` 1).

| Seats | Outcome | Coded | Source |
|---|---|---|---|
| Arunachal Pradesh 1999: Anini (41); 2004: Mukto (3), Dirang (4), Sagalee (15); Sikkim 2004: Wak (12), Damthang (13), Melli (14), Kabi Tingda (25) | Won unopposed | Poll_No 0, one row, Votes 0 | ECI's report for that election: one contesting candidate, "Uncontested" |
| Assam 1996: Dispur (52), Dergaon (97), Nazira (104), Margherita (124) | Polled 11 October 1996 | Poll_No 1, 1996, month 10 | ECI's by-election results, 1996 (not in ECI's 1996 report) |
| Uttar Pradesh 1996: Shikarpur (385) | Polled 8 February 1997 | Poll_No 1, 1997, month 2 | ECI's by-election results, February 1997 (not in ECI's 1996 report) |

An unopposed winner is one row with `Votes` 0, `Valid_Votes` 0,
`Turnout_Percentage` 0, `Deposit_Lost` "no" and `Margin` 0, as in 220 of
TCPD's 268 one-candidate rows. (The 2024 and by-election files here leave
those columns empty for unopposed seats instead.) Each by-election page is
checked against itself: its candidates must be as many as its count of
contesting candidates and add up to its valid votes, and its general and
service electors to its total. For an unopposed seat, the seat summary must
count one contesting candidate, and Detailed Results must list that one
candidate as the summary's winner. Seat facts come from the seat's latest TCPD
row on the same boundaries, and the build stops if ECI's name or reservation
differs (ECI spells Dergaon "Dergoan"; TCPD types Sikkim's Bhutia-Lepcha seats
ST until 1999 and BL from 2004, as ECI does in 2004). Four Assam candidates'
sex is blank on ECI's page and stays empty. Matching parties ignores the year,
so a match to a party PPI first records after the poll is dropped: `LSP` in
Shikarpur, 1997, is not the Lok Satta Party of 2006.

The other 46 entries are not added:

- **Polled later, no candidate results (2).** Beas (Punjab 2007, 12): ECI's
  report has its seat summary only (winner Manjinder Singh Kang, SAD, 53,014
  votes) and prints the original polling date, 13 February; the poll was
  deferred to 11 March 2007 after violence (The Tribune, UNI). Bajpur
  (Uttarakhand 2007, 59): the Chief Electoral Officer's press note of
  21 February 2007 reopens nominations for the Congress candidate only and
  sets the poll for 25 March; ECI's report has the seat summary only, and the
  CEO's AC-wise result marks it "Election is scheduled for 25-3-2007". No
  Form 20 turned up for either.
- **In TCPD as a by-election (3).** Rajakhera (Rajasthan 1993) and Hastinapur
  (Uttar Pradesh 1993), polled 1994, and Patna (Lok Sabha 1991), polled 1993,
  are TCPD rows with `Poll_No` 1. ECI's by-election workbook for 1952 to 1995
  lists all three; for the two assembly seats TCPD has only the workbook's
  winner and runner-up.
- **Not polled before the next general election (20).** Shampukur (West Bengal
  1971): "poll countermanded ... due to death of the candidate"; it is in the
  March 1972 general election. Lungleh (Assam 1967): "no nomination filed".
  Assam 1983, 17 seats: ECI's report has 109 of 126; 14 have no page and three
  (Bongaigaon, Dhekiajuli, Sootea) a blank one. Lok Sabha 1980, 12 of Assam's
  14 seats: the 1980 volume's Assam electorate (1,209,486) is Karimganj's and
  Silchar's; all 14 polled in 1985, as part of the 8th Lok Sabha. ECI records
  no poll for any of these before the next general election.
- **Unresolved (20).** ECI's reports note a countermand or the lack of a
  nomination for Nathupur (Uttar Pradesh 1974, 207), Viramgam (Gujarat 1975,
  63) and Chilka (Odisha 1974, 58), and leave out without a note six Manipur
  1990 seats (1, 2, 4, 5, 20, 21), Kulu (Himachal Pradesh 1990, 56),
  Manjhanpur (Uttar Pradesh 1993, 279), six Meerut-district seats (Uttar
  Pradesh 1991: Agota, Kithore, Hastinapur, Meerut Cantonment, Meerut,
  Kharkhauda) and, in the Lok Sabha, Purnea and Meerut (1991) and Shillong
  (1980). ECI publishes no result for a later poll in any of them. Its
  by-election workbook is incomplete (it has no entries at all for 1973 to
  1977, and lists Meerut's later winner without a year or votes), so its
  silence does not show that a seat was never polled.
- **ECI's report merges two seats (1).** Delhi 1983 prints Krishan Nagar (30)
  as a second seat 31 beside Gandhi Nagar, with one candidate list. TCPD's
  Gandhi Nagar rows are Krishan Nagar's result: they add up to its 68,518
  valid votes and carry its 136,384 electors. Gandhi Nagar's own candidates
  are not in the report, so neither seat can be set right from it.

The seat numbers are TCPD's. The ECI reports and volumes are in
`data/raw/eci_reports/adjourned/` with the rest, downloaded on 19 November
2026.

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
- [`data/raw/eci_reports/adjourned/`](data/raw/eci_reports/adjourned/): the
  files for the five adjourned polls (above), ECI's Tamil Nadu 2016 and Odisha
  2019 Detailed Results that leave three of them out, and the Tamil Nadu Form
  7A lists, downloaded by Priyadarshi Amar on 18 and 19 November 2026;
  `MANIFEST.csv` and `fetch_log.jsonl` as for the by-elections. The same
  folder has the files for the seats TCPD lacks before 2008 (above), downloaded
  on 19 November 2026: ECI's statistical reports for each election concerned
  (old.eci.gov.in, one PDF each, with a text layer), its Lok Sabha volumes for
  1980, 1985, 1991 and 1992, its by-election results of 1996 and 1997 and its
  workbook of by-elections from 1952 to 1995, and the Chief Electoral
  Officer, Uttarakhand's 2007 press note, notification, candidate list and
  AC-wise result.
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
