"""每日新闻采集入口：遍历各数据源爬虫，结果去重写入 SQLite。

由 cron 每日定时调用（部署到 Ubuntu 后配置 crontab），例如：
    30 7 * * * cd /opt/website_crawler && uv run scripts/collect_daily.py >> logs/collect.log 2>&1
"""
import sys
from pathlib import Path
# 保证从任意工作目录（cron）运行时都能按包根导入
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from datetime import datetime

from ai_news import AiNewsCrawler
from cctv_news import CCTVNewsCrawler
from gov_news import CommerceNewsCrawler, TransportNewsCrawler
from paper_news import RMRBNewsCrawler, GMRBNewsCrawler
from storage import save_news_response

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("collect_daily")

# 待采集的数据源，新增爬虫时在此登记即可
CRAWLERS = {
    "ai": AiNewsCrawler(url=r"https://news.aibase.com/zh/daily"),
    "cctv": CCTVNewsCrawler(url=r"https://tv.cctv.com/lm/xwlb/"),
    "transport": TransportNewsCrawler(url=r"https://www.mot.gov.cn/xinwen/jiaotongyaowen/index.html"),
    "commerce": CommerceNewsCrawler(url=r"https://www.mofcom.gov.cn/"),
    "rmrb": RMRBNewsCrawler(url=r"http://www.people.com.cn/#lm1"),
    "gmrb": GMRBNewsCrawler(),
}


def main():
    logger.info(f"===== 每日采集开始 {datetime.now():%Y-%m-%d %H:%M:%S} =====")
    total = 0
    for name, crawler in CRAWLERS.items():
        try:
            resp = crawler.get_news()
        except Exception as e:
            logger.error(f"[{name}] 爬虫执行异常: {e}")
            continue
        if resp.status != "OK" or not resp.news_list:
            logger.warning(f"[{name}] 未获取到数据: {resp.err_info}")
            continue
        inserted = save_news_response(resp)
        total += inserted
        logger.info(f"[{name}] 新增 {inserted}/{len(resp.news_list)} 条")
    logger.info(f"===== 每日采集结束，共新增 {total} 条 =====")


if __name__ == "__main__":
    main()
