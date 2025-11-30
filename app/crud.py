from typing import Optional, Sequence
import json

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models


def get_all_terms(db: Session) -> Sequence[models.Term]:
    stmt = select(models.Term).order_by(models.Term.term.asc())
    return db.execute(stmt).scalars().all()


def get_term_by_name(db: Session, term: str) -> Optional[models.Term]:
    stmt = select(models.Term).where(models.Term.term == term)
    return db.execute(stmt).scalar_one_or_none()


def get_term_by_id(db: Session, term_id: int) -> Optional[models.Term]:
    stmt = select(models.Term).where(models.Term.id == term_id)
    return db.execute(stmt).scalar_one_or_none()


def create_term(db: Session, term: str, description: str, sources: Optional[list[str]] = None) -> models.Term:
    sources_json = json.dumps(sources) if sources else None
    new_term = models.Term(term=term, description=description, sources=sources_json)
    db.add(new_term)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(new_term)
    return new_term


def update_term_description(db: Session, term: str, description: Optional[str] = None, sources: Optional[list[str]] = None) -> Optional[models.Term]:
    existing = get_term_by_name(db, term)
    if existing is None:
        return None
    if description is not None:
        existing.description = description
    if sources is not None:
        existing.sources = json.dumps(sources)
    db.commit()
    db.refresh(existing)
    return existing


def delete_term(db: Session, term: str) -> bool:
    existing = get_term_by_name(db, term)
    if existing is None:
        return False
    db.delete(existing)
    db.commit()
    return True


# ===== Graph/Relations CRUD =====

def get_all_relations(db: Session) -> Sequence[models.TermRelation]:
    stmt = select(models.TermRelation)
    return db.execute(stmt).scalars().all()


def create_relation(db: Session, source_term_name: str, target_term_name: str, relation_type: str = "related") -> Optional[models.TermRelation]:
    source = get_term_by_name(db, source_term_name)
    target = get_term_by_name(db, target_term_name)
    
    if source is None or target is None:
        return None
    
    new_relation = models.TermRelation(
        source_term_id=source.id,
        target_term_id=target.id,
        relation_type=relation_type
    )
    db.add(new_relation)
    db.commit()
    db.refresh(new_relation)
    return new_relation


def delete_relation(db: Session, relation_id: int) -> bool:
    stmt = select(models.TermRelation).where(models.TermRelation.id == relation_id)
    relation = db.execute(stmt).scalar_one_or_none()
    if relation is None:
        return False
    db.delete(relation)
    db.commit()
    return True

