from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from jose import JWTError

import models
import schemas
import auth
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ---------------------------
# CORS (Frontend on 5500)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Database Dependency
# ---------------------------


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# Auth Dependency
# ---------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = auth.decode_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(models.User).filter(
        models.User.username == username
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ===========================
# AUTH ROUTES
# ===========================

@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400, detail="Username already registered")

    hashed = auth.hash_password(user.password)

    new_user = models.User(
        username=user.username,
        password_hash=hashed
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created"}


@app.post("/login", response_model=schemas.Token)
def login(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if not db_user or not auth.verify_password(
        user.password,
        db_user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({
        "sub": db_user.username
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# ===========================
# TASK ROUTES (PER USER)
# ===========================

# Add these to the bottom of main.py

@app.get("/cart")
def get_cart(db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    return db.query(models.CartItem).filter(models.CartItem.owner_id == user.id).all()


@app.post("/cart/add")
def add_to_cart(name: str, price: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    item = db.query(models.CartItem).filter(
        models.CartItem.owner_id == user.id,
        models.CartItem.product_name == name
    ).first()

    if item:
        item.quantity += 1
    else:
        new_item = models.CartItem(
            product_name=name, price=price, quantity=1, owner_id=user.id)
        db.add(new_item)

    db.commit()
    return {"message": "Added to cart"}


@app.post("/cart/update")
def update_cart_qty(item_id: int, delta: int, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    item = db.query(models.CartItem).filter(
        models.CartItem.id == item_id,
        models.CartItem.owner_id == user.id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.quantity += delta

    if item.quantity <= 0:
        db.delete(item)

    db.commit()
    return {"message": "Cart updated"}


@app.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Deleted"}


@app.patch("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.owner_id == user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = True
    db.commit()

    return {"message": "Completed"}
