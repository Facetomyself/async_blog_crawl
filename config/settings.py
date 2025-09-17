"""
博客爬虫项目配置（UTF-8）
"""
from pathlib import Path


# 路径设置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
LOGS_DIR = BASE_DIR / "logs"


# API 配置
API_BASE_URL = "https://api.cuiliangblog.cn/v1/blog"
CLASSIFY_URL = f"{API_BASE_URL}/classify"
HEADERS = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'origin': 'https://www.cuiliangblog.cn',
    'priority': 'u=1, i',
    'referer': 'https://www.cuiliangblog.cn/',
    'sec-ch-ua': '"Not;A=Brand";v="99", "Microsoft Edge";v="139", "Chromium";v="139"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 Edg/139.0.0.0',
}

# 图片下载专用 headers
IMAGE_HEADERS = {
    'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'accept-encoding': 'gzip, deflate, br',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'referer': 'https://www.yuque.com/',
    'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'image',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}


# 监控与网络配置
MONITOR_INTERVAL = 60  # 监控默认间隔（秒）
MONITOR_DEFAULT_INTERVAL = MONITOR_INTERVAL
MONITOR_DEFAULT_OFFLINE = False
MONITOR_CRAWL_ON_UPDATE_DEFAULT = True

REQUEST_TIMEOUT = 30  # 请求超时（秒）
MAX_CONCURRENT_REQUESTS = 5  # 最大并发请求数


# 日志配置
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5


# 数据文件与目录
CLASSIFY_FILE = DATA_DIR / "classify.json"
MONTH_DATA_DIR = DATA_DIR / "months"
CONTENT_DATA_DIR = DATA_DIR / "content"


# 抓取行为配置
CONTENT_BATCH_SIZE = 10  # 内容抓取分批大小
MIN_MARKDOWN_BYTES = 100  # 判定 markdown 有效的最小字节数
MIN_META_BYTES = 10       # 判定 meta.json 有效的最小字节数


# 确保目录存在
for dir_path in [DATA_DIR, IMAGES_DIR, LOGS_DIR, MONTH_DATA_DIR, CONTENT_DATA_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

