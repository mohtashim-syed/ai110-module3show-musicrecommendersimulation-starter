# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

The most significant bias discovered during testing is a **low-energy cluster effect** caused by a bimodal energy distribution in the catalog: 8 of the 20 songs have energy below 0.45 (lofi, ambient, folk, classical), 10 have energy above 0.70, and only 2 songs — Velvet Hours and Island Morning — fall in the 0.45–0.70 mid-range. Because the proximity formula scores every song on every profile, those 8 low-energy songs earn moderate energy-similarity points on any profile that does not explicitly target very high energy, which causes tracks like Midnight Coding, Spacewalk Thoughts, and Focus Flow to appear in the top-5 of profiles they have no business serving — during experiments each of those three songs appeared in three different top-5 lists, including profiles targeting hip-hop, synthwave, and ambient genres. This is a filter bubble: a user who wants reggae or r&b will likely receive lofi songs at positions #4 and #5 simply because the catalog lacks mid-energy variety, not because those songs are a good match. The problem is not the scoring weights — doubling energy's weight did not eliminate these appearances — it is the absence of songs in the energy middle-ground that leaves the scorer with no better candidate to fill the lower slots. In a production system this would be addressed by enforcing diversity constraints (no more than one song per genre per result list) and by expanding the catalog so every energy bracket has at least five songs competing for each position.

---

## 7. Evaluation  

Six user profiles were tested in total: three standard profiles designed to produce sensible, expected results (high_energy_pop, chill_lofi, deep_intense_rock), and three adversarial profiles designed to stress-test the scoring logic (sad_banger, ghost_genre, neutral_listener). For each profile, the top-5 recommendations were inspected to check whether the #1 result was the obvious correct answer, whether the top-3 felt coherent as a playlist, and whether any song appeared that had no business being there.

**What matched expectations:** Every standard profile returned a near-perfect #1 result. Sunrise City (pop/happy, 9.62/10) was the clear winner for high_energy_pop, Library Rain (lofi/chill, 9.82/10) for chill_lofi, and Storm Runner (rock/intense, 9.91/10) for deep_intense_rock. In all three cases the top song matched the genre, mood, and energy target simultaneously, producing very high scores with no surprises.

**What was surprising:** Three results were unexpected and revealed genuine weaknesses.

First, Gym Hero (pop/intense) appeared at #3 for the high_energy_pop profile despite having the wrong mood — it is intense, not happy. This happens because the catalog only has two pop/happy songs, so once those two are used at #1 and #2, the system has no better pop option and reaches for the closest remaining pop song regardless of mood.

Second, Iron Cathedral (metal/angry) ranked above Heartbreak Porch (country/sad) for the sad_banger profile — meaning an angry metal song was recommended to someone who asked for sad music. The energy mismatch on Heartbreak Porch (asked for 0.92, song is 0.41) cost more points than the mood mismatch penalty on Iron Cathedral, exposing that the scorer cannot detect contradictory user preferences.

Third, the ghost_genre profile (genre=bluegrass, which does not exist in the catalog) returned top-3 scores of 8.94, 8.62, and 8.59 — all within 0.35 points of each other, making the ranking feel nearly arbitrary. Removing the genre signal collapsed the separation between results, showing how much the system depends on categorical matches to create meaningful distance between songs.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
