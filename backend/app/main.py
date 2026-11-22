from fastapi import FastAPI
from app.database import Base, engine
import app.models  # noqa: F401  (registers tables)

app = FastAPI(title="CRICKET-IQ API", version="0.1.0")


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}
