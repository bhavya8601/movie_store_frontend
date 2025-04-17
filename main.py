import streamlit as st
import requests
import logging
import os

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/frontend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("frontend")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
USER_ID = 123

def main():
    st.set_page_config(page_title="Movie Store", layout="centered")
    st.title("🎬 Movie Store")

    page = st.sidebar.selectbox("Choose a page", [
        "Home",
        "Movie Detail",
        "Search",
        "My Purchases",
        "Feedback",
        "Add Movie (Admin)"
    ])

    if page == "Home":
        st.header("Available Movies")
        try:
            logger.info("Fetching all movies from backend...")
            res = requests.get(f"{BACKEND_URL}/movies")
            res.raise_for_status()
            movies = res.json()
            logger.info(f"Movies fetched successfully: {movies}")
            for movie in movies:
                st.subheader(movie["title"])
                st.write(f"Price: ${movie['price']}")
                if st.button(f"Buy {movie['title']}", key=f"buy_{movie['id']}"):
                    logger.info(f"Sending purchase request for movie ID {movie['id']}, user {USER_ID}")
                    response = requests.post(f"{BACKEND_URL}/purchase", json={
                        "movie_id": movie["id"],
                        "user_id": USER_ID
                    })
                    logger.info(f"Purchase response: {response.json()}")
                    st.success(response.json()["message"])
        except Exception as e:
            st.error("Could not fetch movies")
            logger.error(e)

    elif page == "Movie Detail":
        movie_id = st.number_input("Enter Movie ID", min_value=1)
        if st.button("Get Movie"):
            try:
                logger.info(f"Fetching movie details for movie ID: {movie_id}")
                response = requests.get(f"{BACKEND_URL}/movies/{movie_id}")
                response.raise_for_status()
                movie = response.json()
                logger.info(f"Movie details received: {movie}")
                st.write(f"🎬 Title: {movie['title']}")
                st.write(f"💲 Price: ${movie['price']}")
            except Exception as e:
                st.error("Movie not found")
                logger.error(e)

    elif page == "Search":
        keyword = st.text_input("Search movies by title:")
        if keyword:
            try:
                logger.info(f"Searching movies with keyword: {keyword}")
                response = requests.get(f"{BACKEND_URL}/movies/search/{keyword}")
                response.raise_for_status()
                results = response.json()
                logger.info(f"Search results: {results}")
                if results:
                    for movie in results:
                        st.subheader(movie["title"])
                        st.write(f"Price: ${movie['price']}")
                else:
                    st.warning("No movies matched your search.")
            except Exception as e:
                st.error("Error searching movies")
                logger.error(e)

    elif page == "My Purchases":
        st.header("🧾 My Purchases")
        try:
            logger.info(f"Fetching purchases for user ID {USER_ID}")
            res = requests.get(f"{BACKEND_URL}/purchases/{USER_ID}")
            res.raise_for_status()
            purchased_titles = res.json()["purchases"]
            logger.info(f"Purchases retrieved: {purchased_titles}")
            if purchased_titles:
                for title in purchased_titles:
                    st.markdown(f"- **{title}**")
            else:
                st.info("No purchases found.")
        except Exception as e:
            st.error("Could not fetch purchases")
            logger.error(e)

    elif page == "Feedback":
        movie_id = st.number_input("Movie ID for Feedback", min_value=1)
        comment = st.text_area("Your Comment")
        if st.button("Submit Feedback"):
            try:
                logger.info(f"Submitting feedback for movie ID {movie_id}: {comment}")
                response = requests.post(f"{BACKEND_URL}/feedback", json={
                    "movie_id": movie_id,
                    "comment": comment
                })
                logger.info(f"Feedback response: {response.json()}")
                st.success(response.json()["message"])
            except Exception as e:
                st.error("Error submitting feedback")
                logger.error(e)

    elif page == "Add Movie (Admin)":
        st.header("🎬 Add New Movie")
        title = st.text_input("Title")
        price = st.number_input("Price", min_value=0.0, format="%.2f")
        if st.button("Add Movie"):
            try:
                logger.info(f"Adding movie - Title: {title}, Price: {price}")
                response = requests.post(f"{BACKEND_URL}/movies", json={
                    "title": title,
                    "price": price
                })
                logger.info(f"Add movie response: {response.json()}")
                st.success(response.json()["message"])
            except Exception as e:
                st.error("Error adding movie")
                logger.error(e)

if __name__ == "__main__":
    main()
