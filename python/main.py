import os
import logging
import pathlib
from fastapi import FastAPI, Form, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import sqlite3
import hashlib

app = FastAPI()
logger = logging.getLogger("uvicorn")
logger.level = logging.INFO
images = pathlib.Path(__file__).parent.resolve() / "images"
origins = [ os.environ.get('FRONT_URL', 'http://localhost:3000') ]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["*"],
)

# dict_factoryの定義
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.get("/")
def root():
    return {"message": "Hello, world!"}

@app.post("/items")
def add_item(name: str = Form(...),category: str = Form(...),image: UploadFile = File(...)):

    #-----------------jsonの時------------
    #jsonファイルをopen
    #with open('items.json','r',encoding='utf-8') as f:
    #    if len(f.readline())==0:
    #        items_json={"items" : []}
    #    #{"items": [{"name": "jacket", "category": "fashion"}, {"name": "jacket", "category": "fashion"},...]}
    #    #読み込み
    #    else:
    #        f.seek(0)
    #        items_json=json.load(f)
    #with open('items.json','w',encoding='utf-8') as f:
    #    item_new={"name": name, "category": category}
    #    items_json["items"].append(item_new)
    #    json.dump(items_json,f,indent=2)
    # ----------------jsonの時------------

    
    #.jpg(拡張子)を除いた部分をhash化
    image_name = image.filename.split('.')[0]
    image_extension = image.filename.split('.')[1]
    hashed_imagename = hashlib.sha256(image_name.encode()).hexdigest() + '.' + image_extension
    
    dbname = "../db/mercari.sqlite3"
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    sql="insert into items(name,category,image) values(?,?,?)"
    cur.execute(sql,[name,category,hashed_imagename])
    conn.commit()
    cur.close()
    conn.close()    

    logger.info(f"Receive item: name:{name} category:{category} image:{image}")
    return {"message": f"item received: name:{name} category:{category} image:{image}"}

@app.get("/items")
def get_item():
    '''#jsonファイルをopen
    with open('items.json','r',encoding='utf-8') as f:
            items = json.load(f)
    return items'''
    dbname = "../db/mercari.sqlite3"
    conn = sqlite3.connect(dbname)
    conn.row_factory = dict_factory #jsonの形
    cur = conn.cursor()
    sql="SELECT * FROM items"
    cur.execute(sql)
    items = cur.fetchall()
    cur.close()
    conn.close()
    return {"items":items}

@app.get("/search")
def get_search(keyword: str ):
    dbname = "../db/mercari.sqlite3"
    conn = sqlite3.connect(dbname)
    conn.row_factory = dict_factory #jsonの形
    cur = conn.cursor()
    sql = "select name,category from items where name like (?)" #keywordをnameに含む商品を探す
    cur.execute(sql,(f"%{keyword}%",))
    result = {"items" : cur.fetchall()}
    cur.close()
    conn.close()
    return result  

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
