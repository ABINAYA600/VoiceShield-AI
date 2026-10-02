from speechbrain.inference.speaker import SpeakerRecognition

print("Loading ECAPA-TDNN...")

verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir=r"C:\models\spkrec-ecapa-voxceleb"
)

print("ECAPA-TDNN loaded!")

# Same synthetic speaker test
score, prediction = verification.verify_files(
    r"..\dataset\trusted_voices\abinaya1.wav",
    r"..\dataset\trusted_voices\abinaya2.wav"
)

print("\n--- Same Speaker Test ---")
print("Similarity Score :", score.item())
print("Same Speaker :", bool(prediction.item()))

# Different synthetic speaker test
score2, prediction2 = verification.verify_files(
    r"..\dataset\trusted_voices\abinaya1.wav",
    r"..\dataset\trusted_voices\father.wav"
)

print("\n--- Different Speaker Test ---")
print("Similarity Score :", score2.item())
print("Same Speaker :", bool(prediction2.item()))