# Indian election results after TCPD

Candidate-level results of Indian Lok Sabha and state assembly general
elections held after the coverage of TCPD's Lok Dhaba data ends, in the same
column layout, so the files can be appended to TCPD's `All_States_GE` and
`All_States_AE`.

TCPD's files (Trivedi Centre for Political Data, Ashoka University) stop with
the 2019 Lok Sabha and the assemblies of May 2023. As of November 2026 the
Lok Dhaba download site refuses connections and TCPD's GitHub archive was last
updated in June 2023. The results here come from the Election Commission of
India (ECI): its statistical reports where they can be obtained (the 2024 Lok
Sabha; the 2023 Mizoram and Telangana assemblies), and its results website for
the other assemblies.

- [`data/release/GE_2024.csv.gz`](data/release/GE_2024.csv.gz): Lok Sabha 2024.
- [`data/release/AE_2023_2026.csv.gz`](data/release/AE_2023_2026.csv.gz):
  assemblies from November 2023 to 2026.

One row per candidate per seat, with NOTA as its own row, as in TCPD.

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

Karanpur (Rajasthan 3) is listed as 2024: its 2023 poll was adjourned to
January 2024 after a candidate died. Not covered: by-elections; Surat (Lok Sabha
2024), won unopposed and absent from ECI's report.

## Columns

Every TCPD column is present, in the order of TCPD's own files (the two
differ: the assembly file adds `Age` and `District_Name`). A column is filled
only where the value is the quantity TCPD's column holds; otherwise it is
empty.

| Columns | How they are filled |
|---|---|
| `Candidate`, `Votes`, `Constituency_No`, `Constituency_Name` | From the source. Lok Sabha seat numbers follow the order of ECI's report, checked against TCPD's 2019 numbers and the results website (see below). |
| `Sex`, `Age`, `Candidate_Type`, `Electors`, `Turnout_Percentage` | Where the source is an ECI statistical report: Lok Sabha 2024, Mizoram and Telangana 2023. The results-website sources do not have them. |
| `Position`, `Valid_Votes`, `N_Cand`, `Vote_Share_Percentage`, `Margin`, `Margin_Percentage`, `Deposit_Lost`, `Turnout_Percentage` | By TCPD's rules, recovered from TCPD's own rows ([`rules.py`](src/eci_results/rules.py)). |
| `Constituency_Type`, `Sub_Region`, `District_Name`, `DelimID` | From the seat's latest TCPD election. Empty for Assam, Jammu and Kashmir and Ladakh, whose seats were redrawn in 2022-23. |
| `Assembly_No` | TCPD's previous number plus one (the 18th Lok Sabha). Empty for the first assembly of the Union Territory of Jammu and Kashmir. |
| `Party`, `Party_ID` | From TCPD's party list (TCPD-PPI, 1962-2021): `Party` is the label TCPD's own rows use for that party. ECI names that differ from PPI's are matched in [`data/party_aliases.csv`](data/party_aliases.csv), each checked by hand. Parties founded or split after 2021 keep the source's name or abbreviation and have no `Party_ID`; [`parties_not_in_ppi.csv`](data/release/parties_not_in_ppi.csv) lists them. |
| `ENOP` | Empty. No formula over TCPD's vote columns reproduces TCPD's values. |
| `Party_Type_TCPD` | Empty. It records a party's ECI recognition at each election, which PPI does not carry. |
| `pid` and the career columns built from it (`last_poll`, `Contested`, `Last_Party`, `Last_Party_ID`, `Last_Constituency_Name`, `Same_Constituency`, `Same_Party`, `No_Terms`, `Turncoat`, `Incumbent`, `Recontest`), `MyNeta_education`, `TCPD_Prof_*` | Empty. They need TCPD's linking of candidates across elections, or sources outside ECI's results. |

Share of each column filled, by file: [`MANIFEST.json`](MANIFEST.json).

### TCPD's rules, recovered

Each rule was found by recomputing the column from `Votes`, `Party` and
`Electors` for every general-election row TCPD publishes for 2014-2023 and
comparing with TCPD's value; [`rule_check.csv`](data/release/rule_check.csv)
has the agreement for each column (`make validate`).

- `Valid_Votes` includes NOTA. (ECI's own "valid votes" leaves NOTA out.)
- `Position` ranks all rows, NOTA included, by votes.
- `N_Cand` counts candidates, not NOTA.
- `Margin` is a row's votes minus the next row's, NOTA included; the last row
  gets 0. `Margin_Percentage` divides by `Valid_Votes`.
- `Deposit_Lost` is `yes` below one sixth of `Valid_Votes`, empty for NOTA.
- `Turnout_Percentage` is `Valid_Votes` over `Electors`.
- NOTA's party is `NOTA` (TCPD writes `None of the Above` from 2022).

### Checks the build enforces

`make build` stops if any of these fail:

- every seat of each state is present (seat numbers 1 to TCPD's highest, or
  126 for Assam and 90 for Jammu and Kashmir after redrawing);
- Lok Sabha seat numbers taken from the report's order equal TCPD's 2019
  numbers for every seat matched by name outside the redrawn states, and their
  first digit equals the results website's number, which the india-votes-data
  copy cut to one digit;
- Lok Sabha `Valid_Votes`, less NOTA, equals ECI's valid votes in every seat;
- no two rows of a seat share a `Position`.

As a check from outside the pipeline, seats won in the 2024 Lok Sabha by party
match ECI's declared result (BJP 240 with Surat, INC 99, SP 37, AITC 29,
DMK 22, TDP 16, JD(U) 12).

## Sources

Pinned with URL and SHA-256 in [`data/source.json`](data/source.json).

- Mizoram and Telangana 2023: ECI statistical report, "10 - Detailed
  Results", from Internet Archive captures (Telangana's of OpenCity's mirror).
- Rajasthan, Madhya Pradesh and Chhattisgarh 2023:
  [azadecon/assembly_elections_2023](https://github.com/azadecon/assembly_elections_2023)
  (GPL-3.0), one workbook per seat scraped from results.eci.gov.in on counting
  day. ECI's statistical reports for these three states could not be obtained
  (eci.gov.in refuses automated and many foreign requests, and the Internet
  Archive holds only refusals); they will replace the scrape when obtained.
  Where both exist, the scrape matches ECI's report exactly in 115 of 119
  Telangana seats and 39 of 40 Mizoram seats, with the same candidates in
  every seat; the largest gap in a seat's total is 774 votes
  ([`scrape_check.csv`](data/release/scrape_check.csv), `make validate`).
- Karanpur (Rajasthan 3), polled 5 January 2024: its page on
  results.eci.gov.in as archived by the Internet Archive.
- Lok Sabha 2024: ECI Statistical Report, report 33, "Constituency Wise
  Detailed Result", as copied into
  [in-rolls/wasted_votes](https://github.com/in-rolls/wasted_votes) (the
  original ECI download URL was not recorded).
- Assemblies of Haryana, Jharkhand, Jammu and Kashmir, Maharashtra (2024),
  Bihar, Delhi (2025), Assam, Kerala, Puducherry, Tamil Nadu, West Bengal
  (2026): [thecont1/india-votes-data](https://github.com/thecont1/india-votes-data)
  (MIT), scraped from results.eci.gov.in.
- Assemblies of Andhra Pradesh, Odisha, Arunachal Pradesh and Sikkim (June
  2024): the constituency pages of results.eci.gov.in as kept by the Internet
  Archive, committed verbatim in [`data/wayback/`](data/wayback/), fetched by
  [`fetch_wayback.py`](src/eci_results/fetch_wayback.py) and parsed by
  [`parse_wayback.py`](src/eci_results/parse_wayback.py), which checks each
  page's final counting round, NOTA row and total. Arunachal Pradesh had
  uncontested seats; they appear with their one candidate and no votes.
- Reference, not redistributed: TCPD Indian Elections Data v2.0 (from a
  mirror of a July 2026 download) and TCPD-PPI, used for seat facts, party
  labels and IDs, and to recover TCPD's rules.

## Rebuild

```
make fetch      # download inputs, check SHA-256
make build      # parse archived pages, build release files and MANIFEST.json
make validate   # recompute TCPD's rules on TCPD's rows
make test
```

`make wayback` re-fetches the archived pages (slow; they are committed).

## Citation and terms

Cite ECI for the results and, where you use the TCPD-derived columns
(`Party`, `Party_ID`, seat facts) or append these rows to TCPD's, cite: Agarwal,
Ananay, et al. 2021. "TCPD Indian Elections Data v2.0." Trivedi Centre for
Political Data, Ashoka University; and "TCPD Political Parties of India
Dataset (TCPD-PPI), 1962-2021." TCPD's data are free for non-commercial use
with citation. This repository is not affiliated with or endorsed by TCPD.
The code is MIT-licensed.
