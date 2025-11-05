from pydantic import BaseModel, Field


class TermBase(BaseModel):
    term: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)


class TermCreate(TermBase):
    pass


class TermUpdate(BaseModel):
    description: str = Field(min_length=1)


class TermOut(BaseModel):
    id: int
    term: str
    description: str

    model_config = {
        "from_attributes": True,
    }

