from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import database, models, schemas, oauth2

router = APIRouter(prefix="/react", tags=["Reactions"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def like_movie(
    like: schemas.LikeCreate,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):

    existing = (
        db.query(models.LikedMovie)
        .filter(models.LikedMovie.user_id == current_user.id)
        .filter(models.LikedMovie.movie_id == like.movie_id)
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Movie already liked.")

    new_like = models.LikedMovie(
        user_id=current_user.id, movie_id=like.movie_id, movie_title=like.movie_title
    )
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return {"msg": f"'{like.movie_title}' liked successfully"}


@router.delete("/", status_code=status.HTTP_200_OK)
def unlike_movie(
    payload: schemas.MovieUnlike,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    movie_id = payload.movie_id

    like_entry = (
        db.query(models.LikedMovie)
        .filter(models.LikedMovie.user_id == current_user.id)
        .filter(models.LikedMovie.movie_id == movie_id)
        .first()
    )

    if not like_entry:
        raise HTTPException(status_code=404, detail="Movie not found in liked list.")

    db.delete(like_entry)
    db.commit()

    return {"msg": f"Movie with ID {movie_id} unliked successfully."}


@router.get("/", response_model=list[schemas.LikedMovieOut])
def get_liked_movies(
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    liked = (
        db.query(models.LikedMovie)
        .filter(models.LikedMovie.user_id == current_user.id)
        .all()
    )
    return liked
