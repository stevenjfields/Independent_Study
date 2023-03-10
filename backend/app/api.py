
from fastapi import FastAPI
from typing import List
import requests
import json

from .constants import BASE_WORKS_URL, WORKS_ID_FILTER
from .models import Article, WeightedEdge
from .helpers import parse_article, create_embeddings, get_similarities

app = FastAPI()

@app.get("/paper/{work_id}/")
async def get_paper(work_id: str) -> Article:
    req = requests.get(BASE_WORKS_URL + f"/{work_id}")
    res = json.loads(req.content)
    article = parse_article(res)
    return article

@app.post("/references/")
async def get_references(parent: Article) -> List[Article]:
    references = []
    if len(parent.references) > 0:
        queries = parent.fetch_references_queries()
    else:
        queries = parent.fetch_related_queries()
            
    for query in queries:
        req = requests.get(BASE_WORKS_URL + WORKS_ID_FILTER + query)
        res = json.loads(req.content)
        
        refs = [parse_article(result) for result in res["results"]]
        references.extend(refs)
    return references

@app.post("/embeddings/")
async def embeddings(articles: List[Article]) -> dict:
    try:
        create_embeddings(articles)
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
    
    return {
        "status": "complete",
        "error": ""
    }

@app.post("/similarities/")
async def similarities(target: Article, sources: List[Article]) -> List[WeightedEdge]:
    try:
        sims = get_similarities(target, sources)
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }
    return sims
