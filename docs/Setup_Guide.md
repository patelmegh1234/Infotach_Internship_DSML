# Setup Guide

## Overview
This guide provides step-by-step instructions to set up the Acousticspace project on your local machine.

---

## Prerequisites

| Requirement | Minimum Version | Notes |
|---|---|---|
| Python | 3.10 | [python.org](https://www.python.org/) |
| pip | 22.0+ | Comes with Python |
| Git | 2.x | For cloning the repository |

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/your-org/acousticspace.git
cd acousticspace
```

---

## Step 2 — Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Step 4 — Configure the Project

1. Copy the example configuration file:
   ```bash
   cp config.example.yaml config.yaml
   ```
2. Open `config.yaml` and fill in the required values:
   - `data_dir` — path to your dataset
   - `output_dir` — where results will be saved
   - Any API keys or model paths if applicable

---

## Step 5 — Verify the Setup

Run the built-in check:

```bash
python main.py --check
```

Expected output:
```
[OK] Python version: 3.10.x
[OK] Dependencies installed
[OK] Config file found
Setup complete.
```

---

## Directory Structure After Setup

```
acousticspace/
├── data/
│   ├── raw/
│   ├── processed/
│   └── labels/
├── docs/
├── results/
├── testing_samples/
├── screenshots/
├── config.yaml
├── main.py
└── requirements.txt
```

---

## Common Setup Issues

| Issue | Cause | Fix |
|---|---|---|
| `pip: command not found` | pip not in PATH | Use `python -m pip install ...` |
| `Activate.ps1 cannot be loaded` | Execution policy restricted | Run `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| Dependency install fails | Network or version conflict | Run `pip install -r requirements.txt --upgrade` |

---

## Next Steps

- Read the [User Guide](User_Guide.md) to start using the project.
- Review the [Project Workflow](Project_Workflow.md) for development guidelines.
