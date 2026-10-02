import torch
import torchaudio
import soundfile as sf

from speechbrain.inference.speaker import (
    SpeakerRecognition
)


# ============================================================
# ECAPA-TDNN MODEL
# ============================================================

MODEL_SOURCE = (
    "speechbrain/spkrec-ecapa-voxceleb"
)

MODEL_DIR = (
    r"C:\models\spkrec-ecapa-voxceleb"
)


verification_model = None


# ============================================================
# LOAD ECAPA-TDNN
# ============================================================

def load_ecapa_model():

    global verification_model

    if verification_model is None:

        print(
            "Loading ECAPA-TDNN model..."
        )

        verification_model = (
            SpeakerRecognition.from_hparams(
                source=MODEL_SOURCE,
                savedir=MODEL_DIR
            )
        )

        print(
            "ECAPA-TDNN model loaded successfully!"
        )

    return verification_model


# ============================================================
# COMPARE TWO AUDIO FILES
# ============================================================

def compare_voices(
    reference_audio,
    test_audio
):

    model = load_ecapa_model()

    score, prediction = (
        model.verify_files(
            reference_audio,
            test_audio
        )
    )

    return {

        "similarity_score":
            float(
                score.item()
            ),

        "same_speaker":
            bool(
                prediction.item()
            )
    }


# ============================================================
# GENERATE SPEAKER EMBEDDING
# ============================================================

def generate_embedding(
    audio_path
):

    model = load_ecapa_model()

    print(
        f"Generating embedding for: "
        f"{audio_path}"
    )


    # --------------------------------------------------------
    # Read audio using soundfile
    # --------------------------------------------------------

    audio, sample_rate = (
        sf.read(
            audio_path
        )
    )


    # --------------------------------------------------------
    # Convert NumPy audio to Torch tensor
    # --------------------------------------------------------

    signal = torch.tensor(
        audio,
        dtype=torch.float32
    )


    # --------------------------------------------------------
    # Convert stereo → mono
    # --------------------------------------------------------

    if signal.ndim > 1:

        signal = signal.mean(
            dim=1
        )


    # --------------------------------------------------------
    # Resample to 16 kHz
    # --------------------------------------------------------

    if sample_rate != 16000:

        print(
            f"Resampling audio: "
            f"{sample_rate} Hz → 16000 Hz"
        )

        resampler = (
            torchaudio.transforms.Resample(
                orig_freq=sample_rate,
                new_freq=16000
            )
        )

        signal = resampler(
            signal.unsqueeze(0)
        ).squeeze(0)


    # --------------------------------------------------------
    # Add batch dimension
    # --------------------------------------------------------

    signal = signal.unsqueeze(0)


    # --------------------------------------------------------
    # Audio length
    # --------------------------------------------------------

    wav_lens = torch.tensor(
        [1.0],
        dtype=torch.float32
    )


    # --------------------------------------------------------
    # Generate embedding
    # --------------------------------------------------------

    with torch.no_grad():

        embedding = (
            model.encode_batch(
                signal,
                wav_lens
            )
        )


    # --------------------------------------------------------
    # Convert embedding to list
    # --------------------------------------------------------

    embedding = (
        embedding
        .squeeze()
        .cpu()
        .tolist()
    )


    print(
        "Embedding generated successfully!"
    )

    print(
        f"Embedding length: "
        f"{len(embedding)}"
    )


    return embedding


# ============================================================
# COSINE SIMILARITY
# ============================================================

def calculate_cosine_similarity(
    embedding1,
    embedding2
):

    # --------------------------------------------------------
    # Convert lists to tensors
    # --------------------------------------------------------

    emb1 = torch.tensor(
        embedding1,
        dtype=torch.float32
    ).unsqueeze(0)

    emb2 = torch.tensor(
        embedding2,
        dtype=torch.float32
    ).unsqueeze(0)


    # --------------------------------------------------------
    # Calculate cosine similarity
    # --------------------------------------------------------

    similarity = (
        torch.nn.functional
        .cosine_similarity(
            emb1,
            emb2
        )
    )


    return float(
        similarity.item()
    )