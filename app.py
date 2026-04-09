from fastapi import FastAPI, HTTPException, Response, Request, Form, Depends
from fastapi.responses import FileResponse, JSONResponse
from typing import Optional
import uuid
import time
from itsdangerous import URLSafeSerializer, BadSignature, BadData
from datetime import datetime

from models import User, Feedback, UserCreate, CommonHeaders

app = FastAPI()

# =============================================================================
# КР 1, 1.2: Возврат HTML страницы на корневом URL /
# =============================================================================
feedbacks = []

@app.get("/")
async def read_root():
    return FileResponse('index.html')

# =============================================================================
# КР 1, 1.4: GET /users (возврат данных пользователя)
# =============================================================================
@app.get("/users")
async def get_user():
    user = User(name="Andranik", id=1)
    return user

# =============================================================================
# КР 1, 2.1: POST /feedback (сбор отзывов)
# =============================================================================
@app.post("/feedback")
async def submit_feedback(feedback: Feedback):
    feedbacks.append(feedback)
    return {"message": f"Feedback received. Thank you, {feedback.name}."}

# =============================================================================
# КР 2, Задание 3.1: POST /create_user (валидация через Pydantic)
# =============================================================================
@app.post("/create_user")
async def create_user(user: UserCreate):
    # Валидация email и age (>0) уже выполнена моделью UserCreate
    return user

# =============================================================================
# КР 2, Задание 3.2: Работа с продуктами (поиск и получение по ID)
# =============================================================================
sample_products = [
    {"product_id": 123, "name": "Smartphone", "category": "Electronics", "price": 599.99},
    {"product_id": 456, "name": "Phone Case", "category": "Accessories", "price": 19.99},
    {"product_id": 789, "name": "Iphone", "category": "Electronics", "price": 1299.99},
    {"product_id": 101, "name": "Headphones", "category": "Accessories", "price": 99.99},
    {"product_id": 202, "name": "Smartwatch", "category": "Electronics", "price": 299.99}
]

@app.get("/products/search")
async def search_products(keyword: str, category: Optional[str] = None, limit: int = 10):
    results = [p for p in sample_products if keyword.lower() in p["name"].lower()]
    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]
    return results[:limit]

@app.get("/product/{product_id}")
async def get_product(product_id: int):
    for p in sample_products:
        if p["product_id"] == product_id:
            return p
    raise HTTPException(status_code=404, detail="Product not found")

# =============================================================================
# КР 2, Задания 5.1 – 5.3: Аутентификация и динамические сессии (itsdangerous)
# =============================================================================
SECRET_KEY = "super_secret_key_for_fastapi_control_work"
serializer = URLSafeSerializer(SECRET_KEY)

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    if not username or not password:
        raise HTTPException(status_code=400, detail="Username and password required")
    
    user_id = str(uuid.uuid4())
    timestamp = int(time.time())
    
    # Формат payload: <user_id>.<timestamp>
    # itsdangerous автоматически добавит .<signature>
    token_payload = f"{user_id}.{timestamp}"
    token = serializer.dumps(token_payload)
    
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=False,
        max_age=300,   # 5 минут
        samesite="lax"
    )
    return response

def verify_and_check_session(token: str) -> tuple[str, bool]:
    """Проверяет подпись, время и решает, нужно ли обновлять куку."""
    try:
        payload = serializer.loads(token)
    except (BadSignature, BadData):
        raise HTTPException(status_code=401, detail="Invalid session")
        
    if "." not in payload:
        raise HTTPException(status_code=401, detail="Invalid session format")
        
    user_id, ts_str = payload.rsplit(".", 1)
    try:
        last_activity = int(ts_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid session format")
        
    current_time = int(time.time())
    elapsed = current_time - last_activity
    
    # > 5 минут → сессия истекла
    if elapsed >= 300:
        raise HTTPException(status_code=401, detail="Session expired")
        
    # 3–5 минут → нужно продлить
    should_renew = 180 <= elapsed < 300
    return user_id, should_renew

@app.get("/user")
async def get_user_profile(request: Request, response: Response):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    user_id, should_renew = verify_and_check_session(token)
    
    if should_renew:
        new_timestamp = int(time.time())
        new_payload = f"{user_id}.{new_timestamp}"
        new_token = serializer.dumps(new_payload)
        response.set_cookie(
            key="session_token",
            value=new_token,
            httponly=True,
            secure=False,
            max_age=300,
            samesite="lax"
        )
        
    return {"user_id": user_id, "message": "Profile access granted"}

# =============================================================================
# КР 2, Задания 5.4 – 5.5: Работа с заголовками через Pydantic модель
# =============================================================================
@app.get("/headers")
async def get_headers(headers: CommonHeaders = Depends()):
    return {
        "User-Agent": headers.user_agent,
        "Accept-Language": headers.accept_language
    }

@app.get("/info")
async def get_info(headers: CommonHeaders = Depends(), response: Response = None):
    server_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    response.headers["X-Server-Time"] = server_time
    
    return {
        "message": "Добро пожаловать! Ваши заголовки успешно обработаны.",
        "headers": {
            "User-Agent": headers.user_agent,
            "Accept-Language": headers.accept_language
        }
    }
