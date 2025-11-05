from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .database import SessionLocal, engine, Base
from . import crud, schemas

app = FastAPI(title="Glossary API", version="1.0.0")


# Create tables automatically on startup
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/terms", response_model=list[schemas.TermOut])
def list_terms(db: Session = Depends(get_db)):
    return crud.get_all_terms(db)


@app.get("/terms/{term}", response_model=schemas.TermOut)
def get_term(term: str, db: Session = Depends(get_db)):
    item = crud.get_term_by_name(db, term)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
    return item


@app.post("/terms", response_model=schemas.TermOut, status_code=status.HTTP_201_CREATED)
def create_term(payload: schemas.TermCreate, db: Session = Depends(get_db)):
    try:
        created = crud.create_term(db, term=payload.term, description=payload.description)
        return created
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Term already exists")


@app.put("/terms/{term}", response_model=schemas.TermOut)
def update_term(term: str, payload: schemas.TermUpdate, db: Session = Depends(get_db)):
    updated = crud.update_term_description(db, term=term, description=payload.description)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
    return updated


@app.delete("/terms/{term}", status_code=status.HTTP_204_NO_CONTENT)
def delete_term(term: str, db: Session = Depends(get_db)):
    ok = crud.delete_term(db, term)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
    return None

