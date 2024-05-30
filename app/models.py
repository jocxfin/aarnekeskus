from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class FeedItem(Base):
    __tablename__ = "feed_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    link = Column(String)
    pub_date = Column(DateTime)
    category = Column(String)
    city = Column(String)