<!-- Shubhangi, Upload Date: 2026-07-28 -->
# Dataset Notes

The selected dataset is:

```text
awsaf49/asvpoof-2019-dataset
```

Use `kagglehub` to download it locally:

```bash
cd backend
python scripts/download_dataset.py
```

## Why Data Is Not Committed

ASVspoof audio datasets are large and should not be pushed to GitHub. Keep raw files under `data/raw/`, which is ignored by git.

## Week 1-2 Validation Goals

- Confirm the dataset downloads successfully.
- Inspect genuine and spoof audio folders.
- Select a small balanced subset for baseline testing.
- Generate spectrogram and RIR-style acoustic features.
- Save processed feature arrays under `data/processed/` locally.

## Feature Validation Checklist

- Audio loads at a consistent sample rate.
- Silent or corrupted files fail gracefully.
- Reverb tail ratio changes between dry and reverberant clips.
- Background consistency is lower when the clip contains unstable room noise.
- Spectrogram values are normalized before model input.

