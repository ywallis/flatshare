from datetime import timedelta

import requests
from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from sqlmodel import Session, select

from src.authentication import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    create_access_token,
    get_current_user,
    google_client_id,
    google_client_secret,
    google_redirect_url,
)
from src.models import User, UserCreateNP
from src.utils import check_hash, get_session

router = APIRouter()


@router.get("/login/google", summary="Initiate Google OAuth Login")
async def login_google():
    """
    Redirects the user to Google's OAuth consent screen.
    The `scope` parameter requests access to the user's OpenID, profile, and email information.
    `access_type=offline` ensures a refresh token is issued (if consented by the user),
    allowing for long-lived access.
    """
    # Ensure google_client_id and google_redirect_url are correctly configured
    if not google_client_id or not google_redirect_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth configuration missing.",
        )

    return {
        "url": (
            f"https://accounts.google.com/o/oauth2/auth?"
            f"response_type=code&client_id={google_client_id}&"
            f"redirect_uri={google_redirect_url}&scope=openid%20profile%20email&"
            f"access_type=offline"
        )
    }


@router.get(
    "/auth/google",
    response_model=Token,
    summary="Handle Google OAuth callback and issue internal token. Creates new user if none exists.",
)
async def auth_google(code: str, session: Session = Depends(get_session)):
    """This endpoint handles the callback from Google after the user grants permission."""
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "redirect_uri": google_redirect_url,
        "grant_type": "authorization_code",
    }
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    tokens = response.json()
    google_access_token = tokens.get("access_token")
    google_id_token = tokens.get("id_token")

    if not google_access_token or not google_id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing access_token or id_token from Google response.",
        )

    idinfo = id_token.verify_oauth2_token(
        google_id_token, google_requests.Request(), google_client_id
    )
    if idinfo["aud"] != google_client_id:
        raise ValueError("Could not verify audience.")
    if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
        raise ValueError("Wrong issuer.")

    user_email = idinfo.get("email")

    if not user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google ID token did not contain an email address.",
        )

    statement = select(User).where(User.email == user_email)
    user = session.exec(statement).one_or_none()
    if not user:
        headers = {"Authorization": f"Bearer {google_access_token}"}
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo", headers=headers
        )
        user_info = resp.json()
        first_name = user_info.get("given_name")
        last_name = user_info.get("family_name")
        new_User = UserCreateNP(
            first_name=first_name, last_name=last_name, email=user_email
        )
        db_user = User.model_validate(new_User)
        session.add(db_user)
        session.commit()
        user = db_user

    token_expiration = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires=token_expiration
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/token", summary="Login endpoint for email/password")
async def login_for_token(
    *,
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """This endpoint allows logging in with a standard OAuth password request form. The email is used as username."""
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Cannot authenticate")
    if user.hashed_password is None:
        raise HTTPException(status_code=404, detail="Cannot authenticate")
    if not check_hash(form_data.password, user.hashed_password):
        raise HTTPException(status_code=404, detail="Cannot authenticate")

    token_expiration = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires=token_expiration
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
async def read_me(current_user: User = Depends(get_current_user)):
    return current_user
