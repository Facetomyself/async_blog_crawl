"""
数据模型定义
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime


class MonthStats(BaseModel):
    """月份统计数据"""
    month: str
    article: int
    section: int


class ContentItem(BaseModel):
    """内容项数据"""
    type: str  # "article" 或 "section"
    id: int
    title: str
    created_time: str


class ArticleDetail(BaseModel):
    """文章详情"""
    id: int
    category: str
    category_id: int
    tags: List[Dict[str, Any]]
    title: str
    abstract: str
    cover: Optional[str]
    body: str
    view: int
    like: int
    collect: int
    comment: int
    created_time: str
    modified_time: str
    is_recommend: bool
    is_release: bool
    author: int


class SectionDetail(BaseModel):
    """笔记详情"""
    id: int
    note: str
    note_id: int
    title: str
    body: str
    view: int
    like: int
    collect: int
    comment: int
    created_time: str
    modified_time: str
    slug: str
    author: int


class CrawlResult(BaseModel):
    """爬取结果"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.now()


class ImageDownloadResult(BaseModel):
    """图片下载结果"""
    url: str
    local_path: Optional[str] = None
    success: bool
    error: Optional[str] = None
    timestamp: datetime = datetime.now()
