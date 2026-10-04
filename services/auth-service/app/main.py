from fastapi import FastAPI

from app.api.auth import router as auth_router


app = FastAPI(
    title="Washing Machine Booking - Auth Service",
    version="1.0.0",
)

app.include_router(auth_router)


@app.get("/health")
def health_check():
    return {"status": "healthy"}