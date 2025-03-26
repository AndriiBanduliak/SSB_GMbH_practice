from fastapi import FastAPI, Depends, HTTPException, status, Form, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
import os
import requests
import logging
from dotenv import load_dotenv
from datetime import datetime, date

from backend.database import SessionLocal, engine
import backend.models as models
import backend.schemas as schemas
import backend.crud as crud
import backend.auth as auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Trading Journal App")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# --- Словарь переводов (переводы для новых полей добавлены) ---
translations = {
    "en": {
        "login_title": "Login",
        "username": "Username",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "show_password": "Show Password",
        "register_title": "Register",
        "register_button": "Register",
        "register_success_msg": "Registration successful! You will be redirected to the login page.",
        "age_error": "You must be at least 16 years old.",
        "password_mismatch": "Passwords do not match.",
        "date_of_birth": "Date of Birth",
        "dashboard": "Dashboard",
        "capital_overview": "Capital Overview",
        "total_trades": "Total Trades",
        "current_balance": "Current Account Balance",
        "total_losses": "Total Trade Losses",
        "total_wins": "Total Trades Win",
        "diagram_capital": "Diagram: Capital increase/decrease",
        "trade_history": "Trade History",
        "auto_trades": "Automatic Trades from API Profile",
        "settings": "Settings",
        "personal_data": "Personal Data",
        "save_settings": "Save Settings",
        "logout": "Log out",
        "api_settings": "API Settings",
        "select_exchange": "Select Exchange",
        "api_key": "API Key",
        "secret_key": "Secret Key",
        "passphrase": "Passphrase",
        "save_api_data": "Save API Data"
    },
    "ru": {
        "login_title": "Вход",
        "username": "Имя пользователя",
        "password": "Пароль",
        "confirm_password": "Повторите пароль",
        "show_password": "Показать пароль",
        "register_title": "Регистрация",
        "register_button": "Зарегистрироваться",
        "register_success_msg": "Регистрация успешна! Вы будете перенаправлены на страницу входа.",
        "age_error": "Вам должно быть не менее 16 лет.",
        "password_mismatch": "Пароли не совпадают.",
        "date_of_birth": "Дата рождения",
        "dashboard": "Личный кабинет",
        "capital_overview": "Обзор капитала",
        "total_trades": "Всего сделок",
        "current_balance": "Текущий баланс",
        "total_losses": "Общие убытки",
        "total_wins": "Всего выигрышей",
        "diagram_capital": "Диаграмма капитала",
        "trade_history": "История сделок",
        "auto_trades": "Автоматическая выгрузка сделок из API профиля",
        "settings": "Настройки",
        "personal_data": "Личные данные",
        "save_settings": "Сохранить",
        "logout": "Выход",
        "api_settings": "Настройка API данных",
        "select_exchange": "Выберите биржу",
        "api_key": "API ключ",
        "secret_key": "Секретный ключ",
        "passphrase": "Passphrase",
        "save_api_data": "Сохранить API данные"
    },
    "de": {
        "login_title": "Anmeldung",
        "username": "Benutzername",
        "password": "Passwort",
        "confirm_password": "Passwort bestätigen",
        "show_password": "Passwort anzeigen",
        "register_title": "Registrierung",
        "register_button": "Registrieren",
        "register_success_msg": "Registrierung erfolgreich! Sie werden zur Anmeldeseite weitergeleitet.",
        "age_error": "Sie müssen mindestens 16 Jahre alt sein.",
        "password_mismatch": "Die Passwörter stimmen nicht überein.",
        "date_of_birth": "Geburtsdatum",
        "dashboard": "Dashboard",
        "capital_overview": "Kapitalübersicht",
        "total_trades": "Gesamtanzahl der Trades",
        "current_balance": "Aktueller Kontostand",
        "total_losses": "Gesamte Verluste",
        "total_wins": "Gesamte Gewinne",
        "diagram_capital": "Diagramm: Kapitalveränderung",
        "trade_history": "Handelshistorie",
        "auto_trades": "Automatische Trades (API)",
        "settings": "Einstellungen",
        "personal_data": "Persönliche Daten",
        "save_settings": "Speichern",
        "logout": "Abmelden",
        "api_settings": "API-Einstellungen",
        "select_exchange": "Börse auswählen",
        "api_key": "API-Schlüssel",
        "secret_key": "Secret-Schlüssel",
        "passphrase": "Passphrase",
        "save_api_data": "API-Daten speichern"
    },
    "es": {
        "login_title": "Iniciar sesión",
        "username": "Nombre de usuario",
        "password": "Contraseña",
        "confirm_password": "Confirmar contraseña",
        "show_password": "Mostrar contraseña",
        "register_title": "Registro",
        "register_button": "Registrar",
        "register_success_msg": "¡Registro exitoso! Serás redirigido a la página de inicio de sesión.",
        "age_error": "Debes tener al menos 16 años.",
        "password_mismatch": "Las contraseñas no coinciden.",
        "date_of_birth": "Fecha de nacimiento",
        "dashboard": "Panel de Control",
        "capital_overview": "Resumen de Capital",
        "total_trades": "Total de Operaciones",
        "current_balance": "Saldo Actual",
        "total_losses": "Pérdidas Totales",
        "total_wins": "Ganancias Totales",
        "diagram_capital": "Gráfico: Aumento/Disminución de Capital",
        "trade_history": "Historial de Operaciones",
        "auto_trades": "Operaciones automáticas (API)",
        "settings": "Configuración",
        "personal_data": "Datos Personales",
        "save_settings": "Guardar",
        "logout": "Cerrar sesión",
        "api_settings": "Configuración de API",
        "select_exchange": "Seleccionar Exchange",
        "api_key": "API Key",
        "secret_key": "Secret Key",
        "passphrase": "Passphrase",
        "save_api_data": "Guardar Datos de API"
    }
}


def get_translations(lang: str):
    return translations.get(lang, translations["ru"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -----------------------------------------------------------------------------
# Главная страница (приветствие)
# -----------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Добро пожаловать в Trading Journal!"})

# -----------------------------------------------------------------------------
# Форма логина
# -----------------------------------------------------------------------------


@app.get("/login_form", response_class=HTMLResponse)
def login_form(request: Request):
    lang = request.query_params.get("lang", "ru")
    t = get_translations(lang)
    return templates.TemplateResponse("login.html", {"request": request, "t": t, "lang": lang, "token": ""})

# -----------------------------------------------------------------------------
# Endpoint для обработки логина и перенаправления в личный кабинет
# -----------------------------------------------------------------------------


@app.post("/login_form_action", response_class=HTMLResponse)
def login_form_action(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    lang = request.query_params.get("lang", "ru")
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        t = get_translations(lang)
        return templates.TemplateResponse("login.html", {"request": request, "t": t, "lang": lang, "error": "Неверные учетные данные", "token": ""})
    token = auth.create_access_token({"sub": user.username})
    return RedirectResponse(url=f"/dashboard?lang={lang}&token={token}", status_code=303)

# -----------------------------------------------------------------------------
# Форма регистрации с сообщением об успехе
# -----------------------------------------------------------------------------


@app.get("/register_form", response_class=HTMLResponse)
def register_form(request: Request):
    lang = request.query_params.get("lang", "ru")
    success = request.query_params.get("success", "")
    t = get_translations(lang)
    return templates.TemplateResponse("register.html", {"request": request, "t": t, "lang": lang, "token": "", "success": success})


@app.post("/register_form_action", response_class=HTMLResponse)
def register_form_action(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    date_of_birth: str = Form(...),  # ожидаем дату в формате YYYY-MM-DD
    db: Session = Depends(get_db)
):
    lang = request.query_params.get("lang", "ru")
    t = get_translations(lang)

    # Проверяем, что пароли совпадают
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "t": t, "lang": lang, "error": t["password_mismatch"], "token": ""})

    # Проверяем возраст пользователя (должен быть не менее 16 лет)
    try:
        dob = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse("register.html", {"request": request, "t": t, "lang": lang, "error": "Неверный формат даты.", "token": ""})

    today = date.today()
    age = today.year - dob.year - \
        ((today.month, today.day) < (dob.month, dob.day))
    if age < 16:
        return templates.TemplateResponse("register.html", {"request": request, "t": t, "lang": lang, "error": t["age_error"], "token": ""})

    if crud.get_user_by_username(db, username):
        return templates.TemplateResponse("register.html", {"request": request, "t": t, "lang": lang, "error": "Пользователь уже существует", "token": ""})

    hashed_pw = auth.get_password_hash(password)
    new_user = crud.create_user(db, username, hashed_pw, dob)
    db.commit()
    return RedirectResponse(url=f"/register_form?lang={lang}&success=1", status_code=303)

# -----------------------------------------------------------------------------
# Форма для админ-регистрации
# -----------------------------------------------------------------------------


@app.get("/admin_register_form", response_class=HTMLResponse)
def admin_register_form(request: Request):
    lang = request.query_params.get("lang", "ru")
    t = get_translations(lang)
    return templates.TemplateResponse("admin_register.html", {"request": request, "t": t, "lang": lang, "token": ""})

# -----------------------------------------------------------------------------
# Страница Dashboard
# -----------------------------------------------------------------------------


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, token: str = None, db: Session = Depends(get_db)):
    lang = request.query_params.get("lang", "ru")
    t = get_translations(lang)

    # Инициализируем переменные балансов как None (если данные отсутствуют)
    bitget_balance = None
    binance_balance = None
    kraken_balance = None
    kucoin_balance = None
    cbpro_balance = None
    mexc_balance = None
    auto_trades = "[Автоматическая выгрузка сделок из API профиля]"
    diagram_placeholder = "[Диаграмма изменения капитала]"

    if token:
        try:
            user = auth.get_current_user_from_token(token, db)
        except Exception as e:
            logger.error(f"Ошибка получения пользователя из токена: {e}")
            user = None

        if user:
            # --- Bitget ---
            bitget_key = crud.get_api_key(db, user.id, "bitget")
            if bitget_key:
                bitget_params = {
                    "token": token,
                    "api_key": bitget_key.api_key,
                    "secret_key": bitget_key.secret_key,
                    "passphrase": bitget_key.passphrase
                }
                try:
                    resp = requests.get(
                        "http://bitget-service:8004/get_balance", params=bitget_params)
                    resp.raise_for_status()
                    real_balance = resp.json()
                    if isinstance(real_balance, dict) and "balance" in real_balance:
                        bitget_balance = f"{real_balance['balance']}"
                    else:
                        bitget_balance = "Нет данных"
                except Exception as e:
                    logger.error(f"Ошибка запроса баланса Bitget: {e}")
                    bitget_balance = "Ошибка получения данных"

            # --- Binance ---
            binance_key = crud.get_api_key(db, user.id, "binance")
            if binance_key:
                binance_params = {
                    "token": token,
                    "api_key": binance_key.api_key,
                    "secret_key": binance_key.secret_key
                }
                try:
                    resp = requests.get(
                        "http://binance-service:8001/get_balance", params=binance_params)
                    resp.raise_for_status()
                    real_balance = resp.json()
                    if isinstance(real_balance, dict) and "USDT" in real_balance and float(real_balance["USDT"]) > 0:
                        binance_balance = f"{real_balance['USDT']} USDT"
                    else:
                        assets = {k: v for k, v in real_balance.items() if float(
                            v) > 0} if isinstance(real_balance, dict) else {}
                        binance_balance = assets if assets else "Нет данных"
                except Exception as e:
                    logger.error(f"Ошибка запроса баланса Binance: {e}")
                    binance_balance = "Ошибка получения данных"

            # --- Kraken ---
            kraken_key = crud.get_api_key(db, user.id, "kraken")
            if kraken_key:
                kraken_params = {
                    "token": token,
                    "api_key": kraken_key.api_key,
                    "secret_key": kraken_key.secret_key
                }
                try:
                    resp = requests.get(
                        "http://kraken-service:8002/get_balance", params=kraken_params)
                    resp.raise_for_status()
                    real_balance = resp.json()
                    if isinstance(real_balance, dict) and "result" in real_balance:
                        balance_value = real_balance.get(
                            "result", {}).get("XXBTZUSD", "Нет данных")
                        kraken_balance = f"{balance_value}"
                    else:
                        kraken_balance = "Нет данных"
                except Exception as e:
                    logger.error(f"Ошибка запроса баланса Kraken: {e}")
                    kraken_balance = "Ошибка получения данных"

            # --- Kucoin ---
            kucoin_key = crud.get_api_key(db, user.id, "kucoin")
            if kucoin_key:
                kucoin_params = {
                    "token": token,
                    "api_key": kucoin_key.api_key,
                    "secret_key": kucoin_key.secret_key,
                    "passphrase": kucoin_key.passphrase
                }
                try:
                    resp = requests.get(
                        "http://kucoin-service:8006/get_balance", params=kucoin_params)
                    resp.raise_for_status()
                    real_balance = resp.json()
                    if isinstance(real_balance, list):
                        accounts = [f"{acc.get('currency')}: {acc.get('balance')}"
                                    for acc in real_balance if float(acc.get('balance', 0)) > 0]
                        kucoin_balance = " , ".join(
                            accounts) if accounts else "Нет данных"
                    else:
                        kucoin_balance = "Нет данных"
                except Exception as e:
                    logger.error(f"Ошибка запроса баланса Kucoin: {e}")
                    kucoin_balance = "Ошибка получения данных"

            # --- CBPro ---
            cbpro_key = crud.get_api_key(db, user.id, "cbpro")
            if cbpro_key:
                cbpro_params = {
                    "token": token,
                    "api_key": cbpro_key.api_key,
                    "secret_key": cbpro_key.secret_key,
                    "passphrase": cbpro_key.passphrase
                }
                try:
                    resp = requests.get(
                        "http://cbpro-service:8003/get_balance", params=cbpro_params)
                    resp.raise_for_status()
                    real_balance = resp.json()
                    if isinstance(real_balance, dict) and "balance" in real_balance:
                        cbpro_balance = f"{real_balance['balance']}"
                    else:
                        cbpro_balance = "Нет данных"
                except Exception as e:
                    logger.error(f"Ошибка запроса баланса CBPro: {e}")
                    cbpro_balance = "Ошибка получения данных"

            # --- Mexc ---
            mexc_key = crud.get_api_key(db, user.id, "mexc")
            if mexc_key:
                mexc_params = {
                    "token": token,
                    "api_key": mexc_key.api_key,
                    "secret_key": mexc_key.secret_key
                }
                try:
                    resp = requests.get(
                        "http://mexc-service:8005/get_balance", params=mexc_params)
                    resp.raise_for_status()
                    real_balance = resp.json()
                    if isinstance(real_balance, dict) and "data" in real_balance:
                        mexc_balance = f"{real_balance['data'].get('balance', 'Нет данных')}"
                    else:
                        mexc_balance = "Нет данных"
                except Exception as e:
                    logger.error(f"Ошибка запроса баланса Mexc: {e}")
                    mexc_balance = "Ошибка получения данных"

    # Формируем итоговую сводку (выводим данные только для бирж, для которых есть API ключи)
    metric_lines = []
    if bitget_balance is not None:
        metric_lines.append(f"Bitget: {bitget_balance}")
    if binance_balance is not None:
        metric_lines.append(f"Binance: {binance_balance}")
    if kraken_balance is not None:
        metric_lines.append(f"Kraken: {kraken_balance}")
    if kucoin_balance is not None:
        metric_lines.append(f"Kucoin: {kucoin_balance}")
    if cbpro_balance is not None:
        metric_lines.append(f"CBPro: {cbpro_balance}")
    if mexc_balance is not None:
        metric_lines.append(f"Mexc: {mexc_balance}")

    capital_overview = " | ".join(metric_lines) if metric_lines else "N/A"

    metrics = {
        "capital_overview": capital_overview,
        "auto_trades": auto_trades or "N/A",
        "diagram_capital": diagram_placeholder or "N/A",
        "total_trades": "N/A",
        "total_profit": "N/A",
        "total_losses": "N/A",
        "total_wins": "N/A"
    }

    trades = []  # Здесь можно добавить историю сделок

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "t": t,
        "lang": lang,
        "metrics": metrics,
        "trades": trades,
        "token": token or ""
    })


# -----------------------------------------------------------------------------
# Страница Settings (обновление персональных данных и API)
# -----------------------------------------------------------------------------


@app.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, db: Session = Depends(get_db)):
    lang = request.query_params.get("lang", "ru")
    token = request.query_params.get("token", "")
    t = get_translations(lang)
    user = None
    if token:
        try:
            user = auth.get_current_user_from_token(token, db)
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя: {e}")
            user = None
    if not user:
        return RedirectResponse(url=f"/login_form?lang={lang}", status_code=303)
    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "t": t,
            "lang": lang,
            "token": token,
            "user": user
        }
    )

# -----------------------------------------------------------------------------
# Endpoint для обновления персональных данных (email, phone)
# -----------------------------------------------------------------------------


@app.post("/update_settings", response_class=HTMLResponse)
def update_settings(
    request: Request,
    email: str = Form(...),
    phone: str = Form(...),
    db: Session = Depends(get_db)
):
    lang = request.query_params.get("lang", "ru")
    token = request.query_params.get("token", "")
    user = auth.get_current_user_from_token(token, db)
    user.email = email
    user.phone = phone
    db.commit()
    db.refresh(user)
    return RedirectResponse(url=f"/dashboard?lang={lang}&token={token}", status_code=303)

# -----------------------------------------------------------------------------
# Endpoint для добавления API Key (через форму, включая скрытое поле token)
# -----------------------------------------------------------------------------


@app.post("/add_api_key")
def add_api_key(
    api_key: str = Form(...),
    secret_key: str = Form(...),
    exchange: str = Form(...),
    token: str = Form(...),
    passphrase: Optional[str] = Form(None),
    lang: str = Query("ru"),
    db: Session = Depends(get_db)
):
    current_user = auth.get_current_user_from_token(token, db)
    if not current_user:
        raise HTTPException(status_code=401, detail="Не авторизован")
    if passphrase:
        logger.info(f"Получен passphrase для {exchange}: {passphrase}")
    new_key = crud.create_api_key(
        db, current_user.id, exchange.lower(), api_key, secret_key, passphrase)
    return RedirectResponse(url=f"/dashboard?lang={lang}&token={token}", status_code=303)

# -----------------------------------------------------------------------------
# Выход (logout)
# -----------------------------------------------------------------------------


@app.get("/logout")
def logout(request: Request):
    lang = request.query_params.get("lang", "ru")
    return RedirectResponse(url=f"/login_form?lang={lang}", status_code=303)

# -----------------------------------------------------------------------------
# Форма создания сделки
# -----------------------------------------------------------------------------


@app.get("/deal_form", response_class=HTMLResponse)
def deal_form(request: Request):
    lang = request.query_params.get("lang", "ru")
    t = get_translations(lang)
    token = request.query_params.get("token", "")
    return templates.TemplateResponse("deal_form.html", {"request": request, "t": t, "lang": lang, "token": token})


@app.post("/deals", response_model=schemas.Deal)
def create_deal(
    full_name: str = Form(...),
    password: str = Form(...),
    api_key: str = Form(...),
    platform: str = Form(...),
    crypto_currency: str = Form(...),
    quantity_bought: float = Form(...),
    quantity_sold: float = Form(...),
    exchange_rate: float = Form(...),
    db: Session = Depends(get_db)
):
    profit = (quantity_sold - quantity_bought) * exchange_rate
    deal_data = schemas.DealCreate(
        full_name=full_name,
        password=password,
        api_key=api_key,
        platform=platform,
        crypto_currency=crypto_currency,
        quantity_bought=quantity_bought,
        quantity_sold=quantity_sold,
        exchange_rate=exchange_rate
    )
    return crud.create_deal(db, deal_data, profit)

# -----------------------------------------------------------------------------
# JSON API эндпоинты (register, token, admin/create_user)
# -----------------------------------------------------------------------------


@app.post("/register", response_model=schemas.User)
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, username):
        raise HTTPException(
            status_code=400, detail="Пользователь уже существует")
    hashed_pw = auth.get_password_hash(password)
    # Здесь вызываем create_user с датой рождения.
    # В данном endpoint-е дату рождения не передают, поэтому этот endpoint можно оставить для API,
    # а регистрацию через форму обрабатывать через /register_form_action.
    return crud.create_user(db, username, hashed_pw, date(1970, 1, 1))


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Неверные учетные данные")
    token = auth.create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/admin/create_user", response_model=schemas.User)
def admin_create_user(username: str = Form(...), password: str = Form(...), token: str = Form(...), db: Session = Depends(get_db)):
    admin_user = auth.get_current_user_from_token(token, db)
    if admin_user.username != "admin":
        raise HTTPException(
            status_code=403, detail="Требуется доступ администратора")
    if crud.get_user_by_username(db, username):
        raise HTTPException(
            status_code=400, detail="Пользователь уже существует")
    hashed_pw = auth.get_password_hash(password)
    return crud.create_user(db, username, hashed_pw, date(1970, 1, 1))

# -----------------------------------------------------------------------------
# Функция для создания мастер-админа (если не существует)
# -----------------------------------------------------------------------------


def seed_admin():
    db = SessionLocal()
    if not crud.get_user_by_username(db, "admin"):
        admin_pw = auth.get_password_hash("admin")
        new_admin = crud.create_user(db, "admin", admin_pw, date(1970, 1, 1))
        db.commit()
        logger.info("Мастер-админ создан: login=admin, password=admin")
    db.close()


seed_admin()

# -----------------------------------------------------------------------------
# Запуск приложения
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)