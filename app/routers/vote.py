from fastapi import APIRouter, Depends, status, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from ..database import get_db
from .. import schemas, database, models, oauth2


router = APIRouter(
    prefix="/vote",
    tags=["Vote"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Vote)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    found_vote = query.first()

    if (vote.dir == 1):
        if found_vote:
            if found_vote.dir == 1:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already upvoted this post")
            else:
                found_vote.dir = 1
                db.commit()
                db.refresh(found_vote)
                return found_vote
        else:
            new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id, dir=1)
            db.add(new_vote)
            db.commit()
            db.refresh(new_vote)
            return new_vote

    else:
        if found_vote:
            if found_vote.dir == 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already downvoted this post")
            else:
                found_vote.dir = 0
                db.commit()
                db.refresh(found_vote)
                return found_vote
        else:
            new_vote = models.Vote(user_id=current_user.id, post_id=vote.post_id, dir=0)
            db.add(new_vote)
            db.commit()
            db.refresh(new_vote)
            return new_vote