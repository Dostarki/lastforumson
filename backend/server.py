import logging
import os
import httpx
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv(Path(__file__).parent / '.env')
from registry import router
from settings import public_config
from x_avatar import router as x_avatar_router
from avatar_provider import TIMEOUT, UA

logging.basicConfig(level=logging.INFO)
client = AsyncIOMotorClient(os.environ['MONGO_URL'])
db = client[os.environ['DB_NAME']]


@asynccontextmanager
async def lifespan(app):
    public_config()
    await db.agents.create_index('handle_key', unique=True)
    await db.agents.create_index('ref_code', unique=True)
    await db.agents.create_index('request_id', unique=True)
    await db.agents.create_index('created_at')
    await db.counters.create_index('name', unique=True)
    await db.counters.update_one({'name': 'agent_number'}, {'$setOnInsert': {'value': 0}}, upsert=True)
    app.state.db = db
    await db.x_avatar_metadata.create_index('handle', unique=True)
    await db.x_avatar_metadata.create_index('expires_at', expireAfterSeconds=0)
    app.state.x_http = httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False, headers={'User-Agent': UA})
    yield
    await app.state.x_http.aclose()
    client.close()


app = FastAPI(title='LastZhood Survivor Registry', lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ['CORS_ORIGINS'].split(','),
    allow_credentials=False,
    allow_methods=['GET', 'POST'],
    allow_headers=['Content-Type'],
)
app.include_router(router, prefix='/api')
app.include_router(x_avatar_router, prefix='/api')


@app.get('/api/')
async def root():
    return {'service': 'LastZhood Survivor Registry', 'status': 'online'}