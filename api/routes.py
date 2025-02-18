from fastapi import APIRouter, Query, HTTPException

router = APIRouter()

@router.get("/health", summary="Health Check")
def health_check():
    """Simple health check endpoint to verify the API is running."""
    return {"status": "ok"}
