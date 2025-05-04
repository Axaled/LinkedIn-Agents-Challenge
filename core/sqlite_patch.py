# =============================================================================
# sqlite_patch.py
#
# This module ensures that on Linux systems the standard `sqlite3` module
# is replaced by `pysqlite3`, thereby guaranteeing a SQLite engine of
# version 3.35.0 or higher for libraries such as Chroma or CrewAI that
# depend on it. On non-Linux platforms, this
# file makes no changes and the system’s default `sqlite3` is used.
# =============================================================================

import sys
import platform

if platform.system().lower() == "linux":
    __import__("pysqlite3")
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")