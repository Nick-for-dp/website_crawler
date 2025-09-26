"""
工具模块，提供爬虫相关的工具函数
"""

from .tool import (
    get_html_from_url,
    get_few_days_ago,
    join_urls,
    is_valid_url,
    get_domain_from_url,
    create_session,
    set_random_user_agent,
    DEFAULT_HEADERS
)

__all__ = [
    'get_html_from_url',
    'get_few_days_ago',
    'join_urls',
    'is_valid_url',
    'get_domain_from_url',
    'create_session',
    'set_random_user_agent',
    'DEFAULT_HEADERS'
]