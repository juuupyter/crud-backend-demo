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

[example](https://raw.githubusercontent.com/juuupyter/project1/refs/heads/main/images/195195.png)
