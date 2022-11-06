# COMMAND TO RUN:
# uvicorn fastapi_app.fastapp:app --reload
import json

from fastapi import FastAPI, Depends, Query, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import os

from fastapi_app.utils.output_tools import json2html
from fastapi_app.utils.process import get_result

BUCKET_NAME = "hack-bucket"


class User(BaseModel):
    name: str
    token: str = None
    is_admin: bool = False
    role: Optional[str] = None


class APIQueryParams:
    def __init__(self,
                 user_id: str = Query(..., example=0, description="ID пользователя"),
                 user_file: str = Query(..., description="Файл сметы (путь к загруженному файлу)"),
                 sheet_number: int = Query(0, description="Порядковый номер листа со сметой (по умолчанию = 0)"),
                 reference: str = Query(..., example="КПГЗ", description="Справочник для сопоставления [КПГЗ, ТЗ]"),
                 user_address: Optional[str] = Query(None, description="Адрес проведения работ"),
                 address: bool = Query(True, description="Искать адрес в смете"),
                 save_data: bool = Query(False, description="Сохранить загруженную смету и результат"),
                 return_html: bool = Query(False, description="Вернуть результат в виде html")
                 ):
        self.user_id = user_id
        self.user_file = user_file
        self.sheet_number = sheet_number
        self.reference = reference
        self.user_address = user_address
        self.address = address
        self.save_data = save_data
        self.html = return_html


app = FastAPI()
templates = Jinja2Templates(directory="fastapi_app/templates")
app.mount("/static", StaticFiles(directory='fastapi_app/static'), name='static')


@app.get('/healthcheck', status_code=200)
async def healthcheck():
    return 'The app is running and healthy'


@app.get("/")
async def root():
    body = """<html>
           <body style='padding: 10px;'>
           <h1>FastAPI</h1>
           <div>
           Example of usage: <a href='/healthcheck</a>
           </div>
           </body>
           </html>"""

    return HTMLResponse(content=body)


@app.get('/process_xls/{user_id}')
async def get_all_results(params: APIQueryParams = Depends()):
    """
    This endpoint is used to get all the results of the pipeline
    """
    config = {"user_id": params.user_id,
              "user_file": params.user_file,
              "sheet_number": params.sheet_number,
              "user_address": params.user_address,
              "address": params.address,
              "reference": params.reference,
              "save_data": params.save_data
              }

    result = get_result(config)
    result = json2html(json_file=result) if params.html else result
    return HTMLResponse(content=result)


@app.post("/file_upload")
async def upload_file_locally(file: UploadFile = File(..., description="Загружаемый файл")):
    try:
        try:
            contents = file.file.read()
        except Exception as e:
            return {"error": f"[{type(e)}] {e}"}
        finally:
            file.file.close()

        file_path = f"./temp_data/{file.filename}"
        if os.path.exists(file_path):
            with open(file_path, "wb") as writer:
                writer.write(contents)
        else:
            return {"error": f"[PathError] Path doesn't exist"}

    except Exception as e:
        return {"error": f"[{type(e)}] {e}"}

    return {"FileName": file.filename, "FilePath": f"{file_path}"}


@app.get("/file_download")
async def download_file_locally(file_path: str = Query(..., description="Путь к скачиваемому файлу")):
    return FileResponse(path=file_path, filename=file_path, media_type='json/application')


