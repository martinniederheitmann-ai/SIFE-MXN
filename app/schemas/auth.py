from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Segundos de validez del token.")


class PasswordChangeBody(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=1, max_length=128)


class UserPublic(BaseModel):
    id: int
    username: str
    email: str | None = None
    full_name: str | None = None
    is_active: bool
    role_name: str

    model_config = {"from_attributes": True}
