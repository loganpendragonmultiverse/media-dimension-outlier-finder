from __future__ import annotations

import json
import math
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
    profiles = data.get("profiles", {})
    if not isinstance(profiles, dict):
        raise TypeError("profiles must be an object of named profiles")
    supported = {"width", "height", "duration", "bytes", "aspect_ratio"}
    for name, profile in profiles.items():
        if (
            not isinstance(name, str)
            or not name.strip()
            or not isinstance(profile, dict)
            or not profile
        ):
            raise ValueError("profiles require nonempty names and constraints")
        for metric, bounds in profile.items():
            if metric == "orientation":
                if bounds not in ("portrait", "landscape", "square"):
                    raise ValueError("orientation must be portrait, landscape or square")
                continue
            if (
                metric not in supported
                or not isinstance(bounds, dict)
                or not bounds
                or set(bounds) - {"min", "max"}
            ):
                raise ValueError("profile metrics require min and/or max bounds")
            for value in bounds.values():
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    or value <= 0
                ):
                    raise ValueError("profile bounds must be finite positive numbers")
            if bounds.get("min", 0) > bounds.get("max", float("inf")):
                raise ValueError("profile minimum exceeds maximum")
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
        for metric in ("width", "height", "duration", "bytes"):
            if metric in item:
                value = item[metric]
                if (
                    isinstance(value, bool)
                    or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    or value <= 0
                ):
                    raise ValueError(f"{metric} must be a finite positive number")
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
    if not math.isfinite(factor) or factor <= 1:
        raise ValueError("factor must be finite and greater than one")
    profile_findings = []
    for index, item in enumerate(prepared):
        if "profile" not in item:
            continue
        name = item["profile"]
        if not isinstance(name, str) or name not in profiles:
            raise ValueError("item profile must name an explicit profile")
        reasons = []
        for metric, bounds in profiles[name].items():
            if metric == "orientation":
                if "width" not in item or "height" not in item:
                    reasons.append("orientation: missing width or height")
                else:
                    actual = (
                        "square"
                        if item["width"] == item["height"]
                        else ("landscape" if item["width"] > item["height"] else "portrait")
                    )
                    if actual != bounds:
                        reasons.append(f"orientation={actual}, expected {bounds}")
            else:
                value = item.get(metric)
                if value is None:
                    reasons.append(f"{metric}: missing metadata")
                elif value < bounds.get("min", 0) or value > bounds.get("max", float("inf")):
                    reasons.append(f"{metric}={value} outside expected bounds")
        profile_findings.append(
            {
                "source_index": index,
                "name": item.get("name") or item.get("path") or "unnamed",
                "profile": name,
                "matches": not reasons,
                "reasons": reasons,
            }
        )
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
    return {
        "items": prepared,
        "medians": medians,
        "outliers": outliers,
        "profiles": profiles,
        "profile_findings": profile_findings,
    }


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
