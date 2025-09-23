---
title: Movie Recommender System
emoji: 🎬
colorFrom: red
colorTo: gray
sdk: streamlit
app_file: app.py
python_version: "3.10"
pinned: false
license: mit
short_description: Content-based movie recommendations with cached TMDb posters
---

# Movie Recommender System

This Streamlit app recommends similar movies and shows posters from TMDb. It separates UI from data logic and caches both successful posters and known failures for robust, fast performance.

## What’s inside
- UI: `app.py`
- Data & fetching logic: `recommender.py`
- Data files: `movies_dict.pkl`, `similarity.pkl`
- Poster cache: `poster_cache/` (images + `.fail` marker files)

## Key improvements
1. Poster fetching reliability
   - Posters are cached to `poster_cache/<movie_id>.jpg`.
   - Known failures are cached with `poster_cache/<movie_id>.fail` to skip re-trying bad IDs or missing posters.
2. Error handling in UI
   - No warnings are shown. If a poster is missing, the movie title is displayed only.
3. Caching logic
   - Failure marker files (`.fail`) prevent repeated failed fetch attempts for the same ID.
4. API data validation
   - Invalid or missing `movie_id` as well as missing `poster_path` are handled gracefully and marked as failures.
5. Code optimization
   - Data fetching and recommendation logic live in `recommender.py`; Streamlit UI is in `app.py`.

## Setup (local)

Install dependencies (Python 3.10 recommended):

```bash
python -m pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## Deploy to Hugging Face Spaces

1. Create a new Space on Hugging Face with SDK set to “Streamlit”.
2. Push this repository to the Space (web upload or `git push`). Large `.pkl` files are tracked with Git LFS via `.gitattributes`.
3. In the Space settings, add a Secret named `TMDB_API_KEY` with your TMDb API key (optional but recommended for posters).
4. The app entrypoint is `app.py`.

## Notes
- To clear the poster cache and failure markers, delete files under `poster_cache/`.
- For production, set `TMDB_API_KEY` as a secret in your Space instead of embedding it in code.
- If you see no recommendations, ensure the selected movie title exists in `movies_dict.pkl` and `similarity.pkl` is aligned.
