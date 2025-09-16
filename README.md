# taskmanagement-API

A simple **Task Management REST API** built with **FastAPI**, **PostgreSQL**, and **SQLModel**.  
Supports full CRUD operations: create, read, update, and delete tasks.  
This project demonstrates clean backend design and can be extended with authentication, user management, and deployment.

---

## Features
- ✅ FastAPI for RESTful APIs
- ✅ PostgreSQL for persistent storage
- ✅ SQLModel (SQLAlchemy + Pydantic hybrid)
- ✅ Dockerized for easy setup
- ✅ CRUD operations for tasks

---

## Tech Stack
- **Backend:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLModel
- **Containerization:** Docker

---

## Project Screenshot

![screenshot](https://github.com/shovonSharma/taskmanagement-API/blob/main/tx.jpg)

## API Endpoints
### Create a task
POST /tasks/
{
  "title": "Learn FastAPI",
  "description": "Build CRUD app",
  "completed": false
}

### Get all tasks
GET /tasks/

### Get a task by ID
GET /tasks/{task_id}

### Update a task
PUT /tasks/{task_id}

### Delete a task
DELETE /tasks/{task_id}
