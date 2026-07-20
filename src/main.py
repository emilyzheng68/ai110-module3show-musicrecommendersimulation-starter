"""
Command line runner for the Music Recommender Simulation.

Run with: python3 -m src.main
"""

from src.recommender import load_songs, recommend_songs

PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "intense", "energy": 0.95},
    "Chill Lofi": {"genre": "lofi", "mood": "chill", "energy": 0.15},
    "Deep Sad Classical": {"genre": "classical", "mood": "sad", "energy": 0.2},
    "Adversarial: Sad + Max Energy": {"genre": "r&b", "mood": "sad", "energy": 0.95},
}


def print_recommendations(profile_name, user_prefs, songs, k=5):
    print(f"\n=== {profile_name} ===")
    print(f"Preferences: {user_prefs}\n")
    recommendations = recommend_songs(user_prefs, songs, k=k)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} by {song['artist']}")
        print(f"   Score: {score:.2f}")
        print(f"   Reasons: {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    for name, prefs in PROFILES.items():
        print_recommendations(name, prefs, songs, k=5)


if __name__ == "__main__":
    main()
