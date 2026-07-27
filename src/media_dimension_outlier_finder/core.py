from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import Any

PROJECT = "media-dimension-outlier-finder"


def _require(data: dict[str, Any], key: str) -> Any:
    value = data.get(key)
    if value is None or value == "" or value == []:
        raise ValueError(f"{key} is required")
    return value


def _media_outliers(data: dict[str, Any]) -> dict[str, Any]:
    items = _require(data, "items")
    metrics: dict[str, list[float]] = {
        "width": [],
        "height": [],
        "duration": [],
        "bytes": [],
    }
    prepared = []
    for raw in items:
        item = dict(raw)
        if item.get("path") and ("width" not in item or "height" not in item):
            from PIL import Image

            path = Path(item["path"])
            with Image.open(path) as image:
                item["width"], item["height"] = image.size
            item.setdefault("bytes", path.stat().st_size)
        width, height = (float(item.get("width", 0)), float(item.get("height", 0)))
        item["aspect_ratio"] = round(width / height, 4) if height else None
        prepared.append(item)
        for metric, collected in metrics.items():
            value = item.get(metric)
            if isinstance(value, (int, float)) and value > 0:
                collected.append(float(value))
    medians = {
        metric: statistics.median(values) if values else None for metric, values in metrics.items()
    }
    factor = float(data.get("factor", 2.0))
    outliers = []
    for item in prepared:
        reasons = []
        for metric, median in medians.items():
            value = item.get(metric)
            if (
                median
                and isinstance(value, (int, float))
                and (value > 0)
                and (value > median * factor or value < median / factor)
            ):
                reasons.append(f"{metric}={value} versus median {median:g}")
        if reasons:
            outliers.append(
                {"name": item.get("name") or item.get("path") or "unnamed", "reasons": reasons}
            )
    return {"items": prepared, "medians": medians, "outliers": outliers}


def analyze(data: dict[str, Any]) -> dict[str, Any]:
    return {"version": 1, "project": PROJECT, **_media_outliers(data)}


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, default=str) + "\n"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [f"# {report['project'].replace('-', ' ').title()} report", ""]
    for key, value in report.items():
        if key not in {"version", "project"}:
            lines.extend(
                [
                    f"## {key.replace('_', ' ').title()}",
                    "",
                    f"```json\n{json.dumps(value, indent=2, ensure_ascii=False, default=str)}\n```",
                    "",
                ]
            )
    return "\n".join(lines).rstrip() + "\n"
