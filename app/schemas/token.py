from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    user_role: str | None = None
    user_id: int | None = None
    user_name: str | None = None

class TokenPayload(BaseModel):
    sub: str | None = None
