from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf

from backend.app.training.cnn_dataset import create_dataset
from backend.app.training.cnn_model import build_cnn_model


# --------------------------------------------------
# Paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

SPLITS_DIR = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "splits"
)

TRAIN_CSV = SPLITS_DIR / "train.csv"
VALIDATION_CSV = SPLITS_DIR / "validation.csv"
TEST_CSV = SPLITS_DIR / "test.csv"

MODEL_DIR = (
    PROJECT_ROOT
    / "backend"
    / "models"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "backend"
    / "results"
    / "cnn"
)

BEST_MODEL_PATH = (
    MODEL_DIR
    / "best_cnn_model.keras"
)

FINAL_MODEL_PATH = (
    MODEL_DIR
    / "cnn_model.keras"
)

TRAINING_HISTORY_PATH = (
    RESULTS_DIR
    / "cnn_training_history.csv"
)

TRAINING_PLOT_PATH = (
    RESULTS_DIR
    / "cnn_training_history.png"
)


# --------------------------------------------------
# Training configuration
# --------------------------------------------------

BATCH_SIZE = 32
EPOCHS = 30


def plot_training_history(
    history: tf.keras.callbacks.History
) -> None:
    """
    Plot training and validation accuracy and loss.
    """

    history_data = history.history
    epochs = range(1, len(history_data["loss"]) + 1)

    plt.figure(figsize=(9, 6))

    plt.plot(
        epochs,
        history_data["accuracy"],
        label="Training Accuracy"
    )

    plt.plot(
        epochs,
        history_data["val_accuracy"],
        label="Validation Accuracy"
    )

    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.title("CNN Training and Validation Accuracy")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(TRAINING_PLOT_PATH)
    plt.show()

    plt.figure(figsize=(9, 6))

    plt.plot(
        epochs,
        history_data["loss"],
        label="Training Loss"
    )

    plt.plot(
        epochs,
        history_data["val_loss"],
        label="Validation Loss"
    )

    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("CNN Training and Validation Loss")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    loss_plot_path = (
        RESULTS_DIR
        / "cnn_training_loss.png"
    )

    plt.savefig(loss_plot_path)
    plt.show()


def main() -> None:
    """
    Train the CNN model using train and validation datasets.
    """

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    print(f"Training CSV: {TRAIN_CSV}")
    print(f"Validation CSV: {VALIDATION_CSV}")

    train_dataset = create_dataset(
        csv_path=TRAIN_CSV,
        batch_size=BATCH_SIZE,
        shuffle=True
    )

    validation_dataset = create_dataset(
        csv_path=VALIDATION_CSV,
        batch_size=BATCH_SIZE,
        shuffle=False
    )

    model = build_cnn_model()

    model.summary()

    callbacks = [
        tf.keras.callbacks.ModelCheckpoint(
            filepath=str(BEST_MODEL_PATH),
            monitor="val_loss",
            save_best_only=True,
            mode="min",
            verbose=1
        ),

        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=6,
            restore_best_weights=True,
            verbose=1
        ),

        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=3,
            min_lr=1e-6,
            verbose=1
        ),

        tf.keras.callbacks.CSVLogger(
            filename=str(
                RESULTS_DIR
                / "cnn_training_log.csv"
            )
        )
    ]

    history = model.fit(
        train_dataset,
        validation_data=validation_dataset,
        epochs=EPOCHS,
        callbacks=callbacks
    )

    model.save(FINAL_MODEL_PATH)

    history_dataframe = pd.DataFrame(
        history.history
    )

    history_dataframe.to_csv(
        TRAINING_HISTORY_PATH,
        index=False
    )

    plot_training_history(history)

    print("\nTraining completed.")
    print(f"Best model saved at: {BEST_MODEL_PATH}")
    print(f"Final model saved at: {FINAL_MODEL_PATH}")
    print(
        f"Training history saved at: "
        f"{TRAINING_HISTORY_PATH}"
    )


if __name__ == "__main__":
    main()