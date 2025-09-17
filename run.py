#!/usr/bin/env python3
"""
博客爬虫启动脚本
"""
import sys
from pathlib import Path

# 添加src目录到Python路径
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    # 导入并运行主应用
    from src.main import main
    import asyncio

    asyncio.run(main())
