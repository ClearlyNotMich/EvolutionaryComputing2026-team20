"""Small SQLite fixtures for the assignment 2 merge and plotting helpers."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from typing import TYPE_CHECKING

import matplotlib as mpl
import pandas as pd
import pytest

mpl.use("Agg")

from assignments.assignment_2.data_analysis import plots
from assignments.assignment_2.data_analysis.database_ops import (
    merge_individual_databases,
)
from assignments.assignment_2.data_analysis.plots import (
    get_max_fitness,
    get_mean_fitness,
    get_min_fitness,
    plot_fitness,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable
    from pathlib import Path


SCHEMA = """
CREATE TABLE individual (
    id INTEGER NOT NULL PRIMARY KEY,
    time_of_birth INTEGER NOT NULL,
    fitness_ FLOAT,
    genotype_ JSON
)
"""


def _make_database(
    path: Path,
    rows: Iterable[tuple[int, int, float | None, str]] = (),
    schema: str = SCHEMA,
) -> Path:
    """Create a small database fixture with the supplied records.

    Returns
    -------
    Path
        The created database path.
    """
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute(schema)
        if rows:
            connection.executemany(
                "INSERT INTO individual VALUES (?, ?, ?, ?)",
                rows,
            )
    return path


def _read_rows(path: Path) -> list[tuple[int, int, float | None, str, str]]:
    """Read merged records without modifying the output database.

    Returns
    -------
    list[tuple[int, int, float | None, str, str]]
        Merged rows in ID order.
    """
    with closing(
        sqlite3.connect(path.as_uri() + "?mode=ro", uri=True),
    ) as connection:
        return connection.execute(
            "SELECT * FROM individual ORDER BY id",
        ).fetchall()


@pytest.mark.parametrize(
    "reader",
    [get_min_fitness, get_max_fitness, get_mean_fitness],
)
def test_missing_statistics_input_is_not_created(
    tmp_path: Path,
    reader: Callable[[Path], pd.DataFrame],
) -> None:
    """Refuse missing input without creating an empty SQLite file."""
    missing = tmp_path / "missing.db"
    with pytest.raises(FileNotFoundError):
        reader(missing)
    assert not missing.exists()


def test_missing_merge_input_creates_no_input_or_output(tmp_path: Path) -> None:
    """Keep all inputs and outputs untouched when a source is missing."""
    valid = _make_database(tmp_path / "first.db", [(17, 0, 1.0, "{}")])
    original = valid.read_bytes()
    missing = tmp_path / "missing.db"
    target = tmp_path / "merged.db"
    with pytest.raises(FileNotFoundError):
        merge_individual_databases([valid, missing], target)
    assert not missing.exists()
    assert not target.exists()
    assert valid.read_bytes() == original


@pytest.mark.parametrize("use_source_as_target", [False, True])
def test_existing_target_and_source_are_unchanged(
    tmp_path: Path,
    *,
    use_source_as_target: bool,
) -> None:
    """Refuse overwriting either an existing result or a source database."""
    source = _make_database(tmp_path / "run.db", [(99, 0, 4.0, "{}")])
    source_bytes = source.read_bytes()
    target = source if use_source_as_target else tmp_path / "existing.db"
    if not use_source_as_target:
        target.write_bytes(b"existing result must survive")
    target_bytes = target.read_bytes()
    with pytest.raises(FileExistsError):
        merge_individual_databases([source], target)
    assert target.read_bytes() == target_bytes
    assert source.read_bytes() == source_bytes


def test_valid_merge_assigns_fresh_ids_and_preserves_provenance(
    tmp_path: Path,
) -> None:
    """Merge overlapping input IDs while retaining records and source names."""
    first = _make_database(
        tmp_path / "first.db",
        [(50, 0, 3.0, '{"shape": "a"}'), (70, 1, None, "{}")],
    )
    second = _make_database(tmp_path / "second.db", [(50, 0, 9.0, "[]")])
    original = {path: path.read_bytes() for path in (first, second)}
    target = tmp_path / "merged.db"

    merge_individual_databases([first, second], target)

    assert _read_rows(target) == [
        (1, 0, 3.0, '{"shape": "a"}', "first.db"),
        (2, 1, None, "{}", "first.db"),
        (3, 0, 9.0, "[]", "second.db"),
    ]
    assert all(
        path.read_bytes() == content for path, content in original.items()
    )


def test_late_schema_failure_leaves_no_partial_output(tmp_path: Path) -> None:
    """Remove the new target if a later source has an incompatible schema."""
    first = _make_database(tmp_path / "first.db", [(1, 0, 2.0, "{}")])
    second = _make_database(
        tmp_path / "second.db",
        schema=SCHEMA.replace("fitness_ FLOAT", "fitness_ TEXT"),
    )
    original = {path: path.read_bytes() for path in (first, second)}
    target = tmp_path / "merged.db"

    with pytest.raises(ValueError, match="Incompatible individual schema"):
        merge_individual_databases([first, second], target)

    assert not target.exists()
    assert not list(tmp_path.glob("merged.db*"))
    assert all(
        path.read_bytes() == content for path, content in original.items()
    )


def test_late_insert_failure_rolls_back_and_removes_new_output(
    tmp_path: Path,
) -> None:
    """Roll back earlier records when a later insertion fails."""
    first = _make_database(
        tmp_path / "first.db",
        [(1, 0, 2.0, "{}")],
        schema=SCHEMA.replace(
            "fitness_ FLOAT",
            "fitness_ FLOAT CHECK (fitness_ >= 0)",
        ),
    )
    second = _make_database(tmp_path / "second.db", [(1, 0, -1.0, "{}")])
    original = {path: path.read_bytes() for path in (first, second)}
    target = tmp_path / "merged.db"
    with pytest.raises(sqlite3.IntegrityError):
        merge_individual_databases([first, second], target)
    assert not target.exists()
    assert all(
        path.read_bytes() == content for path, content in original.items()
    )


@pytest.mark.parametrize(
    "schema",
    [
        SCHEMA.replace("INTEGER NOT NULL PRIMARY KEY", "INT PRIMARY KEY"),
        SCHEMA.replace(
            "INTEGER NOT NULL PRIMARY KEY",
            "INTEGER PRIMARY KEY DESC",
        ),
        SCHEMA + " WITHOUT ROWID",
        SCHEMA.replace("genotype_ JSON", "source_db TEXT"),
    ],
)
def test_unsupported_primary_keys_and_existing_provenance_are_rejected(
    tmp_path: Path,
    schema: str,
) -> None:
    """Reject schemas that cannot receive fresh IDs and provenance."""
    source = _make_database(tmp_path / "source.db", schema=schema)
    original = source.read_bytes()
    target = tmp_path / "merged.db"
    with pytest.raises(ValueError, match=r"single INTEGER|source_db"):
        merge_individual_databases([source], target)
    assert not target.exists()
    assert source.read_bytes() == original


def test_no_sources_is_an_explicit_error(tmp_path: Path) -> None:
    """Report an empty source list without creating a target."""
    target = tmp_path / "merged.db"
    with pytest.raises(ValueError, match="No source databases"):
        merge_individual_databases([], target)
    assert not target.exists()


@pytest.mark.parametrize(
    ("reader", "column", "expected"),
    [
        (get_min_fitness, "min_fitness", [2.0, -2.0]),
        (get_max_fitness, "max_fitness", [8.0, 4.0]),
        (get_mean_fitness, "mean_fitness", [5.0, 1.0]),
    ],
)
def test_statistics_ignore_null_fitness_and_group_by_birth_generation(
    tmp_path: Path,
    reader: Callable[[Path], pd.DataFrame],
    column: str,
    expected: list[float],
) -> None:
    """Aggregate evaluated records by generation and preserve the source."""
    source = _make_database(
        tmp_path / "run?#.db",
        [
            (1, 2, 4.0, "{}"),
            (2, 0, 8.0, "{}"),
            (3, 0, None, "{}"),
            (4, 2, -2.0, "{}"),
            (5, 0, 2.0, "{}"),
            (6, 1, None, "{}"),
        ],
    )
    original = source.read_bytes()
    result = reader(source)
    pd.testing.assert_frame_equal(
        result,
        pd.DataFrame({"generation": [0, 2], column: expected}),
    )
    assert source.read_bytes() == original


@pytest.mark.parametrize(
    ("reader", "column"),
    [
        (get_min_fitness, "min_fitness"),
        (get_max_fitness, "max_fitness"),
        (get_mean_fitness, "mean_fitness"),
    ],
)
def test_all_null_fitness_returns_empty_frame_with_stable_columns(
    tmp_path: Path,
    reader: Callable[[Path], pd.DataFrame],
    column: str,
) -> None:
    """Return predictable empty result columns when no fitness is recorded."""
    source = _make_database(tmp_path / "run.db", [(1, 0, None, "{}")])
    result = reader(source)
    assert result.empty
    assert list(result.columns) == ["generation", column]


def test_plot_uses_requested_series_and_labels_without_changing_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Plot only the requested curve and label while preserving its source."""
    source = _make_database(tmp_path / "run.db", [(1, 0, 2.0, "{}")])
    original = source.read_bytes()
    monkeypatch.setattr(plots.plt, "show", lambda: None)
    try:
        plot_fitness([source], labels=["Trial"], minimum=False, maximum=False)
        lines = plots.plt.gca().get_lines()
        assert len(lines) == 1
        assert lines[0].get_label() == "Mean: Trial"
        assert list(lines[0].get_ydata()) == [2.0]
        assert source.read_bytes() == original
    finally:
        plots.plt.close("all")
