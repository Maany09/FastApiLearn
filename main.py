from fastapi import Depends, FastAPI, Query, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime
from typing import Any, Annotated
from contextlib import asynccontextmanager

# Created campaign Model.
class Campaign(SQLModel, table=True):
    campaign_id: int | None= Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime
    created_at: datetime


# create database engine
sqlite_file_name = "campaigns.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}

engine = create_engine(sqlite_url, connect_args=connect_args)


# created database session
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


# created db and table, engine called
def create_db_tables():
    SQLModel.metadata.create_all(engine)

# created db tables on start
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()

    yield

app = FastAPI(root_path="/api/v1", lifespan=lifespan)


@app.get("/")
async def get_root():
    return {"message": "Hello World"}


@app.get("/campaigns")
async def get_campaigns(session: SessionDep):

    statement = select(Campaign)

    campaign = session.exec(statement).all()

    return {"message": "All campaigns fetched succesfully",
            "campaigns": campaign}


# get campaign by id
@app.get("/campaigns/{campaign_id}")
async def get_campaign_by_id(campaign_id: int, session: SessionDep):

    campaign_with_id = session.get(Campaign, campaign_id)

    if campaign_with_id["campaign_id"] != campaign_id:
        return {"No campaign with the id {campaign_id} is found"}
    else:
        return {"campaign by id": campaign_with_id}


# Get campaign by name
@app.get("/campaigns_by_name/{name}")
async def get_campaign_by_name(name: str, session: SessionDep):

    campaign_with_name = session.get(Campaign, name)

    if campaign_with_name["name"] != name:
        return {f"message": "No campaigns with the name - {name} is found"}
    else:
        return {"campaign by name": campaign_with_name}


# to add the campaign
@app.post("/campaigns")
async def create_campaigns(body: dict[str, Any], session: SessionDep):

    # will take name
    name = body.get("name")

    # checks for empty name 
    if name == None or name.strip() == "":
        return {"error : Name cant be empty"}

    # we dont give id manually because we have set campaign_id to Primary key which generates  id automatically and can also handle the uniqueness of the id assigned to the campaign.
    new_campaign = Campaign(
        name= name,
        due_date= datetime.now(),
        created_at= datetime.now()
    )

    # adding campaign to the databse
    session.add(new_campaign)

    # saving campaign
    session.commit()

    # refreshing and showing the generated campaign
    session.refresh(new_campaign)

    return {"message": "campaign creation - Success",
            "campaign": new_campaign}


# created put request for updating campaigns
@app.put("/campaigns/{campaign_id}")
async def update_existing_campaign(campaign_id: int, 
                                   body: dict[str, Any],
                                   session: SessionDep):

    # to find the existing campaign id
    campaign = session.get(Campaign, campaign_id)

    # check if campaign with entered id, exist or not
    if campaign == None:
        raise HTTPException(status_code=404,
                            detail="No campaign found")

    # if exist then it will take a new name
    name = body.get("name")

    # checks if name is empty
    if name == None or name.strip() == "":
        raise HTTPException(status_code=404,
                            detail="name cant be empty")

    # update the name
    campaign.name = name

    # it will save it to database
    session.commit()

    # it will refresh the updated campaign in database
    session.refresh(campaign)

    # it will show the updated database
    return {"message":"Campaign updation - successs", "campaign": campaign}


# created delete request
@app.delete("/campaigns/{campaign_id}")
async def delete_existing_campaign(campaign_id: int):

    for element in data:
        if element["campaign_id"] == campaign_id:


            # delete the given campaign by its campaign_id
            data.remove(element)

            return {"message": "campaign removed successfully","campaign": element}

    return {"error": "campaign does not exist"}

