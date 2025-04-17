from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from news_fetcher import fetch_news_for_category, FEEDS

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "categories": FEEDS.keys()
    })

@app.get("/news/{category}")
async def get_news(category: str, request: Request):
    if category not in FEEDS:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "message": "Invalid category",
            "categories": FEEDS.keys()
        })

    # Pass category instead of feed_url, assuming fetch_news_for_category internally uses FEEDS[category]
    news_items = fetch_news_for_category(category)

    return templates.TemplateResponse("news.html", {
        "request": request,
        "category": category,
        "news": news_items,
        "categories": FEEDS.keys()
    })
