# User Guide

## Introduction
Welcome to **Acousticspace**. This guide walks you through the features, usage, and workflows available in the project from an end-user perspective.

---

## Table of Contents
1. [Getting Started](#getting-started)
2. [Running the Application](#running-the-application)
3. [Features](#features)
4. [Workflows](#workflows)
5. [Troubleshooting](#troubleshooting)
6. [FAQ](#faq)

---

## 1. Getting Started

Before using Acousticspace, make sure you have completed the setup steps in [`Setup_Guide.md`](Setup_Guide.md).

### Prerequisites
- Python 3.10 or later
- All dependencies installed (`pip install -r requirements.txt`)
- Audio input files placed in the `data/raw/` directory

---

## 2. Running the Application

Open a terminal in the project root and run:

```bash
python main.py
```

To specify a custom input file:

```bash
python main.py --input data/raw/sample.wav
```

To specify an output directory:

```bash
python main.py --input data/raw/sample.wav --output results/
```

---

## 3. Features

| Feature | Description |
|---|---|
| Audio Analysis | Processes and analyses audio recordings |
| Label Classification | Classifies audio into predefined categories |
| Report Generation | Exports results to CSV or JSON |
| Visualisation | Generates waveform and spectrogram plots |

---

## 4. Workflows

### Basic Workflow
1. Place your audio file in `data/raw/`.
2. Run `python main.py --input <your_file>`.
3. View results in the `results/` folder.

### Batch Processing
```bash
python main.py --batch --input data/raw/ --output results/
```

---

## 5. Troubleshooting

| Issue | Possible Cause | Fix |
|---|---|---|
| `ModuleNotFoundError` | Dependencies not installed | Run `pip install -r requirements.txt` |
| `FileNotFoundError` | Input path is incorrect | Check that the file path is correct |
| No output generated | Processing error | Check terminal logs for details |

---

## 6. FAQ

**Q: What audio formats are supported?**  
A: `.wav` and `.mp3` files are supported.

**Q: Where are the results saved?**  
A: By default, results are saved in the `results/` directory.

**Q: Can I process multiple files at once?**  
A: Yes, use the `--batch` flag with an input directory.
