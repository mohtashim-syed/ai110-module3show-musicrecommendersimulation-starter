# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Real-world recommenders like Spotify and YouTube combine two strategies: collaborative filtering, which surfaces songs that users with similar taste histories have enjoyed, and content-based filtering, which matches songs by their audio attributes — things like energy, tempo, or mood. In practice, platforms layer both approaches together and add context signals like time of day or device type to refine results further. This simulation focuses on the content-based half of that equation. Rather than tracking what other users do, it builds a taste profile from a single user's preferred genre, mood, and target energy level, then scores every song in the catalog by how closely its attributes match those preferences. Each numerical attribute (energy, valence, acousticness) is scored using proximity — songs closer to the user's target receive higher marks — while categorical attributes (genre, mood) use an exact-match rule. The five feature scores are combined into a point total, with mood and energy carrying the most weight because they best capture the "vibe" a listener is after in a given moment. The songs are then ranked by total score and the top results are returned as recommendations. This makes the system transparent and easy to reason about: every recommendation can be explained by pointing to exactly which features matched and by how much.

---

### Algorithm Recipe

**Inputs:** one `UserProfile` (genre, mood, target_energy, target_valence, target_acousticness) and one `Song` dict per evaluation.

**Step 1 — Mood (categorical, +3.0 pts)**
Award the full 3.0 points if `song.mood` exactly equals the user's target mood; otherwise award zero. Mood carries the highest single value because it is the most context-sensitive signal — a listener who wants something "chill right now" should get chill songs even if they cross genre lines.

**Step 2 — Energy similarity (numerical, up to +2.0 pts)**
```
energy_pts = 2.0 × (1 − |song.energy − target_energy|)
```
Energy spans 0.22–0.97 across the catalog — the widest perceptual spread of any feature. Proximity scoring means a song 0.50 away from the target earns only 1.0 pt, not a flat bonus. Wrong energy feels immediately wrong to a listener regardless of everything else.

**Step 3 — Genre (categorical, +2.0 pts)**
Award 2.0 points for an exact genre match; otherwise zero. Genre ranks below mood because it is an identity label, not an in-the-moment feeling — a jazz fan might love an ambient track when studying, even though the genres differ.

**Step 4 — Valence similarity (numerical, up to +1.5 pts)**
```
valence_pts = 1.5 × (1 − |song.valence − target_valence|)
```
Valence separates the edge cases that energy and genre cannot: a high-energy happy song (pop, valence 0.84) vs. a high-energy angry song (metal, valence 0.25) look identical to a mood+energy scorer. Valence catches the emotional color difference.

**Step 5 — Acousticness similarity (numerical, up to +0.5 pts)**
```
acoustic_pts = 0.5 × (1 − |song.acousticness − target_acousticness|)
```
Acousticness distinguishes organic/quiet texture from synthetic/loud texture. It is a refining signal rather than a deciding one — hence the smallest point ceiling.

**Total score:** 0.0 – 9.0 pts. All songs are sorted descending by total, and the top `k` are returned with a per-feature explanation.

---

### Known Biases and Limitations

This system is transparent and simple, but that simplicity creates predictable failure modes worth knowing before interpreting results.

**1. Exact-match penalty for near-synonym moods**
The scorer awards full points or zero points for mood and genre — there is no partial credit. A user who wants "relaxed" songs will score zero on "chill" songs, even though those moods are nearly identical in practice. This makes the system brittle when the user's vocabulary does not exactly match the catalog's labels.

**2. Genre monopoly in a small catalog**
With 17 unique genres across 20 songs, most genres appear exactly once. A +2.0 genre bonus is effectively a named-song bonus — it almost always picks one specific track rather than a family of similar songs. In a real catalog of millions, genre is a broad filter; here it is a near-exact pointer.

**3. Implicit valence default favors moderately positive songs**
When a user profile omits `target_valence`, the scorer defaults to 0.65 — a mildly positive value. This silently penalizes very sad songs (classical, country) and very euphoric songs (k-pop) without the user asking for it. A user who does not know to set valence will unknowingly receive a mid-valence-biased list.

**4. No diversity enforcement — top results can cluster**
The ranking picks the k highest scores with no penalty for repetition. For a "lofi/focused" profile, all three top spots are lofi songs by the same two artists. A real system would enforce diversity by suppressing the same artist or genre from appearing more than once in a short list.

**5. Context blindness**
The system has no concept of time of day, current activity, listening history, or how many times a song has already been played. A real recommender would down-rank recently played songs and adjust for context (workout vs. bedtime). This system would recommend the same list every single time for the same profile.

---

## Data Flow

**Written map:**

```
INPUT              PROCESS                          OUTPUT
─────────────────  ───────────────────────────────  ──────────────────────
User Preferences   load_songs()                     Top k Recommendations
genre              reads data/songs.csv         ┐   ranked by total score
mood          ───► returns 20 song dicts         │   with explanations
target_energy      recommend_songs()             │
target_valence     loops over every song         │
target_acoustic      ↳ score_song() per song     │
                       mood match?   +3.0 pts    │
                       energy prox   +0–2.0 pts  │
                       genre match?  +2.0 pts    │
                       valence prox  +0–1.5 pts  │
                       acoustic prox +0–0.5 pts  ├──► song · score · reason
                     collect all scored tuples   │
                     sort descending by score    │
                     slice top k              ───┘
```

**Mermaid flowchart:**

```mermaid
flowchart TD
    A["📋 User Preferences
    genre · mood
    target_energy · valence · acousticness"]

    B["load_songs()
    Reads data/songs.csv
    Returns list of 20 song dicts"]

    C["recommend_songs()
    Start loop over all 20 songs"]

    A --> B --> C --> D

    D(["Pick next song from catalog"])

    subgraph SCORE ["score_song() — called once per song"]
        F["Mood match?
        +3.0 pts if exact match · +0.0 if miss"]
        G["Energy similarity
        2.0 × (1 − |song.energy − target|)"]
        H["Genre match?
        +2.0 pts if exact match · +0.0 if miss"]
        I["Valence similarity
        1.5 × (1 − |song.valence − target|)"]
        J["Acousticness similarity
        0.5 × (1 − |song.acousticness − target|)"]
        K["Sum all contributions
        Total score: 0.0 – 9.0 pts
        Build explanation list"]
        F --> G --> H --> I --> J --> K
    end

    D --> F
    K --> L{"More songs
    in catalog?"}
    L -- "Yes — loop back" --> D
    L -- "No — all songs scored" --> M

    M["Collect all scored tuples
    song · score · explanation"]
    N["Sort descending by score"]
    O["Slice top k results"]
    P["🏆 Top k Recommendations
    Ranked · Scored · Explained"]

    M --> N --> O --> P
```

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python src/main.py
```

### Sample Output

Default profile: `pop_happy` (genre=pop, mood=happy, energy=0.80)

```
Loaded songs: 20
============================================================
  Music Recommender Simulation
  Profile : pop_happy
  genre=pop  |  mood=happy  |  energy=0.8
============================================================

  Top 5 Recommendations
------------------------------------------------------------

  #1  Sunrise City  —  Neon Echo
       Score : 8.96 / 9.0 pts
       Why   :
         +3.0 mood matches 'happy'
         +1.96 energy similarity (song 0.82, target 0.80)
         +2.0 genre matches 'pop'
         +1.50 valence similarity (song 0.84, target 0.84)
         +0.50 acousticness similarity (song 0.18, target 0.18)

  #2  Rooftop Lights  —  Indigo Parade
       Score : 6.79 / 9.0 pts
       Why   :
         +3.0 mood matches 'happy'
         +1.92 energy similarity (song 0.76, target 0.80)
         +1.46 valence similarity (song 0.81, target 0.84)
         +0.42 acousticness similarity (song 0.35, target 0.18)

  #3  Gym Hero  —  Max Pulse
       Score : 5.57 / 9.0 pts
       Why   :
         +1.74 energy similarity (song 0.93, target 0.80)
         +2.0 genre matches 'pop'
         +1.40 valence similarity (song 0.77, target 0.84)
         +0.43 acousticness similarity (song 0.05, target 0.18)

  #4  Paloma Del Sol  —  Conjunto Vivo
       Score : 3.88 / 9.0 pts
       Why   :
         +1.96 energy similarity (song 0.78, target 0.80)
         +1.48 valence similarity (song 0.85, target 0.84)
         +0.43 acousticness similarity (song 0.31, target 0.18)

  #5  Neon Seoul  —  Starfall K
       Score : 3.75 / 9.0 pts
       Why   :
         +1.84 energy similarity (song 0.88, target 0.80)
         +1.42 valence similarity (song 0.89, target 0.84)
         +0.48 acousticness similarity (song 0.15, target 0.18)

============================================================
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

