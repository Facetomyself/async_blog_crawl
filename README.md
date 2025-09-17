# 博客爬虫项目

基于 FastAPI 的博客内容爬虫，用于监控更新、抓取数据并校验本地文件。

## 功能特性

- 异步实现，支持高并发请求
- 自动监控分类接口更新（watch）
- 批量抓取月份数据与内容详情（crawl）
- 本地数据校验，支持到每篇内容的明细（verify?detail=true）
- 离线调试：可使用本地样例数据（design/response）
- 结构化日志输出

## 项目结构

```
blog_crawl/
├─ config/
│  └─ settings.py               # 配置
├─ src/
│  ├─ api/
│  │  ├─ app.py                 # FastAPI 应用入口
│  │  ├─ dependencies.py        # 依赖注入（在线/离线 HTTP 客户端）
│  │  └─ routers/
│  │     ├─ watch.py            # /watch 检查更新
│  │     ├─ crawl.py            # /crawl 相关接口
│  │     └─ verify.py           # /verify 本地校验
│  ├─ crawler/
│  │  ├─ base_crawler.py        # 爬虫基类（支持依赖注入）
│  │  ├─ classify_monitor.py    # 分类监控
│  │  ├─ month_data_fetcher.py  # 月份数据获取
│  │  └─ content_fetcher.py     # 内容详情获取
│  ├─ services/
│  │  └─ verification.py        # 本地校验逻辑
│  └─ utils/
│     ├─ http_client.py         # HTTP 客户端（在线/离线桩）
│     ├─ logger.py              # 日志
│     └─ models.py              # 数据模型
├─ data/                        # 本地数据
│  ├─ classify.json
│  ├─ months/
│  ├─ content/
│  └─ images/
├─ design/response/             # 离线样例数据（用于 offline=true）
├─ logs/                        # 日志
├─ main.py                      # 跨平台启动脚本（Python）
├─ pyproject.toml               # uv/构建配置
└─ README.md
```

## 环境与安装

- 要求：Python 3.11+（3.13 已验证），Windows 11

使用 uv 创建虚拟环境并安装依赖：

```bash
uv venv
uv sync
# Windows:  . .venv/Scripts/Activate.ps1
# POSIX:    source .venv/bin/activate
python main.py --port 8000 --reload
```

## 启动与接口

```bash
python main.py --port 8000 --reload

# 访问接口示例
# 健康检查:      GET  http://127.0.0.1:8000/health
# 检查分类更新:  GET  http://127.0.0.1:8000/watch?offline=true
# 校验本地文件:  GET  http://127.0.0.1:8000/verify
# 细粒度校验:    GET  http://127.0.0.1:8000/verify?detail=true
# 执行一次爬取:  POST http://127.0.0.1:8000/crawl/run?offline=true
# 单条内容爬取:  POST http://127.0.0.1:8000/crawl/item/article/123?offline=true
#                POST http://127.0.0.1:8000/crawl/item/section/456?offline=true
#                可加 &force=true 强制重新抓取
```

说明：`offline=true` 使用 `design/response` 下的样例数据，无需网络。

## 跳过逻辑（去重）

- 月份数据：若本地已有 `data/months/<month>.json` 且非空，跳过下载
- 内容详情：若存在 `content/{type}_{id}.md` (>100B) 和对应 `_meta.json` (>10B)，视为已完成并跳过

## 配置说明

主要配置位于 `config/settings.py`：
- `API_BASE_URL`: API 基础 URL
- `MONITOR_INTERVAL`: 监控间隔（秒）
- `REQUEST_TIMEOUT`: 请求超时（秒）
- `MAX_CONCURRENT_REQUESTS`: 最大并发
- `HEADERS` / `IMAGE_HEADERS`: 请求头
- 各类数据保存目录：`DATA_DIR` / `MONTH_DATA_DIR` / `CONTENT_DATA_DIR` / `IMAGES_DIR`

## 备注

- 程序会自动创建必要目录
- 图片下载失败不影响主要内容获取
- 日志位于 `logs/`，控制台与文件双输出，轮转 10MB×5



# 监控接口

```bash
# 启动监控（每 60 秒，离线调试，检测到更新时执行全量抓取）
curl -X POST http://127.0.0.1:8000/monitor/start -H "content-type: application/json" ^
  -d '{"interval_seconds":60,"offline":true,"crawl_on_update":true}'

# 查询状态
curl http://127.0.0.1:8000/monitor/status

# 修改间隔
curl -X POST http://127.0.0.1:8000/monitor/interval -H "content-type: application/json" -d '{"interval_seconds":300}'

# 停止监控
curl -X POST http://127.0.0.1:8000/monitor/stop
```
