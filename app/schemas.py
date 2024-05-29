from pydantic import BaseModel
from datetime import datetime

class FeedItemBase(BaseModel):
    title: str
    description: str
    link: str
    pub_date: datetime
    category: str
    city: str

class FeedItemCreate(FeedItemBase):
    pass

class FeedItem(FeedItemBase):
    id: int

    class Config:
        from_attributes = True
