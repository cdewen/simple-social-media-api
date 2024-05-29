from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db
from typing import List, Optional

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/", status_code=status.HTTP_200_OK, response_model=List[schemas.PostOut])
def get__all_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), 
                   Limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    """
    Get all posts
    """
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.title.contains(search)).offset(skip).limit(Limit).all()

    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")

    return posts

@router.get("/{post_id}", status_code=status.HTTP_200_OK, response_model=schemas.PostOut)
def get_specific_post(post_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Get a single post
    """
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(
            models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    return post

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Create a new post
    """
    new_post = models.Post(user_id = current_user.id, **post.model_dump())

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def del_post(post_id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Delete a post
    """
    post = db.query(models.Post).filter(models.Post.id==post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to delete this post")
    
    db.delete(post)
    db.commit()

    return {"msg": "Post deleted successfully"}

@router.put("/{post_id}", status_code=status.HTTP_200_OK, response_model=schemas.Post)
def update_post(post_id: int, post: schemas.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    """
    Update a post
    """
    post_query = db.query(models.Post).filter(models.Post.id==post_id)

    if not post_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post_query.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authorized to update this post")

    post_query.update(post.model_dump())
    db.commit()

    return post_query.first()