from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Field, create_engine, Session, select
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional, List
import os
from dotenv import load_dotenv

# -----------------------------
# Config & Setup
# -----------------------------
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/mydb")
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

engine = create_engine(DATABASE_URL, echo=True)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# -----------------------------
# Models
# -----------------------------
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    completed: bool = Field(default=False)
    owner_id: int = Field(foreign_key="user.id")

SQLModel.metadata.create_all(engine)

# -----------------------------
# Helpers
# -----------------------------
def get_session():
    with Session(engine) as session:
        yield session

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise credentials_exception
    return user

# -----------------------------
# App & Endpoints
# -----------------------------
app = FastAPI(title="Minimal Task API")

@app.post("/register")
def register(username: str, password: str, session: Session = Depends(get_session)):
    if session.exec(select(User).where(User.username == username)).first():
        raise HTTPException(400, "Username already taken")
    user = User(username=username, hashed_password=get_password_hash(password))
    session.add(user)
    session.commit()
    return {"message": "User created"}

@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form.username)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(400, "Invalid username or password")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/tasks/")
def create_task(title: str, description: Optional[str] = None,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    task = Task(title=title, description=description, owner_id=current_user.id)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/", response_model=List[Task])
def list_tasks(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    return session.exec(select(Task).where(Task.owner_id == current_user.id)).all()

@app.put("/tasks/{task_id}")
def update_task(task_id: int, title: str, description: Optional[str] = None, completed: bool = False,
                current_user: User = Depends(get_current_user),
                session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(404, "Task not found")
    task.title, task.description, task.completed = title, description, completed
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(404, "Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}
