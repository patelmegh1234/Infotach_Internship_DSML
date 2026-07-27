import librosa
import numpy as np


TARGET_SR = 16000
TARGET_DURATION = 2
TARGET_SAMPLES = TARGET_SR * TARGET_DURATION


def load_audio(audio_path):
    audio, sr = librosa.load(audio_path, sr=TARGET_SR, mono=True)
    return audio, sr


def normalize_audio(audio):
    max_amp = np.max(np.abs(audio))

    if max_amp > 0:
        audio = audio / max_amp

    return audio


def pad_or_trim(audio):

    if len(audio) > TARGET_SAMPLES:
        audio = audio[:TARGET_SAMPLES]

    elif len(audio) < TARGET_SAMPLES:
        padding = TARGET_SAMPLES - len(audio)
        audio = np.pad(audio, (0, padding))

    return audio