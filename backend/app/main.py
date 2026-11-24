from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine
import app.models  # noqa: F401  (registers tables)
from app.routes import imports, matches, matchups, players, rankings, stats, teams


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="AiCric API", version="0.4.0", lifespan=lifespan)
app.include_router(teams.router)
app.include_router(players.router)
app.include_router(matches.router)
app.include_router(imports.router)
app.include_router(stats.router)
app.include_router(rankings.router)
app.include_router(matchups.router)


@app.get("/health")
def health():
    return {"status": "ok"}
