from pydantic import BaseModel, Field


class NewsSchema(BaseModel):
    created_by: str = Field(..., min_length=3, max_length=140)
    context: str = Field(..., min_length=3, max_length=4096)
    published_date: str = Field(..., min_length=3, max_length=32)


class NewsDB(NewsSchema):
    id: int
