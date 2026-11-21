from pydantic import Field

from .common import APIModel


class LoginRequest(APIModel):
    email: str
    password: str = Field(min_length=1)


class LoginResponse(APIModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_seconds: int
