# Test Cases

## Overview
This document lists all test cases for the Acousticspace project, organised by module or feature.

---

## Test Case Format

| Field | Description |
|---|---|
| **ID** | Unique test case identifier (e.g. TC-001) |
| **Title** | Short description of what is being tested |
| **Module** | The component or module under test |
| **Preconditions** | State required before running the test |
| **Steps** | Numbered steps to execute |
| **Expected Result** | What should happen |
| **Actual Result** | What actually happened (filled during execution) |
| **Status** | Pass / Fail / Blocked / Skipped |

---

## Module: Preprocessing

### TC-001 — Load valid WAV file

| Field | Details |
|---|---|
| **ID** | TC-001 |
| **Title** | Load a valid WAV audio file |
| **Module** | Preprocessing |
| **Preconditions** | A valid `.wav` file exists in `data/raw/` |
| **Steps** | 1. Run `python main.py --input data/raw/sample.wav` |
| **Expected Result** | File loads without error; duration and sample rate are printed |
| **Actual Result** | — |
| **Status** | — |

---

### TC-002 — Handle missing input file

| Field | Details |
|---|---|
| **ID** | TC-002 |
| **Title** | Gracefully handle a missing input file |
| **Module** | Preprocessing |
| **Preconditions** | The specified file does NOT exist |
| **Steps** | 1. Run `python main.py --input data/raw/missing.wav` |
| **Expected Result** | Error message: `FileNotFoundError: Input file not found.` |
| **Actual Result** | — |
| **Status** | — |

---

### TC-003 — Load unsupported file format

| Field | Details |
|---|---|
| **ID** | TC-003 |
| **Title** | Reject an unsupported audio format |
| **Module** | Preprocessing |
| **Preconditions** | A `.txt` file exists in `data/raw/` |
| **Steps** | 1. Run `python main.py --input data/raw/sample.txt` |
| **Expected Result** | Error message: `ValueError: Unsupported file format.` |
| **Actual Result** | — |
| **Status** | — |

---

## Module: Feature Extraction

### TC-004 — Extract features from valid audio

| Field | Details |
|---|---|
| **ID** | TC-004 |
| **Title** | Successfully extract features from a valid audio file |
| **Module** | Feature Extraction |
| **Preconditions** | Preprocessed file exists in `data/processed/` |
| **Steps** | 1. Run `python src/features.py --input data/processed/sample.wav` |
| **Expected Result** | Feature vector output saved to `data/features/sample.npy` |
| **Actual Result** | — |
| **Status** | — |

---

## Module: Analysis / Classification

### TC-005 — Classify audio sample

| Field | Details |
|---|---|
| **ID** | TC-005 |
| **Title** | Classify an audio sample to the correct category |
| **Module** | Analysis |
| **Preconditions** | Feature file exists in `data/features/` |
| **Steps** | 1. Run `python src/analyze.py --input data/features/sample.npy` |
| **Expected Result** | Returns correct label with confidence score |
| **Actual Result** | — |
| **Status** | — |

---

## Module: Batch Processing

### TC-006 — Batch process a directory

| Field | Details |
|---|---|
| **ID** | TC-006 |
| **Title** | Process all files in a directory |
| **Module** | Batch Processing |
| **Preconditions** | Multiple `.wav` files exist in `data/raw/` |
| **Steps** | 1. Run `python main.py --batch --input data/raw/ --output results/` |
| **Expected Result** | All files processed; results saved to `results/` |
| **Actual Result** | — |
| **Status** | — |

---

## Test Execution Log

| TC ID | Tester | Date | Status | Notes |
|---|---|---|---|---|
| TC-001 | — | — | — | — |
| TC-002 | — | — | — | — |
| TC-003 | — | — | — | — |
| TC-004 | — | — | — | — |
| TC-005 | — | — | — | — |
| TC-006 | — | — | — | — |
