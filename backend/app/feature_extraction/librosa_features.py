import librosa
import numpy as np


def compute_silence_ratio(y, frame_length=2048, hop_length=512):
    """
    Calculate the proportion of silent frames in an audio signal.
    """

    rms = librosa.feature.rms(
        y=y,
        frame_length=frame_length,
        hop_length=hop_length
    )[0]

    threshold = 0.02

    silent_frames = np.sum(rms < threshold)

    return silent_frames / len(rms)
def compute_spectral_entropy(y, sr):
    
    S = np.abs(librosa.stft(y))

    power = S ** 2

    power = power / (np.sum(power, axis=0, keepdims=True) + 1e-10)

    entropy = -np.sum(power * np.log2(power + 1e-10), axis=0)

    return np.mean(entropy)
def compute_reverb_tail_ratio(y):
    """
    Ratio of energy in the last 20% of the signal
    compared to the total energy.
    """

    total_energy = np.sum(y ** 2)

    tail = y[int(len(y) * 0.8):]

    tail_energy = np.sum(tail ** 2)

    return tail_energy / (total_energy + 1e-10)
def compute_energy_decay_slope(y):
    """
    Compute the slope of the audio energy decay curve.

    A more negative slope indicates that the signal energy decreases
    faster over time. A slope closer to zero indicates slower decay
    or persistent background/reverberation energy.
    """

    frame_length = 2048
    hop_length = 512

    rms = librosa.feature.rms(
        y=y,
        frame_length=frame_length,
        hop_length=hop_length
    )[0]

    energy = rms ** 2

    energy_db = librosa.power_to_db(
        energy,
        ref=np.max
    )

    time_frames = np.arange(len(energy_db))

    if len(time_frames) < 2:
        return 0.0

    slope, _ = np.polyfit(
        time_frames,
        energy_db,
        1
    )

    return float(slope)
def compute_background_consistency(y, sr):
    """
    Measure the consistency of the audio spectrum across time.

    Lower spectral variation indicates a more consistent background.
    Higher variation indicates a less stable or changing background.
    """

    spectrogram = np.abs(
        librosa.stft(
            y,
            n_fft=2048,
            hop_length=512
        )
    )

    frame_energy = np.mean(spectrogram, axis=0)

    if len(frame_energy) < 2:
        return 0.0

    mean_energy = np.mean(frame_energy)

    if mean_energy <= 1e-10:
        return 0.0

    coefficient_of_variation = (
        np.std(frame_energy) / (mean_energy + 1e-10)
    )

    return float(coefficient_of_variation)
def extract_features(audio_path):
    """
    Extract Librosa features from a single audio file.
    Returns a dictionary of numerical features.
    """

    y, sr = librosa.load(audio_path, sr=16000)

    features = {}

    # -----------------------------
    # Time-domain Features
    # -----------------------------
    features["rms"] = np.mean(librosa.feature.rms(y=y))

    features["zcr"] = np.mean(
        librosa.feature.zero_crossing_rate(y)
    )

    # -----------------------------
    # Spectral Features
    # -----------------------------
    features["spectral_centroid"] = np.mean(
        librosa.feature.spectral_centroid(
            y=y,
            sr=sr
        )
    )

    features["spectral_bandwidth"] = np.mean(
        librosa.feature.spectral_bandwidth(
            y=y,
            sr=sr
        )
    )

    features["spectral_rolloff"] = np.mean(
        librosa.feature.spectral_rolloff(
            y=y,
            sr=sr
        )
    )

    features["spectral_flatness"] = np.mean(
        librosa.feature.spectral_flatness(y=y)
    )

    features["spectral_contrast"] = np.mean(
        librosa.feature.spectral_contrast(
            y=y,
            sr=sr
        )
    )

    # -----------------------------
    # Harmonic Features
    # -----------------------------
    chroma = librosa.feature.chroma_stft(
        y=y,
        sr=sr
    )

    features["chroma_mean"] = np.mean(chroma)

    # -----------------------------
    # MFCC Features
    # -----------------------------
    mfcc = librosa.feature.mfcc(
        y=y,
        sr=sr,
        n_mfcc=13
    )

    for i in range(13):
        features[f"mfcc_{i+1}"] = np.mean(mfcc[i])

    
    # -----------------------------
    # Acoustic Space Feature
    # -----------------------------

    features["silence_ratio"] = compute_silence_ratio(y)
    features["spectral_entropy"] = compute_spectral_entropy(y, sr)
    features["reverb_tail_ratio"] = compute_reverb_tail_ratio(y)
    features["energy_decay_slope"] = compute_energy_decay_slope(y)
    features["background_consistency"] = compute_background_consistency(y, sr)

    return features