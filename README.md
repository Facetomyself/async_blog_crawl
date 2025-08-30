# 博客爬虫项目

基于异步实现的博客内容爬虫，用于监控和下载博客文章及笔记。

## 功能特性

- ✅ 异步实现，支持高并发请求
- ✅ 自动监控分类接口更新
- ✅ 批量获取月份数据（支持断点续传）
- ✅ 下载文章和笔记详情（支持断点续传）
- ✅ 自动下载和替换图片链接（支持断点续传）
- ✅ 完善的日志记录
- ✅ 支持单次执行和监控模式
- ✅ 智能断点续传，大幅提升性能

## 项目结构

```
blog_crawl/
├── config/
│   └── settings.py          # 配置文件
├── src/
│   ├── crawler/
│   │   ├── base_crawler.py      # 基础爬虫类
│   │   ├── classify_monitor.py  # 分类接口监控器
│   │   ├── month_data_fetcher.py # 月份数据获取器
│   │   ├── content_fetcher.py   # 内容详情获取器
│   │   └── __init__.py
│   ├── utils/
│   │   ├── http_client.py       # HTTP客户端
│   │   ├── logger.py           # 日志管理器
│   │   ├── models.py           # 数据模型
│   │   └── __init__.py
│   └── main.py                # 主应用
├── data/                      # 数据存储目录
│   ├── classify.json          # 分类数据
│   ├── months/               # 月份数据
│   │   └── 2020-10.json      # 各月份的文章/笔记列表
│   ├── content/              # 内容详情
│   │   ├── article_123.md    # 文章正文（markdown格式）
│   │   ├── article_123_meta.json # 文章元数据（除body外的所有信息）
│   │   ├── section_456.md    # 笔记正文（markdown格式）
│   │   └── section_456_meta.json # 笔记元数据
│   └── images/               # 下载的图片
├── logs/                     # 日志文件
├── demo.py                   # 演示脚本
├── run.py                    # 启动脚本
├── requirements.txt          # 依赖包
└── README.md                # 说明文档
```

## 环境要求

- Python 3.11+
- conda环境: spider

## 安装和使用

### 1. 环境准备

```bash
# 创建conda环境
conda create -n spider python=3.11 -y

# 激活环境
conda activate spider

# 安装依赖
pip install -r requirements.txt
```

### 2. 单次执行

```bash
# 使用演示脚本
python demo.py

# 或使用启动脚本
python run.py
```

### 3. 监控模式

```bash
# 启动监控模式，默认每小时检查一次
python run.py --monitor

# 自定义监控间隔（秒）
python run.py --monitor --interval 1800
```

## 配置说明

主要配置位于 `config/settings.py`：

- `API_BASE_URL`: API基础URL
- `MONITOR_INTERVAL`: 监控间隔时间（秒）
- `REQUEST_TIMEOUT`: 请求超时时间（秒）
- `MAX_CONCURRENT_REQUESTS`: 最大并发请求数
- `HEADERS`: 请求头配置

## 数据流程

1. **监控阶段**: 检查 `classify` 接口是否有更新
2. **月份数据**: 获取所有月份的文章/笔记列表
3. **内容详情**: 下载每个文章和笔记的完整内容
4. **文件保存**:
   - **正文内容**: 保存为 `{type}_{id}.md` markdown文件（只包含API返回的body字段）
   - **元数据**: 保存为 `{type}_{id}_meta.json` 文件（包含除body外的所有字段）
5. **图片处理**: 自动下载markdown中的图片并替换为本地路径

## 日志管理

- 日志文件存储在 `logs/` 目录
- 支持控制台和文件双重输出
- 日志轮转：单个文件最大10MB，保留5个备份

## 注意事项

- 程序会自动创建必要的目录结构
- 图片下载失败不会影响主要内容的获取
- 支持智能断点续传，避免重复下载
- 分类数据：每次都重新获取（数据量小，变化快）
- 月份数据：检查本地文件，存在则跳过下载
- 内容详情：检查本地markdown文件，存在则跳过下载
- 图片下载：检查本地文件，存在则跳过下载

## 性能说明

通过智能断点续传机制，大幅提升运行效率：

- **首次运行**: 下载所有数据（58个月 + 1179内容项 + 图片）
- **后续运行**: 只下载新增内容，大幅减少重复下载
- **实际效果**: 1179个内容项中，1157个跳过下载，仅下载22个新增内容
- **节省时间**: 避免重复网络请求，显著提升运行速度

## 开发说明

项目遵循以下设计原则：

- **SOLID原则**: 使用类和实例，确保代码的可维护性
- **单一职责**: 每个类负责特定的功能
- **异步优先**: 所有网络请求都使用异步实现
- **错误处理**: 完善的异常处理和日志记录
