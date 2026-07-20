# 🎵 Music Recommender Simulation

## Project Summary

This project simulates a content-based music recommender. It scores each song in a catalog against a user's taste profile using genre, mood, and energy (plus an optional acoustic bonus), then returns a ranked, explained top-K list of recommendations — each with a plain-language reason for why it was suggested.

---

## How The System Works

Real music platforms like Spotify or YouTube generally combine two different prediction strategies. Collaborative filtering looks at other users' behavior — if listeners who share your taste also loved a certain song, that song gets recommended to you, even if it doesn't sound anything like your usual favorites. Content-based filtering, which is what this project implements, ignores other users entirely and instead compares a song's own measurable attributes (genre, mood, energy, tempo) against a profile of what a specific listener tends to enjoy. Real platforms also draw on data like likes, skips, replays, playlist adds, and listening duration to keep refining their picture of a user's taste over time — our simulation only uses a small, static slice of that: genre, mood, and energy, pulled from a fixed CSV of songs rather than live user behavior. This simulation prioritizes explainability: every recommendation comes with a plain-language reason (e.g., "genre match," "energy similarity") so it's clear why a song was suggested, which is something real black-box systems rarely expose to users.

**Collaborative Filtering**
- How it works: This method relies on the listening behavior of users. It assumes that if two users have similar listening habits, they are likely to enjoy the same songs. It doesn't analyze the content of the songs themselves.
- Example: If User A and User B both listen to Artist X, and User B also listens to Artist Y, the system might recommend Artist Y to User A.
- Strengths: Learns from large-scale user behavior; can recommend songs even if the system knows little about the song's attributes.
- Weaknesses: Struggles with the "cold start problem" (e.g., new users or songs with no listening history); relies heavily on user data.

**Content-Based Filtering**
- How it works: This method analyzes the attributes of the songs themselves, such as tempo, genre, key, lyrics, or instrumentation. It recommends songs that are similar to what the user has already liked or listened to.
- Example: If a user listens to a lot of upbeat pop songs with a fast tempo, the system might recommend other songs with similar characteristics.
- Strengths: Works well for users with limited listening history; doesn't require data from other users.
- Weaknesses: Limited to the attributes of the songs; may lead to a "filter bubble," where recommendations lack diversity.

**Key Difference**
Collaborative Filtering focuses on patterns in user behavior and relationships between users. Content-Based Filtering focuses on the intrinsic properties of the songs themselves. Most platforms use a hybrid approach, combining both methods to leverage the strengths of each and mitigate their weaknesses.

### Feature Evaluation

Looking at `data/songs.csv`, the most effective features for a content-based recommender are:

1. **Genre** — Effectiveness: High. A strong, broad indicator of taste; most listeners have a fairly consistent genre preference.
2. **Mood** — Effectiveness: High. Captures emotional tone (happy, chill, intense); users often pick music based on desired emotional state.
3. **Energy** — Effectiveness: Medium-High. Reflects intensity; useful for context (workout vs. relaxing), though importance varies by user.
4. **Valence** — Effectiveness: Medium. Measures positivity/happiness; refines mood-based recommendations but isn't universally prioritized.
5. **Danceability** — Effectiveness: Medium. Relevant for rhythm-focused listeners, less so for ambient/instrumental fans.
6. **Tempo (BPM)** — Effectiveness: Medium. Useful for activity-matching (e.g., running), but overlaps a lot with energy.
7. **Acousticness** — Effectiveness: Low-Medium. Distinguishes acoustic vs. electronic-sounding tracks; adds nuance but isn't critical for general recommendations.

**My take:** I agree genre and mood are the strongest signals — those are the first two things I think about when picking music. I'm less sure energy should outrank valence, though. In my experience, "vibe" is often more about emotional tone (valence) than raw intensity (energy) — a slow, low-energy song can still feel uplifting, and a fast, high-energy song can feel dark. In the dataset, "Night Drive Loop" is tagged "moody" with a valence of only 0.49, while "Coffee Shop Stories" is "relaxed" but has a higher valence of 0.71 — that gap between the mood label and the actual valence number is exactly the kind of nuance a simple genre+mood system can miss. I'll start with genre, mood, and energy to match the assignment's suggested recipe, but I think valence deserves more weight than "medium" and is a strong candidate to add next.

### Our Algorithm Recipe

Each song is scored against a user's taste profile using four weighted rules:

**1. Genre Match — +2.0 points**
If the song's genre exactly matches the user's favorite genre, award 2.0 points. Genre gets the biggest weight because it's the broadest and most stable signal of taste — most listeners have a fairly consistent genre preference that doesn't shift day to day.

**2. Mood Match — +1.0 point**
If the song's mood exactly matches the user's favorite mood, award 1.0 point. Mood is weighted at half of genre because it's a narrower, more situational preference — the same listener might want "happy" music one day and "chill" the next, so it's treated as a secondary refinement rather than a primary filter.

**3. Energy Closeness — up to +1.5 points**
Rather than rewarding high or low energy directly, this rule rewards how close a song's energy is to the user's target energy:
```
gap = abs(song_energy - user_target_energy)
points = 1.5 * (1 - gap)
```
A perfect match (gap = 0) earns the full 1.5 points; a complete mismatch (gap = 1.0) earns 0 points. This scaled approach was chosen deliberately over a simple "above/below threshold" rule, since it lets two songs with a small energy difference score almost as well as an exact match, instead of an all-or-nothing pass/fail.

**4. Acoustic Bonus — up to +1.0 point (conditional)**
If the user's profile has `likes_acoustic = True`, the song earns bonus points equal to its `acousticness` value (0.0–1.0) scaled up to 1.0. Users who don't specify an acoustic preference (`likes_acoustic = False`) get no bonus or penalty here.

**Total score** = genre points + mood points + energy points + (conditional) acoustic points, and each song's result is paired with a plain-language list of *reasons* (e.g., `"genre match (+2.0)"`) so every recommendation is explainable rather than a black-box number.

**Why weight genre highest?** This is a deliberate trade-off worth naming: weighting genre so heavily means the system can over-favor genre matches even when a song's mood or energy is a poor fit — a bias confirmed in the evaluation phase (see below and `model_card.md`).

*(Stretch idea, not yet implemented: `valence` could be added as a fifth closeness-scored feature, similar to energy, to better capture emotional "vibe" independent of the mood label.)*

### Data Objects

**Song** — each row in `data/songs.csv` becomes a song record with these fields:
- `id` — unique identifier
- `title` — song name
- `artist` — artist name
- `genre` — category (e.g., pop, lofi, rock, ambient, jazz, synthwave, indie pop, folk, hip hop, classical, r&b, punk, k-pop)
- `mood` — emotional tag (e.g., happy, chill, intense, relaxed, moody, focused, nostalgic, energetic, sad, angry, calm)
- `energy` — intensity, 0.0–1.0
- `tempo_bpm` — beats per minute
- `valence` — musical positivity/happiness, 0.0–1.0
- `danceability` — how suitable for dancing, 0.0–1.0
- `acousticness` — how acoustic vs. electronic/produced, 0.0–1.0

**UserProfile** — a taste profile used for scoring, containing:
- `favorite_genre` — target genre for genre-match scoring
- `favorite_mood` — target mood for mood-match scoring
- `target_energy` — target energy value (0.0–1.0) for closeness scoring
- `likes_acoustic` — boolean; if true, songs earn an additional acoustic bonus

`genre`, `mood`, `energy`, and (conditionally) `acousticness` are used for scoring in this version — `tempo_bpm`, `valence`, and `danceability` are captured in the dataset but not yet part of the recipe.

**Proposed User Profile (initial testing)**
```python
user_profile = {
    "favorite_genre": "pop",
    "favorite_mood": "happy",
    "target_energy": 0.75
}
```

**Critique: Can this differentiate "intense rock" vs. "chill lofi"?**

Yes — quite well, actually. Checked against the dataset:
- **Storm Runner** (rock, intense, energy 0.91): genre doesn't match ("pop" ≠ "rock"), mood doesn't match ("happy" ≠ "intense"), energy gap is `|0.91 - 0.75| = 0.16` → small energy credit only, low total score.
- **Library Rain** (lofi, chill, energy 0.35): genre doesn't match, mood doesn't match, energy gap is `|0.35 - 0.75| = 0.40` → very little credit anywhere, lowest total score.
- **Sunrise City** (pop, happy, energy 0.82): genre matches, mood matches, energy gap only `0.07` → high score.

So this profile correctly separates all three clusters — pop/happy songs rank highest, rock/intense songs score low on genre+mood but get partial energy credit, and lofi/chill songs score lowest overall since they're low-energy and mismatched on both categorical fields.

**Where it's too narrow:**
- A user who likes pop *and* occasional lofi has no way to express that — `favorite_genre` only accepts one value.
- Two songs that both fail genre + mood matching get scored purely on energy closeness, even though they could be wildly different vibes.
- It ignores valence entirely, so a "happy" mood match doesn't verify the song actually feels positive (per the mood/valence mismatch found in the feature evaluation above).

**Verdict:** the three-field profile clearly separates broad clusters like "intense rock" vs. "chill lofi," but it's a blunt instrument for anything more nuanced (mixed tastes, within-genre preference, mood/valence mismatches) — see Limitations below.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
```

2. Install dependencies

```bash
   pip install -r requirements.txt
```

3. Run the app:

```bash
   python3 -m src.main
```

### Running Tests

Run the starter tests with:

```bash
python3 -m pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Baseline run with the default pop/happy profile:

```
Loaded songs: 18
=== Top Recommendations (pop / happy / energy=0.8) ===
1. Sunrise City by Neon Echo
   Score: 4.47
   Reasons: genre match (+2.0), mood match (+1.0), energy similarity (+1.47, gap=0.02)
2. Gym Hero by Max Pulse
   Score: 3.30
   Reasons: genre match (+2.0), energy similarity (+1.3, gap=0.13)
3. Rooftop Lights by Indigo Parade
   Score: 2.44
   Reasons: mood match (+1.0), energy similarity (+1.44, gap=0.04)
4. Cherry Skyline by NEON DAWN
   Score: 2.43
   Reasons: mood match (+1.0), energy similarity (+1.43, gap=0.05)
5. Concrete Bloom by MC Solace
   Score: 1.48
   Reasons: energy similarity (+1.48, gap=0.01)
```

Stress-test run with four diverse profiles (High-Energy Pop, Chill Lofi, Deep Sad Classical, and an adversarial sad+high-energy profile):

```
Loaded songs: 18

=== High-Energy Pop ===
Preferences: {'genre': 'pop', 'mood': 'intense', 'energy': 0.95}
1. Gym Hero by Max Pulse
   Score: 4.47
   Reasons: genre match (+2.0), mood match (+1.0), energy similarity (+1.47, gap=0.02)
2. Sunrise City by Neon Echo
   Score: 3.30
   Reasons: genre match (+2.0), energy similarity (+1.3, gap=0.13)
3. Storm Runner by Voltline
   Score: 2.44
   Reasons: mood match (+1.0), energy similarity (+1.44, gap=0.04)
4. Broken Glass Anthem by Riot Static
   Score: 1.48
   Reasons: energy similarity (+1.48, gap=0.01)
5. Cherry Skyline by NEON DAWN
   Score: 1.35
   Reasons: energy similarity (+1.35, gap=0.10)

=== Chill Lofi ===
Preferences: {'genre': 'lofi', 'mood': 'chill', 'energy': 0.15}
1. Library Rain by Paper Lanterns
   Score: 4.20
   Reasons: genre match (+2.0), mood match (+1.0), energy similarity (+1.2, gap=0.20)
2. Midnight Coding by LoRoom
   Score: 4.09
   Reasons: genre match (+2.0), mood match (+1.0), energy similarity (+1.09, gap=0.27)
3. Focus Flow by LoRoom
   Score: 3.12
   Reasons: genre match (+2.0), energy similarity (+1.12, gap=0.25)
4. Spacewalk Thoughts by Orbit Bloom
   Score: 2.30
   Reasons: mood match (+1.0), energy similarity (+1.3, gap=0.13)
5. Still Water by Elena Voss
   Score: 1.50
   Reasons: energy similarity (+1.5, gap=0.00)

=== Deep Sad Classical ===
Preferences: {'genre': 'classical', 'mood': 'sad', 'energy': 0.2}
1. Piano in the Rain by Elena Voss
   Score: 4.47
   Reasons: genre match (+2.0), mood match (+1.0), energy similarity (+1.47, gap=0.02)
2. Still Water by Elena Voss
   Score: 3.42
   Reasons: genre match (+2.0), energy similarity (+1.42, gap=0.05)
3. Heartline by Marlowe James
   Score: 2.35
   Reasons: mood match (+1.0), energy similarity (+1.35, gap=0.10)
4. Spacewalk Thoughts by Orbit Bloom
   Score: 1.38
   Reasons: energy similarity (+1.38, gap=0.08)
5. Library Rain by Paper Lanterns
   Score: 1.28
   Reasons: energy similarity (+1.28, gap=0.15)

=== Adversarial: Sad + Max Energy ===
Preferences: {'genre': 'r&b', 'mood': 'sad', 'energy': 0.95}
1. Heartline by Marlowe James
   Score: 3.53
   Reasons: genre match (+2.0), mood match (+1.0), energy similarity (+0.53, gap=0.65)
2. Slow Burn Confession by Marlowe James
   Score: 2.73
   Reasons: genre match (+2.0), energy similarity (+0.73, gap=0.51)
3. Broken Glass Anthem by Riot Static
   Score: 1.48
   Reasons: energy similarity (+1.48, gap=0.01)
4. Gym Hero by Max Pulse
   Score: 1.47
   Reasons: energy similarity (+1.47, gap=0.02)
5. Storm Runner by Voltline
   Score: 1.44
   Reasons: energy similarity (+1.44, gap=0.04)
```

---

## Experiments You Tried

I ran a weight-shift experiment: halved the genre weight (2.0 → 1.0) and doubled the energy weight (1.5 → 3.0). The effect was most visible on the adversarial profile above (r&b genre, sad mood, but a near-max energy target of 0.95 — a real but contradictory combination). With the original weights, the top result ("Heartline," a genuine genre and mood match) beat the #2 result by a comfortable 0.80 points. With the shifted weights, that gap collapsed to just 0.08 — nearly letting "Broken Glass Anthem," a punk/angry song with zero connection to sad r&b, outrank the actual match purely because its energy happened to be close to the target. I reverted back to the original weights afterward, since the shift made results *different*, not more accurate — a listener asking for sad r&b almost certainly wouldn't want a punk anthem regardless of tempo.

I also tested the system across four different user types (High-Energy Pop, Chill Lofi, Deep Sad Classical, and the adversarial profile above). No single song dominated every list, which suggested genre wasn't so overweighted that it flattened all variety. Full profile-by-profile comparisons are in `model_card.md`, Section 7.

---

## Limitations and Risks

- The system over-relies on exact-match genre and mood labels — a song that's a near-perfect emotional/energy fit but tagged with a different genre string loses out to a lower-quality match that merely shares a genre label.
- It cannot blend contradictory preferences. The adversarial test (sad mood + near-max energy) showed the system just picks whichever single dimension scores best, producing an incoherent list rather than finding a genuine middle-ground song.
- With only 18 songs in the catalog, there's limited room to demonstrate nuance — a larger catalog might reveal further genre-bias patterns a small dataset can't surface.
- It doesn't understand lyrics, language, or cultural context at all — taste shaped by lyrical meaning is invisible to this system.

Full analysis with concrete evidence (exact scores, specific songs) is in `model_card.md`, Section 6 (Limitations and Bias).

---

## Reflection

Read the complete reflection in [`model_card.md`](model_card.md), Section 9.

Short version: the biggest lesson was how much a recommender's behavior depends on seemingly arbitrary weight choices — the weight-shift experiment showed that halving genre's weight nearly let a completely irrelevant song outrank a real match. I also found it surprising how "smart" a system with zero actual learning can feel — no training data, no other users, just a handful of if-statements and a subtraction, and the output still feels like a personalized recommendation. That's a useful reminder that perceived intelligence often comes from clear feature design, not necessarily algorithmic sophistication.



