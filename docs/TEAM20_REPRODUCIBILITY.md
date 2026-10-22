# Reproducing and inspecting Team 20 work

Run commands from the repository root unless stated otherwise. Start with the lightweight analysis checks in the [README](../README.md); they do not launch a simulation or require the full ARIEL environment.

## Full environment

```bash
uv sync --locked
```

The repository pins Python 3.12.9 in `.python-version`; `uv.lock` records the dependency versions. The manifest includes PyTorch, MuJoCo/MJX, notebooks and visualization packages, so a full install can be large. `uv sync --locked --dry-run` can preview it. Platform-specific graphics and accelerator support still need a working local driver/runtime.

The inherited README's brain-evolution example requires the optional `evotorch` extra: install it with `uv sync --locked --extra evotorch` if using that upstream example. The package's declared `ariel` console entry point refers to a module absent from this snapshot; use the explicit script commands below.

## Protect previous runs

ARIEL's `EASettings` defaults to deleting an existing output database with the same name. Set its environment override before launching a new experiment:

```bash
export DB_HANDLING=halt
```

PowerShell equivalent:

```powershell
$env:DB_HANDLING = "halt"
```

This makes the EA engine raise `FileExistsError` for an existing database. Keep each experiment's output in a separate working copy/directory, or move completed databases to a clearly labeled archive before repeating a configuration. Do not delete an old run merely to make a command succeed. This setting protects the EA database; it is not a general no-overwrite switch for plots, videos or other upstream scripts.

`__data__/` and extracted databases under `assignments/assignment_2/results/` are ignored. Committed ZIP archives remain the preserved experiment records.

## Assignment 1: body morphology

```bash
uv run --locked assignments/assignment_1/A1_template_2026.py
```

The template-named entry point runs `Assignment1EA.evolve()` and then renders its best body. The checked-in algorithm uses a population of 75, 100 generations, at most 20 modules, tournament size 4, local seed 21 and `P_MUTATION = 1.0`. Fitness is minimized: mean weighted tree-edit distance to five target morphologies plus its standard deviation. It writes `__data__/database.db`; the default rendering mode is `frame`, which needs a functioning MuJoCo rendering backend.

Configuration remains in `assignments/assignment_1/algorithm.py`; this script has no command-line experiment configuration. For a new research run, record the source revision, constants, all random generators and environment. The local Python/NumPy seeds do not by themselves establish that every ARIEL random generator was seeded consistently.

`A1_ea.py` is an earlier incomplete prototype, not the entry point. `random_evolve()` currently evaluates the initial population and then repeats the evaluation operation without generating new candidates. Do not use it as a validated equal-budget random-search baseline.

## Assignment 2: controller evolution

Inspect options without starting an experiment:

```bash
uv run --locked assignments/assignment_2/A2_template_2026.py --help
```

Full runs, after setting `DB_HANDLING=halt`:

```bash
uv run --locked assignments/assignment_2/A2_template_2026.py --seed 21 --mutation n --workers 2
uv run --locked assignments/assignment_2/A2_template_2026.py --seed 21 --mutation one --workers 2
uv run --locked assignments/assignment_2/A2_template_2026.py --seed 21 --random True --workers 2
```

The current parser expects a value after `--random` and uses Python's `bool` conversion; omit the option to disable random search. Passing the text `False` would still enable it. Use a positive worker count appropriate for the machine.

These are full experiments: 150 generations, 15 initial individuals, 105 candidates per subsequent generation and 15 seconds of simulated time per evaluation. Evaluations run headlessly in separate processes, but the script opens an interactive viewer for the best controller at the end. A display is therefore required to complete the default entry point; no headless end-to-end run is claimed here.

Output names are `__data__/db_n_<seed>.db`, `db_one_<seed>.db` or `db_random_<seed>.db`. The current implementation uses a snake body on `SimpleFlatWorld`, target `[-3.0, 0.0, 0.1]`, and minimizes `fitness_direct_path`: change in distance to target plus a penalty for excess path length. Body, fitness and baseline settings changed during development. Archive names alone cannot establish that a database used today's configuration.

## Available saved results

| Location | Contents | Reproduction limits |
| --- | --- | --- |
| `assignments/assignment_1/data.zip` | 21 SQLite databases in `sts`, `hcc`, `random` and `combined` directories; about 270 MB uncompressed. | Historical outputs; the baseline behavior and exact generating revision need verification before comparing conditions. |
| `assignments/assignment_2/results/db_n_*.db.zip` | Six SQLite databases, seeds 21, 42, 61, 84, 105 and 126; about 130 MB per database uncompressed. | Only the per-weight-step-size condition is committed. |

List an archive without extracting it:

```bash
uv run --no-project --python 3.12 python -m zipfile -l assignments/assignment_2/results/db_n_21.db.zip
```

To inspect one saved run, this Python snippet copies only its expected member into an ignored output folder and refuses to overwrite an existing file:

```python
from pathlib import Path
import shutil
import zipfile

destination = Path("__data__/n_results/db_n_21.db")
destination.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile("assignments/assignment_2/results/db_n_21.db.zip") as archive:
    with archive.open("db_n_21.db") as source, destination.open("xb") as target:
        shutil.copyfileobj(source, target)
```

With the full environment, read its summary from the repository root:

```bash
uv run --locked python -c "from assignments.assignment_2.data_analysis.plots import get_mean_fitness; print(get_mean_fitness('__data__/n_results/db_n_21.db').tail())"
```

The analysis helper functions open input databases read-only. `merge_individual_databases()` produces a new `individual` table with fresh IDs and a `source_db` column; it refuses to overwrite an existing target and removes its new output if the merge fails. It does not copy unrelated tables and is not a lossless database-backup format. Keep original databases and archives.

The notebooks were written for a working directory of `assignments/assignment_2/` and expect `__data__/one_results`, `n_results` and `random_results`. The later notebook also references `one_results.zip`, `n_results.zip` and `random_results.zip`, none of which is committed under those names. Its first merge cells run before the later extraction cell. Do not expect “Run all” to reproduce every chart from a fresh clone. Supply the missing condition data and verify configurations/evaluation budgets before reporting a comparison; current saved notebook output is retained as historical evidence.

## Validation scope

The cleanup checks cover database merge failure handling and read-only fitness summaries with temporary fixtures, plus compatibility with a committed result database. Full morphology/controller experiments, all historical notebooks and GPU/GUI behavior have not been rerun. The existing framework test suite remains available separately via `uv run --locked python -m pytest tests/unit tests/test_geno_vec.py`; passing focused analysis checks does not imply that this entire suite passes.

The cleanup leaves algorithm behavior, simulation parameters, dependency lock, result archives and upstream framework code unchanged. Entry-point descriptions were corrected to match their existing full-experiment behavior.
