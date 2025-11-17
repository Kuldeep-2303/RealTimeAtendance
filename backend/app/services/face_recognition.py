import face_recognition
import numpy as np
from fastapi import HTTPException
from typing import List, Optional, IO, Tuple, Union
from app.models import User

def extract_face_embeddings(image_file: IO[bytes], return_position: bool = False) -> Union[Tuple[Optional[bytes], Optional[float]], Optional[bytes]]:
    """
    Extract face embeddings and optionally the horizontal position of the face.
    """
    image = face_recognition.load_image_file(image_file)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    if len(face_encodings) == 0:
        return (None, None) if return_position else None
    
    # Calculate horizontal position of the first detected face
    if return_position:
        top, right, bottom, left = face_locations[0]
        image_width = image.shape[1]
        face_center_x = (left + right) / 2
        horizontal_position = face_center_x / image_width
        return face_encodings[0].tobytes(), horizontal_position
    
    return face_encodings[0].tobytes()

def find_best_match(unknown_encoding_bytes: bytes, known_encodings: List[np.ndarray], known_users: List[User], tolerance: float = 0.6) -> Optional[User]:
    """
    Finds the best matching user from a list of users.

    Args:
        unknown_encoding_bytes: The face embeddings of the unknown face.
        known_encodings: A list of known face encodings (numpy arrays).
        known_users: A list of User objects corresponding to the encodings.
        tolerance: How much distance between faces to consider it a match.
                   Lower is stricter. 0.6 is the typical default.

    Returns:
        The User object of the best match, or None if no match is found within tolerance.
    """
    if not known_encodings:
        return None

    unknown_encoding = np.frombuffer(unknown_encoding_bytes, dtype=np.float64)

    # Compare the new face with all known faces and get the distances
    face_distances = face_recognition.face_distance(known_encodings, unknown_encoding)

    # Find the index of the best match (the one with the smallest distance)
    best_match_index = np.argmin(face_distances)

    # If the best match is within the tolerance, return the corresponding user
    if face_distances[best_match_index] <= tolerance:
        return known_users[best_match_index]

    return None
