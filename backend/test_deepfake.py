from services.deepfake_detection import detect_deepfake

audio_path = r"..\dataset\trusted_voices\abinaya1.wav"

result = detect_deepfake(audio_path)

print("\n================================")
print("DEEPFAKE DETECTION RESULT")
print("================================")

print("Result:", result["result"])
print("Is Deepfake:", result["is_deepfake"])
print(
    "Bonafide Probability:",
    result["bonafide_probability"]
)
print(
    "Spoof Probability:",
    result["spoof_probability"]
)