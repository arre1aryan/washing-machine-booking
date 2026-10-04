from fastapi import FastAPI

app = FastAPI(
    title="Washing Machine Booking - Auth Service",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}