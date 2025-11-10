#!/usr/bin/env python3
"""Entry point wrapper for labtools CLI."""

from __future__ import annotations

import sys

from labtools.cli import main


def run() -> int:
    """Invoke the labtools CLI."""
    result = main(standalone_mode=False)
    return int(result) if isinstance(result, int) else 0


if __name__ == "__main__":
    try:
        exit_code = run()
    except SystemExit as exc:
        exit_code = exc.code
    except Exception as exc:  # pylint: disable=broad-except
        print(f"labtools failed: {exc}", file=sys.stderr)
        exit_code = 1
    sys.exit(exit_code)


