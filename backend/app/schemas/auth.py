from datetime import datetime

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    name: str | None = Field(default=None, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    name: str | None = None


class ProfileUpdateRequest(BaseModel):
    current_salary: int | None = None
    current_role_title: str | None = Field(default=None, max_length=150)


class UserResponse(BaseModel):
    id: int
    email: str | None
    name: str | None
    current_salary: int | None = None
    current_role_title: str | None = None
    created_at: datetime
