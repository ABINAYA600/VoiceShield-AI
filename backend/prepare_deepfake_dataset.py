from pathlib import Path
import csv


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_ROOT = PROJECT_ROOT / "dataset" / "Deepfake"

METADATA_ROOT = PROJECT_ROOT / "dataset" / "deepfake_metadata"


# ============================================================
# DATASET DIRECTORIES
# ============================================================

TRAIN_AUDIO_DIR = DATASET_ROOT / "ASVspoof2019_LA_train"
DEV_AUDIO_DIR = DATASET_ROOT / "ASVspoof2019_LA_dev"
EVAL_AUDIO_DIR = DATASET_ROOT / "ASVspoof2019_LA_eval"


# ============================================================
# PROTOCOL FILES
# ============================================================

PROTOCOL_DIR = DATASET_ROOT / "ASVspoof2019_LA_cm_protocols"

TRAIN_PROTOCOL = PROTOCOL_DIR / "ASVspoof2019.LA.cm.train.trn.txt"
DEV_PROTOCOL = PROTOCOL_DIR / "ASVspoof2019.LA.cm.dev.trl.txt"
EVAL_PROTOCOL = PROTOCOL_DIR / "ASVspoof2019.LA.cm.eval.trl.txt"


# ============================================================
# OUTPUT FILES
# ============================================================

TRAIN_OUTPUT = METADATA_ROOT / "train_metadata.csv"
DEV_OUTPUT = METADATA_ROOT / "dev_metadata.csv"
EVAL_OUTPUT = METADATA_ROOT / "eval_metadata.csv"


# ============================================================
# FIND AUDIO FILE - FAST VERSION
# ============================================================

def find_audio_file(audio_root, utterance_id):

    flac_file = (
        audio_root
        / "flac"
        / f"{utterance_id}.flac"
    )

    if flac_file.exists():
        return flac_file

    wav_file = (
        audio_root
        / "wav"
        / f"{utterance_id}.wav"
    )

    if wav_file.exists():
        return wav_file

    return None


# ============================================================
# PREPARE DATASET SPLIT
# ============================================================

def prepare_split(
    protocol_path,
    audio_root,
    output_path,
    split_name
):

    print()
    print("==========================================")
    print(f"Preparing {split_name.upper()} dataset")
    print("==========================================")

    print("Protocol:")
    print(protocol_path)

    print("Audio directory:")
    print(audio_root)

    if not protocol_path.exists():
        raise FileNotFoundError(
            f"Protocol file not found:\n{protocol_path}"
        )

    if not audio_root.exists():
        raise FileNotFoundError(
            f"Audio directory not found:\n{audio_root}"
        )

    METADATA_ROOT.mkdir(
        parents=True,
        exist_ok=True
    )

    protocol_entries = 0
    valid_files = 0
    bonafide_count = 0
    spoof_count = 0
    missing_count = 0
    malformed_count = 0

    rows = []

    # ========================================================
    # READ PROTOCOL
    # ========================================================

    with open(
        protocol_path,
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            protocol_entries += 1

            parts = line.split()

            if len(parts) < 5:
                malformed_count += 1
                continue

            speaker_id = parts[0]

            utterance_id = parts[1]

            attack_id = parts[-2]

            label_name = parts[-1].lower()

            # ------------------------------------------------
            # LABEL
            # ------------------------------------------------

            if label_name == "bonafide":

                label = 0
                bonafide_count += 1

            elif label_name == "spoof":

                label = 1
                spoof_count += 1

            else:

                malformed_count += 1
                continue

            # ------------------------------------------------
            # FIND AUDIO
            # ------------------------------------------------

            audio_path = find_audio_file(
                audio_root,
                utterance_id
            )

            if audio_path is None:

                missing_count += 1

                continue

            relative_path = audio_path.relative_to(
                PROJECT_ROOT
            )

            rows.append({

                "audio_path": str(relative_path),

                "utterance_id": utterance_id,

                "speaker_id": speaker_id,

                "attack_id": attack_id,

                "label": label,

                "label_name": label_name,

                "split": split_name

            })

            valid_files += 1

            # ------------------------------------------------
            # Progress
            # ------------------------------------------------

            if valid_files % 1000 == 0:

                print(
                    f"Processed {valid_files} files..."
                )

    # ========================================================
    # SAVE CSV
    # ========================================================

    with open(
        output_path,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "audio_path",
            "utterance_id",
            "speaker_id",
            "attack_id",
            "label",
            "label_name",
            "split"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(rows)

    # ========================================================
    # SUMMARY
    # ========================================================

    print()
    print("------------------------------------------")
    print(f"{split_name.upper()} SUMMARY")
    print("------------------------------------------")

    print(
        "Protocol entries:",
        protocol_entries
    )

    print(
        "Valid audio files:",
        valid_files
    )

    print(
        "Bonafide:",
        bonafide_count
    )

    print(
        "Spoof:",
        spoof_count
    )

    print(
        "Missing audio:",
        missing_count
    )

    print(
        "Malformed lines:",
        malformed_count
    )

    print()
    print("Metadata saved to:")
    print(output_path)


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("==========================================")
    print("       VOICESHIELD AI")
    print("ASVSPOOF 2019 LA DATASET PREPARATION")
    print("==========================================")

    print()
    print("Project root:")
    print(PROJECT_ROOT)

    print()
    print("Dataset root:")
    print(DATASET_ROOT)

    # ========================================================
    # TRAIN
    # ========================================================

    prepare_split(
        TRAIN_PROTOCOL,
        TRAIN_AUDIO_DIR,
        TRAIN_OUTPUT,
        "train"
    )

    # ========================================================
    # DEV
    # ========================================================

    prepare_split(
        DEV_PROTOCOL,
        DEV_AUDIO_DIR,
        DEV_OUTPUT,
        "dev"
    )

    # ========================================================
    # EVAL
    # ========================================================

    prepare_split(
        EVAL_PROTOCOL,
        EVAL_AUDIO_DIR,
        EVAL_OUTPUT,
        "eval"
    )

    # ========================================================
    # COMPLETE
    # ========================================================

    print()
    print("==========================================")
    print("DATASET PREPARATION COMPLETED")
    print("==========================================")

    print()
    print("Created files:")

    print(TRAIN_OUTPUT)
    print(DEV_OUTPUT)
    print(EVAL_OUTPUT)

    print()
    print("Label mapping:")
    print("0 = bonafide")
    print("1 = spoof")


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()