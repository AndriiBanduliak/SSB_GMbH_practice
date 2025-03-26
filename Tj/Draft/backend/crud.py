from sqlalchemy.orm import Session
import backend.models as models

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, username: str, hashed_password: str, date_of_birth):
    """
    Создает пользователя с указанной датой рождения.
    :param db: Сессия SQLAlchemy.
    :param username: Имя пользователя.
    :param hashed_password: Хэшированный пароль.
    :param date_of_birth: Дата рождения (тип date).
    :return: Объект пользователя.
    """
    user = models.User(
        username=username, 
        hashed_password=hashed_password, 
        date_of_birth=date_of_birth
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_api_key(db: Session, user_id: int, exchange: str, api_key: str, secret_key: str, passphrase: str = None):
    """
    Создает или обновляет API-ключ для данного пользователя и биржи.
    """
    existing = db.query(models.APIKey).filter(
        models.APIKey.user_id == user_id,
        models.APIKey.exchange == exchange
    ).first()
    if existing:
        existing.api_key = api_key
        existing.secret_key = secret_key
        existing.passphrase = passphrase
        db.commit()
        db.refresh(existing)
        return existing
    else:
        db_api_key = models.APIKey(
            user_id=user_id, 
            exchange=exchange, 
            api_key=api_key, 
            secret_key=secret_key,
            passphrase=passphrase
        )
        db.add(db_api_key)
        db.commit()
        db.refresh(db_api_key)
        return db_api_key

def get_api_key(db: Session, user_id: int, exchange: str):
    return db.query(models.APIKey).filter(
        models.APIKey.user_id == user_id,
        models.APIKey.exchange == exchange
    ).first()

def create_balance(db: Session, user_id: int, exchange: str, balance: str):
    db_balance = models.Balance(user_id=user_id, exchange=exchange, balance=balance)
    db.add(db_balance)
    db.commit()
    db.refresh(db_balance)
    return db_balance

def get_balances(db: Session):
    return db.query(models.Balance).all()

def create_deal(db: Session, deal, profit: float):
    db_deal = models.Deal(
        full_name=deal.full_name,
        password=deal.password,
        api_key=deal.api_key,
        platform=deal.platform,
        crypto_currency=deal.crypto_currency,
        quantity_bought=str(deal.quantity_bought),
        quantity_sold=str(deal.quantity_sold),
        exchange_rate=str(deal.exchange_rate),
        profit=str(profit)
    )
    db.add(db_deal)
    db.commit()
    db.refresh(db_deal)
    return db_deal
