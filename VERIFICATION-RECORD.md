# Verification record

Local preparation date: 2026-10-24. This record concerns version 1.0.0 of the
certificate package, before publication.

## Clean-clone check

A new local clone of commit
`03b1b73e39d3bea3cc9f311c1a3ba17c65cc2033` was made with `git clone --no-hardlinks`.
It began with no upstream input and a new Python virtual environment. The
documented requirements were installed into that environment: Python 3.14.7,
SymPy 1.14.0 and mpmath 1.3.0, on macOS. One command ran at a time with nice 10.

The pinned upstream input was downloaded directly from the recorded raw URL.
Its 395599 bytes matched SHA256
`517d1f16f890159185f5384fa2ab089ec4d270e03efe31161ed29489121e252c`.
No raw JSON or transcribed replacement matrices are distributed.

| Command, using the clone's Python | Exit | Measured wall time |
| --- | --- | --- |
| `python -B tools/fetch_input.py` | 0 | 0.307 s |
| `python -B verify.py --stdlib-only` | 0 | 0.181 s |
| `python -B verify.py` | 0 | 14.569 s |

The full verifier's internal elapsed time was 14.436 s. Maximum child RSS
across these commands was 88276992 bytes (about 88 MB), reported by macOS
`getrusage`. Git remained clean after the checks.

The run covered all 375 Cramer certificates, all 375 resultant certificates
through explicit Sylvester determinants, the full B1 table, and the fixed B3
example in both t and z coordinates. Degrees agree network by network; the
retained coordinate differs in 79 cases. The three special equation-transform
IDs are 48328, 74814 and 100108. The three B3 root pairs were matched by the
exact coordinate map, a one-root Sturm count on each interval union, and all
four Hurwitz signs.

All six corruption controls were rejected: a changed upstream byte, changed
Cramer denominator, changed residual, reversed denominator sign, changed
Sylvester root factor, and reversed removed-factor sign. A separate `python
-O verify.py` run was rejected with exit code 1 before verification.

Exact machine-readable outputs are in
`provenance/clean-clone-verification.json`, `clean-clone-stdlib.json` and
`clean-clone-audit.json` (all under `provenance/`). Their source commit predates
the addition of these records. The later documentation-and-record commit
changes no checker, certificate or scientific manuscript content.

The full check is deterministic apart from timing and environment metadata;
it never samples positive rate vectors as a substitute for the symbolic
identities and coefficient-sign checks. The 7-page PDF was rebuilt with
Tectonic 0.17.0, with no TeX warnings, and all rendered pages were inspected.
Its source body through the references before Adata is identical to the
reviewed lab v1. `provenance/paper-qa.json` gives hashes and the edit boundary.
The repository's writing diagnostic found no advisory issues in README.md;
that diagnostic does not assess mathematical truth or authorship.

## Assurance boundary

The Cramer route uses sparse rational polynomial arithmetic from Python's
standard library. The Sylvester route uses SymPy polynomial arithmetic and
permutation determinants, without calling its resultant or factorization
routines. B3 uses exact Sturm sequences, rational interval arithmetic and
Jacobian signs; its z outputs are compared in full with the bundled record.
No floating-point tolerance determines a verdict.

The mathematical implications of the identities and signs are proved in the
article. These programs have not been formally verified. The historical
independent derivation preceded comparison; public assembly saw both outputs.
There was no new independent agent review during packaging. See PROVENANCE.md.

The GitHub Actions workflow is prepared for Python 3.11 on Linux. A local
macOS check does not establish that hosted CI has run. The original 375-network
enumeration, existence witnesses for all 375 networks and the 373-network
stability classification are outside this verification.
