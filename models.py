from pydantic import BaseModel

# Задание 1.4: Модель пользователя
class User(BaseModel):
    name: str
    id: int

# Задание 2.1: Модель отзыва
class Feedback(BaseModel):
    name: str
    message: str