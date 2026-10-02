from speechbrain.inference.speaker import SpeakerRecognition

print("Loading ECAPA-TDNN...")
verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="C:/models/spkrec-ecapa-voxceleb",
)
print("Loaded successfully!")