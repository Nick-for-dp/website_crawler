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
2. **央视新闻联播** - https://tv.cctv.com/lm/xwlb/ (t-1日)
3. **商务部新闻** - https://www.mofcom.gov.cn/
4. **交通部新闻** - https://www.mot.gov.cn/xinwen/jiaotongyaowen/
5. **人民日报** - https://paper.people.com.cn/rmrb/ (当日头版)
6. **光明日报** - https://epaper.gmw.cn/gmrb/ (当日头版)

### 自动化管线
- **每日采集落库** - cron 早 8 点执行 `scripts/collect_daily.py`，六源新闻去重写入 SQLite
- **大模型简报推送** - cron 早 9 点执行 `scripts/push_daily_digest.py`，DeepSeek 归纳后经钉钉机器人推送到群（已推送过的不重复推送）
- **超期数据清理** - cron 每月 1 日凌晨执行 `scripts/cleanup_old_news.py`，清理一年前的历史数据

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

### 获取政府新闻
```http
GET /api/get_transport_gov_news
GET /api/get_commerce_gov_news
```
返回交通部 / 商务部时效窗口内的官方新闻

### 获取纸媒头版
```http
GET /api/get_daily_rmrb_news
GET /api/get_daily_gmrb_news
```
返回当日人民日报 / 光明日报头版新闻

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
├── AGENTS.md              # AI 协作者指南（约定与路线图）
├── .env.example           # 密钥配置模板
│
├── ai_news/               # AI新闻爬虫模块
│   └── ai_new_crawler.py  # Aibase新闻爬虫
│
├── cctv_news/             # 央视新闻模块
│   └── cctv_news_crawler.py # 新闻联播爬虫
│
├── gov_news/              # 政府新闻模块
│   ├── commerce_news_crawler.py  # 商务部新闻爬虫
│   ├── commerce_news_advanced_crawler.py # 商务部(Selenium备用)
│   └── transport_news_crawler.py # 交通部新闻爬虫
│
├── paper_news/            # 纸媒模块
│   ├── rmrb_news_crawler.py    # 人民日报(当日头版)
│   └── gmrb_news_crawler.py    # 光明日报(当日头版)
│
├── api/                   # API接口模块
│   ├── ai_news_api.py     # AI新闻API
│   ├── cctv_news_api.py   # 央视新闻API
│   ├── gov_news_api.py    # 政府新闻API
│   └── paper_news_api.py  # 纸媒API
│
├── storage/               # SQLite持久化
│   └── db.py              # 建表/去重落库/推送登记/超期清理
│
├── llm/                   # 大模型归纳
│   └── summarizer.py      # DeepSeek简报生成(OpenAI兼容协议)
│
├── notify/                # 消息推送
│   └── dingtalk.py        # 钉钉群机器人(加签模式)
│
├── scripts/               # 定时任务入口(cron调用)
│   ├── collect_daily.py       # 每日采集落库
│   ├── push_daily_digest.py   # 每日简报推送
│   └── cleanup_old_news.py    # 超期数据清理
│
├── model/                 # 数据模型
│   └── response/
│       ├── news.py        # 新闻数据模型
│       └── news_response.py # API响应模型
│
└── utils/                 # 工具函数
    └── tool.py           # 通用工具函数
```

## 🔧 环境部署适配

### 开发环境配置
1. **Python环境**：使用UV管理Python环境和依赖
2. **浏览器依赖**：需要安装Playwright的Chromium浏览器
3. **网络要求**：需要能够访问目标新闻网站

### 生产环境部署（Ubuntu）

```bash
# 1. 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# 2. 克隆项目
git clone https://github.com/Nick-for-dp/website_crawler.git /opt/website_crawler
cd /opt/website_crawler

# 3. 安装依赖（自动创建虚拟环境）
uv sync

# 4. 配置密钥：DeepSeek API Key + 钉钉机器人 webhook/secret
cp .env.example .env
vim .env

# 5. 创建日志目录
mkdir -p logs

# 6. 手动验证一次完整管线（采集 → 落库 → 简报 → 推送）
uv run scripts/collect_daily.py
uv run scripts/push_daily_digest.py

# 7. 配置定时任务
crontab -e
```

crontab 内容（早 8 点采集、早 9 点推送、每月 1 日凌晨清理超期数据）：

```cron
0 8 * * * cd /opt/website_crawler && uv run scripts/collect_daily.py >> logs/collect.log 2>&1
0 9 * * * cd /opt/website_crawler && uv run scripts/push_daily_digest.py >> logs/digest.log 2>&1
0 3 1 * * cd /opt/website_crawler && uv run scripts/cleanup_old_news.py >> logs/cleanup.log 2>&1
```

如需对外提供 API 服务，可配合 systemd 常驻：

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

> 说明：日常采集与推送管线仅需 requests，无需浏览器；仅当商务部主用方案失效、需要 Playwright/Selenium 备用爬虫时，才执行 `uv run playwright install chromium`。

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
密钥配置在项目根目录 `.env` 文件中（模板见 `.env.example`，`.env` 已被 `.gitignore` 排除，严禁入库）：
- `deepseek_api_key`: DeepSeek API Key，大模型归纳简报用
- `dingding_webhook`: 钉钉群自定义机器人 webhook
- `dingding_secret`: 钉钉机器人加签密钥（SEC 开头）

可选环境变量：
- `NEWS_DB_PATH`: SQLite 库文件路径（默认 `data/news.db`）
- `UV_INDEX_URL`: PyPI镜像地址（默认为清华镜像）

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