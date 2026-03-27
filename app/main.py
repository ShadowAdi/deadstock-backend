from fastapi import FastAPI
from .db import Base,engine
app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "FastAPI + Docker is working 🚀"}