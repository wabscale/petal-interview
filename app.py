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
    >>>    raise RequestAbort("some condition was not met")

    Then the response the client will see is:
    {
        "error": "some condition was not met"
    }
    """


@app.errorhandler(RequestAbort)
def abort_errorhandler(e: RequestAbort):
    return (
        jsonify(
            {
                "error": str(e)
                or "An error occured while processing the request. Please try again later."
            }
        ),
        400,
    )


@cache.memoize()
def reverse_and_uppercase_str(s: str) -> str:
    reverse_s = s[::-1]

    r = requests.post(
        "http://api.shoutcloud.io/V1/SHOUT",
        json={"INPUT": reverse_s},
        headers={"Content-Type": "application/json"},
        timeout=1,
    )

    return r.json()["OUTPUT"]


@app.get("/health")
def health_view():
    assert reverse_and_uppercase_str("test") == "TSET"
    return "success"


@app.post("/")
@app.post("/v1")
@app.post("/v1/")
def index_view():
    data: Optional[str] = None

    # Handle json requests
    if request.content_type == "application/json":
        data = request.json.get("data", None)

    # Handle form requests
    if request.content_type == "application/x-www-form-urlencoded":
        data = request.form.get("data", None)

    if data is None:
        raise RequestAbort(
            "Data was not able to be parsed from request. Please try again."
        )

    return jsonify({"data": reverse_and_uppercase_str(data)})


if __name__ == "__main__":
    app.run(debug=True)
