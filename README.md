# FastAPI news app CRUD operations with raw SQL

## install
```bash
cd news_fastapi
# create virtual environment
python3.11 -m venv venv
# activate venv
source venv/bin/activate
# install packages
pip install -r requirements.txt
# copy .env file
cp .env.example .env
# edit .env file by your credentials

# 1. create your database in the postgresql
# CREATE DATABASE db_news;
# ALTER DATABASE db_news OWNER TO <your-user>
# Test database
# CREATE DATABASE db_test_news;
# ALTER DATABASE db_test_news OWNER TO <your-user>
# Create Tables
curl -X POST http://0.0.0.0:8000/initdb
```
## Run
```bash
uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 8000
```

## OpenAPI/Swagger
- http://0.0.0.0:8000/docs

## Run Tests
```bash
$ pytest -s --disable-warnings

# Expected Output
===================================================== test session starts =====================================================
platform darwin -- Python 3.11.0, pytest-7.4.0, pluggy-1.2.0
rootdir: /Users/dev/webdev/projects/news_fastapi
plugins: anyio-3.7.0
collecting ... Tables are dropped...
Tables are created successfully...
collected 14 items                                                                                                            

tests/test_views.py ..............

=============================================== 14 passed, 9 warnings in 0.22s ================================================

```
