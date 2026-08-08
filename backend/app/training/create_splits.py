import re

import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from backend.app.dataset.config import (
    FEATURE_PATH,
    SPLITS_PATH,
)


def get_utterance_id(filename):
    """
    Extract the original LJSpeech utterance ID.

    Example:
    0717__LJ002-0201_generated__X__real_bg.wav
    -> LJ002-0201
    """

    match = re.search(
        r"LJ\d+-\d+",
        str(filename)
    )

    if match:
        return match.group(0)

    return None


def create_data_splits():

    # --------------------------------------------------
    # Load feature dataset
    # --------------------------------------------------

    df = pd.read_csv(
        FEATURE_PATH / "features.csv"
    )

    print("=" * 60)
    print("DATASET")
    print("=" * 60)

    print("Dataset shape:", df.shape)

    print("\nClass distribution:")
    print(df["label"].value_counts())


    # --------------------------------------------------
    # Extract utterance group
    # --------------------------------------------------

    df["utterance_id"] = (
        df["filename"]
        .apply(get_utterance_id)
    )

    missing_ids = (
        df["utterance_id"]
        .isna()
        .sum()
    )

    print(
        "\nMissing utterance IDs:",
        missing_ids
    )

    if missing_ids > 0:
        raise ValueError(
            "Some filenames do not contain "
            "a valid LJ utterance ID."
        )

    print(
        "Unique utterances:",
        df["utterance_id"].nunique()
    )


    # --------------------------------------------------
    # STEP 1
    # Create approximately 90% development + 10% test
    #
    # StratifiedGroupKFold keeps:
    # - class distribution balanced
    # - each utterance in only one split
    # --------------------------------------------------

    outer_split = StratifiedGroupKFold(
        n_splits=10,
        shuffle=True,
        random_state=42
    )

    development_indices, test_indices = next(
        outer_split.split(
            X=df,
            y=df["label"],
            groups=df["utterance_id"]
        )
    )

    development_df = (
        df.iloc[development_indices]
        .reset_index(drop=True)
    )

    test_df = (
        df.iloc[test_indices]
        .reset_index(drop=True)
    )


    # --------------------------------------------------
    # STEP 2
    # Split remaining ~90% into
    # approximately 80% train + 10% validation
    #
    # 1 fold from 9 = about 10% of total dataset
    # --------------------------------------------------

    inner_split = StratifiedGroupKFold(
        n_splits=9,
        shuffle=True,
        random_state=42
    )

    train_indices, val_indices = next(
        inner_split.split(
            X=development_df,
            y=development_df["label"],
            groups=development_df["utterance_id"]
        )
    )

    train_df = (
        development_df
        .iloc[train_indices]
        .reset_index(drop=True)
    )

    val_df = (
        development_df
        .iloc[val_indices]
        .reset_index(drop=True)
    )


    # --------------------------------------------------
    # Verify utterance leakage
    # --------------------------------------------------

    train_ids = set(
        train_df["utterance_id"]
    )

    val_ids = set(
        val_df["utterance_id"]
    )

    test_ids = set(
        test_df["utterance_id"]
    )

    train_val_overlap = len(
        train_ids.intersection(val_ids)
    )

    train_test_overlap = len(
        train_ids.intersection(test_ids)
    )

    val_test_overlap = len(
        val_ids.intersection(test_ids)
    )

    print("\n" + "=" * 60)
    print("UTTERANCE LEAKAGE CHECK")
    print("=" * 60)

    print(
        "Train <-> Validation:",
        train_val_overlap
    )

    print(
        "Train <-> Test:",
        train_test_overlap
    )

    print(
        "Validation <-> Test:",
        val_test_overlap
    )

    if (
        train_val_overlap > 0
        or train_test_overlap > 0
        or val_test_overlap > 0
    ):
        raise RuntimeError(
            "Utterance leakage detected."
        )


    # --------------------------------------------------
    # Display split information
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL SPLITS")
    print("=" * 60)

    print(
        "Train:",
        train_df.shape
    )

    print(
        "Validation:",
        val_df.shape
    )

    print(
        "Test:",
        test_df.shape
    )


    print("\nTrain labels:")
    print(
        train_df["label"]
        .value_counts()
    )

    print("\nValidation labels:")
    print(
        val_df["label"]
        .value_counts()
    )

    print("\nTest labels:")
    print(
        test_df["label"]
        .value_counts()
    )


    print("\nUnique utterances:")

    print(
        "Train:",
        train_df["utterance_id"].nunique()
    )

    print(
        "Validation:",
        val_df["utterance_id"].nunique()
    )

    print(
        "Test:",
        test_df["utterance_id"].nunique()
    )


    # --------------------------------------------------
    # Remove helper column before saving
    #
    # This keeps the CSV structure compatible with
    # your existing Random Forest and CNN pipelines.
    # --------------------------------------------------

    train_df = train_df.drop(
        columns=["utterance_id"]
    )

    val_df = val_df.drop(
        columns=["utterance_id"]
    )

    test_df = test_df.drop(
        columns=["utterance_id"]
    )


    # --------------------------------------------------
    # Save
    # --------------------------------------------------

    SPLITS_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    train_df.to_csv(
        SPLITS_PATH / "train.csv",
        index=False
    )

    val_df.to_csv(
        SPLITS_PATH / "validation.csv",
        index=False
    )

    test_df.to_csv(
        SPLITS_PATH / "test.csv",
        index=False
    )

    print(
        "\nLeakage-safe splits saved successfully."
    )


if __name__ == "__main__":
    create_data_splits()