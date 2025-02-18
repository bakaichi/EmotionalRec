from fastapi import FastAPI
from api.routes import router

app = FastAPI()

# Register API routes
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to EmotionalRec API"}

# Run with: uvicorn main:app --reload
