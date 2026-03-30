#!/usr/bin/env python3
from onelog import get_logger
import logging

log = get_logger(__name__, level=logging.DEBUG, show_loc=True)

log.info("正常运行中...")
log.warning("有点问题")
log.fatal("数据库连接彻底失败，无法继续")  # 打印后退出
log.info("这行不会执行")
