import fastapi, os, passlib
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from contextlib import asynccontextmanager
from passlib.hash import pbkdf2_sha256


load_dotenv()
DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, fastapi.Depends(get_session)]

@asynccontextmanager 
async def lifespan(app: fastapi.FastAPI):
    #startup
    SQLModel.metadata.create_all(engine)
    yield
    #shutdown 

app = fastapi.FastAPI(lifespan=lifespan)

#basic layout for SQLModel classes and inheritance

class UserBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class User(UserBase, table=True): #inherits UserBase
    id: int | None = Field(default=None, primary_key=True)
    hashed_secret: str = Field()
    projects: list["Project"] = Relationship(back_populates="owner")

class UserPublic(UserBase):
    id: int #for the API

class UserCreate(UserBase):
    secret: str 

class UserUpdate(UserBase): #optional so a variable amount of fields can be updated in any request
    name: str | None = None
    age: int | None = None
    secret: str | None = None

#Users have projects which have tasks > create project class > create task class

class ProjectBase(SQLModel):
    name: str = Field(index=True)
    description: str | None 

class Project(ProjectBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int = Field(foreign_key="user.id") #sqlmodel will lowercase User > user by default. 
    owner: "User" = Relationship(back_populates="projects")
    tasks: list["Task"] = Relationship(back_populates='project')

class ProjectCreate(ProjectBase):
    pass

class ProjectPublic(ProjectBase):
    id: int
    owner_id: int 

#Tasks
class TaskBase(SQLModel):
    title: str = Field(index=True)
    done: bool = False 

class Task(TaskBase, table =True):
    id: int | None = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    project: Project = Relationship(back_populates="tasks")

class TaskCreate(TaskBase):
    pass

class TaskPublic(TaskBase):
    id: int 
    project_id: int 

def hash_secret(secret: str) -> str:
    hash = pbkdf2_sha256.hash(secret)
    return hash

@app.post('/users/', response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    hashed_secret = hash_secret(user.secret)
    extra_data = {'hashed_secret': hashed_secret}
    db_user = User.model_validate(user, update=extra_data) #Replace the secret field from UserCreate with User's hashed_secret field. 
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.get('/users/', response_model=list[UserPublic])
def read_users(session: SessionDep, offset: int = 0, limit: Annotated[int, fastapi.Query(le=100)] = 100):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users 

@app.patch('/users/', response_model=UserPublic)
def update_users(user_id: int, user: UserUpdate, session: SessionDep):
    db_user = session.get(User, user_id)
    if not db_user:
        raise fastapi.HTTPException(status_code=404, detail='User not found')
    user_data = user.model_dump(exclude_unset=True) #dont override unsent data with null values
    extra_data = {}
    if "secret" in user_data: 
        secret = user_data["secret"]
        hashed_secret = hash_secret(secret)
        extra_data['hashed_secret'] = hashed_secret
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.delete('/users/')
def delete_user(user_id: int, session: SessionDep):
    db_user = session.get(User, user_id)
    if not db_user:
        raise fastapi.HTTPException(status_code=404, detail='User not found')
    session.delete(db_user)
    session.commit()
    return {'ok': True}

#We set up project and task backpopulation from the User class > Make an API for accessing projects by user_id.

@app.post('/users/{user_id}/projects/', response_model=ProjectPublic)
def create_project(user_id: int, project: ProjectCreate, session: SessionDep):
    db_user = session.get(User, user_id)
    if not db_user:
        raise fastapi.HTTPException(status_code=404, detail='User not found')
    extra_data = {'owner_id': user_id}
    db_project = Project.model_validate(project, update=extra_data)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

#Now make an API for accessing the tasks of that project

@app.post('/projects/{project_id}/tasks/')
def create_task(project_id: int, task: TaskCreate, session: SessionDep):
    db_project = session.get(Project, project_id)
    if not db_project:
        raise fastapi.HTTPException(status_code=404, detail='Project not found')
    extra_data = {'project_id': project_id}
    db_task = Task.model_validate(task,update=extra_data)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@app.get('/users/{user_id}/tasks/', response_model=list[TaskPublic])
def read_user_tasks(user_id: int, session: SessionDep):
    statement = (select(Task)
                 .join(Project, Task.project_id == Project.id)
                 .where(Project.owner_id == user_id)
    )
    tasks = session.exec(statement).all()
    return tasks
