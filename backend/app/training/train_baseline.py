import joblib
import pandas as pd

from pathlib import Path

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import LabelEncoder

from backend.app.dataset.config import SPLITS_PATH


MODEL_PATH = Path("backend/checkpoints")
MODEL_PATH.mkdir(
    parents=True,
    exist_ok=True
)

RESULTS_PATH = Path(
    "backend/results/baseline"
)
RESULTS_PATH.mkdir(
    parents=True,
    exist_ok=True
)


FEATURE_COLUMNS = [
    "rms",
    "zcr",
    "spectral_centroid",
    "spectral_bandwidth",
    "spectral_rolloff",
    "spectral_flatness",
    "spectral_contrast",
    "chroma_mean",

    "mfcc_1",
    "mfcc_2",
    "mfcc_3",
    "mfcc_4",
    "mfcc_5",
    "mfcc_6",
    "mfcc_7",
    "mfcc_8",
    "mfcc_9",
    "mfcc_10",
    "mfcc_11",
    "mfcc_12",
    "mfcc_13",

    "silence_ratio",
    "spectral_entropy",
    "reverb_tail_ratio",
    "energy_decay_slope",
    "background_consistency",

    "breath_event_count",
    "breath_duration_mean",
    "breath_duration_std",
    "breath_interval_mean",
    "breath_interval_std",
    "breathing_cadence_score",
]


def train():

    # -----------------------------------------
    # Load leakage-safe data splits
    # -----------------------------------------

    train_df = pd.read_csv(
        SPLITS_PATH / "train.csv"
    )

    val_df = pd.read_csv(
        SPLITS_PATH / "validation.csv"
    )

    test_df = pd.read_csv(
        SPLITS_PATH / "test.csv"
    )

    print("Train:", train_df.shape)
    print("Validation:", val_df.shape)
    print("Test:", test_df.shape)

    # -----------------------------------------
    # Validate feature columns
    # -----------------------------------------

    missing_features = [
        col
        for col in FEATURE_COLUMNS
        if col not in train_df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing feature columns: "
            f"{missing_features}"
        )

    X_train = train_df[
        FEATURE_COLUMNS
    ]

    X_val = val_df[
        FEATURE_COLUMNS
    ]

    X_test = test_df[
        FEATURE_COLUMNS
    ]

    print(
        "\nNumber of features used:",
        X_train.shape[1]
    )

    print("Features used:")
    print(
        X_train.columns.tolist()
    )

    # -----------------------------------------
    # Encode labels
    # -----------------------------------------

    encoder = LabelEncoder()

    y_train = encoder.fit_transform(
        train_df["label"]
    )

    y_val = encoder.transform(
        val_df["label"]
    )

    y_test = encoder.transform(
        test_df["label"]
    )

    print("\nLabel mapping:")

    for encoded_value, class_name in enumerate(
        encoder.classes_
    ):
        print(
            f"{encoded_value} = "
            f"{class_name}"
        )

    # -----------------------------------------
    # Train Random Forest
    # -----------------------------------------

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train
    )

    # -----------------------------------------
    # Predictions
    # -----------------------------------------

    val_pred = model.predict(
        X_val
    )

    test_pred = model.predict(
        X_test
    )

    test_prob = model.predict_proba(
        X_test
    )[:, 1]

    # -----------------------------------------
    # Validation result
    # -----------------------------------------

    val_accuracy = accuracy_score(
        y_val,
        val_pred
    )

    print(
        "\nValidation Accuracy"
    )

    print(
        val_accuracy
    )

    # -----------------------------------------
    # Test metrics
    # -----------------------------------------

    test_accuracy = accuracy_score(
        y_test,
        test_pred
    )

    test_precision = precision_score(
        y_test,
        test_pred,
        zero_division=0
    )

    test_recall = recall_score(
        y_test,
        test_pred,
        zero_division=0
    )

    test_f1 = f1_score(
        y_test,
        test_pred,
        zero_division=0
    )

    test_roc_auc = roc_auc_score(
        y_test,
        test_prob
    )

    print(
        "\nTest Metrics"
    )

    print(
        "Accuracy:",
        test_accuracy
    )

    print(
        "Precision:",
        test_precision
    )

    print(
        "Recall:",
        test_recall
    )

    print(
        "F1:",
        test_f1
    )

    print(
        "ROC-AUC:",
        test_roc_auc
    )

    # -----------------------------------------
    # Classification report
    # -----------------------------------------

    print(
        "\nClassification Report"
    )

    report = classification_report(
        y_test,
        test_pred,
        target_names=encoder.classes_,
    )

    print(
        report
    )

    # -----------------------------------------
    # Confusion matrix
    # -----------------------------------------

    cm = confusion_matrix(
        y_test,
        test_pred
    )

    print(
        "\nConfusion Matrix"
    )

    print(
        cm
    )

    # -----------------------------------------
    # Save metrics
    # -----------------------------------------

    metrics_df = pd.DataFrame({
        "accuracy": [
            test_accuracy
        ],
        "precision": [
            test_precision
        ],
        "recall": [
            test_recall
        ],
        "f1_score": [
            test_f1
        ],
        "roc_auc": [
            test_roc_auc
        ],
    })

    metrics_df.to_csv(
        RESULTS_PATH
        / "baseline_test_metrics.csv",
        index=False
    )

    # -----------------------------------------
    # Save predictions
    # -----------------------------------------

    predictions_df = pd.DataFrame({
        "actual": y_test,
        "predicted": test_pred,
        "real_probability": test_prob,
    })

    predictions_df.to_csv(
        RESULTS_PATH
        / "baseline_test_predictions.csv",
        index=False
    )

    # -----------------------------------------
    # Save confusion matrix
    # -----------------------------------------

    cm_df = pd.DataFrame(
        cm,
        index=[
            "actual_fake",
            "actual_real"
        ],
        columns=[
            "predicted_fake",
            "predicted_real"
        ]
    )

    cm_df.to_csv(
        RESULTS_PATH
        / "baseline_confusion_matrix.csv"
    )

    # -----------------------------------------
    # Save classification report
    # -----------------------------------------

    with open(
        RESULTS_PATH
        / "baseline_classification_report.txt",
        "w"
    ) as file:

        file.write(
            report
        )

    # -----------------------------------------
    # Save model
    # -----------------------------------------

    model_data = {
        "model": model,
        "label_encoder": encoder,
        "feature_columns":
            FEATURE_COLUMNS,
    }

    joblib.dump(
        model_data,
        MODEL_PATH
        / "baseline_random_forest.pkl",
    )

    print(
        "\nModel saved successfully."
    )

    print(
        "Evaluation results saved to:",
        RESULTS_PATH
    )


if __name__ == "__main__":
    train()