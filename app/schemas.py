from pydantic import BaseModel, Field
from typing import Optional


class TermBase(BaseModel):
    term: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    sources: Optional[list[str]] = Field(default=None, description="List of source URLs or references")


class TermCreate(TermBase):
    pass


class TermUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=1)
    sources: Optional[list[str]] = None


class TermOut(BaseModel):
    id: int
    term: str
    description: str
    sources: Optional[list[str]] = None

    model_config = {
        "from_attributes": True,
    }


# Graph/Relation schemas
class RelationCreate(BaseModel):
    source_term: str = Field(description="Source term name")
    target_term: str = Field(description="Target term name")
    relation_type: str = Field(default="related", description="Type: related, synonym, antonym, parent, child, example, reference")


class RelationOut(BaseModel):
    id: int
    source_term_id: int
    target_term_id: int
    relation_type: str

    model_config = {
        "from_attributes": True,
    }


class GraphNode(BaseModel):
    id: int
    label: str
    description: str
    sources: Optional[list[str]] = None


class GraphEdge(BaseModel):
    id: int
    from_id: int
    to_id: int
    type: str


class GraphData(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]

