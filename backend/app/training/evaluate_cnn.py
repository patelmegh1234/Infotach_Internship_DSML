from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve
)

from backend.app.training.cnn_dataset import create_dataset


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

TEST_CSV = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "splits"
    / "test.csv"
)

MODEL_PATH = (
    PROJECT_ROOT
    / "backend"
    / "models"
    / "best_cnn_model.keras"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "backend"
    / "results"
    / "cnn"
)

METRICS_PATH = (
    RESULTS_DIR
    / "cnn_test_metrics.csv"
)

PREDICTIONS_PATH = (
    RESULTS_DIR
    / "cnn_test_predictions.csv"
)

CONFUSION_MATRIX_PATH = (
    RESULTS_DIR
    / "cnn_confusion_matrix.png"
)

ROC_CURVE_PATH = (
    RESULTS_DIR
    / "cnn_roc_curve.png"
)


BATCH_SIZE = 32
THRESHOLD = 0.5


def collect_true_labels(
    dataset: tf.data.Dataset
) -> np.ndarray:
    """
    Extract all true labels from a TensorFlow dataset.
    """

    true_labels = []

    for _, labels in dataset:
        true_labels.extend(
            labels.numpy().astype(int)
        )

    return np.asarray(true_labels)


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> None:
    """
    Create and save the confusion matrix.
    """

    matrix = confusion_matrix(
        y_true,
        y_pred
    )

    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix,
        display_labels=[
            "Fake",
            "Real"
        ]
    )

    display.plot(
        values_format="d"
    )

    plt.title(
        "CNN Confusion Matrix"
    )

    plt.tight_layout()

    plt.savefig(
        CONFUSION_MATRIX_PATH,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()


def plot_roc_curve(
    y_true: np.ndarray,
    y_probability: np.ndarray
) -> None:
    """
    Create and save the ROC curve.
    """

    false_positive_rate, true_positive_rate, _ = (
        roc_curve(
            y_true,
            y_probability
        )
    )

    auc_score = roc_auc_score(
        y_true,
        y_probability
    )

    plt.figure(
        figsize=(8, 6)
    )

    plt.plot(
        false_positive_rate,
        true_positive_rate,
        label=f"CNN AUC = {auc_score:.4f}"
    )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
        label="Random Classifier"
    )

    plt.xlabel(
        "False Positive Rate"
    )

    plt.ylabel(
        "True Positive Rate"
    )

    plt.title(
        "CNN ROC Curve"
    )

    plt.legend(
        loc="lower right"
    )

    plt.grid(
        alpha=0.3
    )

    plt.tight_layout()

    plt.savefig(
        ROC_CURVE_PATH,
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()


def main() -> None:
    """
    Evaluate the trained CNN model using the test split.
    """

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not TEST_CSV.exists():
        raise FileNotFoundError(
            f"Test CSV not found: {TEST_CSV}"
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"CNN model not found: {MODEL_PATH}"
        )

    print(
        f"Loading test split from: {TEST_CSV}"
    )

    test_dataset = create_dataset(
        csv_path=TEST_CSV,
        batch_size=BATCH_SIZE,
        shuffle=False
    )

    print(
        f"Loading CNN model from: {MODEL_PATH}"
    )

    model = tf.keras.models.load_model(
        MODEL_PATH
    )

    print(
        "\nEvaluating model on test data..."
    )

    evaluation_results = model.evaluate(
        test_dataset,
        verbose=1,
        return_dict=True
    )

    print(
        "\nGenerating predictions..."
    )

    prediction_probabilities = (
        model.predict(
            test_dataset,
            verbose=1
        )
        .reshape(-1)
    )

    predicted_labels = (
        prediction_probabilities
        >= THRESHOLD
    ).astype(int)

    true_labels = collect_true_labels(
        test_dataset
    )

    accuracy = accuracy_score(
        true_labels,
        predicted_labels
    )

    precision = precision_score(
        true_labels,
        predicted_labels,
        zero_division=0
    )

    recall = recall_score(
        true_labels,
        predicted_labels,
        zero_division=0
    )

    f1 = f1_score(
        true_labels,
        predicted_labels,
        zero_division=0
    )

    auc = roc_auc_score(
        true_labels,
        prediction_probabilities
    )

    metrics = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "roc_auc": auc,
        "loss": evaluation_results.get(
            "loss"
        )
    }

    print(
        "\nCNN Test Metrics"
    )

    for metric_name, metric_value in metrics.items():
        print(
            f"{metric_name}: "
            f"{metric_value:.4f}"
        )

    print(
        "\nClassification Report"
    )

    print(
        classification_report(
            true_labels,
            predicted_labels,
            target_names=[
                "Fake",
                "Real"
            ],
            zero_division=0
        )
    )

    metrics_dataframe = pd.DataFrame(
        [metrics]
    )

    metrics_dataframe.to_csv(
        METRICS_PATH,
        index=False
    )

    predictions_dataframe = pd.DataFrame(
        {
            "true_label": true_labels,
            "predicted_label": predicted_labels,
            "real_probability": (
                prediction_probabilities
            )
        }
    )

    predictions_dataframe.to_csv(
        PREDICTIONS_PATH,
        index=False
    )

    plot_confusion_matrix(
        true_labels,
        predicted_labels
    )

    plot_roc_curve(
        true_labels,
        prediction_probabilities
    )

    print(
        "\nEvaluation completed."
    )

    print(
        f"Metrics saved at: {METRICS_PATH}"
    )

    print(
        f"Predictions saved at: "
        f"{PREDICTIONS_PATH}"
    )

    print(
        f"Confusion matrix saved at: "
        f"{CONFUSION_MATRIX_PATH}"
    )

    print(
        f"ROC curve saved at: "
        f"{ROC_CURVE_PATH}"
    )


if __name__ == "__main__":
    main()