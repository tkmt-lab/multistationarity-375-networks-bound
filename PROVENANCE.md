# Origins and verification boundary

The package is derived from the R023 study at research commit
`6d658ccfa1dd81d383aa808216ff051b73b9a21c` (2026-10-24). The original v1 PDF
had SHA256 `c8865c8edda87c60a8787a75d60ad2bd503ed1a15dc49c9d17904bd6e158f608`.
The public copy changes only the appendix's internal paths and adds an explicit
pending-DOI marker to the Adata reference. It has not undergone a new reader
review after those packaging edits. The preceding scientific v1 went through
three bounded AI reader passes, ending in acceptance; that is not human peer
review or a mathematical proof.

`provenance/source-files.json` gives hashes of the lab inputs used during
assembly. The manifest gives the resulting public files. Lab paths in that
provenance record are historical locators, not dependencies of the checks.

| Public material | Source within the R023 study | Adaptation |
| --- | --- | --- |
| Cramer records | `B/elimination-full/rows.jsonl` | Retain candidate IDs and certificate fields for B2; remove stability metadata and unused identity strings; rename `bound_nondegenerate` to `positive_root_bound` after verifying the nonzero specialization and branch conditions |
| Cramer checker | `B/check_charts.py` | Keep sparse Fraction algebra; remove 373-network stability outputs; reject uncertified parameter-only factors; require complete coverage in the runner |
| Resultant records | `independent-B/all-resultants.json`, `exceptional-resultants.json` | Combine 372 successes and three equation-transform successes; retain the exact proof expressions needed by the checker |
| Sylvester checker | `independent-B/sylvester_verifier.py` | Make each check callable; validate the retained variable and nonzero rational scalar; no resultant generation or factorization |
| B1 | `independent-B/structure_checker.py`, `structure-result.json` | Local input loader and output paths; reproduce the entire finite table |
| B3 t records | `B/extension/completion.json` | Retain fixed rates, search history, polynomial, root intervals and signs; recompute coordinate and Hurwitz enclosures rather than copying their unused interval outputs |
| B3 z records/checker | `independent-B/seven-reaction-result.json`, `seven_reaction_checker.py` | Bundle and rerun the first, article-used sample; retain all exact checked z outputs |
| Fraction routines | `independent-1/rational_polynomials.py` | Unchanged polynomial, Sturm and interval functions |

The verification team committed the resultant, structure and seven-reaction
work before comparison at `76a64cdbbfbb3d3e146baba9255806b012886ee9`.
Comparison was recorded at `73dcedb40`. Before that comparison, the verifier
received the pinned author input and the disclosed hypotheses and counts; it
did not read the producer's B code or outputs. Independence therefore concerns
the implementation and derivation, not a blinded prediction of the outcome.
The explicit Sylvester check used a second algorithm on those certificates.
The resultant development and Sylvester checker share SymPy arithmetic.

Assembly used both completed sets of evidence and added no independent-agent
review. The public Cramer checker uses Python Fraction arithmetic without
SymPy; the public Sylvester checker uses SymPy. Neither program is formally
verified. Successful execution checks the stated algebraic certificates; the
article explains why their identities, signs and fiber bounds imply the claims
over arbitrary positive real parameters.

The upstream input is fetched at a fixed revision and SHA256. It is not
bundled or relicensed. No transcribed replacement matrix table was needed:
the fixed upstream URL was accessible during local preparation. Hosted CI
availability remains to be observed after an authorized publication.
