import sys
sys.path.append(".")
from fastapi import APIRouter, HTTPException
from paper_news import RMRBNewsCrawler, GMRBNewsCrawler
from model import NewsResponse


paper_news_router = APIRouter()


@paper_news_router.get("/get_daily_rmrb_news")
async def get_daily_rmrb_news() -> NewsResponse:
    """
    获取当日人民日报头版新闻
    """
    try:
        # 创建人民日报爬取机器人
        rmrb_crawler = RMRBNewsCrawler(url=r"http://www.people.com.cn/#lm1")

        # 获取人民日报头版新闻数据
        daily_news = rmrb_crawler.get_news()

        return daily_news

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Website url error: {str(e)}"
        )


@paper_news_router.get("/get_daily_gmrb_news")
async def get_daily_gmrb_news() -> NewsResponse:
    """
    获取当日光明日报头版新闻
    """
    try:
        # 创建光明日报爬取机器人
        gmrb_crawler = GMRBNewsCrawler()

        # 获取光明日报头版新闻数据
        daily_news = gmrb_crawler.get_news()

        return daily_news

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Website url error: {str(e)}"
        )
