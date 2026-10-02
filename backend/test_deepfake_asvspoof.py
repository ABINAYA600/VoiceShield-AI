from pathlib import Path
import pandas as pd

from services.deepfake_detection import detect_deepfake


BACKEND_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_ROOT.parent

DEV_CSV = (
    PROJECT_ROOT
    / "dataset"
    / "deepfake_metadata"
    / "dev_metadata.csv"
)

dev_df = pd.read_csv(DEV_CSV)

print("=" * 60)
print("ASVSPOOF DEEPFAKE MODEL TEST")
print("=" * 60)

# Test 3 bonafide + 3 spoof samples
bonafide = dev_df[dev_df["label"] == 0].head(3)
spoof = dev_df[dev_df["label"] == 1].head(3)

test_samples = pd.concat([
    bonafide,
    spoof
])

correct = 0
total = 0

for _, row in test_samples.iterrows():

    audio_path = PROJECT_ROOT / row["audio_path"]

    true_label = (
        "Bonafide"
        if int(row["label"]) == 0
        else "Spoof"
    )

    print("\n" + "-" * 60)
    print("File:", audio_path.name)
    print("Actual:", true_label)

    try:

        result = detect_deepfake(audio_path)

        predicted = result["result"]

        print("Predicted:", predicted)

        print(
            "Bonafide probability:",
            result["bonafide_probability"]
        )

        print(
            "Spoof probability:",
            result["spoof_probability"]
        )

        if predicted == true_label:
            correct += 1

        total += 1

    except Exception as e:

        print("ERROR:", e)


print("\n" + "=" * 60)
print("TEST SUMMARY")
print("=" * 60)

print("Correct:", correct)
print("Total:", total)

if total > 0:
    print(
        "Accuracy:",
        f"{correct / total:.2%}"
    )