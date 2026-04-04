#!/usr/bin/env python3
"""
Session Query Runner

Finds all un-run query placeholders in a session.md file, executes them
against the local card pool via search_cards.py, and fills the results
in-place so the AI receives a fully populated candidate pool.

Usage:
    python scripts/run_session_queries.py Decks/2026-04-03_My_Deck/session.md
    python scripts/run_session_queries.py Decks/2026-04-03_My_Deck/session.md --dry-run
    python scripts/run_session_queries.py Decks/2026-04-03_My_Deck/session.md --force

Flags:
    --dry-run       Show which queries would be run, without executing them
    --force         Re-run ALL queries, even ones that already have results
    --timeout N     Per-query timeout in seconds (default: 60)

Exit codes:
    0  All queries completed (or nothing to run)
    1  session.md not found or unreadable
    2  search_cards.py not found
    3  One or more queries failed
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mtg_utils import RepoPaths

# Matches a fenced code block that contains a search_cards.py command
# followed by either a placeholder or actual output
QUERY_BLOCK_RE = re.compile(
    r"(```\n\$ (python [^\n]+search_cards\.py[^\n]*)\n)(.*?)(```)",
    re.DOTALL,
)

PLACEHOLDER = "(run this query and paste results here)"


def find_queries(content: str, force: bool = False):
    """
    Yield (match, command, has_output) for every search_cards.py block.
    If force=False, skip blocks that already have real output.
    Skips template/placeholder commands containing <...> tokens.
    """
    for m in QUERY_BLOCK_RE.finditer(content):
        cmd = m.group(2)
        # Skip template lines like: search_cards.py --type <type> --colors <colors>
        if re.search(r"<[^>]+>", cmd):
            continue
        body = m.group(3).strip()
        has_output = body and body != PLACEHOLDER and body != "(paste output here)"
        if has_output and not force:
            continue
        yield m, cmd, has_output


def run_query(command: str, repo_root: Path, timeout: int) -> tuple[str, bool]:
    """Execute a search_cards.py command string. Returns (output, success)."""
    # Replace 'python scripts/search_cards.py' with the actual path
    scripts_dir = repo_root / "scripts"
    cmd = command.replace(
        "python scripts/search_cards.py",
        f"{sys.executable} {scripts_dir / 'search_cards.py'}",
    ).replace(
        "python search_cards.py",
        f"{sys.executable} {scripts_dir / 'search_cards.py'}",
    )

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(repo_root),
            timeout=timeout,
            env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"},
        )
        output = result.stdout.strip() or result.stderr.strip() or "(no output)"
        return output, result.returncode == 0
    except subprocess.TimeoutExpired:
        return f"(timed out after {timeout}s)", False
    except Exception as e:
        return f"(error: {e})", False


def main() -> None:
    p = argparse.ArgumentParser(
        description="Execute pending search_cards.py queries in a session.md file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("session_file", help="Path to session.md")
    p.add_argument("--dry-run", action="store_true", help="Show queries without running them")
    p.add_argument("--force", action="store_true", help="Re-run all queries, even completed ones")
    p.add_argument("--timeout", type=int, default=60, help="Per-query timeout in seconds (default: 60)")
    args = p.parse_args()

    session_path = Path(args.session_file)
    if not session_path.exists():
        print(f"ERROR: {session_path} not found.", file=sys.stderr)
        sys.exit(1)

    paths = RepoPaths()
    search_script = paths.scripts_dir / "search_cards.py"
    if not search_script.exists():
        print(f"ERROR: search_cards.py not found at {search_script}", file=sys.stderr)
        sys.exit(2)

    content = session_path.read_text(encoding="utf-8")
    queries = list(find_queries(content, force=args.force))

    if not queries:
        print("Nothing to run — all query blocks already have results.")
        print("Use --force to re-run all queries.")
        sys.exit(0)

    print("=" * 60)
    print(f"  SESSION QUERY RUNNER")
    print(f"  File:    {session_path}")
    print(f"  Queries: {len(queries)} pending")
    if args.dry_run:
        print(f"  Mode:    DRY RUN (no changes)")
    print("=" * 60)
    print()

    if args.dry_run:
        for i, (_, cmd, has_output) in enumerate(queries, 1):
            status = "[re-run]" if has_output else "[pending]"
            print(f"  [{i}] {status} {cmd}")
        print()
        print(f"Run without --dry-run to execute.")
        sys.exit(0)

    failures = 0
    new_content = content

    for i, (match, cmd, has_output) in enumerate(queries, 1):
        label = "[re-run]" if has_output else "[pending]"
        print(f"  [{i}/{len(queries)}] {label} {cmd[:70]}...")
        output, success = run_query(cmd, paths.root, args.timeout)

        if not success:
            failures += 1
            print(f"           FAILED")
        else:
            # Count result lines for feedback
            result_lines = [l for l in output.splitlines() if l.strip() and not l.startswith("-")]
            print(f"           -> {len(result_lines)} lines of output")

        # Replace the block body in content
        old_block = match.group(0)
        new_block = (
            match.group(1)          # ```\n$ command\n
            + "\n"
            + output
            + "\n"
            + match.group(4)        # ```
        )
        new_content = new_content.replace(old_block, new_block, 1)

    # Write updated session.md
    session_path.write_text(new_content, encoding="utf-8")

    print()
    print("=" * 60)
    if failures:
        print(f"  Done with {failures} failure(s). session.md updated.")
    else:
        print(f"  All {len(queries)} queries completed. session.md updated.")
    print("=" * 60)

    sys.exit(3 if failures else 0)


if __name__ == "__main__":
    main()
