from typing import Optional

import requests

from flask import Flask, jsonify, request
from flask_caching import Cache

config = {
    # Very simple in-memory cache. Cache will not
    # persist across container restarts.
    "CACHE_TYPE": "FileSystemCache",
    # Directory used by filesystem cache for storing
    # items.
    "CACHE_DIR": "/tmp/flask-cache",
    # Max number of items in the cache at any one
    # time. Items will begin to clear when this
    # limit is hit. Setting this basically turns
    # the cache into a LRU (least recently used)
    # cache.
    "CACHE_THRESHOLD": 100,
}

# Create the flask app
app = Flask(__name__)

# Configure the app
app.config.from_mapping(config)

# Create the cache
cache = Cache(app)


class RequestAbort(Exception):
    """
    Rasing this exception in an the flask applicaiton will
    result in the message string being passed back to the
    client as a json response.

    For example:
    >>> if some_condition():
    >>>    raise RequestAbort("some condition was not met", 400)

    Then the response the client will see is:
    {
        "error": "some condition was not met"
    }
    """

    def __init__(self, msg: str, status_code: int = 500):
        super(RequestAbort, self).__init__(msg)
        self.status_code = status_code


@app.errorhandler(RequestAbort)
def abort_errorhandler(e: RequestAbort):
    return (
        jsonify(
            {
                "error": str(e)
                or "An error occured while processing the request. Please try again later."
            }
        ),
        e.status_code,
    )


@cache.memoize()
def reverse_and_uppercase_str(s: str) -> str:
    """
    This function is by far the most critical part of this API.
    A whole lot of things can go wrong here. This function is cached
    in flask-caching in an attempt to limit the number of times this
    function is actually called.
    """

    # Reverse the string using the sushi operator
    reverse_s = s[::-1]

    # Attempt to connect to the shoutcloud api
    try:

        # There are a whole lot of bad things that could happen
        # here. All of the possible requests exceptions that
        # could be raised here are downstream of the
        # requests.exceptions.RequestException exception object.
        r = requests.post(
            "http://api.shoutcloud.io/V1/SHOUT",
            json={"INPUT": reverse_s},
            headers={"Content-Type": "application/json"},
            timeout=1,
        )

        # This will raise requests.exceptions.JSONDecodeError
        # if there is an issue parsing the response body
        data = r.json()

    # Catch any requests error
    except requests.exceptions.RequestException:
        raise RequestAbort("Failed to contact shoutcloud api")

    # Catch a json decode error
    except requests.exceptions.JSONDecodeError:
        raise RequestAbort("Shoutcloud failed to retun proper response")

    # Verify that the expected field is in the response, and
    # that it is of the proper type.
    if 'OUTPUT' not in data and isinstance(data['OUTPUT'], str):
        raise RequestAbort("shoutcloud api gave back bad response")

    return data["OUTPUT"]


@app.get("/health")
def health_view():
    """
    Endpoint for the health checks. All that is required
    is calling the core reverse_and_uppercase_str function,
    raising an unhandled exception if there is an issue.
    """
    assert reverse_and_uppercase_str("test") == "TSET"
    return "success"


@app.post("/")
@app.post("/v1")
@app.post("/v1/")
def index_view():
    """
    Main endpoint for the api. Will reverse and upper case any strings
    that are sent here. Given some ambiguity in the assignment spec, I am
    accepting both form and json data at this endpoint. In either case,
    send a data field with the string you would like modified.
    """

    # User specified data to be reversed and uppercased
    data: Optional[str] = None

    # Handle json requests
    if request.content_type == "application/json":
        data = request.json.get("data", None)

    # Handle form requests
    if request.content_type == "application/x-www-form-urlencoded":
        data = request.form.get("data", None)

    # Verify that there is actually data to
    if data is None or not isinstance(data, str):
        raise RequestAbort(
            "Data was not able to be parsed from request. Please try again.",
            400,
        )

    return jsonify({"data": reverse_and_uppercase_str(data)})


if __name__ == "__main__":
    app.run(debug=True)
