"""
Auth routes — OAuth 2.0 (Google / GitHub) + username/password.

─── OAuth flow ───────────────────────────────────────────────────────────────
  1. POST /login?provider=google|github
       → generate state nonce, store in short-lived cookie
       → return the provider's authorization URL to the frontend

  2. GET /callback/{provider}
       → verify state nonce (CSRF check)
       → exchange code for access token
       → fetch user info from provider
       → upsert player in DB (auto-merge with existing password account if
         the provider email matches an existing password-auth account)
       → set signed HttpOnly session cookie
       → redirect browser to /game

─── Password flow ────────────────────────────────────────────────────────────
  3. POST /signup
       Body: { username, email, password }
       → validate uniqueness
       → hash password with bcrypt
       → insert player (oauth_id = "local:<email>", provider = "password")
       → set session cookie → return PlayerProfile

  4. POST /login/password
       Body: { email, password }
       → look up player by email where auth_method = 'password'
       → verify bcrypt hash
       → set session cookie → return PlayerProfile

─── Shared ───────────────────────────────────────────────────────────────────
  5. GET /me        → verify session cookie → return PlayerProfile
  6. POST /logout   → clear session cookie → return 200

─── OAuth ↔ password auto-merge ─────────────────────────────────────────────
  If an OAuth provider returns an email that already belongs to a password
  account, we merge them rather than creating a duplicate row.  The existing
  account's `provider` and `auth_method` are left untouched (so password
  login and the UserMenu badge stay consistent); the linked OAuth provider
  name is stored in the separate `linked_provider` column.
"""

import json
import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, field_validator
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.oauth import (
    GITHUB_AUTHORIZE_URL,
    GITHUB_EMAILS_URL,
    GITHUB_TOKEN_URL,
    GITHUB_USERINFO_URL,
    GOOGLE_AUTHORIZE_URL,
    GOOGLE_TOKEN_URL,
    GOOGLE_USERINFO_URL,
    get_github_client,
    get_google_client,
)
from app.core.security import (
    CurrentPlayer,
    clear_oauth_state_cookie,
    clear_session_cookie,
    create_oauth_state,
    create_session_cookie,
    hash_password,
    set_oauth_state_cookie,
    verify_oauth_state,
    verify_password,
)
from app.db.database import get_db
from app.models.player import PlayerProfile

logger = logging.getLogger(__name__)

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)

_POST_LOGIN_REDIRECT = "http://localhost:3000/game"


# ─── Request / Response schemas ───────────────────────────────────────────────


class SignupRequest(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 32:
            raise ValueError("Username must be 2–32 characters")
        if not re.match(r"^[\w\- ]+$", v):
            raise ValueError("Username may only contain letters, numbers, spaces, hyphens, underscores")
        return v

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("Invalid email address")
        return v

    @field_validator("password")
    @classmethod
    def password_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginPasswordRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_norm(cls, v: str) -> str:
        return v.strip().lower()


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _namespace_id(provider: str, raw_id: str | int) -> str:
    """Prefix the provider name to avoid cross-provider ID collisions."""
    return f"{provider}:{raw_id}"


async def _upsert_oauth_player(
    db,
    oauth_id: str,
    username: str,
    provider: str,
    email: str | None,
) -> str:
    """
    Insert a new OAuth player or update on re-login.

    Auto-merge: if the provider supplies an email that already belongs to a
    password-auth account, we *upgrade* that account to also accept this OAuth
    identity instead of creating a duplicate row.  The canonical player_id
    returned is always the one stored in the session cookie.

    Returns the player_id to put in the session cookie.
    """
    # Check for an existing password account with the same email
    if email:
        cursor = await db.execute(
            "SELECT oauth_id FROM players WHERE email = ? AND auth_method = 'password'",
            (email,),
        )
        existing = await cursor.fetchone()
        if existing:
            # Merge: attach this OAuth identity to the existing password account.
            # We keep the existing oauth_id (local:<email>) as the primary key and
            # leave `provider` / `auth_method` untouched so the password login path
            # and the UserMenu badge remain consistent.  The linked OAuth provider
            # is recorded in `linked_provider` for informational purposes only.
            existing_id: str = existing["oauth_id"]
            logger.info(
                "OAuth merge: linking %s identity to existing password account %s",
                provider,
                existing_id,
            )
            await db.execute(
                """
                UPDATE players
                SET linked_provider = ?, last_login = CURRENT_TIMESTAMP
                WHERE oauth_id = ?
                """,
                (provider, existing_id),
            )
            await db.commit()
            return existing_id

    # Normal upsert
    await db.execute(
        """
        INSERT INTO players (oauth_id, username, provider, email, auth_method, last_login)
        VALUES (?, ?, ?, ?, 'oauth', CURRENT_TIMESTAMP)
        ON CONFLICT(oauth_id) DO UPDATE SET
            username   = excluded.username,
            email      = excluded.email,
            last_login = CURRENT_TIMESTAMP
        """,
        (oauth_id, username, provider, email),
    )
    await db.commit()
    return oauth_id


# ─── OAuth routes ─────────────────────────────────────────────────────────────


@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, provider: str, response: Response):
    """
    Initiate the OAuth flow.

    Returns the provider's authorization URL so the frontend can redirect
    the user (or open a popup). Also sets a short-lived state cookie for
    CSRF protection on the callback.
    """
    if provider not in ("google", "github"):
        raise HTTPException(status_code=400, detail="Unsupported provider")

    state = create_oauth_state()
    set_oauth_state_cookie(response, state)

    if provider == "google":
        client = get_google_client()
        url, _ = client.create_authorization_url(
            GOOGLE_AUTHORIZE_URL,
            state=state,
            access_type="offline",
            prompt="select_account",
        )
    else:
        client = get_github_client()
        url, _ = client.create_authorization_url(
            GITHUB_AUTHORIZE_URL,
            state=state,
        )

    return {"redirect_url": url}


@router.get("/callback/google")
@limiter.limit("10/minute")
async def callback_google(
    request: Request,
    response: Response,
    code: str,
    state: str,
    db=Depends(get_db),
):
    """Handle Google's OAuth callback."""
    verify_oauth_state(request, state)

    client = get_google_client()
    try:
        await client.fetch_token(GOOGLE_TOKEN_URL, code=code)
    except Exception as exc:
        logger.error("Google token exchange failed: %s", exc)
        raise HTTPException(status_code=400, detail="Authentication failed — please try again")

    try:
        resp = await client.get(GOOGLE_USERINFO_URL)
        resp.raise_for_status()
        info = resp.json()
    except Exception as exc:
        logger.error("Google userinfo fetch failed: %s", exc)
        raise HTTPException(status_code=400, detail="Authentication failed — please try again")

    raw_id = info.get("sub")
    if not raw_id:
        raise HTTPException(status_code=400, detail="Google did not return a user ID")

    oauth_id = _namespace_id("google", raw_id)
    username = info.get("name") or info.get("email", "Adventurer")
    email = info.get("email")

    player_id = await _upsert_oauth_player(db, oauth_id, username, "google", email)

    redirect = RedirectResponse(url=_POST_LOGIN_REDIRECT, status_code=302)
    create_session_cookie(redirect, player_id)
    clear_oauth_state_cookie(redirect)
    return redirect


@router.get("/callback/github")
@limiter.limit("10/minute")
async def callback_github(
    request: Request,
    response: Response,
    code: str,
    state: str,
    db=Depends(get_db),
):
    """Handle GitHub's OAuth callback."""
    verify_oauth_state(request, state)

    client = get_github_client()
    try:
        await client.fetch_token(GITHUB_TOKEN_URL, code=code)
    except Exception as exc:
        logger.error("GitHub token exchange failed: %s", exc)
        raise HTTPException(status_code=400, detail="Authentication failed — please try again")

    try:
        resp = await client.get(GITHUB_USERINFO_URL)
        resp.raise_for_status()
        info = resp.json()
    except Exception as exc:
        logger.error("GitHub userinfo fetch failed: %s", exc)
        raise HTTPException(status_code=400, detail="Authentication failed — please try again")

    raw_id = info.get("id")
    if not raw_id:
        raise HTTPException(status_code=400, detail="GitHub did not return a user ID")

    oauth_id = _namespace_id("github", raw_id)
    username = info.get("login") or info.get("name") or "Adventurer"

    email: str | None = info.get("email")
    if not email:
        try:
            emails_resp = await client.get(GITHUB_EMAILS_URL)
            emails_resp.raise_for_status()
            emails = emails_resp.json()
            primary = next(
                (e["email"] for e in emails if e.get("primary") and e.get("verified")),
                None,
            )
            email = primary
        except Exception:
            pass

    player_id = await _upsert_oauth_player(db, oauth_id, username, "github", email)

    redirect = RedirectResponse(url=_POST_LOGIN_REDIRECT, status_code=302)
    create_session_cookie(redirect, player_id)
    clear_oauth_state_cookie(redirect)
    return redirect


# ─── Password routes ──────────────────────────────────────────────────────────


@router.post("/signup", response_model=PlayerProfile)
@limiter.limit("5/minute")
async def signup(
    request: Request,
    body: SignupRequest,
    response: Response,
    db=Depends(get_db),
):
    """
    Create a new account with username + email + password.

    - Rejects duplicate emails (regardless of auth method).
    - Rejects duplicate usernames (case-insensitive).
    - Hashes the password with bcrypt before storing.
    - Sets a session cookie on success.
    """
    email = body.email  # already normalised by validator

    # Check email uniqueness.
    # We return a generic message rather than confirming the email exists,
    # to avoid leaking which addresses are registered (email enumeration).
    cursor = await db.execute("SELECT oauth_id FROM players WHERE email = ?", (email,))
    if await cursor.fetchone():
        raise HTTPException(
            status_code=409,
            detail="Unable to create account. If you already have an account, try logging in.",
        )

    # Check username uniqueness (case-insensitive)
    cursor = await db.execute(
        "SELECT oauth_id FROM players WHERE LOWER(username) = LOWER(?)", (body.username,)
    )
    if await cursor.fetchone():
        raise HTTPException(status_code=409, detail="That username is already taken.")

    player_id = f"local:{email}"
    pw_hash = hash_password(body.password)

    await db.execute(
        """
        INSERT INTO players
            (oauth_id, username, provider, email, password_hash, auth_method, last_login)
        VALUES (?, ?, 'password', ?, ?, 'password', CURRENT_TIMESTAMP)
        """,
        (player_id, body.username, email, pw_hash),
    )
    await db.commit()

    create_session_cookie(response, player_id)

    return PlayerProfile(
        username=body.username,
        provider="password",
        email=email,
        auth_method="password",
        legacy_spellbook=[],
        grimoire_count=0,
    )


@router.post("/login/password", response_model=PlayerProfile)
@limiter.limit("10/minute")
async def login_password(
    request: Request,
    body: LoginPasswordRequest,
    response: Response,
    db=Depends(get_db),
):
    """
    Log in with email + password.

    Uses a constant-time comparison to prevent timing attacks.
    Returns a generic error for both "no account" and "wrong password"
    to avoid leaking which emails are registered.
    """
    _GENERIC_ERROR = "Invalid email or password."

    cursor = await db.execute(
        "SELECT * FROM players WHERE email = ? AND auth_method = 'password'",
        (body.email,),
    )
    row = await cursor.fetchone()

    if not row:
        # Still run a dummy hash check to keep response time constant
        verify_password("dummy", "$2b$12$KIXtq8QKlBqBqBqBqBqBqOKIXtq8QKlBqBqBqBqBqBqBqBqBqBqBq")
        raise HTTPException(status_code=401, detail=_GENERIC_ERROR)

    player_data = dict(row)
    stored_hash: str = player_data.get("password_hash") or ""

    if not stored_hash or not verify_password(body.password, stored_hash):
        raise HTTPException(status_code=401, detail=_GENERIC_ERROR)

    if player_data.get("is_banned"):
        raise HTTPException(status_code=403, detail="Account suspended")

    player_id: str = player_data["oauth_id"]

    # Update last_login
    await db.execute(
        "UPDATE players SET last_login = CURRENT_TIMESTAMP WHERE oauth_id = ?",
        (player_id,),
    )
    await db.commit()

    create_session_cookie(response, player_id)

    return PlayerProfile(
        username=player_data["username"],
        provider=player_data["provider"],
        email=player_data["email"],
        auth_method=player_data.get("auth_method", "password"),
        legacy_spellbook=json.loads(player_data.get("legacy_spellbook") or "[]"),
        grimoire_count=player_data.get("grimoire_count", 0),
    )


# ─── Shared routes ────────────────────────────────────────────────────────────


@router.get("/me", response_model=PlayerProfile)
@limiter.limit("60/minute")
async def get_me(request: Request, player: CurrentPlayer):
    """Return the current player's profile. Requires a valid session cookie."""
    return PlayerProfile(
        username=player.username,
        provider=player.provider,
        email=player.email,
        auth_method=player.auth_method,
        legacy_spellbook=player.legacy_spellbook,
        grimoire_count=player.grimoire_count,
    )


@router.post("/logout")
@limiter.limit("10/minute")
async def logout(request: Request, response: Response):
    """Clear the session cookie. Safe to call even if not logged in."""
    clear_session_cookie(response)
    return {"message": "Logged out"}
