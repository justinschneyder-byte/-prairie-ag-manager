from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .config import get_settings
from .database import Base, SessionLocal, engine
from .routers import blue_book, chat, crops, data, fields, inputs, machines, maintenance, sprays, weather

settings = get_settings()

app = FastAPI(title="Prairie Ag Manager API")

origins = ["*"] if settings.cors_origins == "*" else [o.strip() for o in settings.cors_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Farm).first() is None:
            db.add(models.Farm())
            db.commit()
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(fields.router)
app.include_router(machines.router)
app.include_router(crops.router)
app.include_router(inputs.router)
app.include_router(sprays.router)
app.include_router(maintenance.router)
for w_router in weather.routers:
    app.include_router(w_router)
app.include_router(chat.router)
app.include_router(data.router)
app.include_router(blue_book.router)
