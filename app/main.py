from fastapi import FastAPI
from .db import Base,engine
from .core.expectations import (
    app_error_handler,
    http_exception_handler,
    validation_exception_handler,
    global_exception_handler
)
from .core.errors import AppError
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI()

# Register exception handlers in order of specificity
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "FastAPI + Docker is working 🚀"}