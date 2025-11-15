from fastapi import Header, HTTPException, status

from core.config import settings


def _extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    return token.strip()


def require_admin_token(
    authorization: str | None = Header(default=None, convert_underscores=False, alias="Authorization"),
    x_admin_token: str | None = Header(default=None, alias="X-Admin-Token"),
) -> str:
    provided_token = _extract_bearer_token(authorization) or (x_admin_token.strip() if x_admin_token else None)

    if not provided_token or provided_token != settings.ADMIN_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing admin token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return provided_token
