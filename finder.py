#!/usr/bin/env python3
"""
finder.py — 子模块

独立运行时自己配置，被 main.py 调用时用顶层配置
"""

from onelog import get_logger
import logging

# 独立调试时这样配（被 main.py 调用时这行参数会被忽略）
log = get_logger(__name__, level=logging.DEBUG, show_loc=True, log_file="finder.log")

def find_data(query):
    log.debug(f"开始搜索: {query}")
    log.info(f"找到 42 条结果")
    return list(range(42))

if __name__ == "__main__":
    # 单独调试 finder.py
    find_data("debug query")
