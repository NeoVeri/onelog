# onelog 📝

**[English](README.md) | 中文**

基于 [Rich](https://github.com/textualize/rich) 的轻量级 Python 日志模块。

## 功能特性

- 🎨 终端彩色输出（WARNING=黄色，ERROR=红色，FATAL=紫色）
- 📁 可选文件日志（纯文本）
- 📍 显示文件名和行号（可开关）
- 📊 脚本退出时自动打印日志统计
- 💀 `log.fatal()` — 打印日志后立即退出脚本
- 🔧 多模块支持 — 顶层配置自动覆盖子模块

## 环境要求

- Python 3.8+
- 仅依赖 `rich`

```bash
pip install rich
```

## 使用方法

```python
from onelog import get_logger

# 顶层模块配置（第一个调用 get_logger 的决定全局配置）
log = get_logger(__name__, level="DEBUG", show_path=True, log_file="app.log")

log.debug("调试信息")
log.info("正常信息")
log.warning("警告信息")
log.error("错误信息")
log.fatal("致命错误，脚本将退出")
```

子模块不需要配置，直接用就行（自动继承顶层配置）：

```python
# finder.py
from onelog import get_logger

log = get_logger(__name__)

def find_data(query):
    log.debug(f"搜索: {query}")
    return []
```

## 日志统计

脚本退出时自动打印统计信息，无需手动调用：

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
