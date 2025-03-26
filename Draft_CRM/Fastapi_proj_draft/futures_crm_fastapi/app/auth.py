from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime

router = APIRouter()
fake_users_db = {}

@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    return request.app.state.templates.get_template("registration/login.html").render({"request": request})

@router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    user = fake_users_db.get(username)
    if user and user["password"] == password:
        response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        response.set_cookie("user", username)
        return response
    return request.app.state.templates.get_template("registration/login.html").render({"request": request, "error": "Неверный логин или пароль"})

@router.get("/signup", response_class=HTMLResponse)
async def signup_get(request: Request):
    return request.app.state.templates.get_template("registration/signup.html").render({"request": request})

@router.post("/signup", response_class=HTMLResponse)
async def signup_post(request: Request, username: str = Form(...), password: str = Form(...)):
    if username in fake_users_db:
        return request.app.state.templates.get_template("registration/signup.html").render({"request": request, "error": "Пользователь уже существует"})
    fake_users_db[username] = {"username": username, "password": password, "created": datetime.utcnow()}
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.set_cookie("user", username)
    return response
