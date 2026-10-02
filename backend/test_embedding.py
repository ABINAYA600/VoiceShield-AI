from services.speaker_verification import generate_embedding


audio_path = r"..\dataset\trusted_voices\abinaya.wav"


embedding = generate_embedding(audio_path)


print("\n===================================")
print("Embedding generated successfully!")
print("===================================")

print("Embedding length:", len(embedding))

print("First 10 values:")
print(embedding[:10])