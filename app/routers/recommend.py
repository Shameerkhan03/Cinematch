from fastapi import APIRouter, Depends, HTTPException, Query
import pandas as pd
from .. import oauth2, models
from sqlalchemy.orm import Session
from ..database import get_db
from ..recommender.cbf_engine import recommend_for_user
from ..recommender.cf_engine import recommend_cf
from ..recommender.pickle_loader import load_cbf_models, load_cf_models
from ..tmdb_api import search_movie_by_title

router = APIRouter(prefix="/recommend", tags=["Recommendation"])

cbf_data, cbf_similarity = load_cbf_models()
cf_movies, cf_likes = load_cf_models()


@router.get("/cbf")
def get_cbf(
    # movie: str,
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):

    liked = (
        db.query(models.LikedMovie)
        .filter(models.LikedMovie.user_id == current_user.id)
        .all()
    )

    liked_titles = [like.movie_title for like in liked]

    if not liked_titles:
        raise HTTPException(
            status_code=400, detail="User has not liked any movies yet."
        )

    return recommend_for_user(liked_titles, cbf_data, cbf_similarity, top_n=64)


@router.get("/cf")
def get_cf(
    current_user: int = Depends(oauth2.get_current_user),
    db: Session = Depends(get_db),
):
    liked_entries = db.query(models.LikedMovie).all()
    likes_data = [{"userId": l.user_id, "movieId": l.movie_id} for l in liked_entries]

    if not likes_data:
        raise HTTPException(status_code=400, detail="No user likes found.")

    likes_df = pd.DataFrame(likes_data)

    print("Current user:", current_user.id)
    print("Likes DF:", likes_df.head())
    print("CF Movies:", cf_movies.head())

    try:
        return recommend_cf(current_user.id, likes_df, cf_movies, top_n=64)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CF error: {str(e)}")


@router.get("/search", tags=["Search"])
def search_movies(
    query: str = Query(..., min_length=1, max_length=100),
    current_user: int = Depends(oauth2.get_current_user),
):
    results = cbf_data[cbf_data["title"].str.contains(query, case=False, na=False)]

    if results.empty:
        raise HTTPException(status_code=404, detail="No matching movies found.")

    output = []
    for _, row in results.iterrows():
        tmdb_info = search_movie_by_title(row["title"])
        poster_path = (
            tmdb_info["results"][0].get("poster_path")
            if tmdb_info.get("results")
            else None
        )

        output.append(
            {
                "movie_id": int(row["id"]),
                "title": row["title"],
                "poster_path": poster_path,
            }
        )

    return output


@router.get("/random")
def get_random_movies(
    n: int = 64, current_user: int = Depends(oauth2.get_current_user)
):
    sample = cbf_data.sample(n=n)
    return (
        sample[["id", "title"]]
        .rename(columns={"id": "movie_id"})
        .to_dict(orient="records")
    )
