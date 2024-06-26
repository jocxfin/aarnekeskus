from fastapi import FastAPI, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import feedparser
import datetime
from . import crud, models, schemas
from .database import SessionLocal, init_db
import asyncio

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

category_translation = {
    "traffic": "Tieliikenneonnettomuus",
    "fire": "Tulipalo",
    "alarm": "Palohälytys",
    "wildfire": "Maastopalo",
    "smoke": "Savuhavainto",
    "spill": "Öljyvahinko",
    "animal_rescue": "Eläimen pelastaminen",
    "human_rescue": "Ihmisen pelastaminen",
    "damage_control": "Vahingontorjunta",
    "other": "Muu"
}

@app.on_event("startup")
async def on_startup():
    init_db()
    asyncio.create_task(update_feed_periodically())

async def update_feed_periodically():
    while True:
        await update_feed()
        await asyncio.sleep(30)  # 30 sekunnin välein

async def update_feed():
    db = SessionLocal()
    try:
        feed = feedparser.parse('https://www.peto-media.fi/tiedotteet/rss.xml')
        for entry in feed.entries:
            pub_date = datetime.datetime(*entry.published_parsed[:6])
            category = "other"
            if "tieliikenneonnettomuus" in entry.title:
                category = "traffic"
            elif "rakennuspalo" in entry.title or "liikennevälinepalo" in entry.title:
                category = "fire"
            elif "tulipalo" in entry.title:
                category = "fire"
            elif "palohälytys" in entry.title:
                category = "alarm"
            elif "maastopalo" in entry.title:
                category = "wildfire"
            elif "savuhavainto" in entry.title:
                category = "smoke"
            elif "öljyvah." in entry.title or "ymp.onnet." in entry.title:
                category = "spill"
            elif "eläimen pelastaminen" in entry.title:
                category = "animal_rescue"
            elif "ihmisen pelastaminen" in entry.title:
                category = "human_rescue"
            elif "vahingontorjunta" in entry.title:
                category = "damage_control"
            
            existing_item = crud.get_feed_item_by_title_and_date(db, entry.title, pub_date)
            if not existing_item:
                db_item = schemas.FeedItemCreate(
                    title=entry.title,
                    description=entry.description,
                    link=entry.link,
                    pub_date=pub_date,
                    category=category,
                    city=entry.title.split("/")[0].strip()
                )
                crud.create_feed_item(db, db_item)
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def read_feed(
    request: Request,
    categories: list[str] = Query(default=[]),
    city: str = Query(default=""),
    db: Session = Depends(get_db)
):
    items = crud.get_feed_items(db, categories, city)
    categories_in_db = crud.get_categories(db)
    cities_in_db = crud.get_cities(db)
    
    translated_categories = [(cat[0], category_translation.get(cat[0], cat[0])) for cat in categories_in_db]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "items": items,
        "categories": translated_categories,
        "cities": cities_in_db,
        "selected_categories": categories,
        "selected_city": city
    })
