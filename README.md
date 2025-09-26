# Website Crawler 网站爬虫项目

一个基于FastAPI的多源新闻爬虫系统，支持从多个网站抓取新闻内容并提供统一的API接口。

## 📋 项目概述

### 代码用途
本项目是一个多源新闻爬虫系统，主要功能包括：
- **AI新闻爬取** - 从Aibase网站抓取每日AI新闻
- **央视新闻爬取** - 从CCTV新闻联播网站抓取新闻内容
- **政府新闻爬取** - 从商务部和交通部网站抓取官方新闻
- **统一API接口** - 提供RESTful API接口供外部调用
- **数据标准化** - 统一的数据模型和响应格式

### 支持的数据源
1. **AI新闻** - https://news.aibase.com/zh/daily
2. **央视新闻联播** - https://tv.cctv.com/lm/xwlb/index.shtml
3. **商务部新闻** - https://www.mofcom.gov.cn/
4. **交通部新闻** - https://www.mot.gov.cn/jiaotongyaowen/

## 🚀 快速开始

### 环境要求
- Python 3.13+
- UV包管理工具
- Playwright (用于浏览器自动化)

### 安装依赖
```bash
# 使用uv安装依赖
uv sync

# 安装Playwright浏览器
playwright install chromium
```

### 启动服务
```bash
# 使用uv运行FastAPI服务
uv run main.py

# 或者使用uvicorn直接运行
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后，访问 http://localhost:8000/docs 查看API文档。

## 📊 API接口

### 获取AI新闻
```http
GET /api/get_daily_ai_news
```
返回当日Aibase网站的AI新闻内容

### 获取央视新闻
```http
GET /api/get_daily_cctv_news
```
返回前一天的新闻联播内容

### 响应格式
所有API返回统一的JSON格式：
```json
{
  "news_list": [
    {
      "title": "新闻标题",
      "url": "新闻原文链接",
      "origin": "来源网站",
      "summary": "新闻摘要",
      "publish_date": "发布日期"
    }
  ],
  "status": "OK",
  "err_code": null,
  "err_info": null
}
```

## 🏗️ 项目结构

```
website-crawler/
├── main.py                 # FastAPI主应用
├── pyproject.toml          # 项目配置和依赖
├── uv.lock                 # 依赖锁文件
├── README.md              # 项目说明文档
│
├── ai_news/               # AI新闻爬虫模块
│   ├── __init__.py
│   └── ai_new_crawler.py  # Aibase新闻爬虫
│
├── cctv_news/             # 央视新闻模块
│   ├── __init__.py
│   └── cctv_news_crawler.py # 新闻联播爬虫
│
├── gov_news/              # 政府新闻模块
│   ├── __init__.py
│   ├── commerce_news_crawler.py  # 商务部新闻爬虫
│   └── transport_news_crawler.py # 交通部新闻爬虫
│
├── api/                   # API接口模块
│   ├── __init__.py
│   ├── ai_news_api.py     # AI新闻API
│   └── cctv_news_api.py   # 央视新闻API
│
├── model/                 # 数据模型
│   ├── __init__.py
│   └── response/
│       ├── __init__.py
│       ├── news.py        # 新闻数据模型
│       └── news_response.py # API响应模型
│
└── utils/                 # 工具函数
    ├── __init__.py
    └── tool.py           # 通用工具函数
```

## 🔧 环境部署适配

### 开发环境配置
1. **Python环境**：使用UV管理Python环境和依赖
2. **浏览器依赖**：需要安装Playwright的Chromium浏览器
3. **网络要求**：需要能够访问目标新闻网站

### 生产环境部署
```bash
# 1. 克隆项目
git clone <repository-url>
cd website-crawler

# 2. 创建虚拟环境并安装依赖
uv venv
uv sync

# 3. 安装Playwright浏览器
playwright install chromium

# 4. 使用生产级服务器运行
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker部署
```dockerfile
FROM python:3.13-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装Python依赖
RUN /root/.cargo/bin/uv sync

# 安装Playwright浏览器
RUN /root/.cargo/bin/uv run playwright install chromium

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["/root/.cargo/bin/uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 环境变量配置
项目支持以下环境变量：
- `UV_INDEX_URL`: PyPI镜像地址（默认为清华镜像）
- `REQUEST_TIMEOUT`: 请求超时时间（默认10秒）
- `RETRY_COUNT`: 重试次数（默认3次）

## 🛠️ 技术栈

- **Web框架**: FastAPI
- **HTML解析**: BeautifulSoup4
- **浏览器自动化**: Playwright
- **HTTP请求**: Requests
- **数据验证**: Pydantic
- **包管理**: UV
- **日志**: Python logging

## 📝 开发说明

### 添加新的爬虫
1. 在相应的模块目录下创建新的爬虫类
2. 实现`get_news()`方法返回`NewsResponse`对象
3. 在api目录下创建对应的API路由
4. 在主应用中注册路由

### 调试爬虫
```bash
# 直接运行爬虫测试
uv run ai_news/ai_new_crawler.py

# 或者使用Python直接运行
python -m ai_news.ai_new_crawler
```

## ⚠️ 注意事项

1. **反爬虫策略**：项目已实现随机User-Agent和请求延迟，但请合理使用
2. **网络稳定性**：爬虫依赖网络连接，建议部署在稳定的网络环境中
3. **网站结构变化**：目标网站结构变化时需要相应更新爬虫逻辑
4. **法律合规**：请确保爬取行为符合目标网站的使用条款和法律法规

## 📄 许可证

MIT License