from fastapi import Depends, FastAPI, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime
import random
from typing import Any, Annotated

# Created campaign Model.
class Campaign(SQLModel, table=True):
    campaign_id: int | None= Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime
    created_at: datetime

app = FastAPI(root_path="/api/v1")

@app.get("/")
async def get_root():
    return {"message": "Hello World"}

# added mock data(no db)

data = [
     {
        "campaign_id": 1,
        "name": "Sam Altman",
        "due_date": datetime.now(),
        "created_at": datetime.now()     
    },

    {
        "campaign_id": 2,
        "name": "Zuck Duffy",
        "due_date": datetime.now(),
        "created_at": datetime.now()
    }
]

"""
Campaigns
- campaign_id
- name
- due_date
- created_at
"""


@app.get("/campaigns")
async def get_campaigns():
    return {"campaigns": data}


# get campaign by id
@app.get("/campaigns/{campaign_id}")
async def get_campaign_by_id(campaign_id: int):

    for element in data:
        if element["campaign_id"] == campaign_id:
            return {"campaigns": element}
        else:
            return "No campaigns found"

# Get campaign by name
@app.get("/campaigns_by_name/{name}")
async def get_campaign_by_name(name: str):
    for elements in data:

        if elements["name"] == name:
            return {f"Campaigns by name {name}": elements}
        
    return {f'no campaigns with name "{name}" is found.'}


@app.post("/campaigns")
async def create_campaigns(body: dict[str, Any]):

    # will take name and campaign_id
    name = body.get("name")
    campaign_id = body.get("campaign_id")

    # checks for empty name 
    if name == None or name.strip() == "":
        return {"error : Name cant be empty"}
    
    # if id empty, it will generate a random num
    if campaign_id == None:
        campaign_id = random.randint(20,1000)

    # checks if id already exist in data
    for campaign in data:
        if campaign["campaign_id"] == campaign_id:
            return{"This campaign already exist."}

    new_campaign = {
                "campaign_id": campaign_id,
                "name": name,
                "due_date": datetime.now(),
                "created_at": datetime.now()
                }

    data.append(new_campaign)

    return {"Campaigns": new_campaign}

# created put request for updating campaigns
@app.put("/campaigns/{campaign_id}")
async def update_existing_campaign(campaign_id: int, body: dict[str, Any]):
    

    for element in data:
        if element["campaign_id"] == campaign_id:

            # add the updated name and campaign id
            name = body.get("name")
            campaign_id = body.get("campaign_id")

            # checks if name or id is not empty
            if name == None or name.strip == "":
                return {"error": "Name cant be empty"}

            if campaign_id == None:
                return {"error": "id cant be empty"}

            # Updates the mock data
            element["name"] = name
            element["campaign_id"] = campaign_id


            # gives the updated campaign on screen
            return {"Message": "Campaign Updated - Success",
                    "campaign": element}

    return {"error" : "campaign not found"}


# created delete request
@app.delete("/campaigns/{campaign_id}")
async def delete_existing_campaign(campaign_id: int):

    for element in data:
        if element["campaign_id"] == campaign_id:


            # delete the given campaign by its campaign_id
            data.remove(element)

            return {"message": "campaign removed successfully","campaign": element}

    return {"error": "campaign does not exist"}

