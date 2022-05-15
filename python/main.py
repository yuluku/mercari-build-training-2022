import os
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "image"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...),category: str = Form(...)):
    #jsonファイルをopen
    with open('items.json','r',encoding='utf-8') as f:
        if len(f.readline())==0:
            items_json={"items" : []}
        #{"items": [{"name": "jacket", "category": "fashion"}, {"name": "jacket", "category": "fashion"},...]}
        #読み込み
        else:
            f.seek(0)
            items_json=json.load(f)
    with open('items.json','w',encoding='utf-8') as f:
        item_new={"name": name, "category": category}
        items_json["items"].append(item_new)
        json.dump(items_json,f,indent=2)
        

    logger.info(f"Receive item: {name}")
    return {"message": f"item received: {name}"}

@app.get("/items")
def get_item():
    #jsonファイルをopen
    with open('items.json','r',encoding='utf-8') as f:
            items = json.load(f)
    return items

@app.get("/image/{items_image}")
async def get_image(items_image):
    # Create image path
    image = images / items_image

    if not items_image.endswith(".jpg"):
        raise HTTPException(status_code=400, detail="Image path does not end with .jpg")

    if not image.exists():
        logger.debug(f"Image not found: {image}")
        image = images / "default.jpg"

    return FileResponse(image)
