import pickle
import os

# This gets you: D:/My Work/cinematch/app/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "models")  # app/models/


def load_cbf_models():
    cbf_data = pickle.load(open(os.path.join(MODEL_PATH, "cbf_movie_data.pkl"), "rb"))
    cbf_similarity = pickle.load(
        open(os.path.join(MODEL_PATH, "cbf_similarity.pkl"), "rb")
    )
    return cbf_data, cbf_similarity


def load_cf_models():
    cf_movies = pickle.load(open(os.path.join(MODEL_PATH, "cf_movies.pkl"), "rb"))
    return cf_movies, None
