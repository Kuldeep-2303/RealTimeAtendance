# This module holds the in-memory cache for face recognition data.
# It's populated at startup and updated when new users are registered.

from typing import List

# Global cache for known face encodings and their corresponding user objects
known_face_encodings: List = []
known_face_users: List = []
