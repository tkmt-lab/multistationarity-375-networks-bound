# Verification record

Local preparation date: 2026-10-24. This record concerns version 1.0.0 of the
certificate package, before publication.

## Checks completed before the clean-clone run

The pinned upstream input was downloaded directly from the recorded raw URL.
Its 395599 bytes matched SHA256
`517d1f16f890159185f5384fa2ab089ec4d270e03efe31161ed29489121e252c`.
No raw JSON or transcribed replacement matrices are distributed.

The initial complete run passed in 15.097 seconds on the preparation Mac, using
Python 3.14.7 and SymPy 1.14.0. It covered all 375 Cramer certificates, all 375
resultant certificates through explicit Sylvester determinants, the full B1
table, and the fixed B3 example in both t and z coordinates. All six corruption
controls were rejected: a changed upstream byte, changed Cramer denominator,
changed residual, reversed denominator sign, changed Sylvester root factor,
and reversed removed-factor sign.

The final clean-clone run, environment, resource measurements and commit are
recorded below after completion. The full check is deterministic apart from
timing and environment metadata; it never samples positive rate vectors as a
substitute for the symbolic identities and coefficient-sign checks.

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
