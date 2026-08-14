"""
Runs pg_dump against the Railway Postgres database and saves a timestamped,
restorable backup file to local disk.

Usage:
    python backup_db.py --database-url "postgresql://user:pass@host:port/db"
    (or set DATABASE_URL as an environment variable instead)

Use the Postgres service's PUBLIC connection string from Railway's Connect tab
(not the internal one the backend uses) when running this from outside
Railway's private network — e.g. from your own machine.

Output: ops/backups/prairie_ag_<timestamp>.dump — pg_dump's custom format
(compressed, supports selective/parallel restore). To restore into a fresh
database:
    pg_restore --clean --if-exists --no-owner --no-privileges -d <target-database-url> <file>

This is a manual, on-demand safety net — nothing runs it automatically yet.
It only writes to local disk, which is not itself durable: move the resulting
file to cloud storage, an external drive, etc. after each run.
"""

import argparse
import datetime
import os
import shutil
import subprocess
import sys
from pathlib import Path

BACKUP_DIR = Path(__file__).resolve().parent / "backups"


def find_pg_dump() -> str:
    found = shutil.which("pg_dump")
    if found:
        return found
    windows_default = Path("C:/Program Files/PostgreSQL")
    if windows_default.exists():
        for version_dir in sorted(windows_default.iterdir(), reverse=True):
            candidate = version_dir / "bin" / "pg_dump.exe"
            if candidate.exists():
                return str(candidate)
    sys.exit("pg_dump not found on PATH. Install PostgreSQL client tools, or pass --pg-dump-path.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="Postgres connection string (defaults to $DATABASE_URL)",
    )
    parser.add_argument("--pg-dump-path", default=None, help="Path to pg_dump executable if not on PATH")
    parser.add_argument("--out-dir", default=str(BACKUP_DIR), help="Directory to write the backup file to")
    args = parser.parse_args()

    if not args.database_url:
        sys.exit(
            "No DATABASE_URL given. Pass --database-url or set the DATABASE_URL env var.\n"
            "Use the Postgres service's PUBLIC connection string from Railway's Connect tab "
            "if running this from outside Railway's network."
        )

    pg_dump = args.pg_dump_path or find_pg_dump()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = out_dir / f"prairie_ag_{timestamp}.dump"

    cmd = [
        pg_dump,
        "--format=custom",
        "--no-owner",
        "--no-privileges",
        f"--file={out_file}",
        args.database_url,
    ]
    print(f"Running pg_dump -> {out_file}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        out_file.unlink(missing_ok=True)  # don't leave a misleading empty/partial file behind
        sys.exit(f"pg_dump failed with exit code {result.returncode}")

    size_kb = out_file.stat().st_size / 1024
    print(f"Backup written: {out_file} ({size_kb:.1f} KB)")
    print("This file is only on local disk right now — copy it to durable storage")
    print("(cloud storage, external drive, etc.) to actually be protected by it.")
    print(f"To restore: pg_restore --clean --if-exists --no-owner --no-privileges -d <target-database-url> {out_file}")


if __name__ == "__main__":
    main()
