"""
Cross-platform launcher for the FastAPI app.

Usage:
  python main.py --host 127.0.0.1 --port 8000 --reload
"""
from __future__ import annotations

import argparse
from pathlib import Path

import uvicorn


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Blog Crawler API server")
    parser.add_argument("--host", default="127.0.0.1", help="Listen host (default: 127.0.0.1)")
    parser.add_argument("--port", "-p", type=int, default=8000, help="Listen port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug", "trace"],
        help="Logging level (default: info)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    # Using import string enables proper reload behavior
    app_path = "src.api.app:app"
    reload_dirs = [str(Path(__file__).parent)] if args.reload else None

    uvicorn.run(
        app_path,
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        reload=args.reload,
        reload_dirs=reload_dirs,
    )


if __name__ == "__main__":
    main()

