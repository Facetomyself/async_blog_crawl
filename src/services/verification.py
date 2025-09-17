from pathlib import Path
from typing import Dict, Any, List, Tuple, Set

from config.settings import CLASSIFY_FILE, MONTH_DATA_DIR, CONTENT_DATA_DIR, IMAGES_DIR, MIN_MARKDOWN_BYTES, MIN_META_BYTES


class Verifier:
    def verify(self, detail: bool = False) -> Dict[str, Any]:
        classify = self._verify_classify()
        months = self._verify_months(classify)
        content = self._verify_content()

        items_summary = self._verify_items(detail=detail)

        overall_ok = classify["exists"] and months["ok"] and content["ok"] and items_summary["ok"]
        return {
            "ok": overall_ok,
            "classify": classify,
            "months": months,
            "content": content,
            "items": items_summary,
        }

    def _verify_classify(self) -> Dict[str, Any]:
        exists = CLASSIFY_FILE.exists()
        count = 0
        error = None
        if exists:
            try:
                import json
                data = json.loads(CLASSIFY_FILE.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    count = len(data.keys())
            except Exception as e:
                error = str(e)
        return {"exists": exists, "month_count": count, "error": error}

    def _verify_months(self, classify: Dict[str, Any]) -> Dict[str, Any]:
        files: List[Path] = sorted(MONTH_DATA_DIR.glob("*.json"))
        file_months = {f.stem for f in files}
        missing: List[str] = []
        if classify.get("month_count"):
            try:
                import json
                data = json.loads(CLASSIFY_FILE.read_text(encoding="utf-8"))
                expected_months = set(data.keys())
                missing = sorted(list(expected_months - file_months))
            except Exception:
                pass
        ok = len(missing) == 0 and len(files) > 0
        return {"ok": ok, "files": [str(f) for f in files], "missing": missing}

    def _verify_content(self) -> Dict[str, Any]:
        # 检查 content 下 .md 与 _meta.json 成对
        md_files = {p.stem for p in CONTENT_DATA_DIR.glob("*.md")}
        meta_files = {p.stem.replace("_meta", "") for p in CONTENT_DATA_DIR.glob("*_meta.json")}
        missing_md = sorted(list(meta_files - md_files))
        missing_meta = sorted(list(md_files - meta_files))

        # 粗略检查 markdown 中图片是否存在
        broken_images: List[str] = []
        for md_path in CONTENT_DATA_DIR.glob("*.md"):
            try:
                text = md_path.read_text(encoding="utf-8", errors="ignore")
                import re
                for _, url in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
                    if url.startswith("./images/"):
                        name = url.split("/")[-1]
                        if not (IMAGES_DIR / name).exists():
                            broken_images.append(f"{md_path.name}:{name}")
            except Exception:
                continue

        ok = len(missing_md) == 0 and len(missing_meta) == 0
        return {
            "ok": ok,
            "missing_md": missing_md,
            "missing_meta": missing_meta,
            "broken_images": broken_images,
        }

    def _collect_expected_items(self) -> List[Tuple[str, int]]:
        expected: Set[Tuple[str, int]] = set()
        for f in sorted(MONTH_DATA_DIR.glob("*.json")):
            try:
                import json
                data = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    for item in data:
                        t = item.get("type")
                        i = item.get("id")
                        if isinstance(t, str) and isinstance(i, int):
                            expected.add((t, i))
            except Exception:
                continue
        return sorted(list(expected))

    def _verify_items(self, detail: bool = False) -> Dict[str, Any]:
        expected = self._collect_expected_items()
        total_expected = len(expected)

        present = set()
        issues: List[Dict[str, Any]] = []

        for t, i in expected:
            md = CONTENT_DATA_DIR / f"{t}_{i}.md"
            meta = CONTENT_DATA_DIR / f"{t}_{i}_meta.json"
            has_md = md.exists() and md.stat().st_size > MIN_MARKDOWN_BYTES
            has_meta = meta.exists() and meta.stat().st_size > MIN_META_BYTES

            broken: List[str] = []
            if has_md:
                try:
                    text = md.read_text(encoding="utf-8", errors="ignore")
                    import re
                    for _, url in re.findall(r"!\[[^\]]*\]\(([^)]+)\)", text):
                        if url.startswith("./images/"):
                            name = url.split("/")[-1]
                            if not (IMAGES_DIR / name).exists():
                                broken.append(name)
                except Exception:
                    pass

            if has_md and has_meta and not broken:
                present.add((t, i))
            else:
                issues.append({
                    "type": t,
                    "id": i,
                    "missing_md": not has_md,
                    "missing_meta": not has_meta,
                    "broken_images": broken[:5],
                })

        ok = len(issues) == 0
        summary: Dict[str, Any] = {
            "ok": ok,
            "total_expected": total_expected,
            "complete_count": len(present),
            "incomplete_count": len(issues),
        }
        if detail:
            summary["issues"] = issues
        return summary

