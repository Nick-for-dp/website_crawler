import sys
sys.path.append(".")
from datetime import date, datetime
from typing import Optional
from bs4 import BeautifulSoup

from utils import get_html_from_url, join_urls
from model import News, NewsResponse


class GMRBNewsCrawler:
    def __init__(self) -> None:
        super(GMRBNewsCrawler, self).__init__()
        self.url = r'https://epaper.gmw.cn/gmrb/html/layout/'
    
    def find_gmrb_paper_link(self) -> Optional[str]:
        today = date.today()
        year, month, day = today.year, today.month, today.day
        year_month = f"{year}{month:02d}"
        day = f"{day:02d}"
        url = f"{self.url}{year_month}/{day}/node_01.html"
        return url
    
    def get_news_dict(self):
        gmrb_url = self.find_gmrb_paper_link()
        html_text = get_html_from_url(url=gmrb_url)
        if not html_text:
            return {}
        soup = BeautifulSoup(html_text.encode('utf-8'), "html5lib") # type: ignore
        # 获取头版文章标题列表所在的div
        div_tag = soup.find('div', class_='m-title-list')
        if not div_tag:
            return {}
        # 遍历div下的a标签,获取当日头版新闻的标题和链接
        news_dict = {}
        for a_tag in div_tag.find_all('a', href=True): # type: ignore
            href = a_tag.get('href', None) # type: ignore
            title = a_tag.get_text(strip=True) # type: ignore
            news_dict[title] = join_urls(gmrb_url, href)
        return news_dict
    
    def get_news(self):
        try:
            news_dict = self.get_news_dict()
            news_list = []
            for title, url in news_dict.items():
                child_html_text = get_html_from_url(url=url)
                child_soup = BeautifulSoup(child_html_text.encode('utf-8'), "html5lib") # type: ignore
                content_div_tag = child_soup.find('div', class_="m-article-text")
                p_tags = content_div_tag.find_all('p') # type: ignore
                child_content = ""
                for p_tag in p_tags:
                    child_content += p_tag.get_text(strip=True)
                today = datetime.today()
                today_str = datetime.strftime(today, r"%Y-%m-%d")
                news = News(title=title, 
                            url=url, 
                            origin='光明日报', 
                            summary=child_content, 
                            publish_date=today_str)
                news_list.append(news)
            result = NewsResponse(news_list=news_list) if len(news_list) > 0 else NewsResponse(news_list=None, status="OK", err_code=None, err_info="未在时效范围内爬取到数据")
        except Exception as e:
            result = NewsResponse(news_list=None, status='ERROR', err_code='500', err_info=f'{str(e)}')
        return result
        

if __name__ == '__main__':
    crawler = GMRBNewsCrawler()
    results = crawler.get_news()
    print(results)
