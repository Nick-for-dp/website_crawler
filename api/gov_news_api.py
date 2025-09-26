import sys
sys.path.append(".")
from fastapi import APIRouter, HTTPException
from gov_news import TransportNewsCrawler, CommerceNewsCrawler
from model import NewsResponse


gov_news_router = APIRouter()


@gov_news_router.get("/get_transport_gov_news")
async def get_transport_gov_news() -> NewsResponse:
    """
    获取n-1日的新闻连播内容
    """
    try:
        # 创建交通部新闻爬取机器人
        url = r'https://www.mot.gov.cn/jiaotongyaowen/'
        transport_gov_news_crawler = TransportNewsCrawler(url=url)
        
        # 获取交通部新闻内容数据
        daily_news = transport_gov_news_crawler.get_news()
        
        return daily_news
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Website url error: {str(e)}"
        )


@gov_news_router.get("/get_commerce_gov_news")
async def get_commerce_gov_news() -> NewsResponse:
    """
    获取n-1日的新闻连播内容
    """
    try:
        # 创建商务部新闻爬取机器人
        url = r'https://www.mofcom.gov.cn/'
        commerce_gov_news_crawler = CommerceNewsCrawler(url=url)
        
        # 获取商务部新闻内容数据
        daily_news = commerce_gov_news_crawler.get_news()
        
        return daily_news
        
    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Website url error: {str(e)}"
        )
