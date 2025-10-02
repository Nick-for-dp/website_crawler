import sys
sys.path.append(".")
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup

from utils import get_html_from_url, get_few_days_ago, join_urls
from model import News, NewsResponse


class CommerceNewsAdvancedCrawler:
    def __init__(self, 
                 url: str,
                 headless: bool = False,
                 timeout: int = 5):
        super(CommerceNewsAdvancedCrawler, self).__init__()
        self.url = url
        self.headless = headless
        self.timeout = timeout
    
    def _setup_driver(self):
        """设置Selenium WebDriver"""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)  # 设置隐式等待时间
        return driver
    
    def get_news_url_dict(self, child_url):
        """使用Selenium获取新闻URL字典"""
        url = join_urls(self.url, child_url=child_url)
        few_days = get_few_days_ago(day_offset=1)
        news_url_dict = {}
        
        driver = self._setup_driver()
        try:
            # 访问页面
            driver.get(url)
            
            # 等待页面加载完成
            wait = WebDriverWait(driver, self.timeout)
            
            # 等待ul元素出现
            ul_selector = "ul.txtList_01"
            ul_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ul_selector))
            )
            
            # 获取所有li元素
            li_elements = ul_element.find_elements(By.CSS_SELECTOR, "li")
            
            # 提取每个li标签下的url title date
            for li in li_elements:
                try:
                    # 查找li下的第一个a标签
                    a_tag = li.find_element(By.CSS_SELECTOR, "a")
                    # 查找直接子span标签
                    span_tag = li.find_element(By.CSS_SELECTOR, "span")
                    
                    # 提取a标签的href和title
                    href = a_tag.get_attribute("href") or None
                    title = a_tag.get_attribute("title") or a_tag.text.strip() or None
                    date_text = span_tag.text.strip() if span_tag else None
                    
                    if date_text:
                        # 处理日期格式，去掉括号
                        date = date_text[1:-1] if date_text.startswith('[') and date_text.endswith(']') else date_text
                    else:
                        date = None
                    
                    if not all([href, title, date]):
                        continue
                    
                    if date not in few_days:
                        # 跳过超过时效的新闻
                        continue
                    
                    news_title = f"{title};{date}"
                    final_url = join_urls(self.url, child_url=href)
                    news_url_dict[news_title] = final_url
                    
                except NoSuchElementException:
                    # 如果某个元素不存在，跳过这个li
                    continue
                except Exception as e:
                    print(f"处理li元素时出错: {str(e)}")
                    continue
            
            return news_url_dict
        
        except TimeoutException:
            print(f"等待元素超时: {url}")
            return {}
        except Exception as e:
            print(f"获取过程出错: {str(e)}")
            return {}
        
        finally:
            # 确保浏览器关闭
            driver.quit()
    
    def get_news(self):
        """获取新闻列表"""
        ldrhd_news_url_dict = self.get_news_url_dict(child_url=r'xwfb/ldrhd/index.html')
        bldhd_news_url_dict = self.get_news_url_dict(child_url=r'xwfb/bldhd/index.html')
        merged = {**ldrhd_news_url_dict, **bldhd_news_url_dict}
        news_lst = []
        
        for title, url in merged.items():
            try:
                html_text = get_html_from_url(url=url)
                if not html_text:
                    continue
                    
                soup = BeautifulSoup(html_text.encode('utf-8'), "html5lib")
                
                # 获取文章内容
                div = soup.find('div', class_='art-con art-con-bottonmLine')
                p_tags = div.find_all('p', style='text-align: justify; text-indent: 2em;') # type: ignore
                text = "".join([p.get_text(strip=True) for p in p_tags])
                
                title_part, publish_date = title.split(";")
                news_lst.append(News(
                    title=title_part, 
                    url=url,
                    origin='商务部', 
                    summary=text, 
                    publish_date=publish_date
                ))
                
            except Exception as e:
                print(f"处理新闻内容时出错 {url}: {str(e)}")
                continue
        result = NewsResponse(news_list=news_lst) if len(news_lst) > 0 else NewsResponse(news_list=None, status="OK", err_code=None, err_info="未在时效范围内爬取到数据")
        return result


if __name__ == '__main__':
    url = r'https://www.mofcom.gov.cn/'
    crawler = CommerceNewsAdvancedCrawler(url=url, headless=False)
    result = crawler.get_news()
    print(result)