from app.database import create_tables, drop_tables
from fastapi import FastAPI, Request, HTTPException, status
# internals
from app import views

app = FastAPI()


@app.get('/')
async def index(request: Request):
    return {
        'message': 'Welcome to news app!',
        "available paths": [
            {
                "news [GET, POST, PUT, DELETE]": f"{request.base_url}news/"
            },
            {
                "initdb [POST]": f"{request.base_url}initdb/"
            },
        ]
    }


@app.post('/initdb')
async def index():
    try:
        drop_tables()
        create_tables()
        return {"message": "Tables dropped and created!"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error {e}"
        )


app.include_router(views.router, prefix='/news', tags=['news'])
