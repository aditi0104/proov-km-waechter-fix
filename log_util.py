# log_util.py
# Minimal homemade logger used by the nightly fleet report.

import time

LOG_LINES: list[str] = []              # accumulated since last flush_log call


def log(message: str) -> None:
    """Timestamp a message, print it, and buffer it for the next flush."""
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}"
    LOG_LINES.append(line)
    print(line)


def flush_log(path: str) -> None:
    """Append all buffered log lines to path, then clear the buffer."""
    with open(path, "a", encoding="utf-8") as f:
        f.writelines(line + "\n" for line in LOG_LINES)
    LOG_LINES.clear()
