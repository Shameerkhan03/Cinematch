from fastapi import APIRouter, HTTPException
from .. import tmdb_api

router = APIRouter(prefix="/tmdb", tags=["TMDb"])


@router.get("/movie/{movie_id}")
def fetch_movie_details(movie_id: int):
    data = tmdb_api.get_movie_details(movie_id)
    if "status_code" in data and data["status_code"] != 1:
        raise HTTPException(status_code=404, detail=data.get("status_message"))
    return data


@router.get("/movie/{movie_id}/credits")
def fetch_movie_credits(movie_id: int):
    data = tmdb_api.get_movie_credits(movie_id)
    if "status_code" in data and data["status_code"] != 1:
        raise HTTPException(status_code=404, detail=data.get("status_message"))
    return data


@router.get("/person/{person_id}")
def fetch_person_details(person_id: int):
    data = tmdb_api.get_person_details(person_id)
    if "status_code" in data and data["status_code"] != 1:
        raise HTTPException(status_code=404, detail=data.get("status_message"))
    return data


@router.get("/search")
def search_movie_by_title(query: str):
    data = tmdb_api.search_movie_by_title(query)
    if not data["results"]:
        raise HTTPException(status_code=404, detail="Movie not found")
    return data["results"]
