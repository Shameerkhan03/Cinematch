import requests
import os

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"
IMG_BASE_URL = "https://image.tmdb.org/t/p/w500"


def get_movie_details(movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US"
    return requests.get(url).json()


def get_movie_credits(movie_id: int):
    url = f"{BASE_URL}/movie/{movie_id}/credits?api_key={TMDB_API_KEY}&language=en-US"
    return requests.get(url).json()


def get_person_details(person_id: int):
    url = f"{BASE_URL}/person/{person_id}?api_key={TMDB_API_KEY}&language=en-US"
    return requests.get(url).json()


def search_movie_by_title(query: str):
    url = f"{BASE_URL}/search/movie"
    params = {"api_key": TMDB_API_KEY, "query": query}
    response = requests.get(url, params=params)
    return response.json()
