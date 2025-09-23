import streamlit as st
import os

from recommender import load_movies, recommend

# Streamlit page config
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# Global lightweight styles (modern cards, rounded images, tighter layout)
st.markdown(
    """
    <style>
    /* Reduce top padding and widen content a bit */
    .block-container {padding-top: 1.0rem; padding-bottom: 2rem;}

    /* Improve column spacing */
    [data-testid="column"] {padding: 0.25rem 0.5rem;}

    /* Card-like feel around each recommendation */
    .movie-card { 
        background: rgba(255,255,255,0.6);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 14px; 
        padding: 12px; 
        transition: box-shadow .16s ease, transform .16s ease; 
        backdrop-filter: saturate(140%) blur(2px);
    }
    .movie-card:hover { box-shadow: 0 6px 22px rgba(0,0,0,0.12); transform: translateY(-2px); }

    /* Round images + subtle shadow */
    .stImage img { 
        border-radius: 12px !important; 
        box-shadow: 0 4px 16px rgba(0,0,0,0.12); 
    }

    /* Title chip */
    .movie-title { 
        margin-top: .5rem; 
        text-align: center; 
        font-weight: 600; 
        font-size: 0.95rem; 
        color: #111; 
    }

    /* Placeholder when poster is missing */
    .poster-placeholder { 
        display: grid; 
        place-items: center; 
        width: 100%; 
        aspect-ratio: 2/3; 
        border-radius: 12px; 
        background: linear-gradient(135deg, #d1d5db, #9ca3af);
        color: white; 
        font-size: 2.25rem; 
        font-weight: 700;
        letter-spacing: .04em;
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }

    /* Sidebar tweaks */
    section[data-testid="stSidebar"] .block-container {padding-top: 1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Ensure poster cache directory exists
os.makedirs('poster_cache', exist_ok=True)

# --- HEADER ---
st.markdown(
    """
    <h1 style='text-align: center; color: #E50914; font-family: "Trebuchet MS", sans-serif;'>
        🎬 Movie Recommender System
    </h1>
    <p style='text-align: center; color: #aaa;'>
        Discover movies you’ll love — powered by TMDb & ML
    </p>
    """,
    unsafe_allow_html=True
)

# Load data (cached inside recommender)
movies = load_movies()

# --- SIDEBAR SEARCH ---
st.sidebar.header("🔍 Find Similar Movies")
all_titles = movies['title'].values.tolist() if 'title' in movies.columns else []

if not all_titles:
    st.sidebar.warning("No movies available to select. Check your data files.")
else:
    # Optional text filter to quickly narrow down titles (does not change core logic)
    query_text = st.sidebar.text_input("Type to search a movie")
    if query_text:
        filtered = [t for t in all_titles if query_text.lower() in t.lower()]
        # Fallback to all if filter removes everything
        options = filtered if filtered else all_titles
    else:
        options = all_titles

    selected_movie = st.sidebar.selectbox("Select a movie", options)
    if st.sidebar.button("Recommend"):
        st.session_state["search"] = selected_movie

# --- RESULTS ---
if "search" in st.session_state:
    query = st.session_state["search"]

    # Run your actual recommender (no functionality change)
    with st.spinner('Finding great movies for you...'):
        recs = recommend(query)

    st.markdown(
        f"<h2 style='color:white;'>🎥 Movies similar to <span style='color:#E50914;'>{query}</span></h2>",
        unsafe_allow_html=True
    )

    if not recs:
        st.info("No recommendations available for this title.")
    else:
        cols = st.columns(5)
        for i, (title, poster_path) in enumerate(recs):
            with cols[i % 5]:
                # Card wrapper
                st.markdown('<div class="movie-card">', unsafe_allow_html=True)
                if poster_path and os.path.exists(poster_path):
                    st.image(poster_path, use_container_width=True)
                else:
                    initial = (title[:1].upper() if title else '?')
                    st.markdown(f'<div class="poster-placeholder">{initial}</div>', unsafe_allow_html=True)

                st.markdown(f"<div class='movie-title'><strong>{title}</strong></div>", unsafe_allow_html=True)

                # Use tags as a lightweight 'overview' if available (keeps logic unchanged)
                overview_text = None
                try:
                    if 'title' in movies.columns and 'tags' in movies.columns:
                        row = movies.loc[movies['title'] == title]
                        if not row.empty:
                            overview_text = str(row.iloc[0]['tags']).replace(' ', ', ')
                except Exception:
                    overview_text = None

                with st.expander("📖 Overview"):
                    st.write(overview_text or "Overview not available.")

                st.markdown('</div>', unsafe_allow_html=True)
