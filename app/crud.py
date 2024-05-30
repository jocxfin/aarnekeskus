from sqlalchemy.orm import Session
from . import models, schemas

def get_feed_items(db: Session, categories: list[str], city: str):
    query = db.query(models.FeedItem)
    if categories:
        query = query.filter(models.FeedItem.category.in_(categories))
    if city:
        query = query.filter(models.FeedItem.city == city)
    return query.all()

def create_feed_item(db: Session, feed_item: schemas.FeedItemCreate):
    db_feed_item = models.FeedItem(**feed_item.dict())
    db.add(db_feed_item)
    db.commit()
    db.refresh(db_feed_item)
    return db_feed_item

def get_categories(db: Session):
    return db.query(models.FeedItem.category).distinct().all()

def get_cities(db: Session):
    return db.query(models.FeedItem.city).distinct().all()