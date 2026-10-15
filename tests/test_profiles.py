import math

import pytest

from media_dimension_outlier_finder.core import analyze


def test_mixed_profiles_inclusive_bounds_and_missing():
    profiles = {
        "cover": {"width": {"min": 600, "max": 1200}, "orientation": "portrait"},
        "screen": {"orientation": "landscape", "aspect_ratio": {"min": 2, "max": 2}},
    }
    report = analyze(
        {
            "profiles": profiles,
            "items": [
                {"name": "cover", "width": 600, "height": 900, "profile": "cover"},
                {"width": 1200, "height": 1400, "profile": "cover"},
                {"width": 800, "height": 400, "profile": "screen"},
                {"width": 599, "height": 500, "profile": "cover"},
                {"name": "unknown dimensions", "profile": "cover"},
            ],
        }
    )
    findings = report["profile_findings"]
    assert [item["matches"] for item in findings] == [True, True, True, False, False]
    assert len(findings[3]["reasons"]) == 2
    assert "missing" in " ".join(findings[4]["reasons"])


def test_relative_results_unchanged_without_profiles():
    items = [
        {"width": 100, "height": 100},
        {"width": 100, "height": 100},
        {"width": 1000, "height": 1000, "name": "poster"},
    ]
    legacy = analyze({"items": items})
    profiled = analyze(
        {
            "items": [{**item, "profile": "square"} for item in items],
            "profiles": {"square": {"orientation": "square"}},
        }
    )
    assert legacy["outliers"] == profiled["outliers"]
    assert legacy["medians"] == profiled["medians"]
    assert legacy["profile_findings"] == []


@pytest.mark.parametrize("value", [0, -1, True, "100", None, math.inf, -math.inf, math.nan])
def test_invalid_metrics(value):
    with pytest.raises(ValueError, match="finite positive"):
        analyze({"items": [{"width": value, "height": 100}]})


@pytest.mark.parametrize(
    "profile",
    [
        {},
        {"width": {}},
        {"width": {"min": 2, "max": 1}},
        {"width": {"max": float("nan")}},
        {"width": {"min": 0}},
        {"width": {"max": True}},
        {"orientation": "guess"},
        {"unknown": {"min": 1}},
    ],
)
def test_invalid_profile(profile):
    with pytest.raises(ValueError):
        analyze({"items": [{"width": 100}], "profiles": {"p": profile}})


def test_unknown_profile_and_invalid_factor():
    with pytest.raises(ValueError, match="explicit profile"):
        analyze({"items": [{"profile": "missing"}]})
    for factor in (0, 1, -2, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="factor"):
            analyze({"items": [{"width": 10}], "factor": factor})


def test_image_dimensions_remain_available(tmp_path):
    from PIL import Image

    path = tmp_path / "image.png"
    Image.new("RGB", (20, 10)).save(path)
    report = analyze(
        {
            "items": [{"path": str(path), "profile": "banner"}],
            "profiles": {"banner": {"width": {"min": 20}, "orientation": "landscape"}},
        }
    )
    assert report["profile_findings"][0]["matches"]
