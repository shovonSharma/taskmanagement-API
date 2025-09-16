from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from database import engine, get_session
from models import Task, SQLModel

# Create tables
SQLModel.metadata.create_all(engine)

app = FastAPI()

# Create a new task
@app.post("/tasks/", response_model=Task)
def create_task(task: Task, session: Session = Depends(get_session)):
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# Get all tasks
@app.get("/tasks/", response_model=list[Task])
def get_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return tasks

# Get task by ID
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# Update task
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: Task, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = updated_task.title
    task.description = updated_task.description
    task.completed = updated_task.completed

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# Delete task
@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return {"message": "Task deleted successfully"}
