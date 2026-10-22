# Evolutionary Computing — Team 20

Master's coursework investigating **robot-body evolution** and **neural-controller evolution in simulation**, using Python, MuJoCo and the ARIEL framework. The repository contains the team's assignment implementations, saved experiment databases and analysis notebooks.

This is a collaborative course fork of [AndrzejSzczepura/EvolutionaryComputing2026](https://github.com/AndrzejSzczepura/EvolutionaryComputing2026), built on [ARIEL](https://github.com/ci-group/ariel) from the Computational Intelligence Group at Vrije Universiteit Amsterdam. The framework, course templates and team work are credited separately below.

## Project contents

| Area | Implementation | What it investigates |
| --- | --- | --- |
| Robot morphology | [Assignment 1](assignments/assignment_1/algorithm.py) | Tree-encoded bodies, subtree variation and selection; fitness combines mean and standard deviation of weighted tree-edit distance to five target bodies. |
| Controller evolution | [Assignment 2](assignments/assignment_2/A2_template_2026.py) | Neural-network weights optimized with self-adaptive evolution strategies, single or per-weight mutation step sizes, recombination and offspring-only selection. Evaluations run in separate processes. |
| Experiment analysis | [Analysis helpers](assignments/assignment_2/data_analysis/) and [notebooks](assignments/assignment_2/) | SQLite result aggregation, per-generation fitness summaries and plots. |
| Supporting work | [Genotype-vector tests](tests/test_geno_vec.py) | Checks for the team's adaptation of ARIEL's dashboard representation. |

The committed Assignment 2 archives contain **six per-weight-step-size runs**, for seeds `21`, `42`, `61`, `84`, `105` and `126`. They do not include the one-step-size and random-search archives referenced by the comparison notebook. Saved output is evidence of past runs, not a newly reproduced performance benchmark. See [results and reproduction limits](docs/TEAM20_REPRODUCIBILITY.md).

## Contributions and upstream credit

**Michal Kozdon** (`ObviouslyNotMich` in the existing Git history) contributed subtree-crossover work, survivor-selection refinements, dashboard genotype-vector support and tests, parallel evaluation work, result archives and analysis experiments. These contributions overlap with subsequent team revisions; they do not imply sole ownership of those components.

The history also records contributions under **Tim Gerling**, **TimG2805**, **Levien**, **levienb** and **Kelly**. Their work includes the evolutionary algorithms, controller inputs, mutation/recombination, result generation and analysis helpers. [Contribution notes](docs/TEAM20_PROVENANCE.md) link representative commits and explain the review baseline.

ARIEL and the course materials remain upstream work. The [inherited ARIEL README](README.upstream.md) is retained as a reference, including its author and citation information; its general framework examples are separate from the Team 20 workflow.

## Start with the analysis checks

With [uv](https://docs.astral.sh/uv/) installed, clone this fork:

```bash
git clone https://github.com/ObviouslyNotMich/EvolutionaryComputing2026-team20.git
cd EvolutionaryComputing2026-team20
```

Run the focused database/plotting tests without installing the full robotics stack:

```bash
uv run --no-project --python 3.12 --with pytest==8.4.2 --with pandas==2.3.3 --with matplotlib==3.10.7 python -m pytest tests/test_assignment2_analysis.py -q
```

For the complete environment, use `uv sync --locked`. It follows `.python-version` and `uv.lock` and installs a substantial simulation, notebook and visualization dependency set. See the [run guide](docs/TEAM20_REPRODUCIBILITY.md) before launching an assignment: the entry points run full experiments, and output databases can otherwise be replaced by ARIEL's default behavior.

## Scope and limitations

- This is simulation coursework; hardware deployment and benchmark superiority are not claimed.
- The original notebooks expect local result folders and some archives that are absent from this snapshot. Their saved outputs should be interpreted with those limits.
- Assignment 1's current `random_evolve()` evaluates its initial population but does not resample it in later generations. Its random-search baseline needs review before a new comparison is reported.
- Generated code-search caches and the MuJoCo state dump are ignored and removed from the current tree. Experiment archives and all previous Git history are retained.

## License

The existing [LICENSE](LICENSE) states **GNU GPL version 3 or later** and credits Jacopo Michele di Matteo and Ioannis Grigoriadis for ARIEL. Its text and notices are preserved. This cleanup does not relicense upstream or team work. See [provenance](docs/TEAM20_PROVENANCE.md) for the distinction between the framework, teaching materials and team additions.
