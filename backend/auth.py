
import os
import sqlite3
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, EmailStr, Field
from pwdlib import PasswordHash

router = APIRouter(prefix="/auth", tags=["Authentication"])

DB_PATH = Path(__file__).resolve().parent / "users.db"
SECRET_FILE = Path(__file__).resolve().parent / ".auth_secret"
ALGORITHM = "HS256"
SESSION_DAYS = 7

password_hash = PasswordHash.recommended()


def get_secret():
    # A persistent secret is needed so sessions survive restarts.
    if SECRET_FILE.exists():
        return SECRET_FILE.read_text(encoding="utf-8").strip()

    secret = secrets.token_urlsafe(48)
    try:
        with SECRET_FILE.open("x", encoding="utf-8") as file:
            file.write(secret)
    except FileExistsError:
        return SECRET_FILE.read_text(encoding="utf-8").strip()

    return secret


SECRET_KEY = os.getenv("CONTRIBMATE_AUTH_SECRET") or get_secret()


def connect_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)


initialize_db()


class SignupData(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginData(BaseModel):
    email: EmailStr
    password: str


def public_user(user):
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
    }


def create_session(response, user_id, request):
    expires = datetime.now(timezone.utc) + timedelta(
        days=SESSION_DAYS
    )

    token = jwt.encode(
        {"sub": str(user_id), "exp": expires},
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response.set_cookie(
        key="contribmate_session",
        value=token,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=SESSION_DAYS * 24 * 60 * 60,
        path="/",
    )


def get_current_user(request):
    token = request.cookies.get("contribmate_session")

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not logged in.",
        )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        user_id = int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Session expired or invalid.",
        )

    with connect_db() as db:
        user = db.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found.",
        )

    return public_user(user)


@router.post("/signup", status_code=201)
def signup(data: SignupData, response: Response, request: Request):
    email = str(data.email).lower().strip()
    name = data.name.strip()

    if not name:
        raise HTTPException(400, "Name cannot be empty.")

    hashed = password_hash.hash(data.password)

    try:
        with connect_db() as db:
            cursor = db.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (?, ?, ?)
                """,
                (name, email, hashed),
            )
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    create_session(response, user_id, request)

    return {
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
        }
    }


@router.post("/login")
def login(data: LoginData, response: Response, request: Request):
    email = str(data.email).lower().strip()

    with connect_db() as db:
        user = db.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()

    if not user or not password_hash.verify(
        data.password, user["password_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    create_session(response, user["id"], request)

    return {"user": public_user(user)}


@router.get("/me")
def me(request: Request):
    return {"user": get_current_user(request)}


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        key="contribmate_session",
        path="/",
        samesite="lax",
    )
    return {"message": "Logged out successfully."}
