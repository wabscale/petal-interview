import requests
import random

lorem_ipsum_phrases = [
    "Lorem ipsum dolor sit amet",
    "consectetur adipiscing elit",
    "sed do eiusmod tempor incididunt",
    "ut labore et dolore magna aliqua",
]


def reverse_and_uppercase_str(s: str) -> str:
    return s.upper()[::-1]


def test_app_json():
    word = "test"
    response = requests.post(
        "http://localhost:5000/",
        json={"data": word},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.json()["data"] == reverse_and_uppercase_str(word)


def test_app_form():
    word = "test"
    response = requests.post(
        "http://localhost:5000/",
        data={"data": word},
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response.json()["data"] == reverse_and_uppercase_str(word)


def test_app_lorem():
    for phrase in lorem_ipsum_phrases:
        response = requests.post(
            "http://localhost:5000/",
            json={"data": phrase},
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.json()["data"] == reverse_and_uppercase_str(phrase)


def test_app_bad_request_content_type():
    word = "test"
    response = requests.post(
        "http://localhost:5000/",
        json={"data": word},
        headers={"Content-Type": "application/aaaa"},
    )
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert (
        response.json()["error"]
        == "Data was not able to be parsed from request. Please try again."
    )


def test_app_json_no_data_field():
    response = requests.post(
        "http://localhost:5000/",
        json={},
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert (
        response.json()["error"]
        == "Data was not able to be parsed from request. Please try again."
    )


def test_app_form_no_data_field():
    response = requests.post(
        "http://localhost:5000/",
        data={},
    )
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"
    assert (
        response.json()["error"]
        == "Data was not able to be parsed from request. Please try again."
    )
