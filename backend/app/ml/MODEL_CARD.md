<!-- Fathima, Upload Date: 2026-07-28 -->
# Baseline Model Card

## Model Type

Interpretable baseline classifier.

## Purpose

This model supports Week 1-2 integration and mid-project review. It is not the final research model.

## Inputs

- Reverb tail ratio
- RIR decay slope proxy
- Background consistency
- Breathing cadence proxy
- Spectral centroid
- Anomaly curve

## Output

- Decision: `suspicious` or `likely_real`
- Confidence score from 0 to 1
- Human-readable risk factors
- Localized suspicious segments

## Upgrade Plan

Replace this baseline with a trained CNN, Transformer, or Audio Spectrogram Transformer after dataset preparation and evaluation.

