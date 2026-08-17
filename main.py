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
    
    campaigns = session.exec(statement).all()

    return {"message": "All campaigns fetched succesfully",
            "campaign": campaigns}


# get campaign by id
@app.get("/campaigns/{campaign_id}")
async def get_campaign_by_id(campaign_id: int, session: SessionDep):

    campaign_with_id = session.get(Campaign, campaign_id)

    if campaign_with_id == None:
        return {"message": "No campaign found"}

    return{"message": f"Campaign with the id {campaign_id} is found successfully","campaign": campaign_with_id}


# Get campaign by name
@app.get("/campaigns_by_name/{name}")
async def get_campaign_by_name(name: str, session: SessionDep):

    statement = select(Campaign).where(Campaign.name == name)

    campaign_by_name = session.exec(statement).all()

    if campaign_by_name == None:
        return {"message" : "No campaign found"}

    return {"message": f'Campaign with the name "{name}" is found successfully', "campaign" : campaign_by_name}


# to add the campaign
@app.post("/campaigns")
async def create_campaigns(body: dict[str, Any], session: SessionDep):

    # will take name
    name = body.get("name")

    # checks for empty name 
    if name == None or name.strip() == "":
        return {"error" : "Name cant be empty"}

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
            "campaign": {
                        "campaign_id": new_campaign.campaign_id,
                        "name": new_campaign.name,
                        "due_date": new_campaign.due_date,
                        "created_at": new_campaign.created_at
                        }
            }


# created put request for updating campaigns
@app.put("/campaigns_by_id/{campaign_id}")
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
    campaign_id = body.get("campaign_id")

    # checks if name is empty
    if name == None or name.strip() == "":
        raise HTTPException(status_code=404,
                            detail="name cant be empty")

    # update the name
    campaign.name = name
    campaign.campaign_id = campaign_id

    # it will save it to database
    session.commit()

    # it will refresh the updated campaign in database
    session.refresh(campaign)

    # it will show the updated campaign
    return {"message":"Campaign updation - successs", "campaign": campaign}


# created delete request (by id)
@app.delete("/campaigns/id/{campaign_id}")
async def delete_existing_campaign(campaign_id: int, session: SessionDep):

    # it retrieves the campaign id that matches with the input campaign id
    campaigns = session.get(Campaign, campaign_id)

    #  checks wether the id does not exist in database (Campaign)
    if campaigns == None:
        return {"message" : f"No campaigns with the id {campaign_id} is found"}

    # if id exist in database, then it will be deleted
    session.delete(campaigns)

    session.commit()

    # prints the deleted id
    return {"message": "Campaign deleted succesfully",
            "campaign": campaigns}


# created delete request (by name)
@app.delete("/campaigns/name/{name}")
async def delete_existing_campaign_by_name(name: str, session: SessionDep):

    # selected the name that matches with input name and finds from database
    statement = select(Campaign).where(Campaign.name == name)

    campaign_name = session.exec(statement).first()

    # checks that the name is not empty
    if campaign_name == None:
        raise HTTPException(status_code=404,detail="No name found to delete")

    # deletes the campaign found by name if name exist in database
    session.delete(campaign_name)

    session.commit()

    # prints the deleted campaign
    return {"message": f"Campaign by name {name} deleted successfully",
            "campaign": campaign_name }

