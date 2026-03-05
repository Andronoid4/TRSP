from fastapi import FastAPI
from fastapi.responses import FileResponse
from models import User, Feedback

app = FastAPI()

# Хранилище для отзывов (Задание 2.1)
feedbacks = []

# =============================================================================
# Задание 1.2: Возврат HTML страницы на корневом URL /
# (Перекрывает задание 1.1, так как это более поздний этап)
# =============================================================================
@app.get("/")
async def read_root():
    return FileResponse('index.html')

# =============================================================================
# Задание 1.4: GET /users (возврат данных пользователя)
# =============================================================================
@app.get("/users")
async def get_user():
    # Создайте экземпляр класса User
    user = User(name="Andranik", id=1)
    return user

# =============================================================================
# Задание 2.1: POST /feedback (сбор отзывов)
# =============================================================================
@app.post("/feedback")
async def submit_feedback(feedback: Feedback):
    # Сохраняем данные в список
    feedbacks.append(feedback)
    # Возвращаем сообщение об успехе (как в примере задания 2.1)
    return {"message": f"Feedback received. Thank you, {feedback.name}."}