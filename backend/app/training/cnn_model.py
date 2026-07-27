import tensorflow as tf
from tensorflow.keras import layers, models


INPUT_SHAPE = (128, 126, 1)


def build_cnn_model(
    input_shape: tuple[int, int, int] = INPUT_SHAPE
) -> tf.keras.Model:
    """
    Build a CNN model for binary audio deepfake classification.

    Labels:
        0 -> Fake
        1 -> Real
    """

    model = models.Sequential(
        [
            layers.Input(shape=input_shape),

            # Convolution block 1
            layers.Conv2D(
                filters=32,
                kernel_size=(3, 3),
                padding="same",
                activation="relu"
            ),
            layers.BatchNormalization(),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Dropout(0.20),

            # Convolution block 2
            layers.Conv2D(
                filters=64,
                kernel_size=(3, 3),
                padding="same",
                activation="relu"
            ),
            layers.BatchNormalization(),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Dropout(0.25),

            # Convolution block 3
            layers.Conv2D(
                filters=128,
                kernel_size=(3, 3),
                padding="same",
                activation="relu"
            ),
            layers.BatchNormalization(),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Dropout(0.30),

            # Convolution block 4
            layers.Conv2D(
                filters=256,
                kernel_size=(3, 3),
                padding="same",
                activation="relu"
            ),
            layers.BatchNormalization(),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Dropout(0.35),

            # Classification layers
            layers.GlobalAveragePooling2D(),

            layers.Dense(
                units=128,
                activation="relu"
            ),
            layers.BatchNormalization(),
            layers.Dropout(0.40),

            # Binary output
            layers.Dense(
                units=1,
                activation="sigmoid"
            )
        ],
        name="audio_deepfake_cnn"
    )

    model.compile(
        optimizer=tf.keras.optimizers.Adam(
            learning_rate=0.001
        ),
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(
                name="accuracy"
            ),
            tf.keras.metrics.Precision(
                name="precision"
            ),
            tf.keras.metrics.Recall(
                name="recall"
            ),
            tf.keras.metrics.AUC(
                name="auc"
            )
        ]
    )

    return model


if __name__ == "__main__":
    cnn_model = build_cnn_model()
    cnn_model.summary()