import sys
sys.path.append(".")
from datetime import date, datetime
from typing import Optional
from bs4 import BeautifulSoup

from utils import get_html_from_url, join_urls
from model import News, NewsResponse
import requests


class RMRBNewsCrawler:
    def __init__(self, url) -> None:
        super(RMRBNewsCrawler, self).__init__()
        self.url = url
        self.basic_url = r'https://paper.people.com.cn/rmrb/pc/'
    
    def find_rmrb_paper_link(self) -> Optional[str]:
        today = date.today()
        year, month, day = today.year, today.month, today.day
        year_month = f"{str(year)}{str(month)}"
        day = f"0{str(day)}" if day < 10 else day
        url = f"{self.basic_url}layout/{year_month}/{day}/node_01.html"
        return url
    
    def _get_html_with_encoding(self, url, encoding='utf-8'):
        """专门为人民日报网站获取HTML，使用指定编码"""
        try:
            response = requests.get(url, timeout=10, verify=False)
            response.raise_for_status()
            response.encoding = encoding
            return response.text
        except Exception as e:
            print(f"获取HTML失败: {e}")
            return None
    
    def get_news_dict(self):
        rmrb_url = self.find_rmrb_paper_link()
        html_text = self._get_html_with_encoding(rmrb_url, encoding='utf-8')
        if not html_text:
            return {}
        soup = BeautifulSoup(html_text, "html5lib") # type: ignore
        # 获取包含日报跳转链接的ul标签
        ul_tag = soup.find('ul', class_='news-list')
        # 遍历ul标签下的li标签,获取当日新闻的标题和链接
        news_dict = {}
        for li_tag in ul_tag.find_all('li'): # type: ignore
            a_tag = li_tag.find('a') # type: ignore
            href = a_tag.get('href', None) # type: ignore
            title = a_tag.get_text(strip=True) # type: ignore
            news_dict[title] = join_urls(rmrb_url, href)
        return news_dict
    
    def get_news(self):
        try:
            news_dict = self.get_news_dict()
            news_list = []
            for title, url in news_dict.items():
                child_html_text = self._get_html_with_encoding(url, encoding='utf-8')
                if not child_html_text:
                    continue
                child_soup = BeautifulSoup(child_html_text, "html5lib") # type: ignore
                content_div_tag = child_soup.find('div', id="ozoom")
                p_tags = content_div_tag.find_all('p') # type: ignore
                child_content = ""
                for p_tag in p_tags:
                    child_content += p_tag.get_text(strip=True)
                today = datetime.today()
                today_str = datetime.strftime(today, r"%Y-%m-%d")
                news = News(title=title, 
                            url=url, 
                            origin='人民日报', 
                            summary=child_content, 
                            publish_date=today_str)
                news_list.append(news)
            result = NewsResponse(news_list=news_list) if len(news_list) > 0 else NewsResponse(news_list=None, status="OK", err_code=None, err_info="未在时效范围内爬取到数据")
        except Exception as e:
            result = NewsResponse(news_list=None, status='ERROR', err_code='500', err_info=f'{str(e)}')
        return result
        

if __name__ == '__main__':
    url = r"http://www.people.com.cn/#lm1"
    crawler = RMRBNewsCrawler(url=url)
    results = crawler.get_news()
    print(results)
