from fastapi import FastAPI, HTTPException, Depends
from fastapi.params import Body
from . import models
from .database import engine
from .routers import post, user, auth, vote

app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

models.Base.metadata.create_all(bind=engine)

