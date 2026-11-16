# Indian election results after TCPD

Every candidate's votes in the Lok Sabha election of 2024 and the state assembly
elections from November 2023 to May 2026, in the column layout of TCPD's Lok
Dhaba files, so they can be appended to TCPD's data without reshaping. The
results are the Election Commission of India's (ECI).

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

Karanpur (Rajasthan, seat 3) appears under 2024 because its 2023 poll was
adjourned to January 2024 after a candidate died. By-elections are not covered.
Surat (Lok Sabha 2024) is missing because its candidate was elected unopposed
and ECI's report leaves it out.

## What each column holds

A column is filled only where the value is the quantity TCPD's column holds.
Otherwise it is empty. [`MANIFEST.json`](MANIFEST.json) gives the share of each
column filled, by file.

| Columns | Filled from |
|---|---|
| `Candidate`, `Votes`, `Constituency_No`, `Constituency_Name` | The source. |
| `Sex`, `Age`, `Candidate_Type`, `Electors`, `Turnout_Percentage` | ECI's statistical reports, where the source is one: Lok Sabha 2024, Mizoram and Telangana 2023. The results website does not publish them. |
| `Position`, `Valid_Votes`, `N_Cand`, `Vote_Share_Percentage`, `Margin`, `Margin_Percentage`, `Deposit_Lost` | TCPD's rules, recovered from TCPD's own rows (below). |
| `Constituency_Type`, `Sub_Region`, `District_Name`, `DelimID` | The seat's latest election in TCPD's files. Empty for Assam, Jammu and Kashmir and Ladakh, whose seats were redrawn in 2022 and 2023. |
| `Assembly_No` | TCPD's previous number plus one; the 2024 Lok Sabha is the 18th. Empty for Jammu and Kashmir's first assembly as a Union Territory. |
| `Party`, `Party_ID` | TCPD's party list (TCPD-PPI, 1962 to 2021). `Party` is the label TCPD's rows print for that party: CPM, not CPI(M). ECI names that PPI spells differently are matched in [`data/party_aliases.csv`](data/party_aliases.csv), each checked by hand. Parties founded after 2021, such as Jan Suraaj and Tamilaga Vettri Kazhagam, keep ECI's name and have no `Party_ID`; [`parties_not_in_ppi.csv`](data/release/parties_not_in_ppi.csv) lists them. |
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

Seats won by party match ECI's declared results in every election we checked,
including the 2024 Lok Sabha (BJP 240 with Surat, INC 99, SP 37, AITC 29, DMK
22) and all five assemblies of 2023.

## Sources

[`data/source.json`](data/source.json) pins every input by URL and SHA-256.

| Elections | Source |
|---|---|
| Lok Sabha 2024 | ECI statistical report 33, "Constituency Wise Detailed Result", as copied into [in-rolls/wasted_votes](https://github.com/in-rolls/wasted_votes). |
| Mizoram, Telangana 2023 | ECI statistical report "10 - Detailed Results", from Internet Archive captures (Telangana's of OpenCity's mirror). |
| Rajasthan, Madhya Pradesh, Chhattisgarh 2023 | [azadecon/assembly_elections_2023](https://github.com/azadecon/assembly_elections_2023) (GPL-3.0), scraped from ECI's results website on counting day. |
| Karanpur (Rajasthan) 2024; Andhra Pradesh, Odisha, Arunachal Pradesh, Sikkim 2024 | ECI's results website as archived by the Internet Archive. The pages are committed in [`data/wayback/`](data/wayback/); [`parse_wayback.py`](src/eci_results/parse_wayback.py) checks that each shows the final counting round, a NOTA row and a matching total. |
| Haryana, Jharkhand, Jammu and Kashmir, Maharashtra 2024; Bihar, Delhi 2025; Assam, Kerala, Puducherry, Tamil Nadu, West Bengal 2026 | [thecont1/india-votes-data](https://github.com/thecont1/india-votes-data) (MIT), scraped from ECI's results website. |

ECI's statistical reports are the official count. For Rajasthan, Madhya Pradesh
and Chhattisgarh they could not be obtained: eci.gov.in refuses automated and
many foreign requests, and the Internet Archive holds only its refusals. The
counting-day scrape used instead matches ECI's report exactly in 154 of the
159 Mizoram and Telangana seats where both exist, with the same candidates in
every seat. The largest difference in a seat's total is 774 votes
([`scrape_check.csv`](data/release/scrape_check.csv)).

TCPD's files and TCPD-PPI are used as references and not redistributed. They
supply the seat facts and party labels and were the basis for recovering
TCPD's rules.

## Open work

Contributions are welcome on any of these.

- ECI's statistical reports for Rajasthan, Madhya Pradesh and Chhattisgarh
  2023, which would replace the counting-day scrape.
- By-elections since 2023.
- `Party_Type_TCPD`, from ECI's notifications of recognized parties for each
  election.
- How TCPD computes `ENOP`.
- Person IDs linking these candidates to their earlier TCPD records, which
  would fill `pid`, `Incumbent` and the other career columns.

If TCPD resumes publishing, these files are meant to fold into theirs.
[in-rolls/candidate_namesakes](https://github.com/in-rolls/candidate_namesakes),
a study of namesake candidates in Indian elections, uses them to extend its
analysis past 2023.

## Rebuild

```
make fetch      # download inputs and check their SHA-256
make build      # parse archived pages; write data/release and MANIFEST.json
make validate   # recompute TCPD's rules on TCPD's rows; compare scrape and report
make test
```

`make wayback` fetches archived pages again. It is slow, and the pages are
already committed.

## Citation and terms

Cite ECI for the results. Where you use the columns derived from TCPD (`Party`,
`Party_ID`, the seat facts) or append these rows to TCPD's files, also cite
Agarwal, Ananay, et al. 2021, "TCPD Indian Elections Data v2.0," and "TCPD
Political Parties of India Dataset (TCPD-PPI), 1962-2021," both Trivedi Centre
for Political Data, Ashoka University. TCPD's data are free for non-commercial
use with citation. This repository is not affiliated with TCPD or endorsed by
it. The code is MIT-licensed.
