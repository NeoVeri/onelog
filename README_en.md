# onelog 📝

**[中文](README.md) | English**

A lightweight Python logging module built on [Rich](https://github.com/textualize/rich).

## Features

- 🎨 Color-coded terminal output (WARNING=yellow, ERROR=red, FATAL=purple)
- 📁 Optional file logging (plain text)
- 📍 File path & line number display (toggleable)
- 📊 Auto log summary on script exit
- 💀 `log.fatal()` — print and exit
- 🔧 Multi-module support — top-level config overrides sub-modules

## Requirements

- Python 3.8+
- `rich` (only dependency)

```bash
pip install rich
```

## Usage

```python
from onelog import get_logger

log = get_logger(__name__, level="DEBUG", show_path=True, log_file="app.log")

log.debug("debug message")
log.info("info message")
log.warning("warning message")
log.error("error message")
log.fatal("fatal error, script exits here")
```

Log summary prints automatically when the script exits:

```
──────────────────────────────── 📊 Log Summary ────────────────────────────────
  DEBUG:   1
  INFO:    1
  WARNING: 1
  ERROR:   1

  Log File: /path/to/app.log
────────────────────────────────────────────────────────────────────────────────
```

## License

MIT
