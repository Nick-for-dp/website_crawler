"""调用 DeepSeek（OpenAI 兼容协议）将当日新闻归纳为简报。API Key 走 .env 的 deepseek_api_key。"""
import os
import logging
from pathlib import Path
from typing import List, Optional

import requests
from dotenv import load_dotenv

from model import News

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
logger = logging.getLogger(__name__)

API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-chat"
SUMMARY_MAX_CHARS = 500  # 单条摘要截断长度，控制 token 消耗

_PROMPT_TEMPLATE = """你是一位专业的新闻编辑。以下是 {date_str} 前后收集到的 {count} 条新闻（来源含新闻联播、商务部、交通部、AI日报）。
请归纳成一份适合钉钉群阅读的中文早报，要求：
1. 开头一句话总览今日要点。
2. 按主题分板块（如：时政要闻、经济商务、交通基建、AI 前沿），每条新闻一行：标题 + 一句话要点。
3. 结尾给出 2-3 条值得关注的趋势点评。
4. 全文使用 Markdown，控制在 1200 字以内。

新闻列表：
{news_block}
"""


def _format_news_block(news_list: List[News]) -> str:
    lines = []
    for i, n in enumerate(news_list, 1):
        summary = (n.summary or "")[:SUMMARY_MAX_CHARS]
        lines.append(f"{i}. 【{n.origin}】{n.title}\n   摘要：{summary}")
    return "\n".join(lines)


def summarize_news(news_list: List[News], date_str: str) -> Optional[str]:
    """将新闻列表归纳成 Markdown 简报，失败返回 None"""
    if not news_list:
        return None
    api_key = os.getenv("deepseek_api_key")
    if not api_key:
        logger.error("未在 .env 配置 deepseek_api_key")
        return None
    prompt = _PROMPT_TEMPLATE.format(
        date_str=date_str, count=len(news_list), news_block=_format_news_block(news_list)
    )
    try:
        resp = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}], "temperature": 0.3},
            timeout=120,
        )
        resp.raise_for_status()
        digest = resp.json()["choices"][0]["message"]["content"].strip()
        logger.info(f"简报生成成功，长度 {len(digest)} 字")
        return digest
    except Exception as e:
        logger.error(f"DeepSeek 调用失败: {e}")
        return None
