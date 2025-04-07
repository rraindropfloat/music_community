from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from datetime import timedelta
from typing import Annotated

from app import models, schemas
from app.api.endpoints import auth
from app.db.session import SessionLocal, engine
from app.core.config import settings
from app.db.session import get_db,Session

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="音乐社区API",
    description="一个音乐爱好者交流的社区平台",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





# 登录接口
@app.post("/api/auth/login", response_model=schemas.Token)
async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[SessionLocal, Depends(get_db)]
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_info": {
            "username": user.username,
            "email": user.email
        }
    }


# 获取当前用户信息
@app.get("/api/users/me", response_model=schemas.User)
async def read_users_me(
        current_user: Annotated[schemas.User, Depends(auth.get_current_active_user)]
):
    return current_user

# 在登录接口之后添加以下路由
@app.post("/api/auth/register", response_model=schemas.User)
async def user_register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    return auth.register_user(db, user)