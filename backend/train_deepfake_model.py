# ============================================================
# VOICESHIELD AI
# train_deepfake_model.py
#
# ASVspoof 2019 LA Wav2Vec2 Deepfake Detector
#
# IMPORTANT:
# This script downloads and loads an already ASVspoof-2019-
# trained Wav2Vec2 anti-spoofing checkpoint.
#
# It does NOT retrain 25,000+ files on your laptop.
#
# Classes:
#   0 = bonafide
#   1 = spoof
#
# Model:
#   facebook/wav2vec2-base
#
# Classification head:
#   768 -> 256 -> GELU -> Dropout -> 2
#
# Input:
#   16 kHz
#   4 seconds
#   64,000 samples
# ============================================================


from pathlib import Path
import json
import shutil

import torch
import torch.nn as nn
import soundfile as sf
import librosa

from huggingface_hub import hf_hub_download
from transformers import Wav2Vec2Model, Wav2Vec2FeatureExtractor


# ============================================================
# 1. PROJECT PATHS
# ============================================================

# This file is:
# VoiceShield AI/backend/train_deepfake_model.py

BACKEND_ROOT = Path(__file__).resolve().parent

PROJECT_ROOT = BACKEND_ROOT.parent

MODEL_DIR = (
    BACKEND_ROOT
    / "model"
    / "deepfake_model"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


print("=" * 70)
print("VOICE SHIELD AI - DEEPFAKE DETECTION MODEL")
print("=" * 70)

print("\nBackend:")
print(BACKEND_ROOT)

print("\nModel directory:")
print(MODEL_DIR)


# ============================================================
# 2. MODEL INFORMATION
# ============================================================

HF_REPO = (
    "caa-speech-detection-asvspoof2019"
    "/wav2vec2"
)

BASE_MODEL = "facebook/wav2vec2-base"

TARGET_SAMPLE_RATE = 16000

TARGET_SAMPLES = 64000

HIDDEN_DIM = 256

DROPOUT = 0.1


# ============================================================
# 3. DEVICE
# ============================================================

# CPU is used intentionally.
# This prevents CUDA/GPU compatibility problems.

DEVICE = torch.device("cpu")

print("\nDevice:")
print(DEVICE)


# ============================================================
# 4. DOWNLOAD ASVSPOOF TRAINED CHECKPOINT
# ============================================================

print("\n" + "=" * 70)
print("DOWNLOADING ASVSPOOF TRAINED WAV2VEC2 CHECKPOINT")
print("=" * 70)

print("\nRepository:")
print(HF_REPO)

print(
    "\nThe checkpoint is approximately 362 MB."
)

print(
    "If already downloaded, Hugging Face will use the cache."
)


checkpoint_path = hf_hub_download(
    repo_id=HF_REPO,
    filename="best.pt"
)


print("\nCheckpoint downloaded/found:")
print(checkpoint_path)


# ============================================================
# 5. COPY CHECKPOINT INTO OUR BACKEND MODEL DIRECTORY
# ============================================================

local_checkpoint = (
    MODEL_DIR
    / "best.pt"
)

if (
    not local_checkpoint.exists()
    or local_checkpoint.stat().st_size
    != Path(checkpoint_path).stat().st_size
):

    shutil.copy2(
        checkpoint_path,
        local_checkpoint
    )

    print(
        "\nCheckpoint copied to:"
    )

    print(
        local_checkpoint
    )

else:

    print(
        "\nCheckpoint already exists locally:"
    )

    print(
        local_checkpoint
    )


# ============================================================
# 6. WAV2VEC2 FEATURE EXTRACTOR
# ============================================================

print("\n" + "=" * 70)
print("LOADING AUDIO FEATURE EXTRACTOR")
print("=" * 70)


feature_extractor = (
    Wav2Vec2FeatureExtractor
    .from_pretrained(
        BASE_MODEL
    )
)


print(
    "\nFeature extractor loaded successfully!"
)


# ============================================================
# 7. VOICESHIELD MODEL ARCHITECTURE
# ============================================================

class VoiceShieldWav2Vec2(nn.Module):

    def __init__(self):

        super().__init__()

        print(
            "\nLoading base Wav2Vec2 model..."
        )

        self.wav2vec2 = (
            Wav2Vec2Model
            .from_pretrained(
                BASE_MODEL
            )
        )

        # ----------------------------------------------------
        # Freeze Wav2Vec2 encoder
        # ----------------------------------------------------

        for parameter in (
            self.wav2vec2.parameters()
        ):

            parameter.requires_grad = False


        # ----------------------------------------------------
        # Classification head
        #
        # 768 -> 256 -> GELU -> Dropout -> 2
        # ----------------------------------------------------

        self.classifier = nn.Sequential(

            nn.Linear(
                768,
                HIDDEN_DIM
            ),

            nn.GELU(),

            nn.Dropout(
                DROPOUT
            ),

            nn.Linear(
                HIDDEN_DIM,
                2
            )
        )


    def forward(
        self,
        frames
    ):

        outputs = self.wav2vec2(
            input_values=frames
        )

        hidden_states = (
            outputs.last_hidden_state
        )

        # Mean pooling over time
        pooled = hidden_states.mean(
            dim=1
        )

        logits = self.classifier(
            pooled
        )

        return logits


# ============================================================
# 8. CREATE MODEL
# ============================================================

print("\n" + "=" * 70)
print("CREATING VOICESHIELD MODEL")
print("=" * 70)


model = VoiceShieldWav2Vec2()

model = model.to(
    DEVICE
)

model.eval()


print(
    "\nModel architecture created."
)


# ============================================================
# 9. LOAD TRAINED ASVSPOOF CHECKPOINT
# ============================================================

print("\n" + "=" * 70)
print("LOADING TRAINED ASVSPOOF WEIGHTS")
print("=" * 70)


state = torch.load(
    local_checkpoint,
    map_location=DEVICE
)


# ------------------------------------------------------------
# Handle checkpoint wrappers
# ------------------------------------------------------------

if isinstance(
    state,
    dict
):

    if "state_dict" in state:

        state = state[
            "state_dict"
        ]

    elif "model_state_dict" in state:

        state = state[
            "model_state_dict"
        ]


# ------------------------------------------------------------
# Remove DataParallel prefix if present
# ------------------------------------------------------------

clean_state = {}

for key, value in state.items():

    new_key = key

    if new_key.startswith(
        "module."
    ):

        new_key = new_key[
            len("module.") :
        ]

    clean_state[
        new_key
    ] = value


# ------------------------------------------------------------
# Load weights
# ------------------------------------------------------------

missing_keys, unexpected_keys = (
    model.load_state_dict(
        clean_state,
        strict=False
    )
)


print(
    "\nCheckpoint loading finished."
)


if missing_keys:

    print(
        "\nWARNING - Missing keys:"
    )

    for key in missing_keys[:20]:

        print(
            " ",
            key
        )


if unexpected_keys:

    print(
        "\nWARNING - Unexpected keys:"
    )

    for key in unexpected_keys[:20]:

        print(
            " ",
            key
        )


# ============================================================
# 10. CHECK MODEL
# ============================================================

model.eval()


print("\nModel ready.")

print(
    "\nClasses:"
)

print(
    "0 = bonafide"
)

print(
    "1 = spoof"
)


# ============================================================
# 11. AUDIO LOADING
# ============================================================

def load_audio(
    audio_path
):

    """
    Load audio and convert it to:

        Mono
        16 kHz
        64,000 samples / 4 seconds
    """

    audio, sample_rate = (
        sf.read(
            str(audio_path),
            dtype="float32"
        )
    )


    # --------------------------------------------------------
    # Stereo -> Mono
    # --------------------------------------------------------

    if audio.ndim > 1:

        audio = audio.mean(
            axis=1
        )


    # --------------------------------------------------------
    # Resample -> 16 kHz
    # --------------------------------------------------------

    if sample_rate != TARGET_SAMPLE_RATE:

        audio = librosa.resample(
            audio,
            orig_sr=sample_rate,
            target_sr=TARGET_SAMPLE_RATE
        )


    audio = audio.astype(
        "float32"
    )


    # --------------------------------------------------------
    # Pad / Trim -> 4 seconds
    # --------------------------------------------------------

    if len(audio) > TARGET_SAMPLES:

        audio = audio[
            :TARGET_SAMPLES
        ]

    elif len(audio) < TARGET_SAMPLES:

        padding = (
            TARGET_SAMPLES
            - len(audio)
        )

        audio = torch.nn.functional.pad(
            torch.tensor(
                audio,
                dtype=torch.float32
            ),
            (
                0,
                padding
            )
        ).numpy()


    return audio


# ============================================================
# 12. PREDICTION FUNCTION
# ============================================================

def predict_voice(
    audio_path
):

    """
    Predict whether an audio file is:

        Bonafide
        or
        Spoof
    """

    audio = load_audio(
        audio_path
    )


    # --------------------------------------------------------
    # Wav2Vec2 preprocessing
    # --------------------------------------------------------

    inputs = feature_extractor(
        audio,
        sampling_rate=TARGET_SAMPLE_RATE,
        return_tensors="pt"
    )


    frames = (
        inputs.input_values
        .float()
        .to(DEVICE)
    )


    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    with torch.no_grad():

        logits = model(
            frames
        )

        probabilities = torch.softmax(
            logits,
            dim=-1
        )


    predicted_class = (
        torch.argmax(
            probabilities,
            dim=-1
        ).item()
    )


    bonafide_probability = (
        probabilities[0][0]
        .item()
    )


    spoof_probability = (
        probabilities[0][1]
        .item()
    )


    # --------------------------------------------------------
    # Label
    # --------------------------------------------------------

    if predicted_class == 0:

        result = "Bonafide"

    else:

        result = "Spoof"


    return {

        "result":
            result,

        "class_id":
            predicted_class,

        "bonafide_probability":
            bonafide_probability,

        "spoof_probability":
            spoof_probability

    }


# ============================================================
# 13. TEST WITH TRUSTED VOICE
# ============================================================

print("\n" + "=" * 70)
print("TESTING MODEL")
print("=" * 70)


test_audio_candidates = [

    PROJECT_ROOT
    / "dataset"
    / "trusted_voices"
    / "abinaya1.wav",

    PROJECT_ROOT
    / "dataset"
    / "trusted_voices"
    / "abinaya2.wav",

    PROJECT_ROOT
    / "dataset"
    / "trusted_voices"
    / "father.wav"

]


test_audio = None


for candidate in test_audio_candidates:

    if candidate.exists():

        test_audio = candidate

        break


if test_audio is not None:

    print(
        "\nTesting audio:"
    )

    print(
        test_audio
    )


    try:

        result = predict_voice(
            test_audio
        )


        print(
            "\nPrediction:"
        )

        print(
            "Result:",
            result["result"]
        )

        print(
            "Class ID:",
            result["class_id"]
        )

        print(
            "Bonafide probability:",
            f"{result['bonafide_probability']:.4f}"
        )

        print(
            "Spoof probability:",
            f"{result['spoof_probability']:.4f}"
        )


    except Exception as error:

        print(
            "\nPrediction test failed:"
        )

        print(
            error
        )


else:

    print(
        "\nNo trusted test audio found."
    )

    print(
        "Model loading was still successful."
    )


# ============================================================
# 14. SAVE VOICESHIELD MODEL
# ============================================================

print("\n" + "=" * 70)
print("SAVING VOICESHIELD MODEL")
print("=" * 70)


final_model_path = (
    MODEL_DIR
    / "voiceshield_wav2vec2_asvspoof.pt"
)


torch.save(
    model.state_dict(),
    final_model_path
)


print(
    "\nSaved trained model:"
)

print(
    final_model_path
)


# ============================================================
# 15. SAVE MODEL CONFIGURATION
# ============================================================

config = {

    "project":
        "VoiceShield AI",

    "model_type":
        "Wav2Vec2 Anti-Spoofing",

    "base_model":
        BASE_MODEL,

    "checkpoint_source":
        HF_REPO,

    "dataset":
        "ASVspoof 2019 Logical Access",

    "task":
        "Binary Voice Deepfake Detection",

    "classes": {

        "0":
            "bonafide",

        "1":
            "spoof"

    },

    "sample_rate":
        TARGET_SAMPLE_RATE,

    "target_samples":
        TARGET_SAMPLES,

    "duration_seconds":
        4,

    "classification_head": [
        "Linear(768,256)",
        "GELU",
        "Dropout(0.1)",
        "Linear(256,2)"
    ],

    "encoder":
        "Frozen",

    "device":
        str(DEVICE)

}


config_path = (
    MODEL_DIR
    / "model_config.json"
)


with open(
    config_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        config,
        file,
        indent=4
    )


print(
    "\nConfiguration saved:"
)

print(
    config_path
)


# ============================================================
# 16. FINAL STATUS
# ============================================================

print("\n")
print("=" * 70)
print("VOICE SHIELD AI DEEPFAKE MODEL READY")
print("=" * 70)

print(
    "\nModel:"
)

print(
    final_model_path
)

print(
    "\nConfiguration:"
)

print(
    config_path
)

print(
    "\nBackend model directory:"
)

print(
    MODEL_DIR
)

print(
    "\nClasses:"
)

print(
    "0 -> Bonafide"
)

print(
    "1 -> Spoof"
)

print("\n" + "=" * 70)