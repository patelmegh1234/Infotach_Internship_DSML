from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

from backend.app.dataset.config import (
    FEATURE_PATH,
    SPLITS_PATH,
)


def create_data_splits():

    df = pd.read_csv(FEATURE_PATH / "features.csv")

    print("=" * 50)
    print("DATASET")
    print("=" * 50)
    print(df.shape)

    # 80% train
    train_df, temp_df = train_test_split(
        df,
        test_size=0.20,
        stratify=df["label"],
        random_state=42,
    )

    # Remaining 20% → 10% validation + 10% test
    val_df, test_df = train_test_split(
        temp_df,
        test_size=0.50,
        stratify=temp_df["label"],
        random_state=42,
    )

    SPLITS_PATH.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(SPLITS_PATH / "train.csv", index=False)
    val_df.to_csv(SPLITS_PATH / "validation.csv", index=False)
    test_df.to_csv(SPLITS_PATH / "test.csv", index=False)

    print("\nTrain :", len(train_df))
    print("Validation :", len(val_df))
    print("Test :", len(test_df))


if __name__ == "__main__":
    create_data_splits()