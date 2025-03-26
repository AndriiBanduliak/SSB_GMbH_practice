from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.database import engine, Base
from app import models, auth, routes

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")
app.state.templates = templates

# Регистрация фильтра escapejs для Jinja2 (аналог Django)


def escapejs(value):
    return value.replace("'", "\\'").replace('"', '\\"').replace("\n", "\\n")


templates.env.filters["escapejs"] = escapejs

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(routes.router, prefix="", tags=["dashboard"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
