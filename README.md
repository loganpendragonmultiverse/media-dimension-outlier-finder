# Media Dimension Outlier Finder

[![CI](https://github.com/loganpendragonmultiverse/media-dimension-outlier-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/media-dimension-outlier-finder/actions/workflows/ci.yml)

Detect unusual media dimensions, aspect ratios, durations, and sizes in a batch. The command uses explicit UTF-8 JSON input and produces reviewable JSON or Markdown output.

## Three-minute start

```bash
python -m pip install .
media-outliers examples/sample.json
media-outliers examples/sample.json --format json --output report.json
```

The example documents the v1 input shape. Existing report files are never overwritten. Source inputs are read-only except where the documented purpose explicitly creates a new output artifact.

## Privacy and platforms

The tool runs locally and does not upload input or include telemetry. Python 3.10 or newer is supported on Windows, macOS, and Linux.

## Interpretation boundary

Outliers are relative to the supplied batch and are not necessarily errors. Video dimensions and durations must be supplied as metadata in v1.

## Development

```bash
python -m pip install -e ".[dev]"
ruff format --check .
ruff check .
mypy src
pytest
python -m build
```

The project is feature-complete for its documented v1 scope. Maintenance focuses on correctness, security, compatibility, and well-supported input improvements.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).

## Named expected profiles (1.1)

Optional profiles map explicit names to constraints; each item selects one with
its profile field. Example:
    "profiles": {"cover": {"width": {"min": 600, "max": 1200}, "orientation": "portrait"}}
Bounds are inclusive and may constrain width, height, aspect_ratio, duration, or
bytes. Orientation is portrait, landscape, or square. Profile findings include
matches and missing-metadata reasons separately from the original relative outliers.
Unassigned items still participate in the original batch medians. Mixed profiles
do not change those medians or infer a profile. Supplied metrics and bounds must
be finite positive numbers; factor must be finite and greater than one.
Image paths can supply image dimensions through Pillow. Video metadata must be
provided explicitly; this tool does not probe videos or alter media.

A supplied positive finite aspect_ratio is preserved when both dimensions are not
available. When width and height are both available, their derived ratio takes
precedence over any supplied ratio; profile bounds use that unrounded value.
Each item reports aspect_ratio_source as supplied, dimensions, or missing.
