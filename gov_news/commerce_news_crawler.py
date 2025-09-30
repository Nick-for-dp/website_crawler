import sys
sys.path.append(".")
import json
import random
import requests
from typing import Optional
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from utils import get_html_from_url, get_few_days_ago, join_urls
from model import News, NewsResponse


class CommerceNewsCrawler:
    def __init__(self, 
                 url: str):
        super(CommerceNewsCrawler, self).__init__()
        self.url = url
        self.user_agent = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
            ]
    
    def get_news_url_dict_by_playwright(self, child_url):
        url = join_urls(self.url, child_url=child_url)
        few_days = get_few_days_ago(day_offset=4)
        news_url_dict = {}
        with sync_playwright() as p:
            # 启动浏览器（可选chromium、firefox、webkit）
            browser = p.chromium.launch(headless=False)  # headless=True表示无头模式（无界面）
            page = browser.new_page()
            
            try:
                # 访问页面并等待JS渲染完成
                page.goto(url, wait_until="networkidle")  # 等待网络空闲，确保JS渲染完成
            
                # 定位class为"txtList_01"的ul标签
                ul_selector = "ul.txtList_01"
            
                # 等待ul元素出现（防止页面加载慢导致元素未渲染）
                page.wait_for_selector(ul_selector, timeout=1000)  # 超时3秒
            
                # 获取ul下的所有li标签
                li_selector = f"{ul_selector} > li"  # 直接子元素li
            
                # 获取所有li元素
                li_elements = page.query_selector_all(li_selector)
            
                # 提取每个li标签下的url title date
                for li in li_elements:
                    a_tag = li.query_selector("a")  # 查找li下的第一个a标签
                    span_tag = li.query_selector("> span")  # 仅查找直接子span
                    if not a_tag or not span_tag:
                        continue
                    # 提取a标签的href和title
                    href = a_tag.get_attribute("href") or None
                    title = a_tag.get_attribute("title") or None
                    date = span_tag.text_content().strip()[1:-1] or None # type: ignore
                    if date not in few_days:
                        # 跳过超过时效的新闻
                        continue
                    news_title = f"{title};{date}"
                    final_url = join_urls(self.url, child_url=href)
                    news_url_dict[news_title] = final_url
            
                return news_url_dict
        
            except Exception as e:
                print(f"获取过程出错: {str(e)}")
                return {}
        
            finally:
                # 确保浏览器关闭
                browser.close()
    
    def extract_request_params(self, soup: Optional[BeautifulSoup]):
        if not soup:
            return None, None
        # 获取网页信息后检索script
        script_node = None
        for candidate in soup.find_all("script"):
            src = candidate.get("src", "")  # type: ignore
            if "AuthorizedRead/unitbuild.js" in src and candidate.get("querydata"): # type: ignore
                script_node = candidate
                break
        if script_node is None:
            raise RuntimeError(f"未找到包含 queryData 的脚本!")
        # 获取api的url信息
        api_url = script_node.get("url") or ""  # type: ignore
        if not api_url.startswith('http'): # type: ignore
            api_url = urljoin(self.url, api_url) # type: ignore
        raw_query = script_node.get("querydata") # type: ignore
        if not raw_query:
            raise RuntimeError("queryData 为空")

        try:
            params = json.loads(raw_query.replace("'", '"')) # type: ignore
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"无法解析 queryData: {raw_query}") from exc

        normalized_params = {k: str(v) for k, v in params.items() if v is not None}
        return api_url, normalized_params
    
    def simulate_request(self, 
                         index_url: str, 
                         api_url: str, 
                         request_params:dict):
        session = requests.Session()
        session.verify = False
        session.trust_env = False
        headers = {
            "User-Agent": random.choice(self.user_agent),
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.5",
            "Referer": index_url,
            "X-Requested-With": "XMLHttpRequest",
        }
        request_params["pageNo"] = "1"
        resp = session.get(api_url, params=request_params, headers=headers, timeout=15)
        resp.raise_for_status()
        payload = resp.json()
        if not payload.get("success"):
            raise RuntimeError(f"页面{api_url}获取失败")
        html_snippet = (payload.get("data") or {}).get("html")
        if not html_snippet:
            raise RuntimeError(f"页面{api_url}信息获取失败")
        return html_snippet
    
    def get_news_url_dict(self, child_url):
        try:
            url = join_urls(self.url, child_url=child_url)
            html_text = get_html_from_url(url=url)
            soup = BeautifulSoup(html_text.encode('utf-8'), "html5lib")  # type: ignore
            api_url, params = self.extract_request_params(soup=soup)
            # 通过请求获取实际需要的html页面
            html_snippet = self.simulate_request(index_url=url, api_url=api_url, request_params=params) # type: ignore
            html_snippet_soup = BeautifulSoup(html_snippet, "html5lib")
            few_days = get_few_days_ago(day_offset=2)
            news_url_dict = {}
            for li in html_snippet_soup.select("ul.txtList_01 li, ul.txtList_02 li, ul.txtList_03 li"):
                a_tag = li.find("a")
                if not a_tag:
                    continue
                title = (a_tag.get("title") or a_tag.get_text(strip=True) or "").strip() # type: ignore
                href = a_tag.get("href", "").strip() # type: ignore
                if not title or not href:
                    continue
                span = li.find("span")
                date_text = (span.get_text(strip=True) if span else li.get_text(" ", strip=True)).strip("[] ")
                if date_text not in few_days:
                    continue
                title = f"{title};{date_text}"
                complete_url = urljoin(self.url, href)
                news_url_dict[title] = complete_url
            return news_url_dict
        except RuntimeError as e:
            print(e)
        

    def get_news(self):
        try:
            ldrhd_news_url_dict = self.get_news_url_dict(child_url=r'xwfb/ldrhd/index.html')
            bldhd_news_url_dict = self.get_news_url_dict(child_url=r'xwfb/bldhd/index.html')
            merged = {** ldrhd_news_url_dict, ** bldhd_news_url_dict} # type: ignore
            news_lst = []
            for title, url in merged.items():
                html_text = get_html_from_url(url=url)
                soup = BeautifulSoup(html_text.encode('utf-8'), "html5lib")  # type: ignore
                div = soup.find('div', class_='art-con art-con-bottonmLine')
                p_tags = div.find_all('p', style='text-align: justify; text-indent: 2em;') # type: ignore
                text = "".join([p.get_text(strip=True) for p in p_tags])
                title, publish_date = title.split(";")
                news_lst.append(News(title=title, 
                                     url=url,
                                     origin='商务部', 
                                     summary=text, 
                                     publish_date=publish_date))
            return NewsResponse(news_list=news_lst)
        except RuntimeError as e:
            return NewsResponse(news_list=None, status="ERROR", err_code='400', err_info=f"{str(e)}")

if __name__ == '__main__':
    url = r'https://www.mofcom.gov.cn/'
    crawler = CommerceNewsCrawler(url=url)
    print(crawler.get_news())
