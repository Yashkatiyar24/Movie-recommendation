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

# 🎬 Movie Recommender System

Recommend similar movies with a clean Streamlit UI and poster images from TMDb. Precomputed similarity keeps responses fast, while a smart poster cache avoids repeated failed fetches.

- Live demo: https://huggingface.co/spaces/yashkatiyar/movie-recommender

## ✨ Features
- Fast, content-based recommendations using a precomputed similarity matrix
- Polished Streamlit UI with responsive layout and card-style results
- Poster fetching from TMDb with local caching
  - Stores downloaded posters under `poster_cache/`
  - Records permanent failures as `.fail` marker files to skip bad IDs
- Works even without a TMDb key (shows an initial-letter placeholder instead of posters)
- Simple, maintainable split between UI (`app.py`) and logic (`recommender.py`)

## 🧰 Tech stack
- Streamlit, pandas, numpy, requests
- Data artifacts: `movies_dict.pkl` (movie meta) and `similarity.pkl` (precomputed similarity matrix)
- Hugging Face Spaces + Git LFS for large files

## 🚀 Quickstart (local)

1) Install dependencies
```bash
python -m pip install -r requirements.txt
```

2) Optional: export TMDb API key (posters)
```bash
# macOS/Linux (zsh)
export TMDB_API_KEY="<your_tmdb_key>"
```

3) Run the app
```bash
streamlit run app.py
```

Open the printed local URL in your browser. Type a movie title and click Recommend.

## 🔧 Configuration
- TMDB_API_KEY (optional): If set, posters are fetched and cached. If not set, titles still appear with placeholders.
- Poster cache: created at runtime under `poster_cache/`. Delete its contents to clear the cache and failure markers.

## 🧠 How it works
- `movies_dict.pkl` is loaded into a pandas DataFrame (with a `title` column and a `movie_id` column for TMDb).
- `similarity.pkl` is a precomputed similarity matrix aligned with the movies DataFrame.
- Given a query title, we look up its index, sort by similarity, and return the top N titles.
- For each recommended movie, we optionally fetch and cache its poster using TMDb.
  - Missing or invalid poster responses create a `.fail` marker to avoid re-trying.

## 📁 Project structure
```
.
├─ app.py                 # Streamlit UI
├─ recommender.py         # Data loading, recommendation + poster cache
├─ movies_dict.pkl        # Movie metadata (pickled dict -> DataFrame)
├─ similarity.pkl         # Precomputed similarity matrix (NumPy array)
├─ poster_cache/          # Cached poster images + .fail markers
├─ requirements.txt       # Python dependencies
├─ .gitattributes         # Git LFS rules (includes *.pkl)
├─ .gitignore             # Local ignores (venv, IDE, cache)
└─ README.md              # This file
```

## ☁️ Deploy to Hugging Face Spaces

1) Create a Space (SDK: Streamlit) at https://huggingface.co/spaces/new

2) Push this repo (PKL files tracked by Git LFS)
```bash
git lfs install
# first time only
huggingface-cli login  # or: hf auth login

git remote add huggingface https://huggingface.co/spaces/<username>/<space-name>
git push -u huggingface main
```

3) Add a secret for posters
- Space Settings → Secrets → Add new secret:
  - Name: TMDB_API_KEY
  - Value: your TMDb API key

The Space builds from `requirements.txt` and launches `app.py` automatically.

## ❓ Troubleshooting
- Build succeeds but posters don’t appear
  - Ensure TMDB_API_KEY is set in the Space Secrets. Without it, placeholders show by design.
- No titles in the dropdown
  - Confirm `movies_dict.pkl` loads and includes a `title` column aligned with `similarity.pkl`.
- LFS push errors
  - Make sure Git LFS is installed and `.gitattributes` includes `*.pkl`.
- ModuleNotFoundError
  - Rebuild the Space or pin versions in `requirements.txt`. Locally, run `pip install -r requirements.txt` again.

## 📝 Notes
- For production, keep your TMDb key in environment variables or Space Secrets—never hard-code it.
- To reset poster cache, delete files under `poster_cache/`.
- Python 3.10+ is recommended; Spaces config uses 3.10.

Enjoy exploring movies! 🍿
