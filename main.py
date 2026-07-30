import fastapi
from pydantic import BaseModel 
from typing import Annotated

class Item(BaseModel):
    name: str
    description: str | None = None #optional 
    price: float 
    tax: float | None = None 

app = fastapi.FastAPI()
@app.get('/')
async def root():
    return {"message": 'hello world'}

item_data = []

@app.post('/items/')
async def create_item(item: Item):
    item_data.append(item.model_dump())
    return item

@app.get('/items/')
async def read_item(q: Annotated[int | None, fastapi.Query(le=5)] = None): #get requests will recieve a list of created items, with an optional query to display a specific item
    if q == None:
        return item_data
    else:
        return item_data[q-1]