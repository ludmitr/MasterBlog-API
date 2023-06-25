import os

import pytest
from backend import data_handler_json

def test_load_add_data():
    data_handler = data_handler_json.DataHandlerJson()
    assert data_handler.load_data() == []
    data_handler.add({"author": "dimon", "title": "test", "content": "test", "date":"2023-06-25"})
    blog = data_handler.load_data()
    assert blog[0]['author'] == "dimon"
    assert blog[0]['title'] == "test"
    assert blog[0]['content'] == "test"
    assert blog[0]['date'] == "2023-06-25"
    assert blog[0]['id'] == 1

    os.remove("blog_data.json")

def test_update_data():
    data_handler = data_handler_json.DataHandlerJson()
    data_handler.add({"author": "dimon", "title": "test", "content": "test",
                      "date": "2023-06-23"})

    post = {"author": "semen", "title": "update_test", "content": "update_test",
                      "date": "2023-06-24", "id": 1}
    assert data_handler.update_data(post) == post
    blog = data_handler.load_data()
    assert blog[0]['author'] == "semen"
    assert blog[0]['title'] == "update_test"
    assert blog[0]['content'] == "update_test"
    assert blog[0]['date'] == "2023-06-24"
    assert blog[0]['id'] == 1

    with pytest.raises(ValueError) as excinfo:
        post = {"author": "semen", "title": "update_test",
                "content": "update_test",
                "date": "2023-16-24", "id": 1}
        data_handler.update_data(post)
    assert str(excinfo.value) == "Incorrect date format, should be 'YYYY-MM-DD'"

    os.remove("blog_data.json")


def test_delete_post():
    data_handler = data_handler_json.DataHandlerJson()
    data_handler.add({"author": "dimon", "title": "test", "content": "test",
                      "date": "2023-06-23"})
    data_handler.add({"author": "kamon", "title": "test", "content": "test",
                      "date": "2013-06-23"})

    data_handler.delete_post(1)
    assert data_handler.load_data()[0]['id'] == 2

    os.remove("blog_data.json")

pytest.main()