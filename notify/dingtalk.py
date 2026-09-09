"""钉钉群自定义机器人推送（加签模式）。webhook / secret 走 .env 的 dingding_webhook / dingding_secret。"""
import os
import time
import hmac
import base64
import hashlib
import logging
import urllib.parse
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
logger = logging.getLogger(__name__)


def _signed_webhook() -> str | None:
    """按钉钉加签规则拼接 timestamp 和 sign 参数"""
    webhook = os.getenv("dingding_webhook")
    secret = os.getenv("dingding_secret")
    if not webhook or not secret:
        logger.error("未在 .env 配置 dingding_webhook / dingding_secret")
        return None
    timestamp = str(round(time.time() * 1000))
    string_to_sign = f"{timestamp}\n{secret}"
    digest = hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(digest))
    sep = "&" if "?" in webhook else "?"
    return f"{webhook}{sep}timestamp={timestamp}&sign={sign}"


def push_markdown(title: str, text: str) -> bool:
    """推送 Markdown 消息到钉钉群，成功返回 True"""
    url = _signed_webhook()
    if not url:
        return False
    try:
        resp = requests.post(
            url,
            json={"msgtype": "markdown", "markdown": {"title": title, "text": text}},
            timeout=15,
        )
        result = resp.json()
        if result.get("errcode") == 0:
            logger.info("钉钉推送成功")
            return True
        logger.error(f"钉钉推送失败: {result}")
        return False
    except Exception as e:
        logger.error(f"钉钉推送异常: {e}")
        return False
