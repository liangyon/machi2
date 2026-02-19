"""
OAuth client factories for Google and GitHub.

Uses Authlib's AsyncOAuth2Client (backed by httpx) so all network calls
are non-blocking and compatible with FastAPI's async request handlers.
"""

from authlib.integrations.httpx_client import AsyncOAuth2Client

from app.core.config import settings

# ─── Provider metadata ────────────────────────────────────────────────────────

GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"

GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USERINFO_URL = "https://api.github.com/user"
GITHUB_EMAILS_URL = "https://api.github.com/user/emails"


def _redirect_uri(provider: str) -> str:
    """Build the callback URL for a given provider."""
    return f"{settings.OAUTH_REDIRECT_BASE}/api/auth/callback/{provider}"


def get_google_client() -> AsyncOAuth2Client:
    return AsyncOAuth2Client(
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scope="openid email profile",
        redirect_uri=_redirect_uri("google"),
    )


def get_github_client() -> AsyncOAuth2Client:
    return AsyncOAuth2Client(
        client_id=settings.GITHUB_CLIENT_ID,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        scope="read:user user:email",
        redirect_uri=_redirect_uri("github"),
    )
