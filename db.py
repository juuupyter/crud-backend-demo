import fastapi, os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Annotated
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager
from pathlib import Path


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

class UserBase(SQLModel, table=True):
    name: str = Field(index=True)
    age: int | None = Field(default=None, index=True)

class User(UserBase, table=True): #inherits UserBase
    id: int | None = Field(default=None, primary_key=True)
    secret: str

class UserPublic(UserBase):
    id: int #for the API

class UserCreate(UserBase):
    secret: str 

class UserUpdate(UserBase): #optional so a variable amount of fields can be updated in any request
    name: str | None = None
    age: int | None = None
    secret: str | None = None


@app.post('/users/', response_model=UserPublic)
def create_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.get('/users/', response_model=list[UserPublic])
def read_users(session: SessionDep, offset: int = 0, limit: Annotated[int, fastapi.Query(le=100)] = 100):
    users = session.exec(select(UserBase).offset(offset).limit(limit)).all()
    return users 

@app.patch('/users', response_model=UserPublic)
def update_users(user_id: int, user: UserUpdate, session: SessionDep):
    db_user = session.get(User, user_id)
    if not db_user:
        raise fastapi.HTTPException(status_code=404, detail='User not found')
    user_data = user.model_dump(exclude_unset=True) #dont override unsent data with null values
    db_user.sqlmodel_update(user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.delete('/users')
def delete_user(user_id: int, session: SessionDep):
    user = session.get(UserBase, user_id)
    if not user:
        raise fastapi.HTTPException(status_code=404, detail='User not found')
    session.delete(user)
    session.commit
    return {'ok': True}

