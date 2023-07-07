import os
import json
from fastapi import status
from fastapi.testclient import TestClient
from datetime import datetime as dt
import pytest
#  internals
from app.main import app
from app.database import create_tables, insert_t_news, drop_tables
from app import models

client = TestClient(app)


#  use test database and create tables
os.environ["DB_NAME"] = "db_test_news"
drop_tables()
create_tables()


#  test functions that will detect by pytest

def test_read_news():
    response = client.get("/news")
    assert response.status_code == status.HTTP_200_OK


def test_create_news():
    payload = {
        'created_by': 'adnankaya', 'context': 'contex1', 'published_date': '05-23-2023 15:15:19'
    }
    expected = {
        'id': 1,
        'created_by': 'adnankaya', 'context': 'contex1', 'published_date': '2023-05-23 15:15:19+03:00'
    }

    response = client.post('/news/', data=json.dumps(payload))
    assert response.status_code == status.HTTP_201_CREATED
    res_json = response.json()
    assert res_json["created_by"] == expected["created_by"]
    assert res_json["context"] == expected["context"]
    req = dt.strptime(res_json["published_date"], '%Y-%m-%d %H:%M:%S%z')
    res = dt.strptime(expected["published_date"], '%Y-%m-%d %H:%M:%S%z')
    assert req == res

    response = client.post('/news/',
                           json={'created_by': 'cb', 'context': 'ct'})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_invalid_news():
    response = client.post('/news/', data=json.dumps({'context': 'context2'}))
    assert response.status_code == 422


def test_read_news_by_id():
    payload = models.NewsSchema(created_by='single_object',
                                context='context single_object',
                                published_date='01-02-2023 13:14:15')
    #  insert database
    obj = insert_t_news(payload)

    # retrieve
    response = client.get(f'/news/{obj["id"]}')
    assert response.status_code == 200
    assert response.json()['id'] == obj['id']
    assert response.json()['created_by'] == obj['created_by']
    assert response.json()['context'] == obj['context']


def test_invalid_read_news_by_id():
    response = client.get('/news/44')
    assert response.status_code == 404
    assert response.json()['detail'] == 'News not found'

    response = client.get('/news/0')
    assert response.status_code == 422


def test_update_news():
    payload = {"created_by": "adnankaya_updated",
               "context": "context1_updated",
               "published_date": "01-22-2071 19:18:17"}

    response = client.put("/news/1/", data=json.dumps(payload))
    assert response.status_code == status.HTTP_200_OK
    res_json = response.json()
    assert res_json["created_by"] == payload["created_by"]
    assert res_json["context"] == payload["context"]
    req = dt.strptime(res_json["published_date"], '%Y-%m-%d %H:%M:%S%z')
    res = dt.strptime(payload["published_date"], '%m-%d-%Y %H:%M:%S')
    assert req.year == res.year
    assert req.month == res.month
    assert req.day == res.day
    assert req.hour == res.hour
    assert req.minute == res.minute
    assert req.second == res.second


@pytest.mark.parametrize(
    'id, payload, status_code',
    [
        [1, {}, 422],
        [1, {'context': 'var'}, 422],
        [44, {'created_by': 'adnan', 'context': 'context',
              'published_date': '12-19-2022 13:14:15'}, 404],
        [1, {'created_by': 'c', 'context': 'var'}, 422],
        [1, {'created_by': 'adnan', 'context': 'd'}, 422],
        [0, {'created_by': 'adnan', 'context': 'context'}, 422],
    ],
)
def test_update_invalid_news(id, payload, status_code):
    response = client.put(f'/news/{id}/', data=json.dumps(payload))
    assert response.status_code == status_code


def test_delete_news_by_id():
    payload = models.NewsSchema(created_by='deleteable_object',
                                context='context deleteable_object',
                                published_date='01-02-2023 13:14:15')
    # insert database
    obj = insert_t_news(payload)
    #  delete request
    response = client.delete(f'/news/{obj["id"]}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.text == ''

    response = client.delete('/news/0/')
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_invalid_delete_news_by_id():
    response = client.delete('/news/44/')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'News not found'
