from fastapi import FastAPI
from .database import engine
from . import models
from .routers import react, user, auth, recommend, comment, tmdb
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import os

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


app.include_router(user.router)
app.include_router(auth.router)
app.include_router(recommend.router)
app.include_router(react.router)
app.include_router(comment.router)
app.include_router(tmdb.router)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
frontend_path = os.path.join(BASE_DIR, "../frontend")

app.mount("/static", StaticFiles(directory=frontend_path), name="static")
templates = Jinja2Templates(directory=frontend_path)


@app.get("/", response_class=HTMLResponse)
def landing_page(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/auth", response_class=HTMLResponse)
def get_auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def get_dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/movie", response_class=HTMLResponse)
def movie_page(request: Request):
    return templates.TemplateResponse("movie.html", {"request": request})


@app.get("/favourites", response_class=HTMLResponse)
def favourites_page():
    return FileResponse("frontend/favourites.html")


@app.get("/settings", response_class=HTMLResponse)
def favourites_page():
    return FileResponse("frontend/settings.html")


@app.get("/onboarding", response_class=HTMLResponse)
def onboarding_page(request: Request):
    return templates.TemplateResponse("onboarding.html", {"request": request})
