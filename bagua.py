#!/usr/bin/env python3
"""向后兼容入口：python bagua.py"""

import sys

from bagua.cli import main

if __name__ == "__main__":
    raise SystemExit(main())