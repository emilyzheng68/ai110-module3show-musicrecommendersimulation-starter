# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

VibeFinder 1.0

---

## 2. Intended Use

This recommender generates song suggestions for a listener based on a stated taste profile: favorite genre, favorite mood, a target energy level, and optionally whether they like acoustic-leaning songs. It assumes the user can express their taste as these simple categories rather than through a listening history — there's no login, no tracked behavior, no other users involved. This is a classroom exploration of content-based filtering, not a production system: it's built to demonstrate how a simple, explainable scoring rule can simulate what a real recommender does, using a small 18-song catalog rather than real streaming data.

---

## 3. How the Model Works

Every song gets scored against a listener's taste profile using four simple rules. If the song's genre matches the listener's favorite genre, it earns 2 points. If the song's mood matches the listener's favorite mood, it earns 1 point. Then, instead of just rewarding high or low energy, the system checks how close the song's energy is to what the listener wants — a perfect match earns up to 1.5 points, and the reward shrinks the further off it is. Finally, if the listener says they like acoustic songs, the song earns a bonus based on how acoustic it actually is. All the points get added up into one score, and every song also comes with a plain-language list of reasons (like "genre match" or "energy similarity") so it's clear why it was suggested — not just a number. The starter logic only had placeholder functions with no real scoring; we built the actual point system, the sorting logic that turns individual scores into a ranked list, and the acoustic bonus rule (needed since the starter's `UserProfile` included a `likes_acoustic` field that wasn't part of the original plan).

---

## 4. Data

The catalog has 18 songs. It spans genres including pop, lofi, rock, ambient, jazz, synthwave, indie pop, folk, hip hop, classical, r&b, punk, and k-pop, and moods including happy, chill, intense, relaxed, moody, focused, nostalgic, energetic, sad, angry, and calm. We expanded the original 10-song starter file by adding 8 more songs specifically chosen to cover genres and moods the starter didn't have (like classical, punk, and k-pop), to give the system more variety to differentiate between. Missing from the dataset: anything about lyrics, language, cultural context, or the acoustic instrumentation actually present in a track beyond the single `acousticness` number — real taste is shaped by lyrics and cultural meaning in ways this dataset can't capture at all.

---

## 5. Strengths

The system does well when a listener's taste maps cleanly onto one clear genre and mood — for example, testing a "High-Energy Pop" profile (genre=pop, mood=intense, high energy) correctly surfaced "Gym Hero," the one song in the catalog matching all three criteria closely, ahead of songs that only partially matched. Similarly, a "Chill Lofi" profile correctly ranked the catalog's actual lofi/chill tracks at the top, and a "Deep Sad Classical" profile correctly found the catalog's classical/sad songs. These results matched my own intuition well: when a clean, non-contradictory taste profile is given, the top-ranked songs feel like genuinely reasonable picks, and the "reasons" list makes it obvious why each one won.

---

## 6. Limitations and Bias

This system over-relies on exact-match genre and mood labels, so a song that's a near-perfect emotional and energetic fit but tagged with a different genre string will lose out to a lower-quality match that happens to share the genre label. The weight-shift experiment showed this concretely: when energy was weighted 2x and genre was halved, "Broken Glass Anthem" (a punk/angry track with zero connection to "sad r&b") nearly tied "Heartline" (an actual genre and mood match) for the Adversarial profile, closing what was an 0.80-point gap down to 0.08 — evidence that genre and mood are carrying real signal that a naive energy-only system would lose. More broadly, the Adversarial test (sad mood + near-max energy, a real but contradictory combination) revealed that this recommender cannot blend conflicting preferences: it picks whichever single dimension scores best and produces an incoherent list below that, rather than finding a genuine middle-ground song. With only 18 songs in the catalog, there's also limited room for the system to demonstrate nuance — a larger catalog might reveal further genre-bias patterns that a small dataset can't surface.

---

## 7. Evaluation

I tested four profiles: High-Energy Pop, Chill Lofi, Deep Sad Classical, and one deliberately adversarial profile (r&b genre + sad mood + energy target of 0.95 — a real but contradictory combination, since sad r&b songs in the catalog are all low-energy). The first three profiles produced results that matched my intuition and didn't repeat the same song across different profiles, which suggested the genre weight wasn't so strong that it flattened all variety. The adversarial profile was the most revealing: its top score (3.53) was noticeably lower than every other profile's top score (all above 4.0), and its winning song ("Heartline") won mostly on genre and mood while giving up a lot on energy fit — the system couldn't find a song that was genuinely good on all three dimensions, because none existed in the catalog. I also ran a weight-shift experiment, halving the genre weight and doubling the energy weight. This closed the gap between the adversarial profile's #1 and #2 results from 0.80 points down to just 0.08 — nearly letting a completely unrelated punk song ("Broken Glass Anthem") outrank the actual genre/mood match, purely because of energy closeness. That was the most surprising result: it showed how sensitive the ranking is to weight choices, and confirmed that genre and mood are carrying real, meaningful signal in the original recipe rather than being redundant with energy.

**Profile-to-profile comparisons:**

- **High-Energy Pop vs. Chill Lofi:** almost no overlap in top 5 — High-Energy Pop pulls fast, intense tracks like "Gym Hero" and "Storm Runner," while Chill Lofi pulls slow, quiet tracks like "Library Rain" and "Midnight Coding." This makes sense: the two profiles have opposite `target_energy` values (0.95 vs. 0.15), so a song can't score well for both at once.
- **Chill Lofi vs. Deep Sad Classical:** both prefer low energy, so their top results share a similar "quiet" quality, but the genre changes what actually shows up — Chill Lofi surfaces lofi tracks, Deep Sad Classical surfaces classical tracks, even though the energy targets (0.15 vs. 0.2) are close. This shows genre matching, not just energy, is steering which specific songs win.
- **Deep Sad Classical vs. Adversarial (Sad + Max Energy):** both want "sad," but Deep Sad Classical also wants low energy (0.2) while the Adversarial profile wants near-max energy (0.95) with the same mood. The results are completely different despite sharing a mood — the Adversarial profile is forced into a much weaker top score (3.53 vs. 4.47) because no song is both sad and high-energy in the catalog, while Deep Sad Classical easily finds "Piano in the Rain," which is genuinely both classical and sad and quiet.

**Explaining "Gym Hero" in plain language:** if you ask this system for "happy pop" music, you might notice a workout-anthem-style song like "Gym Hero" sneaking into your results, even though it's tagged "intense," not "happy." Here's why: the system gives credit for being close in energy level even when the mood doesn't perfectly match. "Gym Hero" is loud and fast, in a similar energy range to a lot of upbeat happy pop, so it picks up enough energy points — combined with matching the genre — to land in the top few, even without a mood match. In other words, the system sometimes confuses "high energy" with "happy," because it only checks mood as an exact label rather than understanding that intense and happy are related but not identical feelings.

---

## 8. Future Work

First, I'd add `valence` as a second closeness-scored feature alongside energy, since our own feature evaluation found cases where a song's mood label and its actual valence score didn't agree — a "moody" song with lower valence than a "relaxed" song, for instance. Second, I'd add a diversity penalty so the top-5 doesn't return two songs from the same artist (as happened with "Piano in the Rain" and "Still Water," both by Elena Voss, in the Deep Sad Classical results) — real recommenders usually try to vary artists even within a matching taste. Third, I'd let users express partial or blended preferences (e.g., 70% happy / 30% sad) instead of one exact-match label, so contradictory-feeling requests like the adversarial profile could actually be satisfied by a genuinely blended song instead of the system just picking whichever single dimension wins.

---

## 9. Personal Reflection

## 9. Personal Reflection

My biggest learning moment was realizing how much a recommender's behavior comes down to arbitrary-seeming weight choices. Genre being worth 2 points and mood being worth 1 point felt like a reasonable starting guess, but the weight-shift experiment showed those exact numbers determine whether a completely irrelevant song can nearly tie a genuinely well-matched one — a system that looks like it's "working" on easy inputs can fall apart the moment you give it a contradictory but realistic request.

My AI coding assistant was most useful for generating boilerplate (the CSV-reading loop, the sorting logic) and for stress-testing my own ideas — asking it to suggest adversarial profiles surfaced the sad-mood-plus-high-energy conflict I hadn't thought of on my own. But I had to double-check its suggestions at least once: it initially proposed computing energy similarity as a plain `1 - gap` with no scaling weight, which would have made a close energy match worth almost as much as a full genre match. That sounded reasonable but wasn't what I intended, so I caught it and added the proper weight scaling myself.

What surprised me most is how "smart" this system can feel with no actual learning involved. There's no training data, no other users, no history — just a handful of if-statements and a subtraction — and yet the ranked list still feels like a real recommendation. That's a useful reminder that perceived intelligence in an app often comes from clear feature design and confident presentation, not from anything sophisticated happening under the hood.

If I extended this project, I'd start by adding `valence` as a real scored feature rather than something I only evaluated and set aside, since it's the piece most likely to fix the "Gym Hero for Happy Pop" problem — a proper valence check would catch that "intense" and "happy" aren't the same feeling even when their energy levels overlap. I'd also want to see how the system behaves with a much larger catalog, since 18 songs is really too small to know whether the genre-bias patterns I found are real trends or just artifacts of a tiny dataset.
