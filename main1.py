from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI()

class Book(BaseModel):
    id:int
    title:str
    author:str
    year:int

books_db=[
    {
        "id":1,
        "title":"GITA",
        "author":"MAHADEV",
        "year":0
    },
    {
        "id":2,
        "title":"RAMAYANA",
        "author":"KRISHNA",
        "year":0
    }
]

@app.get("/books")
def get_books():
    return books_db   # {"msg":"HAR HAR MAHADEV"}
    
# R
@app.get("/books/{book_id}")
def get_book(book_id:int):
    for book in books_db:
        if book["id"]==book_id:
            return book
            
    return {"error":"book not found"}
    
# C
@app.post("/books")
def create_book(book:Book):
    books_db.append(book.model_dump())
    return book
    
# U
@app.put("/books/{book_id}")
def update_book(book_id:int,updated_book:Book):
    for index,book in enumerate(books_db):
        if book["id"]==book_id:
            books_db[index]=updated_book.model_dump()
            return updated_book
            
    return {"error":"book not found"}
            
# D
@app.delete("/books/{book_id}")
def delete_book(book_id:int):
    for index,book in enumerate(books_db):
        if book["id"]==book_id:
            deleted=books_db.pop(index)
            return {"message":"Book DELETED","book":deleted}
    
    return {"error":"book not found"}
            