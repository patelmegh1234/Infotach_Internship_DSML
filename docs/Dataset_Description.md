# Dataset Description

## Overview
This document describes the datasets used in the Acousticspace project, including their sources, structure, and usage guidelines.

## Dataset Summary

| Dataset Name | Format | Size | Source | Description |
|---|---|---|---|---|
| Dataset_01 | .wav / .mp3 | — | — | Primary acoustic recordings |
| Dataset_02 | .csv | — | — | Metadata and labels |

## Data Structure

```
data/
├── raw/          # Original, unprocessed recordings
├── processed/    # Cleaned and normalized audio files
└── labels/       # Annotation and label files
```

## Fields / Columns

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique identifier for each sample |
| `filename` | string | Name of the audio file |
| `label` | string | Class or category label |
| `duration` | float | Length of the recording in seconds |
| `sample_rate` | int | Audio sample rate in Hz |

## Preprocessing Notes

- All audio files are normalized to a consistent sample rate.
- Silence is trimmed from the start and end of each recording.
- Labels are verified and cross-checked against annotations.

## Data Collection

- **Collection Method:** Field recordings / controlled lab environment
- **Date Range:** —
- **License / Usage Rights:** —

## Known Issues / Limitations

- Some recordings may contain background noise.
- Class imbalance may be present in the label distribution.

## References

- Add any relevant papers, repositories, or data portals here.
