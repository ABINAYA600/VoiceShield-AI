from speechbrain.inference.speaker import SpeakerRecognition
from speechbrain.utils.fetching import LocalStrategy

print("Loading ECAPA-TDNN...")

verification = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="../pretrained_models/spkrec-ecapa-voxceleb",
    local_strategy=LocalStrategy.COPY_SKIP_CACHE
)

print("ECAPA-TDNN loaded successfully!")