import librosa
import numpy as np


def compute_breathing_cadence_features(
    y,
    sr,
    frame_length=1024,
    hop_length=256
):
    """
    Estimate breathing/pause cadence characteristics from audio.

    This is an experimental acoustic proxy. It detects low-energy
    regions occurring between speech-like regions and summarizes
    their timing and duration.

    Returns:
        dict containing:
        - breath_event_count
        - breath_duration_mean
        - breath_duration_std
        - breath_interval_mean
        - breath_interval_std
        - breathing_cadence_score
    """

    # --------------------------------------------------
    # Calculate RMS energy per frame
    # --------------------------------------------------

    rms = librosa.feature.rms(
        y=y,
        frame_length=frame_length,
        hop_length=hop_length
    )[0]

    if len(rms) < 3:
        return {
            "breath_event_count": 0.0,
            "breath_duration_mean": 0.0,
            "breath_duration_std": 0.0,
            "breath_interval_mean": 0.0,
            "breath_interval_std": 0.0,
            "breathing_cadence_score": 0.0,
        }

    # --------------------------------------------------
    # Adaptive low-energy threshold
    # --------------------------------------------------

    low_energy_threshold = np.percentile(
        rms,
        30
    )

    low_energy_frames = (
        rms <= low_energy_threshold
    )

    # --------------------------------------------------
    # Find consecutive low-energy regions
    # --------------------------------------------------

    breath_regions = []

    start = None

    for index, is_low_energy in enumerate(
        low_energy_frames
    ):

        if is_low_energy and start is None:
            start = index

        elif not is_low_energy and start is not None:

            end = index - 1

            breath_regions.append(
                (start, end)
            )

            start = None

    if start is not None:
        breath_regions.append(
            (
                start,
                len(low_energy_frames) - 1
            )
        )

    # --------------------------------------------------
    # Convert regions into durations
    # --------------------------------------------------

    frame_duration = (
        hop_length / sr
    )

    durations = []

    centers = []

    for start, end in breath_regions:

        number_of_frames = (
            end - start + 1
        )

        duration = (
            number_of_frames
            * frame_duration
        )

        # Ignore extremely short regions
        if duration < 0.03:
            continue

        # Ignore very long silence regions
        if duration > 0.8:
            continue

        durations.append(
            duration
        )

        center_frame = (
            start + end
        ) / 2

        centers.append(
            center_frame
            * frame_duration
        )

    breath_event_count = len(
        durations
    )

    # --------------------------------------------------
    # Duration statistics
    # --------------------------------------------------

    if breath_event_count > 0:

        breath_duration_mean = float(
            np.mean(durations)
        )

        breath_duration_std = float(
            np.std(durations)
        )

    else:

        breath_duration_mean = 0.0
        breath_duration_std = 0.0

    # --------------------------------------------------
    # Interval statistics
    # --------------------------------------------------

    if len(centers) >= 2:

        intervals = np.diff(
            centers
        )

        breath_interval_mean = float(
            np.mean(intervals)
        )

        breath_interval_std = float(
            np.std(intervals)
        )

    else:

        breath_interval_mean = 0.0
        breath_interval_std = 0.0

    # --------------------------------------------------
    # Cadence consistency score
    #
    # Higher score -> more regular timing
    # Lower score  -> irregular / insufficient cadence
    # --------------------------------------------------

    if (
        breath_interval_mean > 0
        and len(centers) >= 2
    ):

        coefficient_of_variation = (
            breath_interval_std
            / (
                breath_interval_mean
                + 1e-10
            )
        )

        breathing_cadence_score = (
            1.0
            / (
                1.0
                + coefficient_of_variation
            )
        )

    else:

        breathing_cadence_score = 0.0

    return {
        "breath_event_count": float(
            breath_event_count
        ),

        "breath_duration_mean": float(
            breath_duration_mean
        ),

        "breath_duration_std": float(
            breath_duration_std
        ),

        "breath_interval_mean": float(
            breath_interval_mean
        ),

        "breath_interval_std": float(
            breath_interval_std
        ),

        "breathing_cadence_score": float(
            breathing_cadence_score
        ),
    }