# A certified three-equilibrium bound for 375 fixed quadratic zero-one reaction networks

Each of the 375 fixed networks in Tang and Zhang's candidate file has at most
three distinct positive equilibria for every choice of strictly positive rate
constants. The bound includes degenerate equilibria. This package contains the
[article v1](paper/paper-v1.pdf), exact algebraic certificates, and two ways to
check the reductions.

The input has three species, six reactions, reactant molecularity at most two,
zero-one reactant and product complexes, and stoichiometric rank three. The
statement concerns this fixed list. It does not certify a new enumeration of
all networks in that class.

Version 1.0.0 is prepared locally; no public archive or DOI is asserted.

## Reproduce the checks

Python 3.11 or later is required. The full check uses SymPy 1.14.0 and its
mpmath dependency; all calculations used for the verdicts are exact. Run from
the repository root on macOS or Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -B tools/fetch_input.py
.venv/bin/python -B verify.py
```

The input download is about 396 kB. It is saved in ignored `work/input/` and
checked against the fixed SHA256 below. An existing file with the wrong hash
is rejected. The verifier checks the package manifest before reading the
certificates. It writes `work/verification.json` and exits with a nonzero code
on a failed check. Its default time limit is 300 seconds on Unix systems.
Do not use Python's `-O` or `-OO` flags: assertions are part of the checks.

The Cramer route and the B1 table also run with the standard library alone:

```sh
python3 -B tools/fetch_input.py
python3 -B verify.py --stdlib-only
```

That command reports `PASS_STDLIB_SUBSET`; it does not run the Sylvester route
or the seven-reaction example. After the input has been downloaded, both modes
can run offline. The [verification record](VERIFICATION-RECORD.md) describes
the checks actually run. The GitHub Actions workflow runs the full check;
preparing that workflow does not establish that hosted CI has run.

## What the files establish

| Item | Result | Evidence |
| --- | --- | --- |
| B2, main bound | At most three distinct positive equilibria for each fixed network, at all positive rates | 375 Cramer reductions; 375 independently obtained resultant reductions, rechecked by explicit Sylvester determinants |
| B1, finite observation | No inflow and an acyclic unimolecular net-production graph select exactly 33449 and 239089 within the list | A table recomputed from the upstream reactant and stoichiometric matrices; two cycle tests |
| B3, seven-reaction family | Adding X3 → 0 to network 33449 gives at most three positive equilibria and at most one exponentially stable positive equilibrium for all seven positive rates | Symbolic elimination identities and the cubic argument in the article; one rational example rechecked in two coordinates |

The Cramer certificates contain 272 cubic and 103 quartic residuals. Each
quartic has a strictly negative leading coefficient and a strictly positive
constant term. A coefficient-sign check also proves that no residual vanishes
identically after any positive specialization. A strict-sign witness in the
denominator or a Cramer numerator rules out a lost positive branch. The
checker verifies every removed factor and the polynomial identities from the
original reaction matrices.

The second B2 route verifies the recorded eliminations using explicit
Sylvester determinants of size at most four. It certifies at most one positive
point in each eliminated fiber and bounds the retained roots by Descartes'
rule. Its checker does not call `resultant()` or `factor_list()`. The historical
resultant route was developed before seeing the producer's reductions; this
package was assembled later with both available. Assembly is not a new blind
verification. [PROVENANCE.md](PROVENANCE.md) records that boundary.

B1 was selected after a twelve-network pilot and inspection of the eight
networks without inflow. It is a post-selected observation, not a predictive
test or a general theorem about stability. Among networks with inflow, 255
have an acyclic graph and 112 have a cycle. Among those without inflow, the
counts are two and six.

B3 uses rates `(a,b,c,d,e,f,h) = (109/32768,235/256,1/2,1/2,1/2,1/2,1/65536)`.
Exact Sturm counts give three simple positive equilibria. Rational interval
checks of the Jacobian give one exponentially stable equilibrium and two
unstable equilibria. The added rate came from a recorded dyadic search ladder;
the example is a fixed witness. The global family argument and its checked
identities are distinct from that single example.

## Fixed upstream input and attribution

The 375-network list, the reported 373/2 stability classification, the two
exceptional identifiers, and the determinant criterion in Lemma 3 belong to
Xiaoxian Tang and Jiandong Zhang, [*The Ubiquity of Three Steady States: Minimal
Multistable Zero-One Reaction Networks*, arXiv:2608.01116v1](https://arxiv.org/abs/2608.01116v1).
Their [source repository](https://github.com/zjdong-sudo/paper-multistability-results)
supplies the input used here:

- Revision: `323360df12c0787f9bbf7f223a6229b98233be39`.
- File: `results/375_multistable_networks.json` (395599 bytes).
- SHA256: `517d1f16f890159185f5384fa2ab089ec4d270e03efe31161ed29489121e252c`.
- [Download the pinned file](https://raw.githubusercontent.com/zjdong-sudo/paper-multistability-results/323360df12c0787f9bbf7f223a6229b98233be39/results/375_multistable_networks.json).

The raw input is excluded because its license has not been confirmed. The
fetch tool obtains it directly from upstream. `candidate_index` identifies a
network; `Y` contains reactants, `N` is the stoichiometric matrix, and `Y+N`
contains products. Matrix rank is calculated from `N`. The input's `rank`
field is a list position, and null stability fields are not evidence.

This package does not reverify the original enumeration, the existence
witnesses for all 375 networks, or the stability classification of the 373
remaining networks. It does not decide nonlinear stability at degenerate
points, boundary dynamics, or global dynamics. The programs are not formally
verified; no proof-assistant theorem, human peer review, or priority claim is
made. The article credits the relevant reduction and inheritance literature.

## Contents and citation

- `paper/`: article v1, with the appendix paths updated for this package.
- `certificates/cramer.jsonl`: one chart and its sign evidence for each network.
- `certificates/resultants.json`: the 372 direct and three equation-transform reductions.
- `certificates/structure.json`: the B1 table and definitions.
- `certificates/seven-reaction-*.json`: the fixed B3 rates and exact records.
- `checkers/`: exact checkers; `verify.py` runs them and mutation controls.
- `claims.json`, `manifest.json`, `provenance/`: claim scopes, file hashes and origins.

Please cite the article and this exact package version using
[CITATION.cff](CITATION.cff), and cite Tang and Zhang for the original list and
classification. The article's scientific body is unchanged from the reviewed
v1; only the appendix paths and the companion-publication citation were edited.

The related collection by Tatsuhiko Takimoto, *Stability certificates for two
exceptional reaction networks*, version 1.0.0 (2026), gives complete
positive-branch reductions and exact stability certificates for the two
exceptional networks 33449 and 239089. Its version DOI is
[10.5281/zenodo.23659209](https://doi.org/10.5281/zenodo.23659209); the
[all-versions DOI](https://doi.org/10.5281/zenodo.23659208) is
10.5281/zenodo.23659208. The source release is
[`tkmt-lab/exception-networks-stability-certificates` v1.0.0](https://github.com/tkmt-lab/exception-networks-stability-certificates/releases/tag/v1.0.0).
These identifiers refer to that two-network collection. This 375-network
package has no DOI yet.

Original prose and derived certificates: CC BY 4.0. Code: Apache 2.0. Full texts
and the upstream-data exclusion are in [LICENSE](LICENSE).
