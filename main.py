from fastapi import FastAPI
# 导入API路由
from api import cctv_news_router, ai_news_router, gov_news_router


app = FastAPI()


# 注册路由
app.include_router(cctv_news_router, prefix="/api", tags=["CCTV News"])
app.include_router(ai_news_router, prefix="/api", tags=["AI News"])
app.include_router(gov_news_router, prefix="/api", tags=["GOVERNMENT News"])

