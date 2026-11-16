# Working on this data repository

This is a point-in-time data collection. Follow the [data-repository policy](https://github.com/soodoku/data-repos#maintenance-policy).

- Inputs are pinned by URL and SHA-256 in `data/source.json`. Fetch them with `make fetch`; do not edit hashes to make a build pass.
- Every TCPD column stays in TCPD's order. Fill a column only with TCPD's quantity; if a rule cannot reproduce TCPD's own values (`make validate`), leave the column empty and say why.
- New party matches go in `data/party_aliases.csv` with the reason, after checking them by eye.
- When outputs change, check row counts, seat counts and hashes in `MANIFEST.json`.
- Do not add blanket CI, pre-commit, version matrices or package-release scaffolding.
