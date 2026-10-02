import os
import shutil
import uuid

from datetime import datetime
from pathlib import Path

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Form,
    HTTPException
)

from fastapi.middleware.cors import (
    CORSMiddleware
)

from bson import ObjectId
from bson.errors import InvalidId


# ============================================================
# PROJECT IMPORTS
# ============================================================

from config import UPLOAD_DIR

from database import (
    trusted_voices_collection,
    analysis_collection,
    test_database
)

from services.speaker_verification import (
    generate_embedding,
    calculate_cosine_similarity
)

from services.deepfake_detection import (
    detect_deepfake
)

from services.risk_analysis import (
    calculate_risk_score
)


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="VoiceShield AI API",
    description=(
        "AI-Powered Voice Deepfake Detection "
        "and Speaker Verification System"
    ),
    version="1.0.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# CREATE UPLOAD DIRECTORY
# ============================================================

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# ============================================================
# STARTUP EVENT
# ============================================================

@app.on_event("startup")
def startup_event():

    print(
        "\n==================================="
    )

    print(
        "VoiceShield AI Backend Starting"
    )

    print(
        "==================================="
    )

    test_database()

    print(
        "Upload directory:",
        UPLOAD_DIR
    )

    print(
        "Backend started successfully!"
    )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "success": True,

        "message":
            "VoiceShield AI Backend is running!",

        "project":
            "VoiceShield AI",

        "version":
            "1.0.0"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {
        "success": True,

        "status":
            "healthy",

        "service":
            "VoiceShield AI Backend"
    }


# ============================================================
# REGISTER TRUSTED VOICE
# ============================================================

@app.post("/trusted-voices")
async def register_trusted_voice(

    name: str = Form(...),

    relationship: str = Form(...),

    audio: UploadFile = File(...)
):

    print(
        "\n==================================="
    )

    print(
        "REGISTERING TRUSTED VOICE"
    )

    print(
        "==================================="
    )

    # --------------------------------------------------------
    # Validate audio file
    # --------------------------------------------------------

    if not audio.filename:

        raise HTTPException(
            status_code=400,
            detail="Audio file is required."
        )

    print(
        "Name:",
        name
    )

    print(
        "Relationship:",
        relationship
    )

    print(
        "Original file:",
        audio.filename
    )

    # --------------------------------------------------------
    # Generate unique filename
    # --------------------------------------------------------

    file_extension = os.path.splitext(
        audio.filename
    )[1].lower()

    if not file_extension:

        file_extension = ".wav"

    unique_filename = (
        f"{uuid.uuid4()}"
        f"{file_extension}"
    )

    file_path = os.path.join(
        UPLOAD_DIR,
        unique_filename
    )

    # --------------------------------------------------------
    # Save uploaded audio
    # --------------------------------------------------------

    try:

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                audio.file,
                buffer
            )

        print(
            "Audio saved:"
        )

        print(
            file_path
        )

    except Exception as e:

        print(
            "Audio saving failed:"
        )

        print(e)

        raise HTTPException(
            status_code=500,
            detail="Failed to save audio file."
        )

    # --------------------------------------------------------
    # Generate ECAPA embedding
    # --------------------------------------------------------

    embedding = None

    embedding_status = "pending"

    try:

        print(
            "\nGenerating "
            "ECAPA-TDNN embedding..."
        )

        embedding = generate_embedding(
            file_path
        )

        embedding_status = "ready"

        print(
            "Embedding generated successfully!"
        )

        print(
            "Embedding dimension:",
            len(embedding)
        )

    except Exception as e:

        print(
            "\nEmbedding generation failed:"
        )

        print(e)

        embedding_status = "failed"

    # --------------------------------------------------------
    # Create MongoDB document
    # --------------------------------------------------------

    now = datetime.utcnow()

    speaker_document = {

        "name":
            name,

        "relationship":
            relationship,

        "original_filename":
            audio.filename,

        "audio_filename":
            unique_filename,

        "audio_path":
            file_path,

        "embedding":
            embedding,

        "embedding_status":
            embedding_status,

        "embedding_dimension":
            (
                len(embedding)
                if embedding is not None
                else 0
            ),

        "created_at":
            now,

        "updated_at":
            now
    }

    # --------------------------------------------------------
    # Insert into MongoDB
    # --------------------------------------------------------

    try:

        result = (
            trusted_voices_collection
            .insert_one(
                speaker_document
            )
        )

        speaker_id = str(
            result.inserted_id
        )

        print(
            "\nMongoDB document created!"
        )

        print(
            "Speaker ID:",
            speaker_id
        )

    except Exception as e:

        print(
            "\nMongoDB insertion failed:"
        )

        print(e)

        if os.path.exists(
            file_path
        ):

            os.remove(
                file_path
            )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save "
                "trusted voice in database."
            )
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "success":
            True,

        "message":
            "Trusted voice registered successfully!",

        "speaker_id":
            speaker_id,

        "name":
            name,

        "relationship":
            relationship,

        "audio_filename":
            unique_filename,

        "embedding_status":
            embedding_status,

        "embedding_dimension":
            (
                len(embedding)
                if embedding is not None
                else 0
            )
    }


# ============================================================
# GET ALL TRUSTED VOICES
# ============================================================

@app.get("/trusted-voices")
def get_trusted_voices():

    try:

        voices = list(
            trusted_voices_collection
            .find()
            .sort(
                "created_at",
                -1
            )
        )

        result = []

        for voice in voices:

            result.append({

                "speaker_id":
                    str(
                        voice["_id"]
                    ),

                "name":
                    voice.get(
                        "name",
                        ""
                    ),

                "relationship":
                    voice.get(
                        "relationship",
                        ""
                    ),

                "original_filename":
                    voice.get(
                        "original_filename",
                        ""
                    ),

                "audio_filename":
                    voice.get(
                        "audio_filename",
                        ""
                    ),

                "embedding_status":
                    voice.get(
                        "embedding_status",
                        "pending"
                    ),

                "embedding_dimension":
                    voice.get(
                        "embedding_dimension",
                        0
                    ),

                "created_at":
                    (
                        voice["created_at"].isoformat()
                        if voice.get("created_at")
                        else None
                    )
            })

        return {

            "success":
                True,

            "count":
                len(result),

            "voices":
                result
        }

    except Exception as e:

        print(
            "Failed to retrieve trusted voices:"
        )

        print(e)

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to retrieve "
                "trusted voices."
            )
        )


# ============================================================
# GET SINGLE TRUSTED VOICE
# ============================================================

@app.get("/trusted-voices/{speaker_id}")
def get_trusted_voice(
    speaker_id: str
):

    try:

        object_id = ObjectId(
            speaker_id
        )

    except InvalidId:

        raise HTTPException(
            status_code=400,
            detail="Invalid speaker ID."
        )

    voice = (
        trusted_voices_collection
        .find_one(
            {
                "_id":
                    object_id
            }
        )
    )

    if not voice:

        raise HTTPException(
            status_code=404,
            detail="Trusted voice not found."
        )

    return {

        "success":
            True,

        "voice": {

            "speaker_id":
                str(
                    voice["_id"]
                ),

            "name":
                voice.get(
                    "name",
                    ""
                ),

            "relationship":
                voice.get(
                    "relationship",
                    ""
                ),

            "original_filename":
                voice.get(
                    "original_filename",
                    ""
                ),

            "audio_filename":
                voice.get(
                    "audio_filename",
                    ""
                ),

            "embedding_status":
                voice.get(
                    "embedding_status",
                    "pending"
                ),

            "embedding_dimension":
                voice.get(
                    "embedding_dimension",
                    0
                ),

            "created_at":
                (
                    voice["created_at"].isoformat()
                    if voice.get("created_at")
                    else None
                )
        }
    }


# ============================================================
# VERIFY INCOMING VOICE
# ============================================================

@app.post("/verify-voice")
async def verify_voice(
    audio: UploadFile = File(...)
):

    print(
        "\n==================================="
    )

    print(
        "VOICE VERIFICATION"
    )

    print(
        "==================================="
    )

    temporary_path = None

    # --------------------------------------------------------
    # Validate incoming audio
    # --------------------------------------------------------

    if not audio.filename:

        raise HTTPException(
            status_code=400,
            detail="Audio file is required."
        )

    print(
        "Incoming audio:",
        audio.filename
    )

    # --------------------------------------------------------
    # Generate temporary filename
    # --------------------------------------------------------

    file_extension = os.path.splitext(
        audio.filename
    )[1].lower()

    if not file_extension:

        file_extension = ".wav"

    temporary_filename = (
        f"verify_"
        f"{uuid.uuid4()}"
        f"{file_extension}"
    )

    temporary_path = os.path.join(
        UPLOAD_DIR,
        temporary_filename
    )

    # --------------------------------------------------------
    # Save incoming audio
    # --------------------------------------------------------

    try:

        with open(
            temporary_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                audio.file,
                buffer
            )

        print(
            "Incoming audio saved:"
        )

        print(
            temporary_path
        )

    except Exception as e:

        print(
            "Failed to save incoming audio:"
        )

        print(e)

        raise HTTPException(
            status_code=500,
            detail="Failed to save audio file."
        )

    try:

        # ====================================================
        # STEP 1
        # Generate embedding
        # ====================================================

        print(
            "\nGenerating embedding "
            "for incoming voice..."
        )

        incoming_embedding = (
            generate_embedding(
                temporary_path
            )
        )

        print(
            "Incoming embedding generated."
        )

        print(
            "Embedding dimension:",
            len(incoming_embedding)
        )

        # ====================================================
        # STEP 2
        # Get ALL trusted voices
        # ====================================================

        trusted_voices = list(
            trusted_voices_collection.find(
                {
                    "embedding":
                        {
                            "$exists":
                                True,

                            "$ne":
                                None
                        }
                }
            )
        )

        if not trusted_voices:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No trusted voices with "
                    "embeddings found."
                )
            )

        print(
            "\nTrusted voices found:",
            len(trusted_voices)
        )

        # ====================================================
        # STEP 3
        # Compare against EVERY trusted voice
        # ====================================================

        comparison_results = []

        for voice in trusted_voices:

            stored_embedding = (
                voice.get(
                    "embedding"
                )
            )

            if not stored_embedding:
                continue

            similarity = (
                calculate_cosine_similarity(
                    incoming_embedding,
                    stored_embedding
                )
            )

            comparison_results.append({

                "speaker_id":
                    str(
                        voice["_id"]
                    ),

                "name":
                    voice.get(
                        "name",
                        "Unknown"
                    ),

                "relationship":
                    voice.get(
                        "relationship",
                        ""
                    ),

                "similarity_score":
                    round(
                        similarity,
                        4
                    )
            })

            print(
                f"{voice.get('name', 'Unknown')} "
                f"-> {similarity:.4f}"
            )

        # ====================================================
        # STEP 4
        # Check comparison results
        # ====================================================

        if not comparison_results:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No valid speaker embeddings "
                    "available for comparison."
                )
            )

        # ====================================================
        # STEP 5
        # Sort by similarity
        # ====================================================

        comparison_results.sort(
            key=lambda x:
                x["similarity_score"],
            reverse=True
        )

        # ====================================================
        # STEP 6
        # Select highest similarity
        # ====================================================

        best_match = (
            comparison_results[0]
        )

        print(
            "\n==================================="
        )

        print(
            "BEST MATCH"
        )

        print(
            "==================================="
        )

        print(
            "Speaker:",
            best_match["name"]
        )

        print(
            "Similarity:",
            best_match[
                "similarity_score"
            ]
        )

        # ====================================================
        # STEP 7
        # Verification threshold
        # ====================================================

        verification_threshold = 0.75

        is_verified = (

            best_match[
                "similarity_score"
            ]

            >=

            verification_threshold
        )

        # ====================================================
        # STEP 8
        # Verification result
        # ====================================================

        if is_verified:

            verification_result = (
                "Verified"
            )

        else:

            verification_result = (
                "Not Verified"
            )

        print(
            "Verification:",
            verification_result
        )

        print(
            "===================================\n"
        )

        # ====================================================
        # STEP 9
        # Return response
        # ====================================================

        return {

            "success":
                True,

            "verification_result":
                verification_result,

            "speaker_verified":
                is_verified,

            "speaker":
                (
                    best_match["name"]
                    if is_verified
                    else None
                ),

            "relationship":
                (
                    best_match["relationship"]
                    if is_verified
                    else None
                ),

            "similarity_score":
                round(
                    best_match[
                        "similarity_score"
                    ],
                    4
                ),

            "verification_threshold":
                verification_threshold,

            "comparisons": [

                {

                    "name":
                        item["name"],

                    "relationship":
                        item["relationship"],

                    "similarity_score":
                        round(
                            item[
                                "similarity_score"
                            ],
                            4
                        )
                }

                for item
                in comparison_results
            ]
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            "\nVoice verification failed:"
        )

        print(e)

        raise HTTPException(
            status_code=500,
            detail="Voice verification failed."
        )

    finally:

        # --------------------------------------------------------
        # Delete temporary verification audio
        # --------------------------------------------------------

        if (
            temporary_path
            and os.path.exists(
                temporary_path
            )
        ):

            try:

                os.remove(
                    temporary_path
                )

                print(
                    "Temporary verification "
                    "audio deleted."
                )

            except Exception as e:

                print(
                    "Could not delete temporary file:"
                )

                print(e)


# ============================================================
# COMPLETE VOICE ANALYSIS
# ECAPA + WAV2VEC2 + RISK ANALYSIS
# ============================================================

@app.post("/analyze-voice")
async def analyze_voice(
    audio: UploadFile = File(...)
):

    print(
        "\n==================================="
    )

    print(
        "VOICESHIELD AI - COMPLETE ANALYSIS"
    )

    print(
        "==================================="
    )

    temporary_path = None

    try:

        # ====================================================
        # STEP 1
        # Validate audio
        # ====================================================

        if not audio.filename:

            raise HTTPException(
                status_code=400,
                detail="Audio file is required."
            )

        file_extension = os.path.splitext(
            audio.filename
        )[1].lower()

        if file_extension not in [
            ".wav",
            ".flac"
        ]:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Please upload a WAV or FLAC "
                    "audio file."
                )
            )

        # ====================================================
        # STEP 2
        # Save temporary audio
        # ====================================================

        temporary_filename = (
            f"analysis_"
            f"{uuid.uuid4()}"
            f"{file_extension}"
        )

        temporary_path = os.path.join(
            UPLOAD_DIR,
            temporary_filename
        )

        with open(
            temporary_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                audio.file,
                buffer
            )

        print(
            "Analysis audio saved:",
            temporary_path
        )

        # ====================================================
        # STEP 3
        # DEEPFAKE DETECTION
        # ====================================================

        print(
            "\n-----------------------------------"
        )

        print(
            "STEP 1: DEEPFAKE DETECTION"
        )

        print(
            "-----------------------------------"
        )

        deepfake_result = detect_deepfake(
            temporary_path
        )

        print(
            "Deepfake result:",
            deepfake_result["result"]
        )

        print(
            "Bonafide probability:",
            deepfake_result[
                "bonafide_probability"
            ]
        )

        print(
            "Spoof probability:",
            deepfake_result[
                "spoof_probability"
            ]
        )

        # ====================================================
        # STEP 4
        # ECAPA SPEAKER EMBEDDING
        # ====================================================

        print(
            "\n-----------------------------------"
        )

        print(
            "STEP 2: SPEAKER VERIFICATION"
        )

        print(
            "-----------------------------------"
        )

        incoming_embedding = generate_embedding(
            temporary_path
        )

        print(
            "Incoming embedding generated."
        )

        print(
            "Embedding dimension:",
            len(incoming_embedding)
        )

        # ====================================================
        # STEP 5
        # GET TRUSTED VOICES
        # ====================================================

        trusted_voices = list(
            trusted_voices_collection.find(
                {
                    "embedding_status":
                        "ready",

                    "embedding":
                        {
                            "$exists":
                                True,

                            "$ne":
                                None
                        }
                }
            )
        )

        if not trusted_voices:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No trusted voices with "
                    "valid embeddings found."
                )
            )

        print(
            "Trusted voices found:",
            len(trusted_voices)
        )

        # ====================================================
        # STEP 6
        # COMPARE SPEAKER EMBEDDINGS
        # ====================================================

        comparison_results = []

        for voice in trusted_voices:

            stored_embedding = voice.get(
                "embedding"
            )

            if not stored_embedding:
                continue

            similarity = (
                calculate_cosine_similarity(
                    incoming_embedding,
                    stored_embedding
                )
            )

            similarity = round(
                similarity,
                4
            )

            comparison_results.append({

                "speaker_id":
                    str(
                        voice["_id"]
                    ),

                "name":
                    voice.get(
                        "name",
                        "Unknown"
                    ),

                "relationship":
                    voice.get(
                        "relationship",
                        ""
                    ),

                "similarity_score":
                    similarity
            })

            print(
                f"{voice.get('name', 'Unknown')} "
                f"-> {similarity:.4f}"
            )

        if not comparison_results:

            raise HTTPException(
                status_code=404,
                detail=(
                    "No valid speaker embeddings "
                    "available for comparison."
                )
            )

        # ====================================================
        # STEP 7
        # FIND BEST SPEAKER MATCH
        # ====================================================

        comparison_results.sort(
            key=lambda item:
                item["similarity_score"],
            reverse=True
        )

        best_match = (
            comparison_results[0]
        )

        best_similarity = (
            best_match[
                "similarity_score"
            ]
        )

        # ====================================================
        # STEP 8
        # SPEAKER VERIFICATION
        # ====================================================

        verification_threshold = 0.75

        speaker_verified = (
            best_similarity
            >=
            verification_threshold
        )

        if speaker_verified:

            verification_result = (
                "Verified"
            )

            speaker_name = (
                best_match["name"]
            )

            relationship = (
                best_match["relationship"]
            )

        else:

            verification_result = (
                "Not Verified"
            )

            speaker_name = None

            relationship = None

        print(
            "Best speaker:",
            best_match["name"]
        )

        print(
            "Similarity:",
            best_similarity
        )

        print(
            "Verification:",
            verification_result
        )

        # ====================================================
        # STEP 9
        # RISK ANALYSIS
        # ====================================================

        print(
            "\n-----------------------------------"
        )

        print(
            "STEP 3: RISK ANALYSIS"
        )

        print(
            "-----------------------------------"
        )

        risk_result = calculate_risk_score(
            speaker_verified=speaker_verified,

            similarity_score=best_similarity,

            spoof_probability=(
                deepfake_result[
                    "spoof_probability"
                ]
            )
        )

        print(
            "Risk score:",
            risk_result[
                "risk_score"
            ]
        )

        print(
            "Risk level:",
            risk_result[
                "risk_level"
            ]
        )

        # ====================================================
        # STEP 10
        # FINAL RESULT
        # ====================================================

        if deepfake_result[
            "is_deepfake"
        ]:

            final_result = (
                "Potential Voice Deepfake"
            )

        elif not speaker_verified:

            final_result = (
                "Unknown Speaker"
            )

        else:

            final_result = (
                "Trusted Voice"
            )

        print(
            "Final result:",
            final_result
        )

        # ====================================================
        # STEP 11
        # SAVE ANALYSIS TO MONGODB
        # ====================================================

        analysis_document = {

            "audio_filename":
                audio.filename,

            "speaker_verification": {

                "result":
                    verification_result,

                "speaker":
                    speaker_name,

                "relationship":
                    relationship,

                "similarity_score":
                    best_similarity,

                "threshold":
                    verification_threshold,

                "comparisons":
                    comparison_results
            },

            "deepfake_detection": {

                "result":
                    deepfake_result[
                        "result"
                    ],

                "is_deepfake":
                    deepfake_result[
                        "is_deepfake"
                    ],

                "class_id":
                    deepfake_result[
                        "class_id"
                    ],

                "bonafide_probability":
                    deepfake_result[
                        "bonafide_probability"
                    ],

                "spoof_probability":
                    deepfake_result[
                        "spoof_probability"
                    ]
            },

            "risk_analysis": {

                "risk_score":
                    risk_result[
                        "risk_score"
                    ],

                "risk_level":
                    risk_result[
                        "risk_level"
                    ]
            },

            "final_result":
                final_result,

            "created_at":
                datetime.utcnow()
        }

        database_result = (
            analysis_collection.insert_one(
                analysis_document
            )
        )

        analysis_id = str(
            database_result.inserted_id
        )

        print(
            "Analysis saved to MongoDB."
        )

        print(
            "Analysis ID:",
            analysis_id
        )

        # ====================================================
        # STEP 12
        # RETURN COMPLETE RESULT
        # ====================================================

        return {

            "success":
                True,

            "analysis_id":
                analysis_id,

            "speaker_verification": {

                "result":
                    verification_result,

                "speaker":
                    speaker_name,

                "relationship":
                    relationship,

                "similarity_score":
                    best_similarity,

                "threshold":
                    verification_threshold,

                "comparisons":
                    comparison_results
            },

            "deepfake_detection": {

                "result":
                    deepfake_result[
                        "result"
                    ],

                "is_deepfake":
                    deepfake_result[
                        "is_deepfake"
                    ],

                "class_id":
                    deepfake_result[
                        "class_id"
                    ],

                "bonafide_probability":
                    deepfake_result[
                        "bonafide_probability"
                    ],

                "spoof_probability":
                    deepfake_result[
                        "spoof_probability"
                    ]
            },

            "risk_analysis": {

                "risk_score":
                    risk_result[
                        "risk_score"
                    ],

                "risk_level":
                    risk_result[
                        "risk_level"
                    ]
            },

            "final_result":
                final_result
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            "\nComplete voice analysis failed:"
        )

        print(e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        # ====================================================
        # Delete temporary analysis audio
        # ====================================================

        if (
            temporary_path
            and os.path.exists(
                temporary_path
            )
        ):

            try:

                os.remove(
                    temporary_path
                )

                print(
                    "Temporary analysis "
                    "audio deleted."
                )

            except Exception as e:

                print(
                    "Could not delete temporary "
                    "analysis audio:"
                )

                print(e)

        print(
            "===================================\n"
        )


# ============================================================
# DELETE TRUSTED VOICE
# ============================================================

@app.delete("/trusted-voices/{speaker_id}")
def delete_trusted_voice(
    speaker_id: str
):

    try:

        object_id = ObjectId(
            speaker_id
        )

    except InvalidId:

        raise HTTPException(
            status_code=400,
            detail="Invalid speaker ID."
        )

    # --------------------------------------------------------
    # Find trusted voice
    # --------------------------------------------------------

    voice = (
        trusted_voices_collection
        .find_one(
            {
                "_id":
                    object_id
            }
        )
    )

    if not voice:

        raise HTTPException(
            status_code=404,
            detail="Trusted voice not found."
        )

    # --------------------------------------------------------
    # Delete MongoDB document
    # --------------------------------------------------------

    try:

        trusted_voices_collection.delete_one(
            {
                "_id":
                    object_id
            }
        )

    except Exception as e:

        print(
            "MongoDB deletion failed:"
        )

        print(e)

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete "
                "trusted voice."
            )
        )

    # --------------------------------------------------------
    # Delete audio file
    # --------------------------------------------------------

    audio_path = voice.get(
        "audio_path"
    )

    if audio_path:

        try:

            if os.path.exists(
                audio_path
            ):

                os.remove(
                    audio_path
                )

                print(
                    "Audio file deleted:",
                    audio_path
                )

        except Exception as e:

            print(
                "Warning: Could not delete "
                "audio file:"
            )

            print(e)

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "success":
            True,

        "message":
            "Trusted voice deleted successfully.",

        "speaker_id":
            speaker_id
    }