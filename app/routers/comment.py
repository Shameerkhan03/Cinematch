from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, database, oauth2
from transformers import pipeline

sentiment_pipeline = pipeline("sentiment-analysis")


router = APIRouter(prefix="/comments", tags=["Comments"])


def analyze_sentiment(text: str) -> str:
    try:
        result = sentiment_pipeline(text)[0]
        label = result["label"].lower()  # returns 'positive' or 'negative'
        return label if label in ["positive", "negative"] else "neutral"
    except Exception:
        return "neutral"


@router.post(
    "/", response_model=schemas.CommentOut, status_code=status.HTTP_201_CREATED
)
def post_comment(
    comment: schemas.CommentCreate,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    sentiment = analyze_sentiment(comment.text_comment)

    new_comment = models.Comment(
        user_id=current_user.id,
        movie_id=comment.movie_id,
        movie_title=comment.movie_title,
        text_comment=comment.text_comment,
        sentiment=sentiment,
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


from sqlalchemy.orm import joinedload


@router.get("/{movie_id}", response_model=list[schemas.CommentOut])
def get_comments_for_movie(
    movie_id: int,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    return (
        db.query(models.Comment)
        .filter(models.Comment.movie_id == movie_id)
        .order_by(models.Comment.created_at.desc())
        .all()
    )


@router.put("/{comment_id}", response_model=schemas.CommentOut)
def update_comment(
    comment_id: int,
    updated_comment: schemas.CommentCreate,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    comment = (
        db.query(models.Comment)
        .filter(models.Comment.id == comment_id)
        .filter(models.Comment.user_id == current_user.id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404, detail="Comment not found or not authorized."
        )

    comment.text_comment = updated_comment.text_comment
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=200)
def delete_comment(
    comment_id: int,
    db: Session = Depends(database.get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    comment = (
        db.query(models.Comment)
        .filter(models.Comment.id == comment_id)
        .filter(models.Comment.user_id == current_user.id)
        .first()
    )

    if not comment:
        raise HTTPException(
            status_code=404, detail="Comment not found or not authorized."
        )

    db.delete(comment)
    db.commit()
    return {"msg": f"Comment {comment_id} deleted successfully."}
