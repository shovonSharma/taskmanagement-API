from sqlmodel import create_engine, Session, SQLModel
from typing import Generator
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://myuser:mypassword@localhost:5432/mydb")

engine = create_engine(DATABASE_URL, echo=True)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


