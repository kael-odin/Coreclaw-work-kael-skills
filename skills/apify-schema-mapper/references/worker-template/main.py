#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fast-fail test worker — CoreClaw「脚本失败不扣费」规则验证.

Minimal-footprint failure case:
  * SCHEMA-INDEPENDENT: never reads any input_schema field and never writes
    anything output_schema describes — runs identically whatever the schemas
    declare (they are not used at all).
  * ZERO OUTPUT: no result rows are pushed — the run produces no valid data.
  * FAST: finishes in well under a second.
  * ALWAYS FAILS: non-zero exit code (sys.exit(1)) — the exact signal the
    platform uses to mark a run "failed".
  * SILENT: emits no log lines and no traceback. The run log therefore
    contains only the platform's own system lines.

The only SDK call is a minimal handshake so the run is a genuine worker run;
it produces no output and its payload is deliberately never used.
"""

import sys
import time

from sdk import CoreSDK


def main():
    # Minimal handshake: connect once, read the payload, never use it.
    # (This call produces no log output; keeping it makes the run a real run.)
    CoreSDK.Parameter.get_input_json_dict()

    # Guaranteed failure with the smallest possible footprint:
    # non-zero exit code, no log lines, no traceback. The tiny delay only
    # keeps the run from being an instant 0 ms abort; it logs nothing.
    time.sleep(0.5)
    sys.exit(1)


if __name__ == "__main__":
    main()
