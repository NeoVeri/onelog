#!/usr/bin/env python3
"""
main.py — 顶层模块

第一个调用 get_logger 的模块决定全局配置
"""

from onelog import get_logger
import logging

# 顶层配置：第一个 get_logger 调用决定全局配置
log = get_logger(__name__, level=logging.DEBUG, show_loc=True, log_file="app.log")

# 子模块的 get_logger 参数会被忽略，继承顶层配置
from finder import find_data, log as finder_log

log.info("=== main.py 启动 ===")
results = find_data("test query")
log.info(f"处理了 {len(results)} 条数据")
log.warning("磁盘空间不足")

try:
    x = int("abc")
except Exception:
    log.exception("类型转换失败")
