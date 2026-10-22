# Team 20 provenance and contributions

## Project lineage

This repository is a fork of [AndrzejSzczepura/EvolutionaryComputing2026](https://github.com/AndrzejSzczepura/EvolutionaryComputing2026), the 2026 Evolutionary Computing course fork of [ARIEL](https://github.com/ci-group/ariel). ARIEL was developed by the Computational Intelligence Group at Vrije Universiteit Amsterdam. Its copyright notice names Jacopo Michele di Matteo and Ioannis Grigoriadis; the existing `LICENSE` grants GPL version 3 or later.

The upstream `ariel` package name, author metadata, license file and source notices remain intact. The inherited framework description and citation information are available in [README.upstream.md](../README.upstream.md). ARIEL's publications are upstream research, not Team 20 publications.

## What the Git history establishes

At the cleanup baseline `ec15baa1736ceef7951a88a61e4c1d2fa4178f3a`, `main` was 60 commits ahead of the course baseline `a435b192066d258096eba3f43f91c43b74cf11fe`, with no commits behind it. These counts include merges and maintenance changes and are not a measure of contribution share.

| Recorded author | Commits beyond the course baseline | Examples visible in history |
| --- | ---: | --- |
| Mich | 20 | Crossover, selection refinements, dashboard genotype vectors, process-based evaluation, result archives and analysis. |
| TimG2805 | 21 | Evolution strategies, recombination/mutation, experiment output, notebook and database/plotting helpers. |
| Tim Gerling | 15 | EA setup, algorithm/reproduction/selection work and controller setup. |
| Levien | 2 | Selection prototype and robot-body changes. |
| levienb | 1 | Controller inputs. |
| Kelly | 1 | Mutation prototype. |

Mich's commits are attributed by GitHub to [ObviouslyNotMich](https://github.com/ObviouslyNotMich); this portfolio identifies that work as Michal Kozdon's. Other names are reproduced as recorded, without assuming that different author aliases represent distinct people or merging their identities.

Representative Michal contributions:

- [Subtree crossover and offspring generation](https://github.com/ObviouslyNotMich/EvolutionaryComputing2026-team20/commit/f20d5b0).
- [Survivor selection](https://github.com/ObviouslyNotMich/EvolutionaryComputing2026-team20/commit/6540ae4) and [later selection refinement](https://github.com/ObviouslyNotMich/EvolutionaryComputing2026-team20/commit/9f6410d).
- [Dashboard genotype-vector support and tests](https://github.com/ObviouslyNotMich/EvolutionaryComputing2026-team20/commit/4bacfa1).
- [Process-based controller evaluation](https://github.com/ObviouslyNotMich/EvolutionaryComputing2026-team20/commit/7184f54).
- [First result archives](https://github.com/ObviouslyNotMich/EvolutionaryComputing2026-team20/commit/b3449be), [additional seeds](https://github.com/ObviouslyNotMich/EvolutionaryComputing2026-team20/commit/6fe1814), and [analysis work](https://github.com/ObviouslyNotMich/EvolutionaryComputing2026-team20/commit/ec15baa).

The current analysis helpers were introduced by [TimG2805](https://github.com/ObviouslyNotMich/EvolutionaryComputing2026-team20/commit/f3b8d21). Earlier prototypes may have been superseded: an experimental Optuna/gait-search change in the history is not advertised as a supported current feature.

## Results and retained material

`assignments/assignment_1/data.zip` contains 21 SQLite databases in the `sts`, `hcc`, `random` and `combined` folders. Six Assignment 2 ZIP archives each contain one `db_n_<seed>.db` result database. The [run guide](TEAM20_REPRODUCIBILITY.md) describes the available results and missing comparison inputs. Archive names alone do not certify the exact source revision or experimental configuration of a run.

The cleanup retains the experiment archives, target-body JSON, notebooks (including saved output), course HTML, upstream documentation assets, license notices, original commits and four pre-existing branches. It stops tracking `.codebase-index/` and `MJDATA.TXT`, which are generated local artifacts. Historical copies of those files remain in Git; the cleanup neither erases their contents nor reduces historical clone size.

## Publication scope

On 22 October 2026, the repository owner confirmed authority/team agreement for continued public publication and a later move to ClearlyNotMich; course/university permission for the solutions and included teaching/assessment materials; and redistribution permission for committed results/assets including retained history. Existing GPL terms and upstream/team credit remain in place.

The course briefs describe assessment constraints, including restrictions on changes to `src/ariel`. This repository also contains historical dashboard adaptations. The portfolio describes the repository's development history; it does not claim that every file here formed part of an assessed submission or certify compliance with assessment rules.
