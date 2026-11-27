import json

from app.pipeline import run_pipeline


def _response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    route = event.get("routeKey", "")
    if route == "GET /health":
        return _response(200, {"status": "ok"})
    if route == "POST /predict":
        try:
            body = json.loads(event.get("body") or "{}")
            return _response(200, run_pipeline(body.get("text")))
        except ValueError as e:
            return _response(400, {"detail": str(e)})
    return _response(404, {"detail": "not found"})