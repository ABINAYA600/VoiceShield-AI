from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

from services.deepfake_detection import detect_deepfake


# ============================================================
# PATHS
# ============================================================

BACKEND_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_ROOT.parent

DEV_CSV = (
    PROJECT_ROOT
    / "dataset"
    / "deepfake_metadata"
    / "dev_metadata.csv"
)


# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_csv(DEV_CSV)

print("=" * 70)
print("VOICESHIELD AI - DEEPFAKE MODEL EVALUATION")
print("=" * 70)

print("\nTotal samples in DEV metadata:", len(df))


# ============================================================
# BALANCED SAMPLE
# 50 BONAFIDE + 50 SPOOF
# ============================================================

bonafide = df[df["label"] == 0].head(50)
spoof = df[df["label"] == 1].head(50)

test_df = pd.concat([bonafide, spoof]).reset_index(drop=True)

print("Bonafide samples:", len(bonafide))
print("Spoof samples:", len(spoof))
print("Total test samples:", len(test_df))


# ============================================================
# EVALUATION
# ============================================================

y_true = []
y_pred = []

correct = 0
total = 0


for index, row in test_df.iterrows():

    audio_path = PROJECT_ROOT / row["audio_path"]

    actual_label = int(row["label"])

    actual_name = (
        "Bonafide"
        if actual_label == 0
        else "Spoof"
    )

    print("\n" + "-" * 70)
    print(f"Sample {index + 1}/100")
    print("File:", audio_path.name)
    print("Actual:", actual_name)

    try:

        result = detect_deepfake(audio_path)

        predicted_label = result["class_id"]

        predicted_name = result["result"]

        print("Predicted:", predicted_name)
        print(
            "Bonafide probability:",
            result["bonafide_probability"]
        )
        print(
            "Spoof probability:",
            result["spoof_probability"]
        )

        y_true.append(actual_label)
        y_pred.append(predicted_label)

        if actual_label == predicted_label:
            correct += 1

        total += 1

    except Exception as e:

        print("ERROR:", e)


# ============================================================
# METRICS
# ============================================================

print("\n")
print("=" * 70)
print("FINAL EVALUATION RESULTS")
print("=" * 70)

if total > 0:

    accuracy = accuracy_score(y_true, y_pred)

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0
    )

    cm = confusion_matrix(
        y_true,
        y_pred
    )

    print("\nCorrect predictions:", correct)
    print("Total evaluated:", total)

    print(
        "\nAccuracy:",
        f"{accuracy:.4f}"
    )

    print(
        "Precision:",
        f"{precision:.4f}"
    )

    print(
        "Recall:",
        f"{recall:.4f}"
    )

    print(
        "F1 Score:",
        f"{f1:.4f}"
    )

    print("\nConfusion Matrix:")
    print(cm)

    print("\nClassification Report:")
    print(
        classification_report(
            y_true,
            y_pred,
            target_names=[
                "Bonafide",
                "Spoof"
            ],
            zero_division=0
        )
    )

else:

    print("No samples were successfully evaluated.")