import csv
from dataclasses import dataclass
from typing import List, Dict, Tuple

# ---------------------------------------------------------------------------
# Algorithm Recipe — point values for each feature (max total = 9.0 pts)
#
# Feature            Points    Why
# ─────────────────  ────────  ──────────────────────────────────────────────
# Mood match         +3.0      Most context-sensitive — listeners say "I want
#                              something chill NOW" even outside their genre
# Energy similarity  up to +2.0 Widest perceptual spread in dataset (0.22–0.97)
#                              Wrong energy feels immediately wrong
# Genre match        +2.0      Cultural identity — prevents jarring cross-genre
#                              surprises, but ranks below mood intentionally
# Valence similarity up to +1.5 Separates "fast-happy" from "fast-sad" —
#                              the edge case genre + energy alone can't catch
# Acousticness sim.  up to +0.5 Texture modifier (organic vs synthetic) —
#                              meaningful but rarely the deciding factor
# ---------------------------------------------------------------------------
_POINTS = {
    "mood_match":    3.0,
    "energy_max":    2.0,
    "genre_match":   2.0,
    "valence_max":   1.5,
    "acoustic_max":  0.5,
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Song:
    """Immutable record of a song and its audio feature attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # New columns added in the expanded dataset — defaulted so existing
    # test fixtures that omit them still construct successfully.
    speechiness: float = 0.0
    instrumentalness: float = 0.0
    liveness: float = 0.0


@dataclass
class UserProfile:
    """Stores a listener's taste preferences for content-based scoring."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool          # True → prefers acoustic; False → prefers synthetic


# ---------------------------------------------------------------------------
# Functional interface  (used by src/main.py)
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Parse a songs CSV file and return a list of dicts with typed numeric fields."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":               int(row["id"]),
                "title":            row["title"],
                "artist":           row["artist"],
                "genre":            row["genre"],
                "mood":             row["mood"],
                "energy":           float(row["energy"]),
                "tempo_bpm":        float(row["tempo_bpm"]),
                "valence":          float(row["valence"]),
                "danceability":     float(row["danceability"]),
                "acousticness":     float(row["acousticness"]),
                "speechiness":      float(row.get("speechiness", 0.0)),
                "instrumentalness": float(row.get("instrumentalness", 0.0)),
                "liveness":         float(row.get("liveness", 0.0)),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences and return (total_pts, reasons_list). Max score = 9.0."""
    score = 0.0
    reasons = []

    # ── Mood (categorical, +3.0 on exact match) ───────────────────────────────
    target_mood = user_prefs.get("mood") or user_prefs.get("favorite_mood", "")
    if song["mood"] == target_mood:
        score += _POINTS["mood_match"]
        reasons.append(f"+{_POINTS['mood_match']:.1f} mood matches '{song['mood']}'")

    # ── Energy (proximity, up to +2.0) ────────────────────────────────────────
    target_energy = float(
        user_prefs.get("target_energy") if user_prefs.get("target_energy") is not None
        else user_prefs.get("energy", 0.5)
    )
    energy_pts = _POINTS["energy_max"] * (1.0 - abs(song["energy"] - target_energy))
    score += energy_pts
    reasons.append(
        f"+{energy_pts:.2f} energy similarity "
        f"(song {song['energy']:.2f}, target {target_energy:.2f})"
    )

    # ── Genre (categorical, +2.0 on exact match) ──────────────────────────────
    target_genre = user_prefs.get("genre") or user_prefs.get("favorite_genre", "")
    if song["genre"] == target_genre:
        score += _POINTS["genre_match"]
        reasons.append(f"+{_POINTS['genre_match']:.1f} genre matches '{song['genre']}'")

    # ── Valence (proximity, up to +1.5) ───────────────────────────────────────
    target_valence = float(user_prefs.get("target_valence", 0.65))
    valence_pts = _POINTS["valence_max"] * (1.0 - abs(song["valence"] - target_valence))
    score += valence_pts
    reasons.append(
        f"+{valence_pts:.2f} valence similarity "
        f"(song {song['valence']:.2f}, target {target_valence:.2f})"
    )

    # ── Acousticness (proximity, up to +0.5) ──────────────────────────────────
    # Accepts either a float target or the legacy bool from UserProfile.
    if user_prefs.get("target_acousticness") is not None:
        target_acoustic = float(user_prefs["target_acousticness"])
    else:
        target_acoustic = 0.8 if user_prefs.get("likes_acoustic") else 0.2
    acoustic_pts = _POINTS["acoustic_max"] * (1.0 - abs(song["acousticness"] - target_acoustic))
    score += acoustic_pts
    reasons.append(
        f"+{acoustic_pts:.2f} acousticness similarity "
        f"(song {song['acousticness']:.2f}, target {target_acoustic:.2f})"
    )

    return round(score, 4), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score every song, sort by score descending, and return the top-k (song, score, explanation) tuples."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = " | ".join(reasons)
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]


# ---------------------------------------------------------------------------
# OOP interface  (used by tests/test_recommender.py)
# ---------------------------------------------------------------------------

class Recommender:
    """
    OOP wrapper around the functional scoring logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        """Store the song catalog for repeated recommendation calls."""
        self.songs = songs

    def _profile_to_dict(self, user: UserProfile) -> Dict:
        """Converts a UserProfile dataclass into a dict for score_song()."""
        return {
            "genre":             user.favorite_genre,
            "mood":              user.favorite_mood,
            "target_energy":     user.target_energy,
            "target_acousticness": 0.8 if user.likes_acoustic else 0.2,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Returns the top-k Song objects sorted by descending score."""
        user_dict = self._profile_to_dict(user)
        scored = []
        for song in self.songs:
            song_dict = {
                "genre":            song.genre,
                "mood":             song.mood,
                "energy":           song.energy,
                "valence":          song.valence,
                "acousticness":     song.acousticness,
                "speechiness":      song.speechiness,
                "instrumentalness": song.instrumentalness,
                "liveness":         song.liveness,
            }
            score, _ = score_song(user_dict, song_dict)
            scored.append((song, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a plain-language explanation of why song was recommended."""
        user_dict = self._profile_to_dict(user)
        song_dict = {
            "genre":            song.genre,
            "mood":             song.mood,
            "energy":           song.energy,
            "valence":          song.valence,
            "acousticness":     song.acousticness,
            "speechiness":      song.speechiness,
            "instrumentalness": song.instrumentalness,
            "liveness":         song.liveness,
        }
        _, reasons = score_song(user_dict, song_dict)
        return " | ".join(reasons)
