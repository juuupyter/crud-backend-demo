## Basics:

```
  git commit -a 
  git push 
```
  Created the first file 'proj.py' on the repository.
```
  git checkout -b feature
```
Created the branch feature to test a new feature for 'proj.py'.
```
  git push --set-upstream origin feature
```
Created the upstream branch for feature.
```
  git add . 
  git push
```
Staged and pushed changes to the feature branch.
```
  git checkout main
```
Switch to the main branch before merging.
```
  git merge feature
  git push
```
Merged main with branch feature and pushed to add the changes. 
```
  git fetch origin main (from github.com/user/project)
  git merge origin/main
  git push origin main
```
Sync remote branches with local copies and merge them.   

  
## FastAPI:
```
app = FastAPI()
@app.get("/")
```
Sets the route to/from the dev server using a path operation.
```
async def root():
    return {'message': 'hello world'}
```
Asynchronous decorator function that will handle GET requests going to the path set above.
Following this the app can be deployed on FastAPI cloud. 

<img width="397" height="128" alt="195195" src="https://github.com/user-attachments/assets/236e5a6c-ada8-4173-a4be-fb0172977afd" />


```
  class Item(pydantic.BaseModel):
    name: str
    description: str | None
    price: float

  item_data = []
  @app.post('/items')
  async def create_item(item:Item):
    item_data.append(item.model_dump())
    return item
```
Using Pydantic for request body handling. When /items/ recieves a post request, we have the model_dump() function inherited from BaseModel save the created item data for use in the next function. 
```
  @app.get('/items/')
  async def read_items(q: Annotated[int | None, fastapi.Query(le=5)] = None):
    if q == None:
      return item_data
    else:
      return item_data[q]
```
Using typing's Annotated for clearer validation. Q is an optional query parameter that can be of type Int or None. These cases are handled below so that get requests either recieve a list of all created items, or a specific created item (q) from the last 5 items.  

