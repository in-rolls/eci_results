"""Readers for each source, returning one row per candidate with NOTA kept.

Common columns: State_Name, Constituency_No, Constituency_Name, Candidate,
Party_Source (the party as the source prints it), Votes, and, where the
source has them, Sex, Age, Candidate_Type and Electors.
"""

import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

STATE_CODES = {
    "HR": "Haryana", "JH": "Jharkhand", "JK": "Jammu_&_Kashmir", "MH": "Maharashtra",
    "BR": "Bihar", "DL": "Delhi", "AS": "Assam", "KL": "Kerala", "PY": "Puducherry",
    "TN": "Tamil_Nadu", "WB": "West_Bengal", "AP": "Andhra_Pradesh",
    "AR": "Arunachal_Pradesh", "OD": "Odisha", "SK": "Sikkim",
}  # fmt: skip
NOTA_NAMES = {"NOTA", "NONE OF THE ABOVE"}
# TCPD's majority codings (it mixes M/MALE and GEN/GENERAL across years).
SEX = {"MALE": "M", "FEMALE": "F", "THIRD": "O", "OTHERS": "O", "TG": "O"}
# BL is Sikkim's Bhutia-Lepcha seat category, which TCPD also uses.
CATEGORY = {"GENERAL": "GEN", "GEN": "GEN", "SC": "SC", "ST": "ST", "BL": "BL"}


# ECI names TCPD writes differently.
STATE_NAMES = {"NCT_OF_Delhi": "Delhi", "NCT_of_Delhi": "Delhi"}


def tcpd_state(name):
    state = str(name).strip().replace(" and ", " & ").replace(" ", "_")
    return STATE_NAMES.get(state, state)


def mark_nota(frame):
    nota = frame["Candidate"].str.upper().str.strip().isin(NOTA_NAMES)
    frame.loc[nota, "Candidate"] = "None of the Above"
    frame.loc[nota, "Party_Source"] = "NOTA"
    return frame


def read_eci_report(path):
    """ECI statistical report 33, Constituency Wise Detailed Result (GE 2024)."""
    report = pd.read_csv(path, encoding="utf-8-sig")
    report = report[report["Candidate Name"].notna()]
    frame = pd.DataFrame(
        {
            "State_Name": report["State Name"].map(tcpd_state),
            "Constituency_No": pd.NA,
            "Constituency_Name": report["PC Name"].str.strip().str.upper(),
            "Candidate": report["Candidate Name"].str.strip(),
            "Party_Source": report["Party Name"].str.strip(),
            "Votes": pd.to_numeric(report["Total"], errors="coerce"),
            "Sex": report["Gender"].str.upper().map(SEX),
            "Age": pd.to_numeric(report["Age"], errors="coerce"),
            "Candidate_Type": report["Category"].str.upper().map(CATEGORY),
            "Electors": pd.to_numeric(report["Total Electors"], errors="coerce"),
            "Source_Valid_Votes": pd.to_numeric(report["Valid Votes"], errors="coerce"),
        }
    )
    return mark_nota(frame)


def read_india_votes_data(path):
    """thecont1/india-votes-data CSV, or our parse of archived ECI pages."""
    table = pd.read_csv(path)
    votes = (
        table["total_votes"]
        if "total_votes" in table
        else table["evm_votes"] + table["postal_votes"]
    )
    frame = pd.DataFrame(
        {
            "State_Name": table["election_state"].map(STATE_CODES),
            "Constituency_No": table["constituency_no"],
            "Constituency_Name": table["constituency"].str.strip().str.upper(),
            "Candidate": table["candidate"].str.strip(),
            "Party_Source": table["party"].str.strip(),
            "Votes": pd.to_numeric(votes, errors="coerce"),
        }
    )
    return mark_nota(frame)


def read_eci_detailed(path):
    """ECI statistical report "10 - Detailed Results" workbook (assemblies).

    One row per candidate, NOTA included. Columns are found by header, because
    the layout changed in 2024: GENDER for SEX, and a second vote percentage
    that pushes TOTAL ELECTORS one column right. Names carry their ballot
    serial ("1 Robert Romawia Royte"), which is dropped.
    """
    raw = pd.read_excel(path, header=None)
    header = raw.index[raw[0].astype(str).str.strip().eq("STATE/UT NAME")][0]
    names = raw.loc[header].astype(str).str.strip().tolist()
    table = raw.loc[header + 1 :]
    table.columns = names
    table = table[pd.to_numeric(table["AC NO."], errors="coerce").notna()]
    sex = "GENDER" if "GENDER" in names else "SEX"
    return mark_nota(
        pd.DataFrame(
            {
                "State_Name": table["STATE/UT NAME"].map(tcpd_state),
                "Constituency_No": table["AC NO."].astype(int),
                "Constituency_Name": table["AC NAME"]
                .astype(str)
                .str.replace(r"\s*\((SC|ST|BL)\)\s*$", "", regex=True)
                .str.strip()
                .str.upper(),
                "Constituency_Type": table["AC NAME"]
                .astype(str)
                .str.extract(r"\((SC|ST|BL)\)\s*$")[0]
                .fillna("GEN"),
                "Candidate": table["CANDIDATE NAME"]
                .astype(str)
                .str.replace(r"^\d+\s+", "", regex=True)
                .str.strip(),
                "Party_Source": table["PARTY"].astype(str).str.strip(),
                "Votes": pd.to_numeric(table["TOTAL"], errors="coerce"),
                "Sex": table[sex].astype(str).str.upper().map(SEX),
                "Age": pd.to_numeric(table["AGE"], errors="coerce"),
                "Candidate_Type": table["CATEGORY"]
                .astype(str)
                .str.upper()
                .map(CATEGORY),
                "Electors": pd.to_numeric(table["TOTAL ELECTORS"], errors="coerce"),
            }
        )
    )


def read_azadecon(folder):
    """azadecon/assembly_elections_2023: one workbook per seat, scraped from
    results.eci.gov.in on counting day. Each ends with a Total row."""
    frames = []
    for path in sorted(Path(folder).glob("*.xlsx")):
        seat = pd.read_excel(path)
        seat = seat[seat["s_n"].notna()]
        frames.append(seat)
    table = pd.concat(frames, ignore_index=True)
    return mark_nota(
        pd.DataFrame(
            {
                "State_Name": None,
                "Constituency_No": table["constituency"].astype(int),
                "Constituency_Name": pd.NA,
                "Candidate": table["candidate"].astype(str).str.strip(),
                "Party_Source": table["party"].astype(str).str.strip(),
                "Votes": pd.to_numeric(table["total_votes"], errors="coerce"),
            }
        )
    )


def form20_columns(page, count):
    """Each vote column's header text on Form 20's first page, from the
    words above the first booth row, grouped by the column they sit over."""
    words = page.extract_words()
    lines = defaultdict(list)
    for word in words:
        lines[round(word["top"])].append(word)
    first = next(
        top
        for top in sorted(lines)
        if len(lines[top]) == count
        and all(w["text"].isdigit() for w in lines[top])
        and min(lines[top], key=lambda w: w["x0"])["text"] == "1"
    )
    centers = [
        (w["x0"] + w["x1"]) / 2 for w in sorted(lines[first], key=lambda w: w["x0"])
    ]
    booth = max(w["top"] for w in words if w["text"] == "Booth" and w["top"] < first)
    heads = defaultdict(list)
    for word in words:
        if booth - 2 <= word["top"] < first - 2:
            middle = (word["x0"] + word["x1"]) / 2
            heads[min(range(count), key=lambda k: abs(middle - centers[k]))].append(
                word
            )
    return [
        " ".join(
            w["text"]
            for w in sorted(heads[k], key=lambda w: (round(w["top"]), w["x0"]))
        )
        for k in range(count)
    ]


def read_eci_form20(path):
    """Form 20, the final result sheet of one assembly seat (a PDF with one
    row per polling station, then postal votes and totals).

    Candidate names and parties are listed, in column order, in
    candidates.csv beside the PDF, because the PDF breaks them across lines;
    each must equal its column's header text in the PDF, spaces aside. The
    booth rows must add up to the "recorded at polling station" row, that row
    plus postal votes to the totals, and the candidates to total valid votes.
    Form 20 does not record candidates' sex, age or category.
    """
    import pdfplumber

    path = Path(path)
    people = pd.read_csv(path.with_name("candidates.csv")).sort_values("column")
    count = len(people) + 6  # booth, candidates, valid, rejected, NOTA, total, tendered
    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text(layout=True) or "" for page in pdf.pages)
        heads = form20_columns(pdf.pages[0], count)
    squash = lambda t: re.sub(r"\s+", "", str(t)).upper()  # noqa: E731
    for k, row in enumerate(people.itertuples(), start=1):
        if squash(heads[k]) != squash(f"{row.Candidate} {row.Party_Source}"):
            raise SystemExit(f"{path}: column {k} reads {heads[k]!r}")
    booths, totals = [], []
    for line in text.splitlines():
        words = line.split()
        tail = len(words)
        while tail and words[tail - 1].isdigit():
            tail -= 1
        values = [int(x) for x in words[tail:]]
        if tail == 0 and len(values) == count:
            booths.append(values)
        elif len(values) == count - 1:  # a totals row, its label maybe in front
            totals.append(values)
    recorded, postal, total = totals[-3:]
    if [r[0] for r in booths] != list(range(1, len(booths) + 1)):
        raise SystemExit(f"{path}: booth numbers do not run 1..n")
    if [sum(col) for col in zip(*(r[1:] for r in booths))] != recorded:
        raise SystemExit(f"{path}: booths do not add up to the recorded votes")
    if [a + b for a, b in zip(recorded, postal)] != total:
        raise SystemExit(f"{path}: recorded and postal votes do not add up")
    votes, valid, nota = (
        total[: len(people)],
        total[len(people)],
        total[len(people) + 2],
    )
    if sum(votes) != valid:
        raise SystemExit(f"{path}: candidates do not add up to total valid votes")
    seat = re.search(r"Name of the Assembly Constituency\s*:\s*(\d+)-(.+?)\s+AC", text)
    electors = int(re.search(r"Total No\.? of Electors[^:]*:\s*(\d+)", text)[1])
    frame = pd.DataFrame(
        {
            "Constituency_No": int(seat[1]),
            "Constituency_Name": seat[2].strip().upper(),
            "Candidate": list(people["Candidate"]) + ["None of the Above"],
            "Party_Source": list(people["Party_Source"]) + ["NOTA"],
            "Votes": votes + [nota],
            "Electors": electors,
        }
    )
    return mark_nota(frame)


def letters(text):
    """A text's letters, uppercased and sorted: equal for two spellings that
    differ only in spacing, punctuation or the order of their lines."""
    return "".join(sorted(re.sub(r"[^A-Za-z]", "", str(text)).upper()))


def sideways_cell(page, cell, top=None):
    """Text set sideways (reading bottom to top) in one table cell. Only rotated
    characters count, so the horizontal headings around the cell do not leak
    in; `top` reads above the cell, for text the cell's border cuts off on the
    page but which the PDF keeps."""
    x0, cell_top, x1, bottom = cell
    upper = cell_top if top is None else top
    chars = [
        c
        for c in page.chars
        if x0 <= (c["x0"] + c["x1"]) / 2 <= x1
        and upper <= (c["top"] + c["bottom"]) / 2 <= bottom
        and c["text"].strip()
        and abs(c["matrix"][1]) > 0.5
    ]
    lines = defaultdict(list)
    for c in chars:
        lines[round((c["x0"] + c["x1"]) / 5)].append(c)
    return " ".join(
        "".join(c["text"] for c in sorted(lines[k], key=lambda c: -c["top"]))
        for k in sorted(lines)
    )


def read_eci_form20_table(path):
    """Form 20 laid out as a spreadsheet table (Tamil Nadu's 2016 sheets): one
    row per polling station, then rows of votes recorded at polling stations,
    postal votes and totals.

    Candidates' names and parties, sideways in the header, are listed in
    column order in candidates.csv beside the PDF; each must have the same
    letters as its column's header. The polling-station rows must run 1..n
    and add up to the recorded row, recorded and postal votes to the totals,
    and the candidates to total valid votes. Form 20 does not record
    candidates' sex, age or category.
    """
    import pdfplumber

    path = Path(path)
    people = pd.read_csv(path.with_name("candidates.csv")).sort_values("column")
    count = len(people)
    booths, totals = [], []
    with pdfplumber.open(path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        first = pdf.pages[0]
        header = first.find_tables()[0].rows
        width = len(header[0].cells)
        ids = width - count - 5  # booth columns before the candidates
        names = [sideways_cell(first, c, top=0) if c else "" for c in header[1].cells]
        parties = [sideways_cell(first, c) if c else "" for c in header[2].cells]
        for page in pdf.pages:
            for table in page.extract_tables():
                for row in table:
                    cells = [(c or "").replace("\n", " ").strip() for c in row]
                    found = [re.findall(r"\d+", c) for c in cells]
                    values = [int(f[-1]) if f else None for f in found]
                    if [re.sub(r"\D", "", c) for c in cells] == [
                        str(k) for k in range(1, width + 1)
                    ]:
                        continue  # the row numbering the columns
                    body = values[ids : ids + count + 4]
                    if None in body or len(cells) != width:
                        continue
                    if cells[0].isdigit():
                        booths.append(values)
                    else:
                        totals.append(values[ids : ids + count + 4])
    for k, row in enumerate(people.itertuples()):
        column = ids + k
        if letters(names[column]) != letters(row.Candidate) or letters(
            parties[column]
        ) != letters(row.Party_Source):
            raise SystemExit(
                f"{path}: column {column + 1} reads {names[column]!r}, "
                f"{parties[column]!r}"
            )
    if [b[0] for b in booths] != list(range(1, len(booths) + 1)):
        raise SystemExit(f"{path}: polling stations do not run 1..n")
    recorded, postal, total = totals[:3]
    sums = [sum(b[ids + k] for b in booths) for k in range(count + 4)]
    if sums != recorded:
        raise SystemExit(f"{path}: polling stations do not add up to the recorded row")
    if [a + b for a, b in zip(recorded, postal)] != total:
        raise SystemExit(f"{path}: recorded and postal votes do not add up")
    votes, valid, nota = total[:count], total[count], total[count + 2]
    if sum(votes) != valid:
        raise SystemExit(f"{path}: candidates do not add up to total valid votes")
    seat = re.search(
        r"(?:CONSTITUENCY\s*:|Segment[^)]*\))\s*(\d+)\s*-?\s*([A-Za-z]+)", text
    )
    electors = re.search(r"ELECTORS[^\n:-]*[:-]\s*([\d+ ]*\d)", text, re.I)[1]
    frame = pd.DataFrame(
        {
            "Constituency_No": int(seat[1]),
            "Constituency_Name": seat[2].upper(),
            "Candidate": list(people["Candidate"]) + ["None of the Above"],
            "Party_Source": list(people["Party_Source"]) + ["NOTA"],
            "Votes": votes + [nota],
            # "200347+5": general and service electors, printed apart
            "Electors": sum(int(x) for x in electors.replace(" ", "").split("+")),
        }
    )
    return mark_nota(frame)


DETAILED_SEAT = re.compile(
    r"Constituency\s+(\d+)\.\s+(.+?)\s+TOTAL ELECTORS\s*:\s*(\d+)", re.I
)
DETAILED_ROW = re.compile(
    r"^\s*(\d+)\s+(.+?)\s+(M|F|TG|O)\s+(\d+)\s+(GEN|SC|ST|BL)\s+(\S+)\s+"
    r"(.*?)\s*(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)\s*$"
)
DETAILED_NOTA = re.compile(
    r"^\s*(\d+)\s+None of the Above\s+NOTA\s+NOTA\s+(\d+)\s+(\d+)\s+(\d+)\s+[\d.]+\s*$"
)
DETAILED_TOTAL = re.compile(r"TURNOUT\s+TOTAL:\s+(\d+)\s+(\d+)\s+(\d+)")


def read_eci_detailed_pdf(path):
    """ECI statistical report "10 - Detailed Results" published as a PDF only
    (Rajasthan 2018). Each seat's block opens with its number, name and total
    electors and closes with a TURNOUT row; within it, each row's general and
    postal votes must add up to its total, serial numbers must run 1..n, and
    the rows must add up to the TURNOUT row.
    """
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        lines = [
            line
            for page in pdf.pages
            for line in (page.extract_text(layout=True) or "").splitlines()
        ]
    seats, rows, current = [], [], None

    def close(totals):
        serials = [r["Serial"] for r in rows]
        label = f"{path}: seat {current['Constituency_No']}"
        if serials != list(range(1, len(serials) + 1)):
            raise SystemExit(f"{label}: rows {serials} do not run 1..n")
        sums = [sum(r[k] for r in rows) for k in ("General", "Postal", "Votes")]
        if totals is not None and sums != totals:
            raise SystemExit(f"{label}: rows add up to {sums}, TURNOUT row {totals}")
        seats.extend({**current, **r} for r in rows)

    for line in lines:
        seat, nota, row = (
            DETAILED_SEAT.search(line),
            DETAILED_NOTA.match(line),
            DETAILED_ROW.match(line),
        )
        total = DETAILED_TOTAL.search(line)
        if seat:
            if current is not None and rows:
                close(None)
            name = seat[2].strip()
            kind = re.search(r"\((SC|ST)\)\s*$", name)
            current = {
                "Constituency_No": int(seat[1]),
                "Constituency_Name": re.sub(r"\s*\((SC|ST)\)\s*$", "", name).upper(),
                "Constituency_Type": kind[1] if kind else "GEN",
                "Electors": int(seat[3]),
            }
            rows = []
        elif total and current is not None:
            close([int(total[k]) for k in (1, 2, 3)])
            current, rows = None, []
        elif nota and current is not None:
            general, postal, votes = (int(nota[k]) for k in (2, 3, 4))
            rows.append(
                {"Serial": int(nota[1]), "Candidate": "None of the Above",
                 "Party_Source": "NOTA", "General": general, "Postal": postal,
                 "Votes": votes}
            )  # fmt: skip
        elif row and current is not None:
            general, postal, votes = (int(row[k]) for k in (8, 9, 10))
            sex = {"M": "MALE", "F": "FEMALE"}.get(row[3], row[3])
            category = {"GEN": "GENERAL"}.get(row[5], row[5])
            rows.append(
                {"Serial": int(row[1]), "Candidate": row[2].strip(),
                 "Sex": SEX.get(sex), "Age": int(row[4]),
                 "Candidate_Type": CATEGORY.get(category),
                 "Party_Source": row[6], "General": general, "Postal": postal,
                 "Votes": votes}
            )  # fmt: skip
    for r in seats:
        if r["General"] + r["Postal"] != r["Votes"]:
            raise SystemExit(f"{path}: seat {r['Constituency_No']} row {r['Serial']}")
    frame = pd.DataFrame(seats).drop(columns=["Serial", "General", "Postal"])
    return mark_nota(frame)


# "Field7:" is printed over "CONSTITUENCY" on old reports' summary pages, so
# the text layer reads "FCieOldN7:STITUENCY : 41 - ANINI (ST)".
SUMMARY_SEAT = re.compile(r"STITUENCY\s*:\s*(\d+)\s*-\s*(.+?)\s*$", re.M)
OLD_DETAILED_SEAT = re.compile(r"^\s*Constituency\s*:?\s*(\d+)\s*\.\s*(.+?)\s*$")
OLD_DETAILED_ROW = re.compile(
    r"^\s*(\d+)\s*\.\s*(.+?)\s+(M|F)\s+(?:(\d+)\s+(GEN|SC|ST|BL)\s+)?(\S+)"
    r"(?:\s+(Uncontested))?\s*$"
)


def seat_name(text):
    kind = re.search(r"\((SC|ST|BL)\)\s*$", text)
    name = re.sub(r"\s*\((SC|ST|BL)\)\s*$", "", text).strip().upper()
    return name, kind[1] if kind else "GEN"


def read_eci_uncontested(path):
    """Seats won unopposed, from an ECI statistical report of 1977 to 2008
    (PDF with a text layer): Arunachal Pradesh 1999 and 2004, Sikkim 2004.

    A seat is unopposed when its "Constituency Data - Summary" page counts one
    contesting candidate. Its block in "Detailed Results" must then list
    exactly one candidate, with no votes, whose name and party equal the
    summary's winner. Electors are the summary's total. Votes is 0, TCPD's
    coding for an unopposed winner (220 of its 268 one-candidate rows; the
    rest are -1, 1 or empty).
    """
    import pdfplumber

    with pdfplumber.open(path) as pdf:
        text = "\n".join(p.extract_text(layout=True) or "" for p in pdf.pages)
    summaries = {}
    marks = list(SUMMARY_SEAT.finditer(text))
    for mark, end in zip(marks, marks[1:] + [None]):
        block = text[mark.end() : end.start() if end else len(text)]
        contested = re.search(r"CONTESTED\s+(\d+)\s+(\d+)\s+(\d+)", block)
        if contested is None or int(contested[3]) != 1:
            continue
        electors = re.search(r"ELECTORS.*?TOTAL\s+(\d+)\s+(\d+)\s+(\d+)", block, re.S)
        winner = re.search(r"Winner\s*:\s*(\S+)\s+(.+?)(?:\s{2,}|\s*$)", block, re.M)
        if electors is None or winner is None:
            raise SystemExit(f"{path}: seat {mark[1]} summary lacks electors or winner")
        if int(electors[1]) + int(electors[2]) != int(electors[3]):
            raise SystemExit(f"{path}: seat {mark[1]} electors do not add up")
        summaries[int(mark[1])] = {
            "Electors": int(electors[3]),
            "Party": winner[1],
            "Candidate": winner[2].strip(),
            "Name": mark[2],
        }
    blocks, current = {}, None
    for line in text.splitlines():
        seat = OLD_DETAILED_SEAT.match(line)
        if seat:
            current = int(seat[1])
            blocks[current] = {"Name": seat[2], "rows": []}
            continue
        row = OLD_DETAILED_ROW.match(line)
        if row and current is not None:
            blocks[current]["rows"].append(row)
    out = []
    for seat, summary in sorted(summaries.items()):
        label = f"{path}: seat {seat}"
        block = blocks.get(seat)
        if block is None or len(block["rows"]) != 1:
            raise SystemExit(f"{label}: Detailed Results does not list one candidate")
        row = block["rows"][0]
        if (row[2].strip(), row[6]) != (summary["Candidate"], summary["Party"]):
            raise SystemExit(
                f"{label}: Detailed Results {row[2].strip()} ({row[6]}), "
                f"summary {summary['Candidate']} ({summary['Party']})"
            )
        if seat_name(block["Name"]) != seat_name(summary["Name"]):
            raise SystemExit(f"{label}: {block['Name']} vs {summary['Name']}")
        name, kind = seat_name(block["Name"])
        sex = {"M": "MALE", "F": "FEMALE"}[row[3]]
        out.append(
            {"Constituency_No": seat, "Constituency_Name": name,
             "Constituency_Type": kind, "Electors": summary["Electors"],
             "Candidate": row[2].strip(), "Sex": SEX[sex],
             "Age": int(row[4]) if row[4] else None,
             "Candidate_Type": CATEGORY.get(row[5]) if row[5] else None,
             "Party_Source": row[6], "Votes": 0}
        )  # fmt: skip
    return pd.DataFrame(out).assign(State_Name=None)


def html_rows(path):
    """Each table row of an HTML page, as its cells' text."""
    from html import unescape

    text = Path(path).read_text(encoding="latin-1")
    rows = []
    for tr in re.findall(r"(?is)<tr.*?</tr>", text):
        cells = re.findall(r"(?is)<td.*?</td>", tr)
        cells = [" ".join(unescape(re.sub(r"<[^>]+>", " ", c)).split()) for c in cells]
        if any(cells):
            rows.append(cells)
    return rows


def read_eci_bye_page(path):
    """One seat's result page from ECI's by-election listings of 1996 to 2007
    (old.eci.gov.in/ByeElection/...): seat, electors, poll date, contesting
    candidates and valid votes, then one row per candidate.

    The candidates must be as many as the page's CONTESTED count and add up to
    its VALID votes (and its Total row, where printed); general and service
    electors must add up to the total.
    """
    rows = html_rows(path)
    flat = [[c for c in r if c] for r in rows]
    label = str(path)

    def line(name, after=None):
        start = 0
        if after is not None:
            start = next(i for i, r in enumerate(flat) if r and r[0].startswith(after))
        for r in flat[start:]:
            if len(r) > 1 and r[1] == name:
                return [int(c) for c in r[2:]]
        raise SystemExit(f"{label}: no {name} row")

    seat = next(
        re.search(r"Constituency\s*-\s*(\d+)\s*-?\s*(.+)$", c)
        for r in flat
        for c in r
        if re.search(r"Constituency\s*-\s*\d+", c)
    )
    state = next(
        re.search(r"Assembl?y\s+of\s+(.+?)(?:\s+Code\b.*)?$", c)[1]
        for r in flat
        for c in r
        if re.search(r"Assembl?y\s+of\s+", c)
    )
    contested = line("CONTESTED")[-1]
    general = line("GENERAL", after="II. ELECTORS")[-1]
    service = line("SERVICE", after="II. ELECTORS")[-1]
    electors = line("TOTAL", after="II. ELECTORS")[-1]
    if general + service != electors:
        raise SystemExit(f"{label}: electors {general} + {service} != {electors}")
    valid = line("VALID")[-1]
    head = next(i for i, r in enumerate(flat) if r[:2] == ["POLLING", "COUNTING"])
    day, month, year = re.split(r"[./]", flat[head + 1][0])
    year = int(year) + (1900 if len(year) == 2 else 0)
    poll_date = f"{year:04d}-{int(month):02d}-{int(day):02d}"
    start = next(i for i, r in enumerate(flat) if r[:2] == ["S.No.", "Candidate"])
    candidates, total = [], None
    for cells in rows[start + 1 :]:
        cells = [c for c in cells]
        filled = [c for c in cells if c]
        if filled and filled[0] == "Total":
            total = int(filled[1])
            continue
        if not filled or not filled[0].isdigit():
            continue
        serial, name, sex, party, votes = cells[:5]
        candidates.append(
            {"Serial": int(serial), "Candidate": name,
             "Sex": SEX.get({"M": "MALE", "F": "FEMALE"}.get(sex, sex)),
             "Party_Source": party, "Votes": int(votes)}
        )  # fmt: skip
    serials = [c["Serial"] for c in candidates]
    if serials != list(range(1, contested + 1)):
        raise SystemExit(f"{label}: rows {serials}, {contested} contested")
    added = sum(c["Votes"] for c in candidates)
    if added != valid or (total is not None and total != valid):
        raise SystemExit(f"{label}: rows add up to {added}, valid {valid}, {total}")
    name, kind = seat_name(re.sub(r"\((SC|ST)\)", r" (\1)", seat[2]))
    frame = pd.DataFrame(candidates).drop(columns="Serial")
    return frame.assign(
        State_Name=tcpd_state(state.title()),
        Constituency_No=int(seat[1]),
        Constituency_Name=name,
        Constituency_Type=kind,
        Electors=electors,
        Poll_Date=poll_date,
    )


READERS = {
    "eci_uncontested": read_eci_uncontested,
    "eci_bye_page": read_eci_bye_page,
    "eci_detailed_pdf": read_eci_detailed_pdf,
    "eci_form20_table": read_eci_form20_table,
    "eci_form20": read_eci_form20,
    "eci_detailed": read_eci_detailed,
    "azadecon": read_azadecon,
    "eci_report": read_eci_report,
    "india_votes_data": read_india_votes_data,
    "wayback": read_india_votes_data,
}
