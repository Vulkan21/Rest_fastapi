from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import json
import os
from pathlib import Path

from .database import SessionLocal, engine, Base
from . import crud, schemas

app = FastAPI(title="Glossary MindMap API", version="2.0.0", description="API for glossary terms with semantic graph visualization")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# Create tables automatically on startup
@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


# Serve frontend
@app.get("/")
async def serve_frontend():
    """Serve the frontend MindMap visualization"""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Frontend not found. Access API docs at /docs"}


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ===== TERM ENDPOINTS =====

@app.get("/terms", response_model=list[schemas.TermOut])
def list_terms(db: Session = Depends(get_db)):
    """Get all glossary terms"""
    terms = crud.get_all_terms(db)
    # Parse JSON sources
    for term in terms:
        if term.sources:
            term.sources = json.loads(term.sources) if isinstance(term.sources, str) else term.sources
    return terms


@app.get("/terms/{term}", response_model=schemas.TermOut)
def get_term(term: str, db: Session = Depends(get_db)):
    """Get a specific term by name"""
    item = crud.get_term_by_name(db, term)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
    # Parse JSON sources
    if item.sources:
        item.sources = json.loads(item.sources) if isinstance(item.sources, str) else item.sources
    return item


@app.post("/terms", response_model=schemas.TermOut, status_code=status.HTTP_201_CREATED)
def create_term(payload: schemas.TermCreate, db: Session = Depends(get_db)):
    """Create a new term"""
    try:
        created = crud.create_term(db, term=payload.term, description=payload.description, sources=payload.sources)
        if created.sources:
            created.sources = json.loads(created.sources) if isinstance(created.sources, str) else created.sources
        return created
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Term already exists")


@app.put("/terms/{term}", response_model=schemas.TermOut)
def update_term(term: str, payload: schemas.TermUpdate, db: Session = Depends(get_db)):
    """Update an existing term"""
    updated = crud.update_term_description(db, term=term, description=payload.description, sources=payload.sources)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
    if updated.sources:
        updated.sources = json.loads(updated.sources) if isinstance(updated.sources, str) else updated.sources
    return updated


@app.delete("/terms/{term}", status_code=status.HTTP_204_NO_CONTENT)
def delete_term(term: str, db: Session = Depends(get_db)):
    """Delete a term"""
    ok = crud.delete_term(db, term)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Term not found")
    return None


# ===== GRAPH/RELATION ENDPOINTS =====

@app.get("/relations", response_model=list[schemas.RelationOut])
def list_relations(db: Session = Depends(get_db)):
    """Get all term relations (graph edges)"""
    return crud.get_all_relations(db)


@app.post("/relations", response_model=schemas.RelationOut, status_code=status.HTTP_201_CREATED)
def create_relation(payload: schemas.RelationCreate, db: Session = Depends(get_db)):
    """Create a relation between two terms"""
    relation = crud.create_relation(
        db,
        source_term_name=payload.source_term,
        target_term_name=payload.target_term,
        relation_type=payload.relation_type
    )
    if relation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="One or both terms not found")
    return relation


@app.delete("/relations/{relation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_relation(relation_id: int, db: Session = Depends(get_db)):
    """Delete a relation"""
    ok = crud.delete_relation(db, relation_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Relation not found")
    return None


@app.get("/graph", response_model=schemas.GraphData)
def get_graph(db: Session = Depends(get_db)):
    """Get full semantic graph (nodes and edges) for visualization"""
    terms = crud.get_all_terms(db)
    relations = crud.get_all_relations(db)
    
    nodes = []
    for term in terms:
        sources = None
        if term.sources:
            sources = json.loads(term.sources) if isinstance(term.sources, str) else term.sources
        nodes.append(schemas.GraphNode(
            id=term.id,
            label=term.term,
            description=term.description,
            sources=sources
        ))
    
    edges = [
        schemas.GraphEdge(
            id=rel.id,
            from_id=rel.source_term_id,
            to_id=rel.target_term_id,
            type=rel.relation_type
        )
        for rel in relations
    ]
    
    return schemas.GraphData(nodes=nodes, edges=edges)

