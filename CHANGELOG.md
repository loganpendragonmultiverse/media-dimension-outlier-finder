# Changelog

## [1.1.1] - 2026-10-19

- Reject existing output symlinks explicitly before exclusive creation on every platform.
- Handle failed stdout writes and flushes without an interpreter-shutdown traceback.
- Reject malformed item/profile containers, invalid factors and out-of-range numeric inputs with concise CLI errors.
- Keep medians finite for large finite metrics without changing profile or aspect-ratio rules.
- Create reports exclusively and ship complete handoff documents and a sample in both distributions.

## 1.1.0 — 2026-10-15

- Preserve explicit aspect ratios without dimensions and report the ratio source.
- Compare media against explicit named dimension, orientation, duration and size profiles.
- Report missing profile metadata and reject invalid numeric metrics and bounds.

## 1.0.0 - 2026-07-26

- Released the first complete Media Dimension Outlier Finder command-line workflow.
- Added deterministic reporting, representative examples, cross-platform tests, and explicit limitations.
