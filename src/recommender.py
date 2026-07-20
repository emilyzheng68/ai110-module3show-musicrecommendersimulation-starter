"""
Core recommendation logic for the Music Recommender Simulation.

This module has two parallel interfaces that share the same Algorithm Recipe:

1. OOP interface (Song, UserProfile, Recommender) - required by tests/test_recommender.py
2. Functional interface (load_songs, score_song, recommend_songs) - required by src/main.py

Algorithm Recipe:
- Genre match:            +2.0 points
- Mood match:              +1.0 point
- Energy closeness:       up to +1.5 points (scaled by how close song.energy is to target_energy)
- Acoustic preference:    up to +1.0 point (only applies when the user says they like acoustic songs)
"""

import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass

GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
MAX_ENERGY_POINTS = 1.5
MAX_ACOUSTIC_POINTS = 1.0


@dataclass
class Song:
    """Represents a song and its attributes."""
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


@dataclass
class UserProfile:
    """Represents a user's taste preferences, including genre, mood, energy, and acoustic preference."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _score_song_object(user: UserProfile, song: Song):
    """Score a Song object against a UserProfile using the Algorithm Recipe."""
    score = 0.0
    reasons = []

    if song.genre == user.favorite_genre:
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match (+{GENRE_MATCH_POINTS})")

    if song.mood == user.favorite_mood:
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match (+{MOOD_MATCH_POINTS})")

    gap = abs(song.energy - user.target_energy)
    energy_points = round(max(MAX_ENERGY_POINTS * (1 - gap), 0.0), 2)
    score += energy_points
    reasons.append(f"energy similarity (+{energy_points}, gap={gap:.2f})")

    if user.likes_acoustic:
        acoustic_points = round(MAX_ACOUSTIC_POINTS * song.acousticness, 2)
        score += acoustic_points
        reasons.append(f"acoustic bonus (+{acoustic_points})")

    return round(score, 2), reasons


class Recommender:
    """OOP wrapper that scores and ranks a fixed catalog of Song objects."""

    def __init__(self, songs: List[Song]):
        """Store the song catalog this recommender will rank."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top k songs for this user, ranked highest score first."""
        scored = [(song, _score_song_object(user, song)[0]) for song in self.songs]
        ranked = sorted(scored, key=lambda pair: pair[1], reverse=True)
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a plain-language explanation of why a song scored the way it did."""
        score, reasons = _score_song_object(user, song)
        if not reasons:
            return f"'{song.title}' scored {score} with no matching preferences."
        return f"'{song.title}' scored {score}: " + ", ".join(reasons)


def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields converted."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["id"] = int(row["id"])
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict):
    """Score a single song dict against a user_prefs dict using the Algorithm Recipe."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs.get("genre"):
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match (+{GENRE_MATCH_POINTS})")

    if song["mood"] == user_prefs.get("mood"):
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match (+{MOOD_MATCH_POINTS})")

    target_energy = user_prefs.get("energy")
    if target_energy is not None:
        gap = abs(song["energy"] - target_energy)
        energy_points = round(max(MAX_ENERGY_POINTS * (1 - gap), 0.0), 2)
        score += energy_points
        reasons.append(f"energy similarity (+{energy_points}, gap={gap:.2f})")

    return round(score, 2), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5):
    """Score every song, then return the top k as (song, score, explanation) tuples, ranked highest first."""
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons) if reasons else "no matching preferences"
        scored.append((song, score, explanation))

    ranked = sorted(scored, key=lambda item: item[1], reverse=True)
    return ranked[:k]
