#!/usr/bin/env python3
"""
onelog.py — 统一日志配置模块

功能：
1. RichHandler 终端彩色输出
2. FileHandler 文件记录
3. 支持显示文件名+行号（可开关）
4. 支持显示时间（可开关）
5. 多模块调用时，顶层配置覆盖子模块
6. get_logger() 本身支持配置参数，子模块可独立运行调试
7. log_summary() 打印各级别日志数量统计（可开关）

调用方式见文件底部示例
"""

import logging
import sys
import atexit
from rich.logging import RichHandler
from rich.traceback import install

# 全局安装 Rich traceback
install(show_locals=True)

# 默认配置
_DEFAULT_CONFIG = {
    "level": logging.DEBUG,
    "show_loc": False,
    "show_time": True,
    "show_summary": True,
    "log_file": None,
    "log_format": "%(asctime)s | %(levelname)-8s | %(pathname)s:%(lineno)d | %(message)s",
    "date_format": "[%H:%M:%S]",
}

# 自定义 FATAL 级别
FATAL = logging.FATAL  # 50，比 CRITICAL 高


class FatalError(Exception):
    """FATAL 日志触发的异常"""
    pass

# 全局配置（首次 get_logger 调用后锁定）
_global_config = None
_configured = False

# 日志计数器
_log_counter = {
    "DEBUG": 0,
    "INFO": 0,
    "WARNING": 0,
    "ERROR": 0,
    "FATAL": 0,
}


class _CountingFilter(logging.Filter):
    """过滤器：统计各级别日志数量"""
    def filter(self, record):
        level_name = record.levelname
        if level_name in _log_counter:
            _log_counter[level_name] += 1
        return True


def log_summary():
    """打印日志统计摘要"""
    from rich.console import Console
    from rich.rule import Rule
    console = Console()
    console.print()
    console.print(Rule("[bold]📊 Log Summary[/bold]", style="cyan"))
    console.print(f"  DEBUG:   {_log_counter['DEBUG']}")
    console.print(f"  INFO:    {_log_counter['INFO']}")
    console.print(f"  WARNING: {_log_counter['WARNING']}", style="yellow")
    console.print(f"  ERROR:   {_log_counter['ERROR']}", style="bold red")
    if _log_counter['FATAL'] > 0:
        console.print(f"  FATAL:   {_log_counter['FATAL']}", style="bold magenta")
    console.print()
    if _global_config and _global_config.get("log_file"):
        import os
        log_path = os.path.abspath(_global_config["log_file"])
        console.print(f"  Log File: {log_path}")
    console.print(Rule(style="cyan"))
    console.print()


def get_logger(
    name: str = None,
    level: int = None,
    show_loc: bool = None,
    show_time: bool = None,
    show_summary: bool = None,
    log_file: str = None,
) -> logging.Logger:
    """
    获取 logger 实例。

    - 如果全局已配置（顶层模块调用过），直接返回 logger，参数被忽略
    - 如果全局未配置，用传入的参数（缺失则用默认值）完成配置

    Args:
        name:        logger 名称，传 __name__
        level:       日志级别 (DEBUG/INFO/WARNING/ERROR)
        show_loc:    终端是否显示 文件:行号，默认 False
        show_time:   终端是否显示时间，默认 True
        show_summary:脚本退出时是否打印 summary，默认 True
        log_file:    日志文件路径（None 则不写文件）

    Returns:
        logging.Logger 实例
    """
    global _global_config, _configured

    if not _configured:
        # 首次调用：用传入参数（或默认值）完成全局配置
        _global_config = dict(_DEFAULT_CONFIG)
        if level is not None:
            _global_config["level"] = level
        if show_loc is not None:
            _global_config["show_loc"] = show_loc
        if show_time is not None:
            _global_config["show_time"] = show_time
        if show_summary is not None:
            _global_config["show_summary"] = show_summary
        if log_file is not None:
            _global_config["log_file"] = log_file
        _apply_config()
        _configured = True

    return logging.getLogger(name)


def _apply_config():
    """应用当前 _global_config 到 root logger"""
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(_global_config["level"])

    # RichHandler — 终端彩色输出
    from rich.console import Console
    from rich.theme import Theme

    # 自定义主题：FATAL 用紫色
    custom_theme = Theme({
        "logging.level.warning": "yellow",
        "logging.level.error": "bold red",
        "logging.level.fatal": "bold magenta",
    })
    console = Console(theme=custom_theme)

    rich_handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_path=_global_config["show_loc"],
        show_level=True,
        show_time=_global_config["show_time"],
        log_time_format=_global_config["date_format"],
        markup=False,
    )
    rich_handler.setLevel(_global_config["level"])
    rich_handler.addFilter(_CountingFilter())

    handlers = [rich_handler]

    # FileHandler — 文件记录
    if _global_config["log_file"]:
        file_handler = logging.FileHandler(
            _global_config["log_file"], encoding="utf-8"
        )
        file_handler.setFormatter(
            logging.Formatter(
                _global_config["log_format"],
                datefmt=_global_config["date_format"],
            )
        )
        file_handler.setLevel(_global_config["level"])
        handlers.append(file_handler)

    logging.basicConfig(
        level=_global_config["level"],
        format="%(message)s",
        handlers=handlers,
        force=True,
    )

    # 给 Logger 添加 fatal() 方法：打印后退出
    _patch_logger_fatal()

    # 注册退出时自动打印 summary（根据配置决定）
    if _global_config["show_summary"]:
        atexit.register(log_summary)


def _patch_logger_fatal():
    """给所有 Logger 实例添加 fatal() 方法：打印日志后 sys.exit(1)"""
    def fatal(self, msg, *args, **kwargs):
        # stacklevel=2 让行号指向调用者而非这里
        kwargs.setdefault("stacklevel", 2)
        self.log(FATAL, msg, *args, **kwargs)
        sys.exit(1)

    logging.Logger.fatal = fatal
    logging.addLevelName(FATAL, "FATAL")


# ============================================================
# 示例
# ============================================================
if __name__ == "__main__":
    from onelog import get_logger

    log = get_logger(__name__, level=logging.DEBUG, show_loc=True, show_time=True, log_file="app.log")

    log.debug("调试信息")
    log.info("处理完成")
    log.info("又一条 info")
    log.warning("注意")
    log.warning("又一个 warning")
    log.error("出错了")
    log.error("又一个 error")
    log.error("第三个 error")
    # show_summary=True，脚本退出时自动打印
