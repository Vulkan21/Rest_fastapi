from sqlalchemy import Integer, String, Text, UniqueConstraint, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional

from .database import Base


class Term(Base):
    __tablename__ = "terms"
    __table_args__ = (
        UniqueConstraint("term", name="uq_terms_term"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    term: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[Optional[str]] = mapped_column(JSON, nullable=True, default=None)
    
    # Relationships for graph
    outgoing_relations: Mapped[list["TermRelation"]] = relationship(
        "TermRelation",
        foreign_keys="TermRelation.source_term_id",
        back_populates="source_term",
        cascade="all, delete-orphan"
    )
    incoming_relations: Mapped[list["TermRelation"]] = relationship(
        "TermRelation",
        foreign_keys="TermRelation.target_term_id",
        back_populates="target_term",
        cascade="all, delete-orphan"
    )


class TermRelation(Base):
    """
    Graph edges between terms (semantic relationships).
    Relation types: 'related', 'synonym', 'antonym', 'parent', 'child', 'example', 'reference'
    """
    __tablename__ = "term_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_term_id: Mapped[int] = mapped_column(Integer, ForeignKey("terms.id", ondelete="CASCADE"), nullable=False)
    target_term_id: Mapped[int] = mapped_column(Integer, ForeignKey("terms.id", ondelete="CASCADE"), nullable=False)
    relation_type: Mapped[str] = mapped_column(String(50), nullable=False, default="related")
    
    # Relationships
    source_term: Mapped["Term"] = relationship("Term", foreign_keys=[source_term_id], back_populates="outgoing_relations")
    target_term: Mapped["Term"] = relationship("Term", foreign_keys=[target_term_id], back_populates="incoming_relations")

