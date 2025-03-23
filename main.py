from fastapi import FastAPI
from api.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# this is used to bypass a bug of frontend not being able to cross-communicate with backend as they're running on 2 separate ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # bypass to allow requests from frontend hosted on port 3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to EmotionalRec API"}

# Run with: uvicorn main:app --reload
