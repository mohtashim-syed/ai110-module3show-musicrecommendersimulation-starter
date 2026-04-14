# Model Card: VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0** — A Content-Based Music Recommender Simulation

Built for: AI 110 Module 3 | Language: Python | Interface: command-line terminal

---

## 2. Goal / Task

VibeFinder takes a listener's stated preferences — their favorite genre, the mood they are in, and how energetic they want the music to feel — and finds the songs from a small catalog that best match those preferences right now.

It does not track listening history, learn from past behavior, or compare listeners to each other. It only looks at the features of each song and compares them to what the user described. Think of it as a knowledgeable friend who has heard every song in the room and quickly says: "Based on what you just told me, here are the five that fit best — and here is exactly why."

The output for each recommendation includes the song title, a score out of 10, and a plain-English breakdown of which features matched and by how much.

---

## 3. Data Used

**Catalog size:** 20 songs stored in `data/songs.csv`

**Features per song (13 total):**

| Feature | Type | What it measures |
|---|---|---|
| genre | text label | Musical style (pop, rock, lofi, jazz, etc.) |
| mood | text label | Emotional feel (happy, chill, intense, sad, etc.) |
| energy | 0.0 – 1.0 | How intense or active the song feels |
| valence | 0.0 – 1.0 | How positive or bright the song sounds |
| acousticness | 0.0 – 1.0 | How organic/unplugged vs synthetic it sounds |
| tempo_bpm | number | Speed in beats per minute |
| danceability | 0.0 – 1.0 | How well it fits rhythmic movement |
| speechiness | 0.0 – 1.0 | How much spoken word or rap is present |
| instrumentalness | 0.0 – 1.0 | Likelihood there are no vocals |
| liveness | 0.0 – 1.0 | Whether it sounds like a live performance |

**Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, classical, country, r&b, metal, reggae, folk, latin, house, k-pop

**Moods represented:** happy, chill, intense, relaxed, focused, moody, confident, melancholic, sad, romantic, angry, uplifting, nostalgic, dreamy

**What was changed from the starter dataset:** The original file had 10 songs. Ten new songs were added to cover genres and moods that were missing (hip-hop, classical, metal, reggae, folk, latin, house, k-pop) and three new feature columns were added (speechiness, instrumentalness, liveness).

**Known data limits:**
- 20 songs is very small. Most genres appear exactly once.
- Only 2 songs fall in the 0.45–0.70 energy range — most songs are either very low or very high energy, with almost nothing in the middle.
- The catalog reflects the tastes and assumptions of one person who built it. It skews toward English-language Western genres.

---

## 4. Algorithm Summary

The system scores every song in the catalog against the user's preferences, then ranks them from highest to lowest score.

**How one song gets scored (maximum 10 points):**

**Mood — up to 3 points.**
If the song's mood label exactly matches the user's target mood, it earns the full 3 points. If the moods are different — even if they are close, like "relaxed" vs "chill" — it earns zero. Mood carries the most weight because it is the most context-sensitive preference: the mood someone wants to listen to right now changes more than their genre preferences do.

**Energy — up to 4 points.**
Energy is not all-or-nothing. The system measures how far the song's energy is from the user's target and awards points based on closeness. A song that is exactly on target earns 4 points. A song that is 0.5 away earns 2 points. A song that is 1.0 away earns zero. This rewards proximity rather than "higher is better" — a user who wants medium energy (0.5) should not get the highest-energy songs just because energy is being measured.

**Genre — up to 1 point.**
Genre is an exact match only, same as mood. Matching earns 1 point, not matching earns zero. Genre carries less weight than mood or energy because genre labels are imprecise — "indie pop" and "pop" are different labels but sound similar — and because mood and energy better capture the in-the-moment feeling the listener is describing.

**Valence — up to 1.5 points.**
Valence measures emotional brightness (happy and upbeat vs dark and melancholy). It uses the same proximity approach as energy. This feature separates songs that look the same on energy and genre but feel completely different — for example, a fast happy song vs a fast angry one.

**Acousticness — up to 0.5 points.**
Acousticness distinguishes organic, instrument-heavy recordings from electronic, synthetic ones. It is scored by proximity, with a small ceiling because it is a refining detail rather than a deciding factor.

**The ranking step:**
After every song is scored, the list is sorted from highest to lowest. The top five results are returned with a breakdown of which features contributed.

---

## 5. Observed Behavior / Biases

**Where the system works well:**

When a user's mood and genre have at least one matching song in the catalog, the system almost always returns that song in the #1 spot by a wide margin. Storm Runner (rock/intense) scored 9.91 out of 10 for the deep_intense_rock profile. Library Rain (lofi/chill) scored 9.82 for the chill_lofi profile. In these cases the recommendations feel completely right — the system is doing exactly what it should.

The explanation feature works well. Every result includes a per-feature breakdown showing how many points each attribute contributed. This makes it possible to understand and question the recommendation, which is something real streaming apps almost never show you.

**Where the system struggles (biases):**

The most significant bias discovered during testing is a **low-energy cluster effect** caused by a bimodal energy distribution in the catalog: 8 of the 20 songs have energy below 0.45 (lofi, ambient, folk, classical), 10 have energy above 0.70, and only 2 songs — Velvet Hours and Island Morning — fall in the 0.45–0.70 mid-range. Because the proximity formula scores every song on every profile, those 8 low-energy songs earn moderate energy-similarity points on any profile that does not explicitly target very high energy, which causes tracks like Midnight Coding, Spacewalk Thoughts, and Focus Flow to appear in the top-5 of profiles they have no business serving — during experiments each of those three songs appeared in three different top-5 lists, including profiles targeting hip-hop, synthwave, and ambient genres. This is a filter bubble: a user who wants reggae or r&b will likely receive lofi songs at positions #4 and #5 simply because the catalog lacks mid-energy variety, not because those songs are a good match. The problem is not the scoring weights — doubling energy's weight did not eliminate these appearances — it is the absence of songs in the energy middle-ground that leaves the scorer with no better candidate to fill the lower slots. In a production system this would be addressed by enforcing diversity constraints (no more than one song per genre per result list) and by expanding the catalog so every energy bracket has at least five songs competing for each position.

A second bias is the **exact-match cliff for mood and genre.** A user who wants "relaxed" music scores zero on all "chill" songs even though those moods are nearly identical. There is no partial credit for near-synonyms. This makes the system brittle when the user's vocabulary does not exactly match the catalog's labels.

A third bias is the **contradiction blindness problem.** If a user asks for mood=sad and energy=0.92 at the same time, the system cannot flag that these two preferences conflict. It just returns the closest mathematical answer, which in testing was an angry metal song — not a sad song at all.

---

## 6. Evaluation Process

Six user profiles were tested in total: three standard profiles designed to produce sensible, expected results (high_energy_pop, chill_lofi, deep_intense_rock), and three adversarial profiles designed to stress-test the scoring logic (sad_banger, ghost_genre, neutral_listener). For each profile, the top-5 recommendations were inspected to check whether the #1 result was the obvious correct answer, whether the top-3 felt coherent as a playlist, and whether any song appeared that had no business being there.

**What matched expectations:** Every standard profile returned a near-perfect #1 result. Sunrise City (pop/happy, 9.62/10) was the clear winner for high_energy_pop, Library Rain (lofi/chill, 9.82/10) for chill_lofi, and Storm Runner (rock/intense, 9.91/10) for deep_intense_rock. In all three cases the top song matched the genre, mood, and energy target simultaneously, producing very high scores with no surprises.

**What was surprising:** Three results were unexpected and revealed genuine weaknesses.

First, Gym Hero (pop/intense) appeared at #3 for the high_energy_pop profile despite having the wrong mood — it is intense, not happy. This happens because the catalog only has two pop/happy songs, so once those two are used at #1 and #2, the system has no better pop option and reaches for the closest remaining pop song regardless of mood.

Second, Iron Cathedral (metal/angry) ranked above Heartbreak Porch (country/sad) for the sad_banger profile — meaning an angry metal song was recommended to someone who asked for sad music. The energy mismatch on Heartbreak Porch (asked for 0.92, song is 0.41) cost more points than the mood mismatch penalty on Iron Cathedral, exposing that the scorer cannot detect contradictory user preferences.

Third, the ghost_genre profile (genre=bluegrass, which does not exist in the catalog) returned top-3 scores of 8.94, 8.62, and 8.59 — all within 0.35 points of each other, making the ranking feel nearly arbitrary. Removing the genre signal collapsed the separation between results, showing how much the system depends on categorical matches to create meaningful distance between songs.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- Classroom exploration of how content-based filtering works
- Learning exercise for understanding scoring logic, feature weighting, and bias in recommendation systems
- A starting point for experimenting with weight changes, new features, or different datasets
- Demonstration of how a simple algorithm can produce explainable recommendations

**Not intended for:**
- Real users making real music choices — the 20-song catalog is far too small
- Commercial or production deployment of any kind
- Drawing conclusions about what music people actually prefer in the real world
- Replacing or simulating the behavior of actual streaming platforms, which use millions of songs, behavioral data, and much more complex models
- Any context where a biased or wrong recommendation would have consequences

---

## 8. Ideas for Improvement

**1. Enforce result diversity.**
Add a rule that prevents the same genre or artist from appearing more than once in the top-5. Right now the system can return three lofi songs in a row. A diversity penalty would force the list to spread across different sounds, which is more useful for a listener who wants variety.

**2. Detect and warn about conflicting preferences.**
Before scoring, check whether the user's preferences are internally consistent. If someone asks for mood=sad and energy=0.92 at the same time, the system should say something like: "Note — sad songs in this catalog tend to have low energy. Your results may not fully satisfy both preferences." This does not change the math, but it gives the user context to interpret the output.

**3. Expand the catalog and fill the energy gap.**
Add at least 30–40 more songs specifically targeting the 0.45–0.70 energy range, where the current catalog has almost nothing. Also add more songs per genre so that a genre match returns a real family of options rather than a single track. This one change would fix most of the filter bubble problems observed in testing without requiring any changes to the scoring logic.

---

## 9. Personal Reflection

Building this system made it clear how much work goes into what feels like a simple feature in a real app. When Spotify says "Daily Mix" or "Because you listened to X," there is a scoring and ranking process happening behind it — but at a scale millions of times larger than this simulation, with behavioral signals (skips, replays, shares) that this system completely ignores. The most surprising discovery was how much the tiny catalog size distorted the results. The scoring logic itself worked correctly, but a 20-song library is so small that it regularly ran out of good options and had to return songs that were only loosely related to the user's request. The bias was not in the math — it was in the data. That felt like an important lesson: a well-designed algorithm can still produce misleading results if the dataset it runs on is unbalanced or incomplete.
