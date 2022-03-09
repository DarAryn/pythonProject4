import typing
from databases import Database
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float

DATABASE_URL = "sqlite:///sneakers.db"
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL)
meta = MetaData()

sneakers = Table(
    "sneakers",
    meta,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("count", Integer),
    Column("manufacture", String),
    Column("price", Float),
    Column("size", Float),
)

meta.create_all(engine)

class Item(BaseModel):
    id: int
    name: str
    count: int
    manufacture: str
    price: float
    size: float

class ItemIn(BaseModel):
    name: str
    count: int
    manufacture: str
    price: float
    size: float

app = FastAPI()

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.post("/item/", response_model=ItemIn)
async def add_sneakers(i: ItemIn):
    query = sneakers.insert().values(name=i.name,
                                     count=i.count,
                                     manufacture=i.manufacture,
                                     price=i.price,
                                     size=i.size)
    last_record_id = await database.execute(query)
    return {**i.dict(), "id": last_record_id}

@app.get('/item/', response_model=typing.List[Item])
async def view_all():
    query = sneakers.select()
    return await database.fetch_all(query)

@app.delete("/item/{item_id}")
async def delete_sneakers(item_id: int):
    query = sneakers.delete().where(sneakers.columns.id == item_id)
    await database.execute(query)
    return {"detail": "Item deleted"}
