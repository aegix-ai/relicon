"""relicon command line. Filled in milestone by milestone."""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="relicon")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("demo", help="full zero-key loop (STUB until M5)")
    a = p.parse_args(argv)
    if a.cmd == "demo":
        print("STUB: relicon demo is not built yet (milestone M1 skeleton).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
