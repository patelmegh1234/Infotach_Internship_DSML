# Shubhangi, Upload Date: 2026-07-28
# Enhanced Acoustic Feature Extractor with Rich Audio Representations
from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly


@dataclass(frozen=True)
class AcousticFeatures:
    sample_rate: int
    duration_seconds: float
    rms_mean: float
    rms_std: float
    zero_crossing_rate: float
    zero_crossing_rate_std: float
    spectral_centroid_mean: float
    spectral_centroid_std: float
    spectral_rolloff_mean: float
    spectral_rolloff_std: float
    spectral_flatness_mean: float
    spectral_flatness_std: float
    low_frequency_ratio: float
    high_frequency_ratio: float
    mfcc_mean: list[float]
    mel_spectrogram_preview: list[float]
    spectral_band_std: list[float]
    reverb_tail_ratio: float
    rir_decay_slope: float
    background_consistency: float
    breathing_cadence_score: float
    anomaly_curve: list[float]
    spectral_bandwidth_mean: float = 0.0
    spectral_bandwidth_std: float = 0.0
    mfcc_std: list[float] = field(default_factory=list)
    delta_mfcc_mean: list[float] = field(default_factory=list)
    spectral_contrast_mean: list[float] = field(default_factory=list)

    def to_public_dict(self) -> dict[str, float | int | list[float]]:
        return {
            "sample_rate": self.sample_rate,
            "duration_seconds": round(self.duration_seconds, 3),
            "rms_mean": round(self.rms_mean, 6),
            "rms_std": round(self.rms_std, 6),
            "zero_crossing_rate": round(self.zero_crossing_rate, 6),
            "zero_crossing_rate_std": round(self.zero_crossing_rate_std, 6),
            "spectral_centroid_mean": round(self.spectral_centroid_mean, 3),
            "spectral_centroid_std": round(self.spectral_centroid_std, 3),
            "spectral_rolloff_mean": round(self.spectral_rolloff_mean, 3),
            "spectral_rolloff_std": round(self.spectral_rolloff_std, 3),
            "spectral_bandwidth_mean": round(self.spectral_bandwidth_mean, 3),
            "spectral_bandwidth_std": round(self.spectral_bandwidth_std, 3),
            "spectral_flatness_mean": round(self.spectral_flatness_mean, 6),
            "spectral_flatness_std": round(self.spectral_flatness_std, 6),
            "low_frequency_ratio": round(self.low_frequency_ratio, 6),
            "high_frequency_ratio": round(self.high_frequency_ratio, 6),
            "mfcc_mean": [round(value, 4) for value in self.mfcc_mean],
            "mfcc_std": [round(value, 4) for value in self.mfcc_std],
            "delta_mfcc_mean": [round(value, 4) for value in self.delta_mfcc_mean],
            "spectral_contrast_mean": [round(value, 4) for value in self.spectral_contrast_mean],
            "mel_spectrogram_preview": [round(value, 4) for value in self.mel_spectrogram_preview],
            "spectral_band_std": [round(value, 4) for value in self.spectral_band_std],
            "reverb_tail_ratio": round(self.reverb_tail_ratio, 6),
            "rir_decay_slope": round(self.rir_decay_slope, 6),
            "background_consistency": round(self.background_consistency, 6),
            "breathing_cadence_score": round(self.breathing_cadence_score, 6),
        }


class LibrosaFeatureExtractor:
    def __init__(self, target_sample_rate: int = 16_000) -> None:
        self.target_sample_rate = target_sample_rate

    def extract(self, audio_bytes: bytes) -> AcousticFeatures:
        waveform, sample_rate = self._load_audio(audio_bytes)
        return self.extract_waveform(waveform=waveform, sample_rate=sample_rate)

    def extract_file(self, path: str | Path) -> AcousticFeatures:
        try:
            waveform, sample_rate = sf.read(str(path), dtype="float32", always_2d=False)
        except Exception as exc:
            raise ValueError(f"Could not decode audio file: {path}") from exc
        return self.extract_waveform(waveform=waveform, sample_rate=sample_rate)

    def extract_waveform(self, waveform: np.ndarray, sample_rate: int) -> AcousticFeatures:
        waveform = _to_mono(waveform)
        if sample_rate != self.target_sample_rate:
            waveform = _resample_audio(waveform, sample_rate, self.target_sample_rate)
            sample_rate = self.target_sample_rate
        waveform = librosa.util.normalize(np.asarray(waveform, dtype=np.float32))
        if waveform.size < sample_rate // 3:
            raise ValueError("Audio is too short for acoustic analysis. Upload at least 0.3 seconds.")

        duration = float(librosa.get_duration(y=waveform, sr=sample_rate))
        n_fft = 1024
        hop_length = 256

        # Librosa features
        mfccs = librosa.feature.mfcc(y=waveform, sr=sample_rate, n_mfcc=20, n_fft=n_fft, hop_length=hop_length)
        delta_mfccs = librosa.feature.delta(mfccs)
        contrast = librosa.feature.spectral_contrast(y=waveform, sr=sample_rate, n_fft=n_fft, hop_length=hop_length)
        bandwidth = librosa.feature.spectral_bandwidth(y=waveform, sr=sample_rate, n_fft=n_fft, hop_length=hop_length)

        # STFT Spectrum & Frame statistics
        stft_matrix = np.abs(librosa.stft(waveform, n_fft=n_fft, hop_length=hop_length))
        frequencies = librosa.fft_frequencies(sr=sample_rate, n_fft=n_fft)
        spectrum_sum = np.sum(stft_matrix, axis=0) + 1e-8
        centroid = np.sum(stft_matrix * frequencies[:, None], axis=0) / spectrum_sum
        rolloff = librosa.feature.spectral_rolloff(y=waveform, sr=sample_rate, n_fft=n_fft, hop_length=hop_length)[0]
        flatness = librosa.feature.spectral_flatness(y=waveform, n_fft=n_fft, hop_length=hop_length)[0]
        rms = librosa.feature.rms(y=waveform, frame_length=n_fft, hop_length=hop_length)[0]
        zcr = librosa.feature.zero_crossing_rate(y=waveform, frame_length=n_fft, hop_length=hop_length)[0]

        # Mel spectrogram bands (16 bins)
        mel_spec = librosa.feature.melspectrogram(y=waveform, sr=sample_rate, n_mels=16, n_fft=n_fft, hop_length=hop_length)
        mel_db = librosa.power_to_db(mel_spec, ref=np.max)
        band_summary = np.mean(mel_db, axis=1)
        band_std = np.std(mel_db, axis=1)

        low_frequency_ratio = _frequency_energy_ratio(stft_matrix, frequencies, low=0.0, high=500.0)
        high_frequency_ratio = _frequency_energy_ratio(stft_matrix, frequencies, low=3500.0, high=8000.0)

        reverb_tail_ratio = self._estimate_reverb_tail_ratio(rms)
        rir_decay_slope = self._estimate_decay_slope(rms)
        background_consistency = self._estimate_background_consistency(waveform, sample_rate)
        breathing_cadence_score = self._estimate_breathing_cadence(waveform, sample_rate)

        anomaly_curve = self._build_anomaly_curve(
            rms=rms,
            zcr=zcr,
            centroid=centroid,
            reverb_tail_ratio=reverb_tail_ratio,
            background_consistency=background_consistency,
        )

        return AcousticFeatures(
            sample_rate=sample_rate,
            duration_seconds=duration,
            rms_mean=float(np.mean(rms)),
            rms_std=float(np.std(rms)),
            zero_crossing_rate=float(np.mean(zcr)),
            zero_crossing_rate_std=float(np.std(zcr)),
            spectral_centroid_mean=float(np.mean(centroid)),
            spectral_centroid_std=float(np.std(centroid)),
            spectral_rolloff_mean=float(np.mean(rolloff)),
            spectral_rolloff_std=float(np.std(rolloff)),
            spectral_bandwidth_mean=float(np.mean(bandwidth)),
            spectral_bandwidth_std=float(np.std(bandwidth)),
            spectral_flatness_mean=float(np.mean(flatness)),
            spectral_flatness_std=float(np.std(flatness)),
            low_frequency_ratio=float(low_frequency_ratio),
            high_frequency_ratio=float(high_frequency_ratio),
            mfcc_mean=np.mean(mfccs, axis=1).astype(float).tolist(),
            mfcc_std=np.std(mfccs, axis=1).astype(float).tolist(),
            delta_mfcc_mean=np.mean(delta_mfccs, axis=1).astype(float).tolist(),
            spectral_contrast_mean=np.mean(contrast, axis=1).astype(float).tolist(),
            mel_spectrogram_preview=band_summary.astype(float).tolist(),
            spectral_band_std=band_std.astype(float).tolist(),
            reverb_tail_ratio=float(reverb_tail_ratio),
            rir_decay_slope=float(rir_decay_slope),
            background_consistency=float(background_consistency),
            breathing_cadence_score=float(breathing_cadence_score),
            anomaly_curve=anomaly_curve,
        )

    def _load_audio(self, audio_bytes: bytes) -> tuple[np.ndarray, int]:
        try:
            waveform, sample_rate = sf.read(BytesIO(audio_bytes), dtype="float32", always_2d=False)
            return waveform, int(sample_rate)
        except Exception:
            pass

        try:
            waveform, sample_rate = librosa.load(
                BytesIO(audio_bytes),
                sr=self.target_sample_rate,
                mono=True,
            )
            return waveform, int(sample_rate)
        except Exception as exc:
            raise ValueError("Could not decode audio file. Try WAV, MP3, FLAC, OGG, or M4A.") from exc

    @staticmethod
    def _estimate_reverb_tail_ratio(rms: np.ndarray) -> float:
        if rms.size < 8:
            return 0.0
        threshold = np.quantile(rms, 0.65)
        energetic = np.where(rms >= threshold)[0]
        if energetic.size == 0:
            return 0.0
        tail_start = min(int(energetic[-1] + 1), rms.size - 1)
        tail_energy = float(np.mean(rms[tail_start:])) if tail_start < rms.size else 0.0
        body_energy = float(np.mean(rms[: tail_start + 1])) + 1e-8
        return float(np.clip(tail_energy / body_energy, 0.0, 1.0))

    @staticmethod
    def _estimate_decay_slope(rms: np.ndarray) -> float:
        if rms.size < 12:
            return 0.0
        envelope = np.maximum(rms, 1e-8)
        tail = envelope[int(envelope.size * 0.55) :]
        x_axis = np.arange(tail.size)
        log_tail = np.log(tail)
        slope, _ = np.polyfit(x_axis, log_tail, deg=1)
        return float(np.clip(slope, -1.0, 1.0))

    @staticmethod
    def _estimate_background_consistency(waveform: np.ndarray, sample_rate: int) -> float:
        window = max(sample_rate // 2, 1)
        usable = waveform[: waveform.size - (waveform.size % window)]
        if usable.size < window * 2:
            return 0.5
        chunks = usable.reshape(-1, window)
        energies = np.mean(np.square(chunks), axis=1)
        variation = float(np.std(energies) / (np.mean(energies) + 1e-8))
        return float(np.clip(1.0 - variation, 0.0, 1.0))

    @staticmethod
    def _estimate_breathing_cadence(waveform: np.ndarray, sample_rate: int) -> float:
        band = np.append(waveform[0], waveform[1:] - (0.97 * waveform[:-1]))
        envelope = np.abs(librosa.util.normalize(band))
        hop = max(sample_rate // 10, 1)
        blocks = [np.mean(envelope[index : index + hop]) for index in range(0, envelope.size, hop)]
        if len(blocks) < 4:
            return 0.5
        block_array = np.asarray(blocks)
        low_energy_pulses = block_array < np.quantile(block_array, 0.35)
        transitions = np.count_nonzero(np.diff(low_energy_pulses.astype(int)))
        cadence = transitions / max(len(block_array), 1)
        return float(np.clip(cadence, 0.0, 1.0))

    @staticmethod
    def _build_anomaly_curve(
        rms: np.ndarray,
        zcr: np.ndarray,
        centroid: np.ndarray,
        reverb_tail_ratio: float,
        background_consistency: float,
    ) -> list[float]:
        min_size = min(rms.size, zcr.size, centroid.size)
        if min_size == 0:
            return []
        rms_norm = _normalize_series(rms[:min_size])
        zcr_norm = _normalize_series(zcr[:min_size])
        centroid_norm = _normalize_series(centroid[:min_size])
        global_pressure = (reverb_tail_ratio + (1.0 - background_consistency)) / 2.0
        curve = (0.4 * rms_norm) + (0.25 * zcr_norm) + (0.2 * centroid_norm) + (0.15 * global_pressure)
        return np.clip(curve, 0.0, 1.0).astype(float).tolist()


def _normalize_series(values: np.ndarray) -> np.ndarray:
    minimum = float(np.min(values))
    maximum = float(np.max(values))
    if maximum - minimum < 1e-8:
        return np.zeros_like(values, dtype=np.float32)
    return (values - minimum) / (maximum - minimum)


def _to_mono(waveform: np.ndarray) -> np.ndarray:
    waveform = np.asarray(waveform, dtype=np.float32)
    if waveform.ndim == 1:
        return waveform
    if waveform.ndim == 2:
        return np.mean(waveform, axis=1)
    return waveform.reshape(-1)


def _resample_audio(waveform: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    gcd = int(np.gcd(source_rate, target_rate))
    up = target_rate // gcd
    down = source_rate // gcd
    return resample_poly(waveform, up=up, down=down).astype(np.float32)


def _frequency_energy_ratio(spectrum: np.ndarray, frequencies: np.ndarray, low: float, high: float) -> float:
    mask = (frequencies >= low) & (frequencies <= high)
    if not np.any(mask):
        return 0.0
    total = float(np.sum(spectrum)) + 1e-8
    return float(np.sum(spectrum[mask, :]) / total)
