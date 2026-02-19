"""
Session security helpers.

Strategy: signed HttpOnly cookie (itsdangerous URLSafeTimedSerializer).
  - The cookie payload is just {"player_id": "google:123"} — no sensitive data.
  - The signature uses SECRET_KEY, so tampering is detectable.
  - HttpOnly + Secure + SameSite=Lax blocks XSS token theft and most CSRF.

get_current_player() is the FastAPI dependency injected into every
protected route. It reads + verifies the cookie, loads the player from DB,
and raises 401/403 as appropriate.
"""

import secrets
from typing import Annotated

import bcrypt

from fastapi import Cookie, Depends, HTTPException, Request, Response
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import settings
from app.db.database import get_db
from app.models.player import Player

# ─── Serializer ───────────────────────────────────────────────────────────────

_serializer = URLSafeTimedSerializer(settings.SECRET_KEY, salt="session")

SESSION_COOKIE_NAME = "session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days in seconds
OAUTH_STATE_COOKIE_NAME = "oauth_state"
OAUTH_STATE_MAX_AGE = 60 * 5  # 5 minutes — only needed during the OAuth dance


# ─── Cookie helpers ───────────────────────────────────────────────────────────


def create_session_cookie(response: Response, player_id: str) -> None:
    """Sign and set the session cookie on a response."""
    payload = {"player_id": player_id}
    signed = _serializer.dumps(payload)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=signed,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    """Delete the session cookie (logout)."""
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
    )


def create_oauth_state() -> str:
    """Generate a cryptographically random state nonce for CSRF protection."""
    return secrets.token_urlsafe(32)


def set_oauth_state_cookie(response: Response, state: str) -> None:
    """Store the OAuth state nonce in a short-lived HttpOnly cookie."""
    response.set_cookie(
        key=OAUTH_STATE_COOKIE_NAME,
        value=state,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
        max_age=OAUTH_STATE_MAX_AGE,
        path="/",
    )


def clear_oauth_state_cookie(response: Response) -> None:
    response.delete_cookie(
        key=OAUTH_STATE_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite="lax",
    )


def verify_oauth_state(request: Request, returned_state: str) -> None:
    """
    Compare the state returned by the OAuth provider against the cookie.
    Raises 400 if they don't match (CSRF attempt or stale request).
    """
    stored_state = request.cookies.get(OAUTH_STATE_COOKIE_NAME)
    if not stored_state or not secrets.compare_digest(stored_state, returned_state):
        raise HTTPException(status_code=400, detail="Invalid OAuth state — possible CSRF")


# ─── Auth dependency ──────────────────────────────────────────────────────────


async def get_current_player(
    request: Request,
    db=Depends(get_db),
) -> Player:
    """
    FastAPI dependency: verify session cookie → load player from DB.

    Raises:
        401 — missing cookie, bad signature, or expired session
        403 — player account is banned
    """
    raw_cookie = request.cookies.get(SESSION_COOKIE_NAME)
    if not raw_cookie:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Verify signature and expiry
    try:
        data = _serializer.loads(raw_cookie, max_age=SESSION_MAX_AGE)
    except SignatureExpired:
        raise HTTPException(status_code=401, detail="Session expired — please log in again")
    except BadSignature:
        raise HTTPException(status_code=401, detail="Invalid session")

    player_id: str = data.get("player_id", "")
    if not player_id:
        raise HTTPException(status_code=401, detail="Malformed session")

    # Load from DB
    cursor = await db.execute(
        "SELECT * FROM players WHERE oauth_id = ?", (player_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=401, detail="Player not found")

    player = Player.from_row(row)

    # Moderation gate
    if player.is_banned:
        raise HTTPException(status_code=403, detail="Account suspended")

    return player


# Convenience type alias for route signatures
CurrentPlayer = Annotated[Player, Depends(get_current_player)]


# ─── Password helpers ─────────────────────────────────────────────────────────


def hash_password(plain: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())
