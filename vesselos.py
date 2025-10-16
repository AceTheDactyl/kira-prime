#!/usr/bin/env python3
from __future__ import annotations

"""Legacy VesselOS entry point that forwards to the Prime CLI."""

import sys
from typing import Iterable, Optional

from cli.prime import main as prime_main


def main(argv: Optional[Iterable[str]] = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    return prime_main(args)


if __name__ == "__main__":
    raise SystemExit(main())

