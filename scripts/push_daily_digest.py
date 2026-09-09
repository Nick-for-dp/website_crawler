"""每日简报推送：取当日及昨日入库且未推送过的新闻 → DeepSeek 归纳 → 钉钉机器人推送。

由 cron 在采集任务之后调用，例如：
    0 9 * * * cd /opt/website_crawler && uv run scripts/push_daily_digest.py >> logs/digest.log 2>&1

说明：news 表保留全量采集结果；本脚本只取未推送过的新闻，推送成功后登记到 push_log，
     保证同一条新闻不会在钉钉群里重复出现。
"""
import sys
from pathlib import Path
# 保证从任意工作目录（cron）运行时都能按包根导入
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from datetime import datetime, timedelta

from storage import fetch_unpushed_news, mark_pushed
from llm import summarize_news
from notify import push_markdown

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("push_daily_digest")


def main():
    today = datetime.today()
    date_str = today.strftime("%Y-%m-%d")
    # 汇总今日与昨日入库的新闻（新闻联播为 t-1，政府类含时效窗口，AI日报与纸媒为当日），并过滤已推送过的
    dates = [date_str, (today - timedelta(days=1)).strftime("%Y-%m-%d")]
    news = fetch_unpushed_news(dates)
    if not news:
        logger.warning("无未推送的新闻，跳过本次推送")
        return
    logger.info(f"待归纳新闻 {len(news)} 条（已过滤历史推送）")

    digest = summarize_news(news, date_str=date_str)
    if not digest:
        logger.error("简报生成失败")
        sys.exit(1)

    title = f"新闻早报 {date_str}"
    if not push_markdown(title, f"# {title}\n\n{digest}"):
        sys.exit(1)
    # 推送成功才登记，失败留待下次重试
    mark_pushed(news)


if __name__ == "__main__":
    main()
