from fastapi import FastAPI
from datetime import datetime

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

@app.get("/campaigns/{campaign_id}")
async def get_campaign_by_id(campaign_id: int):

    for element in data:
        if element["campaign_id"] == campaign_id:
            return {"campaigns": element}
        else:
            return "No campaigns found"
        
@app.get("/campaigns/{name}")
async def get_campaign_by_name(name: str):
    for element in data:
        if element["name"] == name:
            return {f"campaigns with name {name}": element}
        else:
            return {f"no campaigns with name {name} is found."}