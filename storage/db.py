"""SQLite 新闻持久化：建表、去重写入、按日期查询。

数据库文件默认在项目根目录 data/news.db，可用环境变量 NEWS_DB_PATH 覆盖。
注意：Aibase 日报内所有新闻共享同一 url，故去重键用 (title, origin, publish_date)。
"""
import os
import sqlite3
import logging
from pathlib import Path
from typing import List

from model import News, NewsResponse

logger = logging.getLogger(__name__)

DB_PATH = Path(os.getenv("NEWS_DB_PATH", str(Path(__file__).resolve().parent.parent / "data" / "news.db")))

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    origin TEXT NOT NULL,
    summary TEXT,
    publish_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE(title, origin, publish_date)
);
"""

# 推送记录表：已推送过的新闻不再重复推送，news 表仍保留全量采集结果
_CREATE_PUSH_LOG_TABLE = """
CREATE TABLE IF NOT EXISTS push_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    origin TEXT NOT NULL,
    publish_date TEXT NOT NULL,
    pushed_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE(title, origin, publish_date)
);
"""


def _get_conn() -> sqlite3.Connection:
    """创建连接并确保表存在"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(_CREATE_TABLE)
    conn.execute(_CREATE_PUSH_LOG_TABLE)
    return conn


def save_news_response(resp: NewsResponse) -> int:
    """将 NewsResponse 落库，重复数据自动忽略，返回新增条数"""
    if not resp.news_list:
        return 0
    inserted = 0
    conn = _get_conn()
    try:
        with conn:  # 自动 commit / 异常回滚
            for news in resp.news_list:
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO news (title, url, origin, summary, publish_date) VALUES (?, ?, ?, ?, ?)",
                    (news.title, news.url, news.origin, news.summary, news.publish_date),
                )
                inserted += cursor.rowcount
    finally:
        conn.close()
    logger.info(f"落库完成：新增 {inserted}/{len(resp.news_list)} 条")
    return inserted


def fetch_news_by_date(publish_date: str) -> List[News]:
    """按发布日期查询新闻（供大模型归纳简报使用）"""
    conn = _get_conn()
    try:
        rows = conn.execute(
            "SELECT title, url, origin, summary, publish_date FROM news WHERE publish_date = ? ORDER BY origin",
            (publish_date,),
        ).fetchall()
    finally:
        conn.close()
    return [News(title=r[0], url=r[1], origin=r[2], summary=r[3], publish_date=r[4]) for r in rows]


def fetch_unpushed_news(publish_dates: List[str]) -> List[News]:
    """查询指定发布日期范围内、尚未推送过的新闻（供每日简报使用）"""
    if not publish_dates:
        return []
    placeholders = ",".join("?" for _ in publish_dates)
    conn = _get_conn()
    try:
        rows = conn.execute(
            f"""
            SELECT n.title, n.url, n.origin, n.summary, n.publish_date
            FROM news n
            LEFT JOIN push_log p
              ON n.title = p.title AND n.origin = p.origin AND n.publish_date = p.publish_date
            WHERE n.publish_date IN ({placeholders}) AND p.id IS NULL
            ORDER BY n.origin
            """,
            publish_dates,
        ).fetchall()
    finally:
        conn.close()
    return [News(title=r[0], url=r[1], origin=r[2], summary=r[3], publish_date=r[4]) for r in rows]


def mark_pushed(news_list: List[News]) -> int:
    """将新闻登记为已推送，返回新登记条数"""
    if not news_list:
        return 0
    marked = 0
    conn = _get_conn()
    try:
        with conn:
            for news in news_list:
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO push_log (title, origin, publish_date) VALUES (?, ?, ?)",
                    (news.title, news.origin, news.publish_date),
                )
                marked += cursor.rowcount
    finally:
        conn.close()
    logger.info(f"推送登记完成：新增 {marked}/{len(news_list)} 条")
    return marked


def delete_news_before(publish_date: str) -> int:
    """删除发布日期早于指定日期的新闻，返回删除条数（publish_date 为 YYYY-MM-DD，可直接字符串比较）"""
    conn = _get_conn()
    try:
        with conn:
            cursor = conn.execute("DELETE FROM news WHERE publish_date < ?", (publish_date,))
    finally:
        conn.close()
    logger.info(f"清理完成：删除 {cursor.rowcount} 条早于 {publish_date} 的新闻")
    return cursor.rowcount
