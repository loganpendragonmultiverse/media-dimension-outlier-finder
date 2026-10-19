import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from media_dimension_outlier_finder.cli import main
from media_dimension_outlier_finder.core import analyze


def valid_input():
    return {"items": [{"width": 10, "height": 20}]}


@pytest.mark.parametrize("data", [None, [], "text", 4, True])
def test_nonobject_input_has_clean_cli_error(data, tmp_path, capsys):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    output = tmp_path / "report.json"
    assert main([str(source), "--output", str(output)]) == 2
    captured = capsys.readouterr()
    assert "input must be a JSON object" in captured.err
    assert not captured.out and not output.exists()


def test_dangling_output_link_is_preserved(tmp_path, capsys):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(valid_input()), encoding="utf-8")
    target, output = tmp_path / "target.json", tmp_path / "report.json"
    try:
        output.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable")
    assert main([str(source), "--output", str(output)]) == 2
    assert output.is_symlink() and not target.exists()
    assert capsys.readouterr().err.startswith("error:")


def test_concurrently_created_output_is_preserved(tmp_path, monkeypatch, capsys):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(valid_input()), encoding="utf-8")
    before = source.read_bytes()
    output = tmp_path / "report.json"
    original_open = Path.open
    injected = False

    def competing_open(path, mode="r", *args, **kwargs):
        nonlocal injected
        if path == output and mode in {"w", "x"} and not injected:
            injected = True
            with original_open(path, "w", encoding="utf-8") as handle:
                handle.write("concurrent user report")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", competing_open)
    assert main([str(source), "--output", str(output)]) == 2
    assert injected and output.read_text() == "concurrent user report"
    assert source.read_bytes() == before
    assert capsys.readouterr().err.startswith("error:")


@pytest.mark.parametrize(
    "data",
    [
        {"items": 5},
        {"items": {}},
        {"items": [None]},
        {"items": [{}], "profiles": []},
        {"items": [{}], "factor": None},
        {"items": [{}], "factor": 10**400},
        {"items": [{"width": 10**400}]},
        {"items": [{"path": 8}]},
        {"items": [{}], "profiles": {"p": {"width": {"min": 10**400}}}},
    ],
)
def test_malformed_or_unrepresentable_values_are_actionable(data, tmp_path, capsys):
    source, output = tmp_path / "source.json", tmp_path / "report.json"
    source.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        analyze(data)
    assert main([str(source), "--output", str(output)]) == 2
    captured = capsys.readouterr()
    assert captured.err.startswith("error:") and "Traceback" not in captured.err
    assert not captured.out and not output.exists()


def test_large_finite_medians_do_not_create_false_outliers_or_invalid_json():
    report = analyze({"items": [{"width": 1e308}, {"width": 1e308}]})
    assert report["medians"]["width"] == 1e308
    assert report["outliers"] == []
    json.dumps(report, allow_nan=False)


def test_ordinary_even_and_odd_medians_remain_unchanged():
    for values, expected in [([2, 8], 5), ([8, 2, 4], 4), ([1, 1, 100], 1)]:
        report = analyze({"items": [{"width": value} for value in values]})
        assert report["medians"]["width"] == expected


def test_closed_stdout_reader_is_a_clean_process_error(tmp_path):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(valid_input()), encoding="utf-8")
    reader, writer = os.pipe()
    os.close(reader)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "media_dimension_outlier_finder", str(source)],
            check=False,
            stdout=writer,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
    finally:
        os.close(writer)
    assert result.returncode == 2
    assert "Traceback" not in result.stderr and "Exception ignored" not in result.stderr


@pytest.mark.skipif(not Path("/dev/full").exists(), reason="/dev/full device unavailable")
def test_small_stdout_device_failure_is_a_clean_process_error(tmp_path):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(valid_input()), encoding="utf-8")
    with Path("/dev/full").open("wb", buffering=0) as full:
        result = subprocess.run(
            [sys.executable, "-m", "media_dimension_outlier_finder", str(source)],
            check=False,
            stdout=full,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
    assert result.returncode == 2
    assert result.stderr.startswith("error:")
    assert "Traceback" not in result.stderr and "Exception ignored" not in result.stderr


def test_existing_link_is_refused_when_exclusive_open_would_follow_it(
    tmp_path, monkeypatch, capsys
):
    source = tmp_path / "source.json"
    source.write_text(json.dumps(valid_input()), encoding="utf-8")
    target, output = tmp_path / "target.json", tmp_path / "report.json"
    try:
        output.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable")
    original_open = Path.open

    def platform_open(path, mode="r", *args, **kwargs):
        if path == output and mode == "x":
            return original_open(target, "w", *args, **kwargs)
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", platform_open)
    assert main([str(source), "--output", str(output)]) == 2
    assert output.is_symlink() and not target.exists()
    assert capsys.readouterr().err.startswith("error:")
