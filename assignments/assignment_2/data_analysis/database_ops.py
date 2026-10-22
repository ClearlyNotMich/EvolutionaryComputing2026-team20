"""Combine individual records without changing the source experiment databases."""

from contextlib import closing
from pathlib import Path
import sqlite3


def quote_identifier(name):
    """Safely quote an SQLite table or column identifier."""
    return '"' + name.replace('"', '""') + '"'


def _open_readonly(path):
    """Open an existing database without SQLite's implicit file creation."""
    return sqlite3.connect(Path(path).resolve(strict=True).as_uri() + "?mode=ro", uri=True)


def _individual_schema(connection, source_path):
    schema_row = connection.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'individual'"
    ).fetchone()
    if schema_row is None:
        raise ValueError(f"No table named 'individual' was found in {source_path}")

    # cid, name, declared type, not-null, default, primary-key position, hidden.
    info = connection.execute("PRAGMA table_xinfo(individual)").fetchall()
    primary_keys = [column for column in info if column[5]]
    primary_key_indexes = [
        index for index in connection.execute("PRAGMA index_list(individual)")
        if index[3] == "pk"
    ]
    if (
        len(primary_keys) != 1
        or primary_keys[0][2].strip().upper() != "INTEGER"
        or primary_key_indexes
    ):
        raise ValueError(
            f"{source_path}: individual needs a single INTEGER rowid primary key "
            "so new IDs can be assigned safely"
        )
    if any(column[6] for column in info):
        raise ValueError(f"{source_path}: generated or hidden columns are not supported")
    if any(column[1].casefold() == "source_db" for column in info):
        raise ValueError(f"{source_path}: individual already contains a source_db column")

    columns = [column[1] for column in info if not column[5]]
    if not columns:
        raise ValueError("No copyable columns were found in individual")
    signature = [
        (column[1], column[2].strip().upper(), column[3], column[4], column[5])
        for column in info
    ]
    return schema_row[0], signature, columns


def merge_individual_databases(source_paths, target_path):
    """Merge compatible individual tables into a new SQLite database.

    Sources are opened read-only. The output receives fresh integer IDs and a
    source_db column containing each input filename, as in the original API.
    Only the individual table is copied, not other tables, triggers or indexes.

    An existing target is never overwritten. All inserts share one transaction;
    a failed merge rolls back and removes only the output file created by this
    call. Missing inputs, incompatible schemas and write failures raise errors.
    """
    source_paths = [Path(path).resolve(strict=True) for path in source_paths]
    target_path = Path(target_path)
    if not source_paths:
        raise ValueError("No source databases were supplied.")
    if target_path.exists() or target_path.is_symlink():
        raise FileExistsError(f"Target database already exists: {target_path}")

    with closing(_open_readonly(source_paths[0])) as source_connection:
        create_sql, expected_schema, columns = _individual_schema(
            source_connection, source_paths[0]
        )

    quoted_columns = ", ".join(quote_identifier(column) for column in columns)
    placeholders = ", ".join("?" for _ in range(len(columns) + 1))
    insert_sql = (
        f"INSERT INTO individual ({quoted_columns}, source_db) "
        f"VALUES ({placeholders})"
    )

    # Exclusive creation also refuses an output that appeared after the check.
    with target_path.open("xb"):
        pass
    created_stat = target_path.stat()
    created_identity = (created_stat.st_dev, created_stat.st_ino)
    try:
        with closing(sqlite3.connect(target_path)) as target_connection:
            target_connection.execute("PRAGMA busy_timeout = 5000")
            with target_connection:
                # Explicit BEGIN includes DDL in the same rollback boundary.
                target_connection.execute("BEGIN")
                target_connection.execute(create_sql)
                target_connection.execute(
                    "ALTER TABLE individual ADD COLUMN source_db TEXT"
                )
                for source_path in source_paths:
                    with closing(_open_readonly(source_path)) as source_connection:
                        _, schema, _ = _individual_schema(source_connection, source_path)
                        if schema != expected_schema:
                            raise ValueError(
                                f"Incompatible individual schema in {source_path}"
                            )
                        rows = source_connection.execute(
                            f"SELECT {quoted_columns} FROM individual ORDER BY rowid"
                        )
                        target_connection.executemany(
                            insert_sql,
                            (tuple(row) + (source_path.name,) for row in rows),
                        )
    except BaseException:
        # Do not remove a pre-existing file or a replacement made by another
        # process while the merge was running.
        try:
            current_stat = target_path.lstat()
        except FileNotFoundError:
            pass
        else:
            if (current_stat.st_dev, current_stat.st_ino) == created_identity:
                target_path.unlink()
        raise

    print(f"Merged {len(source_paths)} databases into: {target_path}")
