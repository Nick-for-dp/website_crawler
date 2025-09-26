import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import time
import random
from urllib.parse import urlparse, urljoin
import logging


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 默认请求头
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}


def get_few_days_ago(day_offset) -> List[str]:
    today = datetime.today()
    few_days = [today - timedelta(days=offset) for offset in range(0, day_offset)]
    return [datetime.strftime(day, r"%Y-%m-%d") for day in few_days]


def join_urls(base_url, child_url):
    """
    将base_url和child_url拼接成合法的完整URL
    
    参数:
        base_url: 基础URL，如https://www.mot.gov.cn/jiaotongyaowen/
        child_url: 子URL，可以是相对路径，如./202509/t20250918_4176896.html
        
    返回:
        str: 拼接后的完整URL
    """
    return urljoin(base_url, child_url)


def get_html_from_url(url: Optional[str], 
                     headers: Optional[Dict[str, str]] = None,
                     timeout: int = 10,
                     retries: int = 3,
                     delay: float = 1.0) -> Optional[str]:
    """
    通过requests库获取URL的HTML内容
    
    Args:
        url: 目标URL
        headers: 请求头，默认为DEFAULT_HEADERS
        timeout: 请求超时时间（秒）
        retries: 重试次数
        delay: 重试延迟（秒）
    
    Returns:
        HTML内容字符串，如果失败返回None
    """
    if not is_valid_url(url=url): # type: ignore
        logger.error("请求失败: 输入的url不合法，请重新确认")
        return None
    else:
        logger.info(f"正在请求{url}")
    
    if headers is None:
        headers = DEFAULT_HEADERS.copy()
    
    for attempt in range(retries):
        try:
            logger.info(f"正在请求URL: {url} (尝试 {attempt + 1}/{retries})")
            
            response = requests.get(
                url,  # type: ignore
                headers=headers, 
                timeout=timeout,
                verify=False  # 忽略SSL证书验证
            )
            
            response.raise_for_status()  # 检查HTTP错误
            
            # 检查内容类型是否为HTML
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                logger.warning(f"响应内容类型不是HTML: {content_type}")
            response.encoding = response.apparent_encoding
            html_content = response.text
            logger.info(f"成功获取HTML内容，长度: {len(html_content)} 字符")
            return html_content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"请求失败 (尝试 {attempt + 1}/{retries}): {e}")
            
            if attempt < retries - 1:
                # 添加随机延迟避免被ban
                sleep_time = delay * (1 + random.random() * 0.5)
                logger.info(f"等待 {sleep_time:.2f} 秒后重试...")
                time.sleep(sleep_time)
            else:
                logger.error(f"所有 {retries} 次尝试都失败了")
                return None
    
    return None

def is_valid_url(url: str) -> bool:
    """检查URL是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_domain_from_url(url: str) -> Optional[str]:
    """从URL中提取域名"""
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc
    except:
        return None

def create_session() -> requests.Session:
    """创建并配置一个requests会话"""
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    return session

def set_random_user_agent(headers: Dict[str, str]) -> Dict[str, str]:
    """设置随机User-Agent"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
    ]
    
    headers = headers.copy()
    headers['User-Agent'] = random.choice(user_agents)
    return headers

# 示例用法
if __name__ == "__main__":
    # 测试get_html_from_url函数
    test_url = r"https://tv.cctv.com/lm/xwlb/index.shtml"
    html = get_html_from_url(test_url)
    
    if html:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html.encode('utf-8'), "html5lib")
        ul_element = soup.find('ul', id="content")
        print(f"HTML ul内容是：{ul_element}") # type: ignore
    else:
        print("获取HTML失败")
