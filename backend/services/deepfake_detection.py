# ============================================================
# VOICESHIELD AI
# Deepfake Detection Service
# ============================================================

from pathlib import Path

import torch
import torch.nn as nn
import soundfile as sf
import librosa

from transformers import (
    Wav2Vec2Model,
    Wav2Vec2FeatureExtractor
)


# ============================================================
# PATHS
# ============================================================

BACKEND_ROOT = Path(__file__).resolve().parent.parent

MODEL_DIR = (
    BACKEND_ROOT
    / "model"
    / "deepfake_model"
)

MODEL_PATH = (
    MODEL_DIR
    / "voiceshield_wav2vec2_asvspoof.pt"
)

BASE_MODEL = "facebook/wav2vec2-base"

TARGET_SAMPLE_RATE = 16000

TARGET_SAMPLES = 64000

DEVICE = torch.device("cpu")


# ============================================================
# MODEL ARCHITECTURE
# ============================================================

class VoiceShieldWav2Vec2(nn.Module):

    def __init__(self):

        super().__init__()

        self.wav2vec2 = Wav2Vec2Model.from_pretrained(
            BASE_MODEL
        )

        # Freeze Wav2Vec2
        for parameter in self.wav2vec2.parameters():
            parameter.requires_grad = False

        self.classifier = nn.Sequential(
            nn.Linear(768, 256),
            nn.GELU(),
            nn.Dropout(0.1),
            nn.Linear(256, 2)
        )

    def forward(self, frames):

        outputs = self.wav2vec2(
            input_values=frames
        )

        hidden_states = outputs.last_hidden_state

        # Mean pooling
        pooled = hidden_states.mean(dim=1)

        logits = self.classifier(pooled)

        return logits


# ============================================================
# GLOBAL MODEL
# ============================================================

deepfake_model = None
feature_extractor = None


# ============================================================
# LOAD MODEL
# ============================================================

def load_deepfake_model():

    global deepfake_model
    global feature_extractor

    if deepfake_model is not None:
        return deepfake_model

    print("Loading VoiceShield Wav2Vec2 deepfake model...")

    # Feature extractor
    feature_extractor = (
        Wav2Vec2FeatureExtractor
        .from_pretrained(BASE_MODEL)
    )

    # Model
    deepfake_model = VoiceShieldWav2Vec2()

    # Load local trained weights
    state = torch.load(
        MODEL_PATH,
        map_location=DEVICE
    )

    # Handle possible checkpoint wrapper
    if isinstance(state, dict):

        if "state_dict" in state:
            state = state["state_dict"]

        elif "model_state_dict" in state:
            state = state["model_state_dict"]

    # Remove module. prefix if present
    clean_state = {}

    for key, value in state.items():

        if key.startswith("module."):
            key = key[len("module."):]

        clean_state[key] = value

    deepfake_model.load_state_dict(
        clean_state,
        strict=True
    )

    deepfake_model.to(DEVICE)

    deepfake_model.eval()

    print(
        "VoiceShield Wav2Vec2 deepfake model loaded!"
    )

    return deepfake_model


# ============================================================
# AUDIO PREPROCESSING
# ============================================================

def load_audio(audio_path):

    audio, sample_rate = sf.read(
        str(audio_path),
        dtype="float32"
    )

    # Stereo → Mono
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    # Resample
    if sample_rate != TARGET_SAMPLE_RATE:

        audio = librosa.resample(
            audio,
            orig_sr=sample_rate,
            target_sr=TARGET_SAMPLE_RATE
        )

    audio = audio.astype("float32")

    # Trim to 4 seconds
    if len(audio) > TARGET_SAMPLES:

        audio = audio[:TARGET_SAMPLES]

    # Pad to 4 seconds
    elif len(audio) < TARGET_SAMPLES:

        padding = TARGET_SAMPLES - len(audio)

        audio = torch.nn.functional.pad(
            torch.tensor(audio),
            (0, padding)
        ).numpy()

    return audio


# ============================================================
# DEEPFAKE PREDICTION
# ============================================================

def detect_deepfake(audio_path):

    model = load_deepfake_model()

    audio = load_audio(audio_path)

    inputs = feature_extractor(
        audio,
        sampling_rate=TARGET_SAMPLE_RATE,
        return_tensors="pt"
    )

    input_values = (
        inputs.input_values
        .float()
        .to(DEVICE)
    )

    with torch.no_grad():

        logits = model(
            input_values
        )

        probabilities = torch.softmax(
            logits,
            dim=-1
        )

    predicted_class = torch.argmax(
        probabilities,
        dim=-1
    ).item()

    bonafide_probability = float(
        probabilities[0][0].item()
    )

    spoof_probability = float(
        probabilities[0][1].item()
    )

    if predicted_class == 0:

        result = "Bonafide"

    else:

        result = "Spoof"

    return {
        "result": result,
        "is_deepfake": predicted_class == 1,
        "class_id": predicted_class,
        "bonafide_probability": round(
            bonafide_probability,
            4
        ),
        "spoof_probability": round(
            spoof_probability,
            4
        )
    }