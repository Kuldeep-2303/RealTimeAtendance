from deepface import DeepFace
from fastapi import HTTPException

def detect_emotion(image_file):
    """
    Detect emotion from a face image using DeepFace.
    """
    try:
        # DeepFace can return a list of dicts (for multiple faces) or a single dict.
        # We need to handle both cases safely.
        analysis_result = DeepFace.analyze(
            img_path=image_file, 
            actions=["emotion"], 
            enforce_detection=False,
            silent=True # Prevents DeepFace from printing its own logs
        )

        # Case 1: It's a list (multiple faces detected)
        if isinstance(analysis_result, list) and len(analysis_result) > 0:
            return analysis_result[0].get("dominant_emotion", "unknown")
        
        # Case 2: It's a dictionary (single face detected)
        if isinstance(analysis_result, dict):
            return analysis_result.get("dominant_emotion", "unknown")

        return "unknown" # No face or emotion detected
    except Exception as e:
        # Log the actual error for debugging, but return a user-friendly message
        # This prevents raising an HTTPException from a service layer.
        print(f"DeepFace analysis failed: {e}")
        return "error"
