import json
import config
from fastapi import FastAPI
from pymongo import MongoClient
from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

client = MongoClient()

db = client[config.DBNAME]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/api/company/{cik}')
async def getCompanyData(cik):
    try:
        return JSONResponse(content=db['company_data'].find_one({'cik' : cik})['data'])
    except:
        return JSONResponse(content={},status_code=status.HTTP_404_NOT_FOUND)