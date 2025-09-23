import os
import time
import pickle
from functools import lru_cache
from typing import List, Optional, Tuple

import pandas as pd
import requests

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSTER_CACHE_DIR = os.path.join(BASE_DIR, "poster_cache")
FAIL_MARKER_EXT = ".fail"

# Ensure poster cache directory exists
os.makedirs(POSTER_CACHE_DIR, exist_ok=True)

# API configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # Read from environment for Hugging Face Spaces
TMDB_MOVIE_URL = "https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500/"


def _poster_path(movie_id: int) -> str:
    return os.path.join(POSTER_CACHE_DIR, f"{movie_id}.jpg")


def _fail_marker_path(movie_id: int) -> str:
    return os.path.join(POSTER_CACHE_DIR, f"{movie_id}{FAIL_MARKER_EXT}")


def _has_fail_marker(movie_id: int) -> bool:
    return os.path.exists(_fail_marker_path(movie_id))


def _write_fail_marker(movie_id: int) -> None:
    try:
        open(_fail_marker_path(movie_id), "a").close()
    except OSError:
        # Silently ignore file system errors to avoid UI noise
        pass


def _is_valid_movie_id(movie_id) -> bool:
    try:
        mid = int(movie_id)
        return mid > 0
    except (TypeError, ValueError):
        return False


def fetch_poster(movie_id: int, timeout: float = 10.0, retries: int = 3) -> Optional[str]:
    """
    Try to fetch and cache the poster image for a given TMDB movie ID.
    Returns absolute file path to the cached image if available, else None.

    Behavior notes:
    - If TMDB_API_KEY is missing, return None without recording a failure (environmental condition).
    - If movie_id is invalid, create a fail marker and return None.
    - If TMDB returns no poster_path or a 404, create a fail marker and return None.
    - Transient network errors do not create a fail marker; they simply return None.
    """
    # If API key is not configured (e.g., on Spaces without secret), skip fetching silently
    if not TMDB_API_KEY:
        return None

    if not _is_valid_movie_id(movie_id):
        _write_fail_marker(movie_id)
        return None

    cache_path = _poster_path(movie_id)
    if os.path.exists(cache_path):
        return cache_path

    if _has_fail_marker(movie_id):
        return None

    url = TMDB_MOVIE_URL.format(movie_id=movie_id, api_key=TMDB_API_KEY)

    # Attempt to fetch metadata a few times in case of transient errors
    for attempt in range(retries):
        try:
            resp = requests.get(url, timeout=timeout)
            # If 404, mark as fail and stop
            if resp.status_code == 404:
                _write_fail_marker(movie_id)
                return None
            resp.raise_for_status()
            data = resp.json() or {}
            poster_path = data.get("poster_path")
            if not poster_path:
                # No poster path -> permanent fail for this ID
                _write_fail_marker(movie_id)
                return None

            full_url = TMDB_IMAGE_BASE + poster_path.lstrip("/")
            img_resp = requests.get(full_url, timeout=timeout)
            if img_resp.status_code == 404:
                _write_fail_marker(movie_id)
                return None
            img_resp.raise_for_status()

            # Save the image to cache
            with open(cache_path, "wb") as f:
                f.write(img_resp.content)
            return cache_path
        except requests.exceptions.RequestException:
            # On the last attempt, give up (but do not create a fail marker for transient errors)
            if attempt < retries - 1:
                time.sleep(1)
            else:
                return None

    return None


@lru_cache(maxsize=1)
def load_movies() -> pd.DataFrame:
    path = os.path.join(BASE_DIR, "movies_dict.pkl")
    with open(path, "rb") as f:
        movies_dict = pickle.load(f)
    df = pd.DataFrame(movies_dict)
    # Normalize column names we rely on
    if "movie_id" not in df.columns:
        # Try common alternatives (best-effort)
        for alt in ("id", "movieId", "tmdb_id"):
            if alt in df.columns:
                df = df.rename(columns={alt: "movie_id"})
                break
    return df


@lru_cache(maxsize=1)
def load_similarity():
    path = os.path.join(BASE_DIR, "similarity.pkl")
    with open(path, "rb") as f:
        return pickle.load(f)


def recommend(movie_title: str, top_n: int = 5) -> List[Tuple[str, Optional[str]]]:
    """
    Given a movie title, return up to top_n recommendations as (title, poster_path_or_none).
    - If the title does not exist, returns an empty list.
    - Poster fetching is failure-cached via marker files.
    - If no TMDB_API_KEY is set, poster paths will be None but titles will still be returned.
    """
    movies = load_movies()
    similarity = load_similarity()

    if "title" not in movies.columns:
        return []

    # Ensure the movie exists
    matches = movies.index[movies["title"] == movie_title].tolist()
    if not matches:
        return []

    movie_index = matches[0]

    try:
        distances = similarity[movie_index]
    except Exception:
        # Similarity lookup failed
        return []

    scored = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)
    # Skip the first one (itself)
    candidates = scored[1 : top_n + 1]

    recs: List[Tuple[str, Optional[str]]] = []
    for idx, _score in candidates:
        row = movies.iloc[idx]
        title = row.get("title")
        movie_id = row.get("movie_id")
        poster = fetch_poster(movie_id) if movie_id is not None else None
        recs.append((title, poster))

    return recs
