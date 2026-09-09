"""历史新闻清理：删除发布日期超过一年的数据。

由 cron 定期调用（每月一次即可），例如：
    0 3 1 * * cd /opt/website_crawler && uv run scripts/cleanup_old_news.py >> logs/cleanup.log 2>&1
"""
import sys
from pathlib import Path
# 保证从任意工作目录（cron）运行时都能按包根导入
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from datetime import datetime, timedelta

from storage import delete_news_before

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("cleanup_old_news")

RETENTION_DAYS = 365  # 新闻保留时长


def main():
    cutoff = (datetime.today() - timedelta(days=RETENTION_DAYS)).strftime("%Y-%m-%d")
    logger.info(f"清理截止日期: {cutoff}")
    delete_news_before(cutoff)


if __name__ == "__main__":
    main()
