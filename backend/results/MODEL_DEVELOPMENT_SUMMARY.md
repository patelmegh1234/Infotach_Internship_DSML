# AcousticSpace – Model Development Summary

## 1. Objective

The objective of the model-development pipeline is to classify audio
samples as Fake or Real using acoustic characteristics and
spectro-temporal representations.

The project investigates whether deepfake audio can be detected using
acoustic-space information along with conventional audio features and
deep-learning representations.

---

## 2. Dataset Preparation

The audio dataset was prepared as 2-second WAV samples.

Audio preprocessing included:

- Loading audio using Librosa
- Resampling audio to 16 kHz
- Mono conversion
- Standardized audio duration
- Metadata generation
- Binary label generation:
  - Fake
  - Real

The final dataset contains:

- 12,000 audio samples
- 6,000 Fake samples
- 6,000 Real samples

---

## 3. Leakage-Safe Dataset Splitting

To prevent the same underlying utterance from appearing in multiple
dataset partitions, utterance-level grouping was used.

StratifiedGroupKFold was used to maintain approximately balanced class
distributions while keeping each utterance in only one split.

Final dataset splits:

| Split | Samples |
|---|---:|
| Training | 9,570 |
| Validation | 1,206 |
| Test | 1,224 |

Utterance overlap between Train, Validation, and Test was verified to
be zero.

---

## 4. Handcrafted Acoustic Features

A total of 32 handcrafted acoustic features were used for the
Random Forest baseline.

The features include:

### Time-domain features
- RMS energy
- Zero-crossing rate

### Spectral features
- Spectral centroid
- Spectral bandwidth
- Spectral rolloff
- Spectral flatness
- Spectral contrast
- Spectral entropy

### Harmonic and cepstral features
- Chroma
- 13 MFCC coefficients

### Acoustic-space features
- Silence ratio
- Reverb tail ratio
- Energy decay slope
- Background consistency

### Breathing-cadence features
- Breath event count
- Mean breath duration
- Breath duration standard deviation
- Mean breath interval
- Breath interval standard deviation
- Breathing cadence score

---

## 5. Random Forest Baseline

A Random Forest classifier with 200 estimators was trained using the
32 handcrafted acoustic features.

Test results:

| Metric | Score |
|---|---:|
| Accuracy | 0.4575 |
| Precision | 0.4666 |
| Recall | 0.4471 |
| F1-score | 0.4566 |
| ROC-AUC | 0.4734 |

The low performance indicates that the handcrafted summary features
alone are insufficient to reliably distinguish Fake and Real samples
under the leakage-safe evaluation setup.

---

## 6. CNN Model

A Convolutional Neural Network was trained using Mel-spectrogram
representations of the audio.

Test results:

| Metric | Score |
|---|---:|
| Accuracy | 0.8433 |
| Precision | 0.8249 |
| Recall | 0.8717 |
| F1-score | 0.8476 |
| ROC-AUC | 0.9421 |

The CNN significantly outperformed the handcrafted Random Forest
baseline, demonstrating the importance of spectro-temporal
representations for this task.

---

## 7. Audio Spectrogram Transformer (AST)

A pretrained Audio Spectrogram Transformer was fine-tuned for binary
Fake/Real audio classification.

Test results:

| Metric | Score |
|---|---:|
| Accuracy | 0.8513 |
| Precision | 0.8369 |
| Recall | 0.8798 |
| F1-score | 0.8578 |
| ROC-AUC | 0.9514 |

AST confusion matrix:

| | Predicted Fake | Predicted Real |
|---|---:|---:|
| Actual Fake | 493 | 107 |
| Actual Real | 75 | 549 |

---

## 8. Model Comparison

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Random Forest | 0.4575 | 0.4666 | 0.4471 | 0.4566 | 0.4734 |
| CNN | 0.8433 | 0.8249 | 0.8717 | 0.8476 | 0.9421 |
| AST | **0.8513** | **0.8369** | **0.8798** | **0.8578** | **0.9514** |

---

## 9. Final Model Selection

The Audio Spectrogram Transformer (AST) was selected as the final
model.

AST achieved the strongest overall test performance:

- 85.13% accuracy
- 83.69% precision
- 87.98% recall
- 85.78% F1-score
- 95.14% ROC-AUC

AST outperformed both the Random Forest baseline and CNN in the
reported test metrics.

The results indicate that learned spectro-temporal representations are
more effective for this dataset than using only handcrafted acoustic
summary features.

---

## 10. Inference Pipeline

An AST inference module was implemented to load the trained model and
classify WAV audio.

The inference pipeline returns:

- Predicted class: Fake or Real
- Prediction confidence
- Fake probability
- Real probability

This provides a simple interface for integration with the project's
backend/API layer.

---

## 11. Conclusion

The dataset preparation and model-development pipeline was completed
from preprocessing through final inference.

Three modeling approaches were evaluated:

1. Random Forest using handcrafted acoustic features
2. CNN using Mel-spectrogram representations
3. Audio Spectrogram Transformer

AST achieved the best overall performance and was therefore selected
as the final model for the deepfake audio classification pipeline.