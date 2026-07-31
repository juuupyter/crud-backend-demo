import fastapi
from pydantic import BaseModel 
from typing import Annotated

class Item(BaseModel):
    name: str
    description: str | None = None #optional 
    price: float 
    tax: float | None = None 

class User(BaseModel):
    username: str
    full_name: str | None

app = fastapi.FastAPI()
@app.get('/')
async def root():
    return {"message": 'hello world'}

item_data = []

@app.post('/items/{item_id}', status_code=fastapi.status.HTTP_201_CREATED)
async def create_item(item_id: int, item: Item):
    item_data.append(item.model_dump())
    results = {'item_id': item_id, 'item': item}
    return results

@app.get('/items/')
async def read_item(q: Annotated[int | None, fastapi.Query(le=5)] = None): #get requests will recieve a list of created items, with an optional query to display a specific item
    if q == None:
        return item_data
    else:
        return item_data[q-1]

@app.put('/items/{item_id}', status_code=fastapi.status.HTTP_202_ACCEPTED)
async def update_item(item_id: int, item: Item, user: User):
    results = {'item_id': item_id, 'item': item, 'user': user}
    return results

