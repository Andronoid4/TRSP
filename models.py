from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from fastapi import Header
import re

# =============================================================================
# КР 1, Задание 1.4
# =============================================================================
class User(BaseModel):
    name: str
    id: int

# =============================================================================
# КР 1, Задание 2.1
# =============================================================================
class Feedback(BaseModel):
    name: str
    message: str

# =============================================================================
# КР 2, Задание 3.1
# =============================================================================
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: Optional[int] = Field(None, gt=0)
    is_subscribed: Optional[bool] = False

# =============================================================================
# КР 2, Задание 5.5 (Модель для переиспользования заголовков)
# =============================================================================
class CommonHeaders(BaseModel):
    user_agent: str = Header(..., alias="User-Agent")
    accept_language: str = Header(..., alias="Accept-Language")

    @field_validator('accept_language')
    @classmethod
    def validate_accept_language(cls, v: str) -> str:
        # Простая проверка формата: en-US,en;q=0.9,es;q=0.8
        pattern = r'^[\w\-]+(,[\w\-]+(;q=0\.\d+)?)*$'
        if not re.match(pattern, v):
            raise ValueError('Invalid Accept-Language format. Example: "en-US,en;q=0.9"')
        return v
