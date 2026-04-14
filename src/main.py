"""
Command line runner for the Music Recommender Simulation.

Run with:
    python src/main.py

Switch between profiles below by changing ACTIVE_PROFILE.
"""

from recommender import load_songs, recommend_songs

# ---------------------------------------------------------------------------
# Taste profiles — change ACTIVE_PROFILE to try a different archetype.
# ---------------------------------------------------------------------------

PROFILES = {
    "pop_happy": {
        "genre":               "pop",
        "mood":                "happy",
        "target_energy":       0.80,
        "target_valence":      0.84,
        "target_acousticness": 0.18,
    },
    "study": {
        "genre":               "lofi",
        "mood":                "focused",
        "target_energy":       0.40,
        "target_valence":      0.58,
        "target_acousticness": 0.75,
    },
    "workout": {
        "genre":               "pop",
        "mood":                "intense",
        "target_energy":       0.92,
        "target_valence":      0.77,
        "target_acousticness": 0.05,
    },
    "night_drive": {
        "genre":               "synthwave",
        "mood":                "moody",
        "target_energy":       0.76,
        "target_valence":      0.49,
        "target_acousticness": 0.20,
    },
    "hiphop": {
        "genre":               "hip-hop",
        "mood":                "confident",
        "target_energy":       0.85,
        "target_valence":      0.72,
        "target_acousticness": 0.06,
    },
}

ACTIVE_PROFILE = "pop_happy"

WIDTH = 60


def print_header(profile_name: str, prefs: dict) -> None:
    print("=" * WIDTH)
    print("  Music Recommender Simulation")
    print(f"  Profile : {profile_name}")
    print(f"  genre={prefs['genre']}  |  mood={prefs['mood']}  |  energy={prefs['target_energy']}")
    print("=" * WIDTH)


def print_recommendation(rank: int, song: dict, score: float, explanation: str) -> None:
    print(f"\n  #{rank}  {song['title']}  —  {song['artist']}")
    print(f"       Score : {score:.2f} / 9.0 pts")
    print(f"       Why   :")
    for reason in explanation.split(" | "):
        print(f"         {reason}")


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    user_prefs = PROFILES[ACTIVE_PROFILE]
    print_header(ACTIVE_PROFILE, user_prefs)

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\n  Top {len(recommendations)} Recommendations\n" + "-" * WIDTH)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print_recommendation(rank, song, score, explanation)

    print("\n" + "=" * WIDTH)


if __name__ == "__main__":
    main()
