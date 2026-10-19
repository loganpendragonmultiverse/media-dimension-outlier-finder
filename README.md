# Media Dimension Outlier Finder

> ⭐ **Gold Star Project — v1.1.1**
> I consider this project complete. Fixes, maintenance and good new ideas are still welcome.
> [About Gold Stars](https://www.loganpendragonforge.com/open-source/?gold=1)
>
> Review supplied media metadata and local image dimensions against batch medians and explicit profiles.


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

## Report and installation contract (1.1.1)

The input root must be a JSON object. Invalid input produces `error:` on stderr
and exit status 2 without creating a report. Existing output paths, including
symlinks and files created between validation and writing, are refused through
exclusive file creation. Parent directories must already exist. An interrupted
or failed write can leave a partial newly created report; multiple-file atomicity
and filesystem rollback are not provided.

Install a downloaded wheel with `python -m pip install /path/to/package.whl`,
or install the source distribution with `python -m pip install /path/to/package.tar.gz`.
Wheel installs include README, DEVELOPMENT, TESTING and CHANGELOG under
`sysconfig.get_path("data")/share/doc/media-dimension-outlier-finder`, with the sample in `examples/sample.json`.
The source distribution contains the same documents and example. Inputs stay local;
no telemetry or network retrieval is added.

Items must be a non-empty list of objects and profiles a named object mapping.
Supplied metrics and profile bounds must fit finite positive floating-point values;
very large integer values are rejected before conversion. Two large finite middle
values retain a finite batch median. Image paths are opened only when dimensions
are incomplete; image errors are reported without changing the image. Video
metadata remains supplied explicitly, and outliers remain review aids.

A failed stdout write or flush returns status 2 without a shutdown traceback,
including a closed reader or a full output device.
