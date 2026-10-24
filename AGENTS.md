# Entry point for a computational reader

Read README.md, claims.json, PROVENANCE.md and VERIFICATION-RECORD.md.
Run the exact commands in README.md from this directory. Use Python without
optimization; assertions are part of the checks. Generated files belong in
ignored work/. Do not commit the fetched upstream JSON or a local environment.

The main claim is a bound on distinct positive equilibria of the fixed 375
networks at all positive rates, including degenerate equilibria. The original
enumeration, reported 373/2 stability classification, exceptional identifiers
and Lemma 3 are Tang–Zhang's work. B1 is post-selected and finite. B3 is one
seven-reaction family, with one rational witness bundled here.

Keep exact polynomial checks, the article's mathematical argument, historical
independent implementation, and post-comparison package assembly distinct.
No formal verification, human peer review, priority or new 373-network
stability certification is established by this repository.

The public repository and DOI have not been created. A-DOI-PENDING marks the
companion citation to fill in README.md and paper/paper-v1.tex before release.
Publication and outside communication require the author's instruction.

After an intentional file change, review the diff, run
`python3 -B tools/update_manifest.py`, and rerun `python3 -B verify.py` in the
documented environment. Do not update hashes to conceal an unexplained
mismatch. The manifest checks file identity, not authenticity or mathematics.
